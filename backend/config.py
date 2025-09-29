from dotenv import load_dotenv
import os

load_dotenv()


class Config:
    FLASK_DEBUG = os.getenv("FLASK_DEBUG")
    FLASK_APP = os.getenv("FLASK_APP")
    FLASK_RUN_PORT = os.environ.get("FLASK_RUN_PORT")
    GEMINI_KEY = os.getenv("GEMINI_KEY")
