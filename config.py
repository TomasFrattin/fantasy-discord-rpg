import os
from dotenv import load_dotenv

# Cargar variables del .env
load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
DB_FILE = os.getenv("DB_FILE", "data/arkanor.db")
PREFIX = os.getenv("PREFIX", "!")
ENERGIA_MAX = 30
WELCOME_CHANNEL_ID = 1422721307455524916