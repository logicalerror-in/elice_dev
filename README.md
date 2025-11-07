# elice_dev — FastAPI 백엔드 과제

## 3줄 요약
1) `docker-compose up -d --build` 한 번으로 **Postgres / Redis / API** 기동  
2) 스모크 테스트: `signup → login → me → refresh → logout` 순서로 호출  
3) 인증 전략: **짧은 Access JWT + Redis기반 Refresh 회전(J1)**, 로그아웃 시 **현재 기기만** 무효화

---

## 기술 스택 & 핵심 구현
- **FastAPI (Python 3.11)**  
- **PostgreSQL 13** + SQLAlchemy(Async) + `asyncpg`  
  - 과제 범위: 앱 기동 시 `create_all()`로 스키마 자동 생성  
- **Redis**  
  - Refresh 토큰 저장소 + **회전(rotation)**  
  - 기기별 세션 분리(동일 계정의 여러 기기 동시 사용 가능)  
- **JWT**  
  - Access: 헤더(`Authorization: Bearer <token>`)  
  - Refresh: 기본 **HTTP-Only 쿠키**, 필요 시 요청 플래그로 **바디 반환**도 지원  
- **보안/검증**  
  - `passlib[bcrypt]` 비밀번호 해시(72바이트 제한에 맞춘 사전 검증)  
  - Pydantic v2 스키마 검증  
- **에러 처리**  
  - FastAPI 표준 `HTTPException` 기반 상태코드/메시지 일관화  
- **트랜잭션**  
  - 쓰기 작업은 async 세션 단위 커밋/롤백  
- **CORS**  
  - `.env`의 `CORS_ORIGINS`로 제어(개발 편의 `*` 또는 CSV 입력)  
- **헬스체크**  
  - `GET /` → `{"status":"ready"}`

---

## 로컬 실행 (Docker 권장)

### 요구사항
- macOS + Docker(Colima/Docker Desktop 등)
- 포트:
  - API: `127.0.0.1:8000`
  - Postgres: `127.0.0.1:25000 → 5432`
  - Redis: `127.0.0.1:25100 → 6379`

### 1) 환경변수 파일 `.env`
`.env.example`를 참고해 `.env`를 생성하세요.

```ini
# App
APP_ENV=dev

# DB & Redis
DATABASE_URL=postgresql+asyncpg://developer:devpassword@postgres:5432/developer
REDIS_URL=redis://redis:6379/0

# JWT
JWT_SECRET=change-me
JWT_ALG=HS256
ACCESS_MIN=15
REFRESH_DAYS=14

# CORS: "*" 또는 CSV
CORS_ORIGINS=*
# 예: CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:5173

# Refresh를 쿠키로 반환할지 여부(기본 true)
REFRESH_IN_COOKIE=true
```2) 서비스 기동/중지
bash
코드 복사
# 빌드 + 백그라운드 기동
docker-compose up -d --build

# 애플리케이션 로그
docker-compose logs -f app

# 전체 중지
docker-compose down
# 볼륨까지 초기화(필요 시)
docker-compose down -v
기동 후 API 기본 주소: http://localhost:8000

API 스모크 테스트 (cURL)
0) 헬스체크
bash
코드 복사
curl -s http://localhost:8000/
# {"status":"ready"}
1) 회원가입
bash
코드 복사
POST /api/v1/auth/signup
bash
코드 복사
curl -i -X POST http://localhost:8000/api/v1/auth/signup \
  -H 'Content-Type: application/json' \
  -d '{"email":"user1@example.com","password":"p@ssw0rd","name":"User One"}'
2) 로그인 (Access + Refresh)
bash
코드 복사
POST /api/v1/auth/login
기본: Refresh는 HttpOnly 쿠키로 반환

필요 시 바디로도 받기: return_refresh_in_body=true

bash
코드 복사
# 쿠키 저장(-c)
curl -i -c cookies.txt -X POST http://localhost:8000/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"user1@example.com","password":"p@ssw0rd","return_refresh_in_body":true}'
응답 예시

json
코드 복사
{
  "access_token": "<JWT>",
  "token_type": "bearer",
  "user": {"id":1,"email":"user1@example.com","name":"User One"},
  "refresh_token": "<선택: 바디 반환 시 포함>"
}
3) 내 정보(me)
bash
코드 복사
GET /api/v1/auth/me
bash
코드 복사
ACCESS="<위 로그인 응답의 access_token>"
curl -i http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer $ACCESS"
4) 토큰 리프레시 (Refresh 회전)
bash
코드 복사
POST /api/v1/auth/refresh
쿠키 기반(권장):

bash
코드 복사
curl -i -b cookies.txt -X POST http://localhost:8000/api/v1/auth/refresh
바디 기반도 지원:

bash
코드 복사
# curl -i -X POST http://localhost:8000/api/v1/auth/refresh \
#   -H 'Content-Type: application/json' \
#   -d '{"refresh_token":"<로그인 시 발급받은 refresh_token>"}'
5) 로그아웃 (현재 기기만)
bash
코드 복사
POST /api/v1/auth/logout
bash
코드 복사
curl -i -b cookies.txt -X POST http://localhost:8000/api/v1/auth/logout
설계 노트 (요약)
JWT + Redis (J1)
Access: 짧은 만료, 헤더 사용

Refresh: Redis에 세션 키로 저장(기기/브라우저 별 분리), 회전(rotation)

로그아웃: 현재 기기의 Refresh만 즉시 폐기(다른 기기 세션에 영향 없음)

트랜잭션 & 예외
가입/로그인 등 쓰기 작업은 async 세션 범위에서 커밋/롤백

실패 시 HTTPException으로 적절한 코드/메시지 반환

CORS
개발 중 전체 허용: CORS_ORIGINS=*

특정만 허용(CSV): CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:5173

주요 파일 구조
bash
코드 복사
app/
 ├─ main.py                 # 앱 부팅, lifespan, 라우터 등록, CORS
 ├─ api/v1/auth.py          # 인증/인가 엔드포인트
 ├─ core/config.py          # 설정(ENV 읽기, CORS 파싱)
 ├─ core/security.py        # JWT 생성/검증, 비밀번호 해시
 ├─ db/session.py           # Async 엔진/세션 팩토리
 ├─ db/base.py              # Base 선언 및 모델 등록
 ├─ models/user.py          # User 모델
 ├─ schemas/auth.py         # Pydantic 스키마
 └─ services/
     ├─ auth.py             # 가입/로그인/리프레시/로그아웃 서비스 로직
     └─ refresh_store.py    # Redis에 Refresh 세션 관리
라이선스
이 저장소는 과제 제출용으로 제작되었습니다.