# backend/services/recs_profiles.py
from __future__ import annotations
from typing import Dict, Any, List
import math

# ========== 유틸: 스케일/커브 ==========
def _clip01(v: float) -> float:
    if v is None or math.isnan(v):
        return 0.0
    return max(0.0, min(100.0, float(v)))

def _to_percent(x) -> float:
    """0~1 비율은 0~100으로, 이미 0~100은 그대로."""
    if x is None:
        return 0.0
    try:
        x = float(x)
    except Exception:
        return 0.0
    return x * 100.0 if 0.0 <= x <= 1.0 else x

def ramp_up(x, start, end):
    """start 이하는 0, end 이상은 100, 그 사이는 선형 증가"""
    if end <= start:  # 가드
        return _clip01(0.0)
    return _clip01((x - start) / (end - start) * 100.0)

def ramp_down(x, start, end):
    """start 이하는 100, end 이상은 0, 그 사이는 선형 감소"""
    if end <= start:
        return _clip01(0.0)
    return _clip01(100.0 - (x - start) / (end - start) * 100.0)

def band_pref(x, low, high, width=15):
    """
    [low, high] 구간은 100점, 양쪽으로 width만큼 선형 하락해 0점.
    """
    left0, right0 = low - width, high + width
    if x < left0:
        return 0.0
    if x < low:
        return _clip01((x - left0) / (low - left0) * 100.0)
    if x <= high:
        return 100.0
    if x <= right0:
        return _clip01((right0 - x) / (right0 - high) * 100.0)
    return 0.0

# ========== 기반 점수(100점) 구성 ==========
def _base_score_from_features(feat: Dict[str, float]) -> float:
    """
    features dict로부터 기반 점수(100점)를 구성.
    사용 키(있으면 사용, 없으면 스킵):
      - foot_traffic (높을수록 +)
      - competitors_500m (높을수록 -)  → 100 - 값
      - rent_cost (높을수록 -)         → 100 - 값
      - access_score 또는 accessibility (높을수록 +)
    값은 0~1 또는 0~100 모두 허용 (내부에서 0~100으로 통일)
    """
    parts = []

    def val(key):
        if key in feat:
            return _clip01(_to_percent(feat.get(key)))
        return None

    ft = val("foot_traffic")
    if ft is not None: parts.append(ft)

    comp = val("competitors_500m")
    if comp is not None: parts.append(100.0 - comp)

    rent = val("rent_cost")
    if rent is not None: parts.append(100.0 - rent)

    acc = val("access_score") if "access_score" in feat else val("accessibility")
    if acc is not None: parts.append(acc)

    if not parts:
        return 0.0
    return sum(parts) / len(parts)

def _income_percentile_from_features(feat: Dict[str, float]) -> float:
    """
    소득 퍼센타일(0~100)을 얻는다.
    우선순위:
      1) income_percentile / avg_income_percentile / income_pct 필드가 있으면 사용
      2) income_min & income_max 제공 시 min-max로 0~100 스케일
      3) avg_income(혹은 average_income)이 0~100 범위면 그대로 사용(이미 퍼센트로 간주)
      4) 위가 모두 없으면 50(중앙)로 폴백
    배치 API에서는 recs.py에서 미리 percentile을 계산해 features["income_percentile"]에 넣어주길 권장.
    """
    for key in ("income_percentile", "avg_income_percentile", "income_pct"):
        if key in feat:
            return _clip01(feat.get(key))

    income = feat.get("avg_income", feat.get("average_income"))
    min_v = feat.get("income_min")
    max_v = feat.get("income_max")
    if income is not None and min_v is not None and max_v is not None:
        try:
            income = float(income); min_v = float(min_v); max_v = float(max_v)
            if max_v > min_v:
                return _clip01((income - min_v) / (max_v - min_v) * 100.0)
        except Exception:
            pass

    if income is not None:
        val = _to_percent(income)
        # 값이 0~100 범위면 그 자체를 퍼센타일로 간주 (데이터 전처리에서 스케일링했다고 가정)
        if 0.0 <= val <= 100.0:
            return _clip01(val)

    return 50.0  # 정보 없으면 중간값

