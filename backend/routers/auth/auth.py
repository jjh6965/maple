import uuid
import datetime
import re
from fastapi import APIRouter, Form, Depends, HTTPException, Request, Query
from sqlalchemy.orm import Session

from database import get_db, User, UserSession
from utils.auth_utils import hash_password, verify_password


auth_router = APIRouter(prefix="/auth", tags=["Authentication"])

USERNAME_PATTERN = re.compile(r"^[a-zA-Z0-9_]{3,30}$")
SESSION_DAYS = 30


# ==================== 회원가입 ====================
@auth_router.post("/register")
def register(
    user_id: str = Form(...),
    user_pw: str = Form(...),
    user_name: str = Form(...),
    user_email: str = Form(...),
    db: Session = Depends(get_db),
):
    user_id = user_id.strip()
    user_name = user_name.strip()
    user_email = user_email.strip().lower()

    if not USERNAME_PATTERN.fullmatch(user_id):
        raise HTTPException(status_code=400, detail="아이디는 3-30자의 영문/숫자/_만 허용됩니다.")
    if len(user_pw) < 8:
        raise HTTPException(status_code=400, detail="비밀번호는 최소 8자 이상이어야 합니다.")
    if len(user_name) < 2 or len(user_name) > 50:
        raise HTTPException(status_code=400, detail="이름은 2-50자여야 합니다.")
    if "@" not in user_email or len(user_email) > 255:
        raise HTTPException(status_code=400, detail="유효한 이메일 형식이 아닙니다.")

    existing_id = db.query(User).filter(User.username == user_id).first()
    if existing_id:
        raise HTTPException(status_code=400, detail="이미 사용 중인 아이디입니다.")

    existing_email = db.query(User).filter(User.email == user_email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="이미 사용 중인 이메일입니다.")

    new_user = User(
        username=user_id,
        password_hash=hash_password(user_pw),
        full_name=user_name,
        email=user_email,
        provider="local",
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "회원가입이 완료되었습니다."}


@auth_router.get("/check-id")
def check_id(user_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == user_id).first()
    if user:
        return {"available": False, "message": "이미 사용 중인 아이디입니다."}
    return {"available": True, "message": "사용 가능한 아이디입니다."}


# ==================== 로그인 ====================
@auth_router.post("/login")
def login(
    request: Request,
    user_id: str = Form(...),
    user_pw: str = Form(...),
    db: Session = Depends(get_db),
):
    user_id = user_id.strip()
    user = db.query(User).filter(User.username == user_id).first()
    if not user or not verify_password(user_pw, user.password_hash):
        raise HTTPException(status_code=401, detail="아이디 또는 비밀번호가 틀렸습니다.")

    # 동시 로그인 제한: 기존 활성 세션 종료
    existing_sessions = db.query(UserSession).filter(
        UserSession.user_id == user.id,
        UserSession.is_active == True,
    ).all()

    for session in existing_sessions:
        session.is_active = False
    db.commit()

    # 새 세션 생성
    session_token = str(uuid.uuid4())
    new_session = UserSession(
        user_id=user.id,
        session_token=session_token,
        created_at=datetime.datetime.utcnow(),
        expires_at=datetime.datetime.utcnow() + datetime.timedelta(days=SESSION_DAYS),
        is_active=True,
        ip_address=None,
        user_agent=None,
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)

    return {
        "message": "로그인 성공",
        "user_name": user.full_name,
        "user_id": user.username,
        "user_db_id": user.id,
        "session_token": session_token,
    }


# ==================== 세션 검증 ====================
@auth_router.get("/sessions/validate")
def validate_session(
    user_id: int = Query(...),
    session_token: str = Query(...),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"is_valid": False, "reason": "사용자를 찾을 수 없습니다."}

    session = db.query(UserSession).filter(
        UserSession.user_id == user_id,
        UserSession.session_token == session_token,
        UserSession.is_active == True,
    ).first()

    if not session:
        return {"is_valid": False, "reason": "세션을 찾을 수 없습니다."}

    if session.expires_at and datetime.datetime.utcnow() > session.expires_at:
        session.is_active = False
        db.commit()
        return {"is_valid": False, "reason": "세션 만료"}

    return {"is_valid": True, "reason": "유효한 세션"}


# ==================== 로그아웃 ====================
@auth_router.post("/logout")
def logout(
    user_id: int = Form(...),
    session_token: str = Form(...),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="사용자를 찾을 수 없습니다.")

    session = db.query(UserSession).filter(
        UserSession.user_id == user_id,
        UserSession.session_token == session_token,
        UserSession.is_active == True,
    ).first()
    if not session:
        raise HTTPException(status_code=401, detail="유효한 세션이 아닙니다.")

    session.is_active = False
    db.commit()

    return {"message": "로그아웃되었습니다."}
