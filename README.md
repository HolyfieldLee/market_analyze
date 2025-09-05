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

<img width="1165" height="892" alt="image" src="https://github.com/user-attachments/assets/627761b0-6e9a-45b1-b709-360308c8780c" />

<img width="1144" height="417" alt="image" src="https://github.com/user-attachments/assets/1f3d3feb-fe1d-4fa0-bac1-a19ccd6177eb" />

<img width="1203" height="775" alt="image" src="https://github.com/user-attachments/assets/731c1397-0e92-4451-a5d4-cf5634614abb" />

<img width="1225" height="681" alt="image" src="https://github.com/user-attachments/assets/7ea03ee9-a939-412c-be84-3f7da7b5eeb5" />

<img width="1209" height="662" alt="image" src="https://github.com/user-attachments/assets/54052f08-f1da-4c43-9ba6-d87116fd0fba" />

<img width="1209" height="662" alt="image" src="https://github.com/user-attachments/assets/d2326c35-6842-4be5-8281-ab4c30641592" />

<img width="1210" height="872" alt="image" src="https://github.com/user-attachments/assets/89a4ae0a-a642-4b70-ab11-d3489e796c76" />

<img width="956" height="613" alt="image" src="https://github.com/user-attachments/assets/cdf59f56-3481-4266-945e-5f0cb50fa42f" />

<img width="1021" height="1011" alt="image" src="https://github.com/user-attachments/assets/39f8b1b4-1ece-470c-bc01-7a05553a0c85" />

<img width="947" height="550" alt="image" src="https://github.com/user-attachments/assets/0a4cf416-d418-4ed6-b956-609350641b10" />
