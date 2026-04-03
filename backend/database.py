import datetime
import os

from dotenv import load_dotenv
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker


# 12-factor: .env는 로컬 개발 전용. 플랫폼(Cloudtype 등) 환경변수가 항상 우선.
load_dotenv(override=False)

# DATABASE_URL 하나로 로컬/운영 통합 관리.
# - 로컬 개발: .env에 DATABASE_URL 설정
# - 운영 배포: Cloudtype 서비스 환경변수에 DATABASE_URL 설정
# DB_HOST/PORT/USER 개별 변수는 DATABASE_URL이 없을 때만 폴백으로 사용.
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
if not DATABASE_URL:
    _host = os.getenv("DB_HOST", "127.0.0.1")
    _port = os.getenv("DB_PORT", "3306")
    _user = os.getenv("DB_USER", "root")
    _password = os.getenv("DB_PASSWORD", "")
    _name = os.getenv("DB_NAME", "maple_guild_app")
    DATABASE_URL = f"mysql+pymysql://{_user}:{_password}@{_host}:{_port}/{_name}?charset=utf8mb4"

DB_POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "3"))
DB_MAX_OVERFLOW = int(os.getenv("DB_MAX_OVERFLOW", "2"))
DB_POOL_RECYCLE = int(os.getenv("DB_POOL_RECYCLE", "1800"))
DB_CONNECT_TIMEOUT = int(os.getenv("DB_CONNECT_TIMEOUT", "10"))

engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_size=max(1, DB_POOL_SIZE),
    max_overflow=max(0, DB_MAX_OVERFLOW),
    pool_recycle=max(300, DB_POOL_RECYCLE),
    connect_args={"connect_timeout": max(3, DB_CONNECT_TIMEOUT)},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "app_users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    provider = Column(String(50), default="local", nullable=False, index=True)
    role = Column(Enum("admin", "user", name="user_roles"), default="user", index=True)
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    is_active = Column(Boolean, default=True, index=True)

    sessions = relationship("UserSession", back_populates="user")


class UserSession(Base):
    __tablename__ = "app_user_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("app_users.id"), nullable=False, index=True)
    session_token = Column(String(255), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.datetime.now)
    expires_at = Column(DateTime, nullable=False, index=True)
    is_active = Column(Boolean, default=True, index=True)
    ip_address = Column(String(45))
    user_agent = Column(Text)

    user = relationship("User", back_populates="sessions")





def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)
