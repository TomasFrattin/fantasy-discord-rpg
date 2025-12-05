# Helper para manejar locks de usuarios durante acciones que no deben ser interrumpidas.
locks = {}

def esta_ocupado(user_id: str) -> bool:
    return locks.get(user_id, False)

def comenzar_accion(user_id: str):
    locks[user_id] = True

def terminar_accion(user_id: str):
    locks[user_id] = False