def _demo_from_features(feat: Dict[str, float]) -> Dict[str, float]:
    """
    성별/연령 파생:
      - 남성(%) / 여성(%) : 둘 중 하나만 있으면 100-값으로 보완
      - 20~30대(%) : age_20s_ratio + age_30s_ratio
      - 40~60대(%) : age_40s_ratio + age_50s_ratio + age_60s_ratio
    """
    male = feat.get("male_ratio")
    female = feat.get("female_ratio")
    male_p = _clip01(_to_percent(male)) if male is not None else None
    female_p = _clip01(_to_percent(female)) if female is not None else None
    if male_p is None and female_p is None:
        male_p, female_p = 50.0, 50.0
    elif male_p is None:
        male_p = _clip01(100.0 - female_p)
    elif female_p is None:
        female_p = _clip01(100.0 - male_p)

    a20 = _clip01(_to_percent(feat.get("age_20s_ratio", 0.0)))
    a30 = _clip01(_to_percent(feat.get("age_30s_ratio", 0.0)))
    a40 = _clip01(_to_percent(feat.get("age_40s_ratio", 0.0)))
    a50 = _clip01(_to_percent(feat.get("age_50s_ratio", 0.0)))
    a60 = _clip01(_to_percent(feat.get("age_60s_ratio", 0.0)))

    a2030 = _clip01(a20 + a30)
    a4060 = _clip01(a40 + a50 + a60)

    return {
        "male": male_p,
        "female": female_p,
        "a2030": a2030,
        "a4060": a4060,
    }

# ========== PROFILES 빌더 ==========
PROFILES: Dict[str, Dict[str, Any]] = {}
def add_profile(name, w_base, w_income, w_age, w_gender, income_fn, age_fn, gender_fn):
    PROFILES[name] = {
        "weights": {"base": w_base, "income": w_income, "age": w_age, "gender": w_gender},
        "income_fn": income_fn,  # lambda p: ...
        "age_fn": age_fn,        # lambda a2030: ...  또는  lambda a4060: ...
        "gender_fn": gender_fn,  # lambda m,f: ...
    }

# ===== 50개 업종 추가 (완전판) =====
# 1~5
add_profile("베이커리", 0.50,0.15,0.25,0.10,
            lambda p: ramp_up(p,50,85),
            lambda a2030: a2030,
            lambda m,f: f)
add_profile("국밥집", 0.50,0.25,0.20,0.05,
            lambda p: ramp_down(p,30,60),
            lambda a4060: a4060,
            lambda m,f: m)
add_profile("루프탑 술집", 0.50,0.20,0.25,0.05,
            lambda p: band_pref(p,60,90,20),
            lambda a2030: a2030,
            lambda m,f: _clip01(100 - abs(m-50)*2))
add_profile("철물점", 0.60,0.10,0.20,0.10,
            lambda p: ramp_down(p,40,70),
            lambda a4060: a4060,
            lambda m,f: m)
add_profile("식료품점", 0.50,0.20,0.20,0.10,
            lambda p: ramp_down(p,30,60),
            lambda a4060: a4060,
            lambda m,f: f)

# 6~10
add_profile("편의점", 0.50,0.15,0.25,0.10,
            lambda p: band_pref(p,40,70,20),
            lambda a2030: a2030,
            lambda m,f: _clip01(100 - abs(m-50)*2))
add_profile("카페", 0.50,0.20,0.20,0.10,
            lambda p: ramp_up(p,55,85),
            lambda a2030: a2030,
            lambda m,f: f)
add_profile("분식집", 0.50,0.10,0.30,0.10,
            lambda p: ramp_down(p,30,60),
            lambda a2030: a2030,
            lambda m,f: f)
add_profile("치킨호프", 0.50,0.15,0.25,0.10,
            lambda p: band_pref(p,45,70,20),
            lambda a2030: a2030,
            lambda m,f: m)
