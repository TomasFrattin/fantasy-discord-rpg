import os
from dotenv import load_dotenv

# Cargar variables del .env
load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
DB_FILE = os.getenv("DB_FILE", "data/arkanor.db")
PREFIX = os.getenv("PREFIX", "!")
ENERGIA_MAX = 3
WELCOME_CHANNEL_ID = 1422721307455524916

# URL para invitar al bot con todos los permisos
# https://discord.com/oauth2/authorize?client_id=1422719749116137623&scope=bot%20applications.commands&permissions=277025508352
