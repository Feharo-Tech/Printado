import os
from dotenv import load_dotenv

load_dotenv()

class Config:

    BASE_URL = os.getenv("BASE_URL", "https://printado.com.br/")
    UPLOAD_URL = os.getenv("UPLOAD_URL", "")
    API_KEY = os.getenv("API_KEY", "DEFAULT_SECRET")

    DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() in ("true", "1")

    @classmethod
    def show_config(cls):
        config_vars = {key: value for key, value in cls.__dict__.items() if not key.startswith("__")}
        for key, value in config_vars.items():
            print(f"{key}: {value}")

if Config.DEBUG_MODE:
    Config.show_config()
