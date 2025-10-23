import os

API_ID = int(os.environ.get("API_ID", "27704224"))
API_HASH = os.environ.get("API_HASH", "c2e33826d757fe113bc154fcfabc987d")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8337038537:AAH-Ej6TORVv1eBx11aFF3bKKJKNGb5x7M8")
OWNER_ID = int(os.environ.get("OWNER_ID", "7534267467"))

DB_URI = os.environ.get("DATABASE_URL", "mongodb+srv://Angel:aloksingh@angel.4qdpllb.mongodb.net/?retryWrites=true&w=majority&appName=Angel")
DB_NAME = os.environ.get("DATABASE_NAME", "Angle")
