# -*- coding: utf-8 -*-
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine
from routers.auth.minimal_router import router as auth_router
from routers.websocket.websocket_events import websocket_app


app = FastAPI(title="Maple Guild Chat API", version="1.0.0")

# 로그인/커뮤니티에서 필요한 테이블 자동 생성
Base.metadata.create_all(bind=engine)

cors_origins_env = os.getenv("CORS_ALLOW_ORIGINS", "")
cors_origins = [origin.strip() for origin in cors_origins_env.split(",") if origin.strip()]
if not cors_origins:
    cors_origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_origin_regex=r"^https?://(?:\d{1,3}\.){3}\d{1,3}(?::\d+)?$",
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 로그인/회원가입/로그아웃 API
app.include_router(auth_router)

# Redis 기반 Socket.IO 통합
app.mount("/socket.io", websocket_app)


@app.get("/")
def root():
    return {"message": "Maple Guild Chat 서버 실행 중"}


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    reload_enabled = os.getenv("UVICORN_RELOAD", "false").lower() == "true"
    workers = int(os.getenv("UVICORN_WORKERS", "1"))

    if reload_enabled:
        uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    else:
        uvicorn.run("main:app", host="0.0.0.0", port=8000, workers=max(1, workers))
