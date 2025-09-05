"""
from typing import Dict, Any

DEFAULT_WEIGHTS = {
    "foot_traffic": 0.35,
    "competitors_500m": -0.25,
    "avg_income": 0.20,
    "rent_cost": -0.10,
    "age_20s_ratio": 0.10
}

def compute_score(features: Dict[str, float], weights: Dict[str, float] = None) -> Dict[str, Any]:
    w = weights or DEFAULT_WEIGHTS
    breakdown = {}
    total = 0.0
    for k, weight in w.items():
        x = float(features.get(k, 0.0))
        contrib = x * weight
        breakdown[k] = {"value": x, "weight": weight, "contrib": contrib}
        total += contrib

    # Normalize to 0~100 for frontends
    normalized = max(0.0, min(100.0, (total + 1.0) * 50.0))  # crude scaling
    return {"score": round(normalized, 2), "breakdown": breakdown}
"""
# backend/blueprints/recs.py
from flask import Blueprint, request, jsonify

# 50업종 로직 (있으면 사용)
try:
    from ..services.recs_profiles import compute_profile_score, compute_profile_score_batch
    HAS_PROFILES = True
except Exception:
    HAS_PROFILES = False

# 폴백(기본 가중치 방식)
from ..services.recsys import compute_score as fallback_single

recs_bp = Blueprint("recs", __name__)

@recs_bp.post("/score")
def score():
    """
    단일 상권 점수화.
    body:
    {
      "biz_type": "베이커리",     # 선택. 있으면 50업종 로직 사용
      "features": { ... }         # 0~1 또는 0~100 비율 허용. 소득은 avg_income 또는 income_percentile
    }
    """
    data = request.get_json() or {}
    biz = data.get("biz_type")
    features = data.get("features") or {}

    if HAS_PROFILES and biz:
        try:
            res = compute_profile_score(features, biz)
            return jsonify(res), 200
        except Exception as e:
            # 문제 있으면 폴백
            pass

    # 폴백: 단순 가중치 방식
    res = fallback_single(features)
    return jsonify(res), 200

@recs_bp.post("/batch")
def batch():
    """
    여러 상권 일괄 점수화.
    body:
    {
      "biz_type": "루프탑 술집",   # 선택. 있으면 50업종 로직 사용(배치 퍼센타일 자동 계산)
      "items": [
        {"id":"A001","name":"...","lat":..,"lon":..,"features":{...}},
        ...
      ]
    }
    """
    data = request.get_json() or {}
    biz = data.get("biz_type")
    items = data.get("items") or []

    if HAS_PROFILES and biz:
        try:
            res = compute_profile_score_batch(items, biz)
            return jsonify({"items": res}), 200
        except Exception:
            pass

    # 폴백: 개별로 fallback_single 호출
    out = []
    for it in items:
        feat = it.get("features") or {}
        res = fallback_single(feat)
        out.append({**{k: v for k, v in it.items() if k != "features"}, **res})
    return jsonify({"items": out}), 200
