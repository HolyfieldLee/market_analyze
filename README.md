# SODAM — 상권분석 앱 스캐폴드

이 저장소는 **프론트엔드(React/SwiftUI)** 와 **플라스크 백엔드**가 쉽게 연동되도록 뼈대를 제공합니다.

## 구조
```
backend/               # Flask API (로그인/회원가입/JWT, 추천 스코어)
  blueprints/          # api, auth, recs
  services/recsys.py   # 점수 계산 로직(임시)
  instance/app.db      # SQLite (자동 생성)
  requirements.txt
frontend/
  react/README.md      # React 연동 예시
  swiftui/README.md    # SwiftUI 연동 예시
  mock/index.html      # 임시 테스트 페이지
```

## 빠른 실행
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r backend/requirements.txt
python -m flask --app backend/wsgi.py run -p 5000
# 브라우저에서 frontend/mock/index.html 열어 테스트
```

## 주요 API
- `POST /api/auth/register` — 회원가입
- `POST /api/auth/login` — 로그인(JWT 발급)
- `GET /api/auth/me` — 내 정보(JWT 필요)
- `POST /api/recs/score` — 특징 → 점수/브레이크다운
- `GET /api/recs/sample` — 더미 상권 리스트 + 점수

프론트엔드는 **JSON**만 주고받으면 되며, CORS는 개발 편의를 위해 열어두었습니다.
실서비스에서는 도메인 화이트리스트를 설정하세요.
