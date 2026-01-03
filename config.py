from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    # 使用环境变量获取API密钥，如果没有设置则使用默认值（仅用于开发）
    API_KEY: str = os.environ.get("DASHSCOPE_API_KEY", "sk-dc5359fc274b496783bc9154d2d55250")
    
    # 数据库路径，也支持通过环境变量配置
    DATABASE_PATH: str = os.environ.get("DATABASE_PATH", "sqlite:///./bank.db")
    
    class Config:
        env_file = ".env"


settings = Settings()
