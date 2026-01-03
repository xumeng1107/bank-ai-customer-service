from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# 获取环境变量中的数据库路径或使用默认路径
DATABASE_PATH = os.environ.get("DATABASE_PATH", "sqlite:///./bank.db")

engine = create_engine(
    DATABASE_PATH, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
