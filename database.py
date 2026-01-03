from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# 在容器环境中使用绝对路径指向可写目录
def get_database_path():
    """获取数据库文件路径，适配容器环境"""
    # 检查是否有自定义数据库路径设置
    custom_path = os.environ.get("DATABASE_PATH")
    if custom_path:
        return custom_path
    
    # 在容器环境中，使用/tmp目录（容器通常对此目录有写权限）
    # 在本地开发环境，使用相对路径
    if os.path.exists('/tmp'):
        # 容器环境
        db_path = '/tmp/bank.db'
        print(f"使用容器环境数据库路径: {db_path}")
    else:
        # 本地开发环境
        db_path = './bank.db'
        print(f"使用本地环境数据库路径: {db_path}")
    
    return f"sqlite:///{db_path}"

DATABASE_PATH = get_database_path()

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
