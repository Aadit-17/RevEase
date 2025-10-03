import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Frontend Origin
    FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")