# tasks.py
import datetime
from discord.ext import tasks
from utils import db

# ---------- Tasks ----------

@tasks.loop(minutes=1)
async def reset_diario():
    """
    Resetea los valores diarios de todos los jugadores a la medianoche.
    """
    ahora = datetime.datetime.now()
    if ahora.hour == 20 and ahora.minute == 0:
        db.resetear_todos()
        print("Reset diario ejecutado.")

# Aquí podés agregar más tasks en el futuro, por ejemplo loot diario, eventos de mapa, etc.

# ---------- Inicialización ----------

def start_all(bot):
    """
    Inicia todas las tasks del bot.
    """
    if not reset_diario.is_running():
        reset_diario.start()
