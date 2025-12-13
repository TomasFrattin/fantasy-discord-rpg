import sqlite3
from config import DB_FILE
import random
from contextlib import contextmanager
from services.jugadores import obtener_jugador

# -------------------- CONEXIÓN --------------------
def conectar():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn

# -------------------- CONTEXTO --------------------
@contextmanager
def get_cursor():
    conn = conectar()
    cursor = conn.cursor()
    try:
        yield cursor
        conn.commit()
    finally:
        conn.close()

# -------------------- STATS --------------------
def recalcular_stats(user_id):
    """Recalcula daño y vida en base al equipamiento."""
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT vida_base, base_damage, 
               arma_equipada, armadura_equipada, casco_equipado, botas_equipadas
        FROM jugadores WHERE user_id = ?
    """, (user_id,))
    pj = cursor.fetchone()

    if not pj:
        conn.close()
        return

    base_hp = pj["vida_base"]
    base_dmg = pj["base_damage"]

    bonus_hp = 0
    bonus_dmg = 0

    from data_loader import EQUIPABLES_BY_ID  # evita import circular

    # ARMA
    if pj["arma_equipada"]:
        arma = EQUIPABLES_BY_ID.get(pj["arma_equipada"])
        if arma:
            bonus_dmg += arma["stats"].get("ataque", 0)

    # ARMADURA / CASCO / BOTAS
    for slot in ("armadura_equipada", "casco_equipado", "botas_equipadas"):
        if pj[slot]:
            item = EQUIPABLES_BY_ID.get(pj[slot])
            if item:
                bonus_hp += item["stats"].get("vida", 0)

    # actualizar stats finales
    cursor.execute("""
        UPDATE jugadores
        SET vida_max = ?, damage = ?, vida = MIN(vida, ?)
        WHERE user_id = ?
    """, (base_hp + bonus_hp, base_dmg + bonus_dmg, base_hp + bonus_hp, user_id))

    conn.commit()
    conn.close()

# -------------------- INVENTARIO --------------------
def agregar_item(user_id: str, item_id: str, cantidad: int = 1):
    with get_cursor() as cursor:
        cursor.execute(
            "INSERT INTO inventario (user_id, item_id, cantidad) VALUES (?, ?, ?)"
            " ON CONFLICT(user_id, item_id) DO UPDATE SET cantidad = cantidad + ?",
            (user_id, item_id, cantidad, cantidad)
        )


def obtener_inventario(user_id: str):
    with get_cursor() as cursor:
        cursor.execute("""
            SELECT i.item_id, it.nombre, i.cantidad, it.tipo, it.rareza
            FROM inventario i
            JOIN items it ON it.id = i.item_id
            WHERE i.user_id = ?
        """, (user_id,))
        rows = cursor.fetchall()

        return [{"item_id": r["item_id"], "nombre": r["nombre"], "cantidad": r["cantidad"],
                "tipo": r["tipo"], "rareza": r["rareza"]} for r in rows]


# --- SISTEMA DE RECOLECCIÓN ---
def tiers_por_nivel(lvl_recoleccion):
    if lvl_recoleccion < 5:
        return ["comun"]
    elif lvl_recoleccion < 10:
        return ["comun", "raro"]
    elif lvl_recoleccion < 15:
        return ["comun", "raro", "epico"]
    else:
        return ["comun", "raro", "epico", "legendario"]


def recolectar_materiales(user_id: str):
    conn = conectar()
    jugador = obtener_jugador(user_id)
    lvl = jugador["lvl_recoleccion"] or 1  # <- cambio aquí
    
    materiales = obtener_materiales()
    if not materiales:
        return []

    # Determinar pool filtrando por rareza permitida
    rarezas_permitidas = tiers_por_nivel(lvl)
    pool = {}
    for item in materiales:
        rareza = item["rareza"] or "comun"
        if rareza not in rarezas_permitidas:
            continue

        # Definir peso y cantidad máxima por rareza
        if rareza == "comun":
            peso, max_q = 50, 3
        elif rareza == "raro":
            peso, max_q = 20, 1  # menos cantidad para niveles bajos
        elif rareza == "epico":
            peso, max_q = 5, 1
        else:  # legendario
            peso, max_q = 1, 1

        pool[item["id"]] = {"peso": peso, "max_q": max_q, "nombre": item["nombre"]}

    if not pool:
        conn.close()
        return []

    # Determinar cantidad de tipos a recolectar según nivel
    if lvl < 5:
        n_types = random.randint(1, 2)
    elif lvl < 10:
        n_types = random.randint(2, 3)
    else:
        n_types = random.randint(2, 4)

    # Selección ponderada sin repetición
    ids, pesos = zip(*[(k, v["peso"]) for k, v in pool.items()])
    chosen_ids = []
    while len(chosen_ids) < n_types and ids:
        seleccionado = random.choices(ids, weights=pesos)[0]
        if seleccionado not in chosen_ids:
            chosen_ids.append(seleccionado)

    # Asignar cantidad aleatoria y agregar al inventario
    resultados = []
    for item_id in chosen_ids:
        max_q = pool[item_id]["max_q"]
        nombre = pool[item_id]["nombre"]
        cantidad = random.randint(1, max_q)
        agregar_item(user_id, item_id, cantidad)
        resultados.append((item_id, nombre, cantidad))

    conn.close()
    return resultados

# -------------------- EQUIPAMIENTO --------------------
def equipar(user_id, slot, item_id):
    with get_cursor() as cursor:
     cursor.execute(f"UPDATE jugadores SET {slot} = ? WHERE user_id = ?", (item_id, user_id))
   
    recalcular_stats(user_id)

# -------------------- ORO / ENERGÍA --------------------

def obtener_materiales():
    with get_cursor() as cursor:
        cursor.execute("SELECT * FROM items WHERE tipo='material'")
        items = cursor.fetchall()
        return items

def obtener_consumibles():
    with get_cursor() as cursor:
        cursor.execute("SELECT * FROM items WHERE tipo='consumible'")
        items = cursor.fetchall()
        return items

def obtener_equipables():
    with get_cursor() as cursor:
        cursor.execute("SELECT * FROM items WHERE tipo IN ('arma','armadura','casco','botas')")
        items = cursor.fetchall()
        return items


# -------------------- EXP: CACERÍA - RECOLECCIÓN --------------------
def obtener_item_por_id(item_id):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, nombre, rareza, url FROM items WHERE id = ?",
        (item_id,)
    )
    
    result = cursor.fetchone()
    
    conn.close()
    return result

def actualizar_exp_caceria(user_id, exp):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE jugadores SET exp_caceria = ? WHERE user_id = ?",
        (exp, user_id)
    )
    conn.commit()
    conn.close()
    
def actualizar_lvl_caceria(user_id, lvl):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE jugadores SET lvl_caceria = ? WHERE user_id = ?",
        (lvl, user_id)
    )
    conn.commit()
    conn.close()

def actualizar_exp_recoleccion(user_id, exp):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE jugadores SET exp_recoleccion = ? WHERE user_id = ?",
        (exp, user_id)
    )
    conn.commit()
    conn.close()

def actualizar_lvl_recoleccion(user_id, lvl):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE jugadores SET lvl_recoleccion = ? WHERE user_id = ?",
        (lvl, user_id)
    )
    conn.commit()
    conn.close()
    
    
def agregar_exp_recoleccion(user_id, exp_obtenida):
    jugador = obtener_jugador(user_id)
    exp_actual = jugador["exp_recoleccion"] or 0
    lvl = jugador["lvl_recoleccion"] or 1

    exp_actual += exp_obtenida
    niveles_subidos = 0

    # Umbral dinámico, similar a cacería
    while exp_actual >= int(120 * (lvl ** 1.25)):
        exp_actual -= int(120 * (lvl ** 1.25))
        lvl += 1
        niveles_subidos += 1

    actualizar_exp_recoleccion(user_id, exp_actual)
    actualizar_lvl_recoleccion(user_id, lvl)

    return lvl, exp_actual, niveles_subidos