# Maple Guild Chat Backend

FastAPI 기반의 최소 인증 + 실시간 채팅 백엔드입니다.

## 주요 기능

- 회원가입, 로그인, 로그아웃, 세션 검증
- MariaDB 기반 사용자/세션 저장
- Socket.IO 기반 실시간 채팅
- Redis 사용 가능 시 멀티 인스턴스 온라인 상태 공유

## 로컬 실행

```bash
cd maple/backend
pip install -r requirements.txt
copy .env.example .env
python main.py
```

기본 접속 주소:

- API: http://localhost:8000
- 문서: http://localhost:8000/docs

## 필수 환경 변수

```env
DB_HOST=127.0.0.1
DB_PORT=3306
DB_USER=app_user
DB_PASSWORD=app_password
DB_NAME=maple_guild_app

CORS_ALLOW_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
USE_REDIS=false
REDIS_URL=redis://127.0.0.1:6379/0
DB_POOL_SIZE=3
DB_MAX_OVERFLOW=2
DB_POOL_RECYCLE=1800
DB_CONNECT_TIMEOUT=10
CHAT_MAX_MESSAGE_LENGTH=500
UVICORN_WORKERS=1
UVICORN_RELOAD=false
```

## Cloudtype 배포 메모

- Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
- Working Directory: backend
- Python Version: 3.11 권장
- DB는 Cloudtype MariaDB 또는 외부 MariaDB를 연결
- Redis가 없으면 in-memory 모드로도 동작하지만 멀티 인스턴스 채팅 동기화는 되지 않음

### Cloudtype DB 주소 기준

- 로컬 PC 또는 DBeaver에서 Cloudtype DB에 접속할 때: `svc.sel3.cloudtype.app:30421`
- Cloudtype에 배포된 backend가 같은 프로젝트의 MariaDB에 붙을 때: `mariadb:3306`
- 앱 연결 계정은 `root`가 아니라 `maple_app` 같은 서비스 전용 계정을 사용
- MariaDB는 HTTP URL이 아니라 TCP 기반이라서 backend 설정은 `DB_HOST`/`DB_PORT` 방식이 기본이며, 원하면 `DATABASE_URL` 한 줄로도 설정 가능

## 운영 보안 체크

- CORS_ALLOW_ORIGINS는 실제 프론트 주소만 허용 (와일드카드 사용 금지)
- DB 비밀번호와 세션 관련 값은 환경 변수로만 관리
- 배포 전/후 DB 비밀번호 주기적 교체
- 로그에 비밀번호, 세션 토큰 출력 금지

## 법적 최소 체크

- 회원가입 화면에 개인정보 수집 및 이용 안내 문구 제공
- 운영자 연락처와 탈퇴/데이터 삭제 요청 방법 제공
- 서비스 목적 외 개인정보 저장 금지 (본 프로젝트는 최소 수집 구조)
- 미성년자 대상 서비스라면 별도 동의/고지 정책 검토

## 핵심 API

- POST /auth/register
- POST /auth/login
- POST /auth/logout
- GET /auth/check-id
- GET /auth/sessions/validate
- /socket.io
