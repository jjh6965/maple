import json
import time

from . import websocket_runtime as runtime


async def broadcast_online_users(force: bool = False):
    current_time = time.time() * 1000

    if not force and current_time - runtime._last_broadcast_time < runtime._broadcast_throttle_ms:
        runtime._pending_broadcast = True
        return

    runtime._last_broadcast_time = current_time
    runtime._pending_broadcast = False

    if runtime.redis_client:
        try:
            users_hash = await runtime.redis_client.hgetall(runtime.ONLINE_USERS_KEY)
            roles_hash = await runtime.redis_client.hgetall(runtime.ONLINE_USER_ROLES_KEY)
            online_list = [
                {"userId": uid, "name": name, "role": roles_hash.get(uid, "user")}
                for uid, name in users_hash.items()
            ]
        except Exception as exc:
            runtime.log("WARNING", f"Redis hgetall 오류 → 로컬 메모리 사용: {exc}")
            online_list = [
                {"userId": uid, "name": name, "role": runtime.online_user_roles_local.get(uid, "user")}
                for uid, name in runtime.online_users_local.items()
            ]
    else:
        online_list = [
            {"userId": uid, "name": name, "role": runtime.online_user_roles_local.get(uid, "user")}
            for uid, name in runtime.online_users_local.items()
        ]

    online_list.sort(key=lambda item: item["name"].lower())
    current_hash = json.dumps(online_list, sort_keys=True)
    if current_hash == runtime._prev_online_users_hash:
        return

    runtime._prev_online_users_hash = current_hash
    await runtime.sio.emit("onlineUsers", online_list)


async def update_redis_online(user_id: str, name: str = "", action: str = "add", role: str = "user"):
    if action == "add" and name:
        runtime.online_users_local[user_id] = name
        runtime.online_user_roles_local[user_id] = role or "user"
    elif action == "remove":
        runtime.online_users_local.pop(user_id, None)
        runtime.online_user_roles_local.pop(user_id, None)

    if not runtime.redis_client:
        return

    try:
        pipe = runtime.redis_client.pipeline()
        if action == "add" and name:
            pipe.hset(runtime.ONLINE_USERS_KEY, user_id, name)
            pipe.hset(runtime.ONLINE_USER_ROLES_KEY, user_id, role or "user")
        elif action == "remove":
            pipe.hdel(runtime.ONLINE_USERS_KEY, user_id)
            pipe.hdel(runtime.ONLINE_USER_ROLES_KEY, user_id)

        pipe.expire(runtime.ONLINE_USERS_KEY, 3600)
        pipe.expire(runtime.ONLINE_USER_ROLES_KEY, 3600)
        await pipe.execute()
    except Exception as exc:
        runtime.log("WARNING", f"Redis 업데이트 실패: {exc}")


async def load_past_messages():
    if not runtime.redis_client:
        return []

    try:
        raw_msgs = await runtime.redis_client.lrange(runtime.CHAT_HISTORY_KEY, 0, -1)
        parsed = []
        for raw in raw_msgs or []:
            if not raw:
                continue
            try:
                msg = json.loads(raw)
                if isinstance(msg, dict):
                    parsed.append(msg)
            except Exception:
                continue
        return parsed
    except Exception as exc:
        runtime.log("WARNING", f"과거 메시지 로드 실패: {exc}")
        return []


async def persist_message(message: dict):
    if not runtime.redis_client:
        return

    try:
        await runtime.redis_client.rpush(runtime.CHAT_HISTORY_KEY, json.dumps(message))
        await runtime.redis_client.ltrim(runtime.CHAT_HISTORY_KEY, -runtime.MAX_HISTORY, -1)
    except Exception as exc:
        runtime.log("WARNING", f"메시지 저장 실패: {exc}")
