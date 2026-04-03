# Maple Guild Chat Frontend

React + Vite 기반의 최소 프론트엔드입니다.

## 포함 기능

- 로그인
- 회원가입
- 메인 실시간 채팅 페이지
- Socket.IO 기반 채팅 연결

## 주요 라우트

- /login
- /register
- /

## 실행 방법

```bash
npm install
npm run dev
```

개발 서버 기본 주소는 http://localhost:5173 입니다.

## 환경 변수

```env
VITE_API_URL=http://localhost:8000
VITE_API_PORT=8000
```

## 현재 구조

```text
frontend/
├── src/
│   ├── components/
│   │   └── RealtimeChatPanel.jsx
│   ├── config/
│   │   └── api.js
│   ├── hooks/
│   │   ├── useLogin.js
│   │   └── useRegister.js
│   ├── pages/
│   │   ├── Login/
│   │   ├── Register/
│   │   └── RealtimeChatPage.jsx
│   ├── App.jsx
│   └── main.jsx
├── vite.config.js
└── package.json
```
