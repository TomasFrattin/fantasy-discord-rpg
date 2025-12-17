# services/contribution.py
from utils.db import get_cursor

# ──────────────── Fondos ────────────────
FONDO_MERCHANT = "merchant_reparacion"
OBJETIVO_MERCHANT = 2500  # oro requerido

def crear_fondo(fondo_id: str, objetivo: int):
    """Crea un nuevo fondo con objetivo dado, si no existe."""
    with get_cursor() as cursor:
        cursor.execute(
            "INSERT OR IGNORE INTO fondos (id, objetivo, acumulado) VALUES (?, ?, 0)",
            (fondo_id, objetivo)
        )

def obtener_fondo(fondo_id: str) -> dict | None:
    """Obtiene los datos de un fondo."""
    with get_cursor() as cursor:
        cursor.execute(
            "SELECT * FROM fondos WHERE id = ?", (fondo_id,)
        )
        fila = cursor.fetchone()
        if fila:
            return dict(fila)
        return None

def actualizar_fondo(fondo_id: str, acumulado: int):
    """Actualiza el acumulado del fondo."""
    with get_cursor() as cursor:
        cursor.execute(
            "UPDATE fondos SET acumulado = ? WHERE id = ?",
            (acumulado, fondo_id)
        )

# ──────────────── Contribuciones ────────────────

def registrar_contribucion(user_id: str, fondo_id: str, cantidad: int):
    """Registra la contribución de un usuario a un fondo. Si ya contribuyó, suma."""
    with get_cursor() as cursor:
        # Verificar si ya hay contribución previa
        cursor.execute(
            "SELECT cantidad FROM contribuciones WHERE user_id = ? AND fondo_id = ?",
            (user_id, fondo_id)
        )
        fila = cursor.fetchone()
        if fila:
            nueva_cantidad = fila["cantidad"] + cantidad
            cursor.execute(
                "UPDATE contribuciones SET cantidad = ? WHERE user_id = ? AND fondo_id = ?",
                (nueva_cantidad, user_id, fondo_id)
            )
        else:
            cursor.execute(
                "INSERT INTO contribuciones (user_id, fondo_id, cantidad) VALUES (?, ?, ?)",
                (user_id, fondo_id, cantidad)
            )

def obtener_contribuciones(fondo_id: str) -> list[dict]:
    """Obtiene todas las contribuciones de un fondo."""
    with get_cursor() as cursor:
        cursor.execute(
            "SELECT * FROM contribuciones WHERE fondo_id = ?", (fondo_id,)
        )
        return [dict(f) for f in cursor.fetchall()]

def total_contribuido(fondo_id: str) -> int:
    """Devuelve el total acumulado según contribuciones individuales."""
    with get_cursor() as cursor:
        cursor.execute(
            "SELECT SUM(cantidad) as total FROM contribuciones WHERE fondo_id = ?", (fondo_id,)
        )
        fila = cursor.fetchone()
        return fila["total"] or 0

# ──────────────── Funcionalidad del merchant ────────────────

def fondo_alcanzado(fondo_id: str) -> bool:
    """Verifica si el fondo ya alcanzó su objetivo."""
    fondo = obtener_fondo(fondo_id)
    if not fondo:
        return False
    return fondo["acumulado"] >= fondo["objetivo"]


def barra_progreso(actual, objetivo, length=20):
    """Devuelve una barra tipo crowdfunding"""
    proporcion = min(actual / objetivo, 1)
    llenos = int(proporcion * length)
    vacios = length - llenos
    barra = "█" * llenos + "░" * vacios
    porcentaje = int(proporcion * 100)
    return barra, porcentaje