add_profile("중식당", 0.55,0.15,0.20,0.10,
            lambda p: band_pref(p,45,70,20),
            lambda a4060: a4060,
            lambda m,f: m)

# 11~15
add_profile("일식집", 0.50,0.25,0.15,0.10,
            lambda p: ramp_up(p,55,90),
            lambda a2030: a2030,
            lambda m,f: _clip01(100 - abs(m-50)*2))
add_profile("고급 레스토랑", 0.50,0.35,0.10,0.05,
            lambda p: ramp_up(p,70,95),
            lambda a2030: a2030,
            lambda m,f: _clip01(100 - abs(m-50)*2))
add_profile("패스트푸드점", 0.50,0.15,0.25,0.10,
            lambda p: band_pref(p,40,70,20),
            lambda a2030: a2030,
            lambda m,f: _clip01(100 - abs(m-50)*2))
add_profile("피자집", 0.50,0.15,0.25,0.10,
            lambda p: band_pref(p,45,70,20),
            lambda a2030: a2030,
            lambda m,f: _clip01(100 - abs(m-50)*2))
add_profile("아이스크림 전문점", 0.45,0.15,0.30,0.10,
            lambda p: band_pref(p,45,70,20),
            lambda a2030: a2030,
            lambda m,f: f)

# 16~20
add_profile("술집(일반포차)", 0.50,0.15,0.25,0.10,
            lambda p: band_pref(p,45,70,20),
            lambda a2030: a2030,
            lambda m,f: m)
add_profile("와인바", 0.50,0.30,0.15,0.05,
            lambda p: ramp_up(p,60,90),
            lambda a2030: a2030,
            lambda m,f: f)
add_profile("노래방", 0.50,0.10,0.30,0.10,
            lambda p: band_pref(p,40,70,20),
            lambda a2030: a2030,
            lambda m,f: _clip01(100 - abs(m-50)*2))
add_profile("PC방", 0.50,0.10,0.30,0.10,
            lambda p: ramp_down(p,30,60),
            lambda a2030: a2030,
            lambda m,f: m)
add_profile("코인노래방", 0.45,0.10,0.35,0.10,
            lambda p: ramp_down(p,30,60),
            lambda a2030: a2030,
            lambda m,f: _clip01(100 - abs(m-50)*2))

# 21~25
add_profile("오락실", 0.50,0.10,0.30,0.10,
            lambda p: ramp_down(p,30,60),
            lambda a2030: a2030,
            lambda m,f: m)
add_profile("학원(보습/입시)", 0.55,0.25,0.15,0.05,
            lambda p: ramp_up(p,55,90),
            lambda a2030: a2030,
            lambda m,f: _clip01(100 - abs(m-50)*2))
add_profile("어린이집", 0.55,0.25,0.15,0.05,
            lambda p: band_pref(p,55,85,15),
            lambda a2030: a2030,
            lambda m,f: f)
add_profile("학원(성인/직장인)", 0.50,0.30,0.15,0.05,
            lambda p: ramp_up(p,55,90),
            lambda a2030: a2030,
            lambda m,f: _clip01(100 - abs(m-50)*2))
add_profile("체육관(헬스장)", 0.50,0.15,0.25,0.10,
            lambda p: band_pref(p,45,75,20),
            lambda a2030: a2030,
            lambda m,f: m)

# 26~30
add_profile("요가/필라테스", 0.50,0.25,0.15,0.10,
            lambda p: ramp_up(p,55,90),
            lambda a2030: a2030,
            lambda m,f: f)
add_profile("뷰티샵(미용실)", 0.55,0.15,0.20,0.10,
            lambda p: band_pref(p,45,75,20),
            lambda a2030: a2030,
            lambda m,f: f)
add_profile("네일샵", 0.50,0.25,0.15,0.10,
            lambda p: ramp_up(p,55,90),
            lambda a2030: a2030,
            lambda m,f: f)
