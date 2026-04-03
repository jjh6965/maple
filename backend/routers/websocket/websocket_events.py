import uuid
import os
from datetime import datetime

from database import User, UserSession, get_db

from . import websocket_runtime as runtime
from .websocket_services import (
    broadcast_online_users,
    load_past_messages,
    persist_message,
    update_redis_online,
)

MAX_MESSAGE_LENGTH = int(os.getenv("CHAT_MAX_MESSAGE_LENGTH", "500"))


def resolve_user_name(user_id: str) -> str:
    normalized_id = str(user_id)

    online_name = runtime.online_users_local.get(normalized_id)
    if online_name:
        runtime.user_names_cache[normalized_id] = online_name
        return online_name

    cached_name = runtime.user_names_cache.get(normalized_id)
    if cached_name:
        return cached_name

    db = next(get_db())
    try:
        user = db.query(User).filter(User.id == int(normalized_id)).first()
        if user and user.username:
            runtime.user_names_cache[normalized_id] = user.username
            return user.username
    except Exception as exc:
        runtime.log("WARNING", f"사용자명 조회 실패(user_id={normalized_id}): {exc}")
    finally:
        db.close()

    return normalized_id


# ==================== 연결 이벤트 ====================
@runtime.sio.event
async def connect(sid, environ, auth=None):
    session_token = (auth or {}).get("session_token")
    if not session_token:
        await runtime.sio.disconnect(sid)
        return

    db = next(get_db())
    try:
        session_record = db.query(UserSession).filter(
            UserSession.session_token == session_token,
            UserSession.is_active == True,
        ).first()

        if not session_record:
            runtime.log("WARNING", "세션 없음/비활성 → 연결 거부")
            await runtime.sio.disconnect(sid)
            return

        if session_record.expires_at and datetime.utcnow() > session_record.expires_at:
            session_record.is_active = False
            db.commit()
            runtime.log("WARNING", "세션 만료 → 연결 거부")
            await runtime.sio.disconnect(sid)
            return

        user = db.query(User).filter(User.id == session_record.user_id).first()
        if not user:
            runtime.log("WARNING", "유저 없음 → 연결 거부")
            await runtime.sio.disconnect(sid)
            return

        user_id = str(user.id)
        name = user.username
        role = str(getattr(user, "role", "user") or "user")

        runtime.sid_to_user[sid] = user_id
        runtime.sid_to_role[sid] = role
        runtime.sid_to_session_token[sid] = session_token
        runtime.user_names_cache[user_id] = name
        await update_redis_online(user_id, name, "add", role)
        runtime.log("INFO", f"접속 → {user_id} ({name})")
    except Exception as exc:
        runtime.log("ERROR", f"DB 조회 오류: {exc}")
        await runtime.sio.disconnect(sid)
        return
    finally:
        db.close()

    past_messages = await load_past_messages()
    if past_messages:
        await runtime.sio.emit("initMessages", past_messages, to=sid)

    await broadcast_online_users(force=True)


@runtime.sio.event
async def disconnect(sid):
    user_id = runtime.sid_to_user.pop(sid, None)
    runtime.sid_to_role.pop(sid, None)
    runtime.sid_to_session_token.pop(sid, None)
    if user_id:
        await update_redis_online(user_id, action="remove")
        runtime.log("INFO", f"퇴장 → {user_id}")

    await broadcast_online_users(force=True)


@runtime.sio.event
async def logout(sid):
    user_id = runtime.sid_to_user.pop(sid, None)
    runtime.sid_to_role.pop(sid, None)
    runtime.sid_to_session_token.pop(sid, None)
    if user_id:
        await update_redis_online(user_id, action="remove")
        leave_msg = {
            "id": str(uuid.uuid4()),
            "senderId": "system",
            "content": f"{user_id}님이 로그아웃했습니다.",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "isSystem": True,
        }
        await runtime.sio.emit("receiveMessage", leave_msg)
        runtime.log("INFO", f"로그아웃 처리 완료 → {user_id}")

    await broadcast_online_users(force=True)


# ==================== 메시지 이벤트 ====================
@runtime.sio.event
async def sendMessage(sid, data):
    user_id = runtime.sid_to_user.get(sid)
    content = (data or {}).get("content", "").strip()

    if not user_id or not content:
        return

    if len(content) > MAX_MESSAGE_LENGTH:
        await runtime.sio.emit(
            "errorMessage",
            {"message": f"메시지는 최대 {MAX_MESSAGE_LENGTH}자까지 전송할 수 있습니다."},
            to=sid,
        )
        return

    sender_name = resolve_user_name(user_id)
    msg = {
        "id": str(uuid.uuid4()),
        "senderId": str(user_id),
        "senderName": sender_name,
        "content": content,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "isSystem": False,
    }

    await persist_message(msg)
    await runtime.sio.emit("receiveMessage", msg)


@runtime.sio.event
async def typing(sid, data):
    user_id = runtime.sid_to_user.get(sid)
    if not user_id:
        return

    user_name = resolve_user_name(user_id)
    await runtime.sio.emit(
        "typing",
        {
            "userId": str(user_id),
            "name": user_name,
            "isTyping": bool((data or {}).get("isTyping", False)),
            "timestamp": datetime.utcnow().isoformat() + "Z",
        },
        skip_sid=sid,
    )
