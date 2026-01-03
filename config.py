from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    API_KEY: str = "sk-dc5359fc274b496783bc9154d2d55250"
    
    class Config:
        env_file = ".env"


settings = Settings()
