import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL")
API_KEY = os.getenv("API_KEY")
MODEL = os.getenv("MODEL")
# DATABASE_URL = os.getenv("DATABASE_URL")

# JWT Auth settings
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# OAuth Google settings
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")  # e.g. https://yourapp.com/google/callback

# Caching settings
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CACHE_TTL = int(os.getenv("CACHE_TTL", "300"))
# Query log flush interval (in days)
QUERY_LOG_FLUSH_INTERVAL_DAYS = int(os.getenv("QUERY_LOG_FLUSH_INTERVAL_DAYS", "7"))
# Convert to seconds
QUERY_LOG_FLUSH_INTERVAL_SECONDS = QUERY_LOG_FLUSH_INTERVAL_DAYS * 86400
