from data_loader import CONSUMIBLES_BY_ID
from utils.db import consumir_consumible


def usar_consumible(user_id: str, item_id: str):
    """Valida la definición y delega la aplicación atómica del efecto."""
    item = CONSUMIBLES_BY_ID.get(item_id)
    if not item or item.get("tipo") != "consumible":
        return False, "Consumible inexistente"

    efecto = item.get("efecto", {})
    recurso = efecto.get("recurso")
    porcentaje = efecto.get("porcentaje")
    if porcentaje is None:
        return False, "Este consumible todavía no se puede usar"

    ok, resultado = consumir_consumible(user_id, item_id, recurso, porcentaje)
    if not ok:
        return False, resultado

    return True, {"nombre": item["nombre"], **resultado}
