import os
from dotenv import load_dotenv

# Cargar variables del .env
load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")
DB_FILE = os.getenv("DB_FILE", "data/arkanor.db")
PREFIX = os.getenv("PREFIX", "!")
ENERGIA_MAX = 15
# WELCOME_CHANNELS = [1422721307455524916, 1447019890669129931, 1447295691536990539]
WELCOME_CHANNELS = [123123]

# URL para invitar al bot con todos los permisos
# https://discord.com/oauth2/authorize?client_id=1422719749116137623&scope=bot%20applications.commands&permissions=277025508352
