# utils/combat_manager.py
from threading import Lock
from typing import Optional, Dict, Any
import time

_lock = Lock()
_combats: Dict[str, Dict[str, Any]] = {}

def create_combat(user_id: str, payload: Dict[str, Any]) -> None:
    """Crea un combate activo para user_id con el payload dado."""
    with _lock:
        _combats[user_id] = dict(payload, started_at=time.time())

def get_combat(user_id: str) -> Optional[Dict[str, Any]]:
    with _lock:
        return _combats.get(user_id)

def delete_combat(user_id: str) -> None:
    with _lock:
        _combats.pop(user_id, None)

def has_combat(user_id: str) -> bool:
    with _lock:
        return user_id in _combats