add_profile("이발소", 0.55,0.15,0.20,0.10,
            lambda p: ramp_down(p,35,65),
            lambda a4060: a4060,
            lambda m,f: m)
add_profile("안경점", 0.55,0.15,0.20,0.10,
            lambda p: band_pref(p,45,75,20),
            lambda a2030: a2030,
            lambda m,f: _clip01(100 - abs(m-50)*2))

# 31~35
add_profile("병원(내과/소아과)", 0.60,0.15,0.15,0.10,
            lambda p: band_pref(p,45,80,20),
            lambda a2030: a2030,
            lambda m,f: _clip01(100 - abs(m-50)*2))
add_profile("치과", 0.55,0.25,0.10,0.10,
            lambda p: ramp_up(p,55,90),
            lambda a2030: a2030,
            lambda m,f: _clip01(100 - abs(m-50)*2))
add_profile("약국", 0.60,0.15,0.15,0.10,
            lambda p: band_pref(p,45,75,20),
            lambda a4060: a4060,
            lambda m,f: f)
add_profile("세탁소", 0.55,0.15,0.20,0.10,
            lambda p: band_pref(p,45,70,20),
            lambda a4060: a4060,
            lambda m,f: f)
add_profile("꽃집", 0.50,0.25,0.15,0.10,
            lambda p: ramp_up(p,55,90),
            lambda a2030: a2030,
            lambda m,f: f)

# 36~40
add_profile("서점", 0.50,0.20,0.20,0.10,
            lambda p: ramp_up(p,50,85),
            lambda a2030: a2030,
            lambda m,f: _clip01(100 - abs(m-50)*2))
add_profile("문구점", 0.50,0.10,0.30,0.10,
            lambda p: ramp_down(p,35,65),
            lambda a2030: a2030,
            lambda m,f: f)
add_profile("반려동물샵", 0.50,0.25,0.15,0.10,
            lambda p: ramp_up(p,55,90),
            lambda a2030: a2030,
            lambda m,f: f)
add_profile("가구점", 0.50,0.25,0.15,0.10,
            lambda p: ramp_up(p,60,90),
            lambda a4060: a4060,
            lambda m,f: _clip01(100 - abs(m-50)*2))
add_profile("전자제품 매장", 0.50,0.25,0.15,0.10,
            lambda p: ramp_up(p,60,90),
            lambda a2030: a2030,
            lambda m,f: m)

# 41~45
add_profile("전통시장 점포", 0.55,0.15,0.20,0.10,
            lambda p: ramp_down(p,30,60),
            lambda a4060: a4060,
            lambda m,f: f)
add_profile("푸드트럭", 0.45,0.20,0.25,0.10,
            lambda p: ramp_down(p,30,60),
            lambda a2030: a2030,
            lambda m,f: _clip01(100 - abs(m-50)*2))
add_profile("중고매장(리세일샵)", 0.50,0.15,0.25,0.10,
            lambda p: ramp_down(p,35,65),
            lambda a2030: a2030,
            lambda m,f: _clip01(100 - abs(m-50)*2))
add_profile("골프연습장", 0.55,0.30,0.10,0.05,
            lambda p: ramp_up(p,65,95),
            lambda a4060: a4060,
            lambda m,f: m)
add_profile("클라이밍장", 0.50,0.20,0.25,0.05,
            lambda p: ramp_up(p,50,85),
            lambda a2030: a2030,
            lambda m,f: _clip01(100 - abs(m-50)*2))

# 46~50
add_profile("헌책방", 0.55,0.10,0.25,0.10,
            lambda p: ramp_down(p,35,65),
            lambda a2030: a2030,
            lambda m,f: m)
add_profile("사진관", 0.50,0.20,0.20,0.10,
            lambda p: ramp_up(p,50,85),
            lambda a2030: a2030,
            lambda m,f: f)
