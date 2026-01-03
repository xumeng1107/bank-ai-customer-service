from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    # 必须通过环境变量获取API密钥，如果没有设置则抛出错误
    API_KEY: str = ""
    
    # 数据库路径，也支持通过环境变量配置
    DATABASE_PATH: str = os.environ.get("DATABASE_PATH", "sqlite:///./bank.db")
    
    class Config:
        env_file = ".env"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 检查API_KEY是否已设置
        if not self.API_KEY:
            api_key_from_env = os.environ.get("DASHSCOPE_API_KEY")
            if not api_key_from_env:
                raise ValueError("DASHSCOPE_API_KEY环境变量未设置。必须设置API密钥才能启动应用程序。")
            self.API_KEY = api_key_from_env


settings = Settings()