add_profile("코워킹 스페이스", 0.50,0.25,0.20,0.05,
            lambda p: ramp_up(p,55,90),
            lambda a2030: a2030,
            lambda m,f: _clip01(100 - abs(m-50)*2))
add_profile("공유주방", 0.50,0.20,0.20,0.10,
            lambda p: ramp_up(p,50,85),
            lambda a2030: a2030,
            lambda m,f: _clip01(100 - abs(m-50)*2))
add_profile("전통찻집", 0.50,0.25,0.15,0.10,
            lambda p: ramp_up(p,55,90),
            lambda a4060: a4060,
            lambda m,f: f)

# ========== 단일/배치 점수 계산 ==========
def compute_profile_score(features: Dict[str, float], biz_type: str) -> Dict[str, Any]:
    """
    features 예시 키:
      foot_traffic, competitors_500m, rent_cost, access_score,
      avg_income 또는 income_percentile,
      age_20s_ratio, age_30s_ratio, age_40s_ratio, age_50s_ratio, age_60s_ratio,
      male_ratio, female_ratio
    """
    if biz_type not in PROFILES:
        raise ValueError(f"Unknown biz_type: {biz_type}")

    prof = PROFILES[biz_type]
    w = prof["weights"]

    base = _base_score_from_features(features)
    income_pct = _income_percentile_from_features(features)
    demo = _demo_from_features(features)
    a2030, a4060 = demo["a2030"], demo["a4060"]
    m, f = demo["male"], demo["female"]

    # age_fn이 a2030을 받는지 a4060을 받는지 간단히 구분
    age_fn = prof["age_fn"]
    try:
        param_names = age_fn.__code__.co_varnames[:age_fn.__code__.co_argcount]
    except Exception:
        param_names = ()
    age_score = age_fn(a4060) if ("a4060" in param_names) else age_fn(a2030)

    income_score = prof["income_fn"](income_pct)
    gender_score = prof["gender_fn"](m, f)

    # clip
    base = _clip01(base)
    income_score = _clip01(income_score)
    age_score = _clip01(age_score)
    gender_score = _clip01(gender_score)

    final = (
        w["base"]   * base +
        w["income"] * income_score +
        w["age"]    * age_score +
        w["gender"] * gender_score
    )
    return {
        "score": round(final, 1),
        "breakdown": {
            "base": round(base, 1),
            "income": round(income_score, 1),
            "age": round(age_score, 1),
            "gender": round(gender_score, 1),
            "weights": w
        }
    }

def compute_profile_score_batch(items: List[Dict[str, Any]], biz_type: str) -> List[Dict[str, Any]]:
    """
    items: [{ "id":..., "name":..., "features": { "avg_income": ..., ... } }, ...]
    배치에서 avg_income이 있을 경우, 이 함수가 **동일 배치 내 퍼센타일**을 계산해
    features["income_percentile"]로 주입한 뒤 점수화합니다.
    """
    # 1) 배치 소득 퍼센타일
    incomes = []
    for it in items:
        feat = it.get("features") or {}
        if "income_percentile" in feat:
            continue
        income = feat.get("avg_income", feat.get("average_income"))
        if income is not None:
            try:
                incomes.append(float(income))
            except Exception:
                pass
    pmin = min(incomes) if incomes else None
    pmax = max(incomes) if incomes else None

    def to_pct(v: float) -> float:
        if pmin is not None and pmax is not None and pmax > pmin:
            return _clip01((float(v) - pmin) / (pmax - pmin) * 100.0)
        # fallbacks
        vv = _to_percent(v)
        return _clip01(vv if 0.0 <= vv <= 100.0 else 50.0)

    # 2) 각 아이템 점수화
    out = []
    for it in items:
        feat = dict(it.get("features") or {})
        if "income_percentile" not in feat:
            inc = feat.get("avg_income", feat.get("average_income"))
            if inc is not None:
                feat["income_percentile"] = to_pct(inc)
        res = compute_profile_score(feat, biz_type)
        out.append({**{k: v for k, v in it.items() if k != "features"}, **res})
    return out
