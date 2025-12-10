import json
import sqlite3
from config import DB_FILE
from datetime import datetime
import random
from config import DB_FILE

# -------------------- CONEXIÓN --------------------
def conectar():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn

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


def sleep(user_id: str):
    conn = conectar()
    cursor = conn.cursor()

    # Obtener vida actual y vida máxima real
    cursor.execute("SELECT vida, vida_max FROM jugadores WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        return None

    vida_actual, vida_max = row["vida"], row["vida_max"]

    recuperar = max(1, int(vida_max * 0.20))
    nueva_vida = min(vida_actual + recuperar, vida_max)

    cursor.execute(
        "UPDATE jugadores SET vida = ? WHERE user_id = ?",
        (nueva_vida, user_id)
    )

    conn.commit()
    conn.close()

    return nueva_vida, recuperar


# -------------------- JUGADOR --------------------
def registrar_jugador(user_id, username, afinidad):
    energia_inicial = energia_max_por_afinidad(afinidad)

    conn = conectar()
    cursor = conn.cursor()
    now_iso = datetime.now().replace(microsecond=0).isoformat(sep=' ')
    cursor.execute("""
        INSERT OR IGNORE INTO jugadores 
        (user_id, username, afinidad, energia, energia_max, last_reset)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, username, afinidad, energia_inicial, energia_inicial, now_iso))
    conn.commit()
    conn.close()


def obtener_jugador(user_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM jugadores WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row

def actualizar_vida(user_id, nueva_vida):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("UPDATE jugadores SET vida = ? WHERE user_id = ?", (nueva_vida, user_id))
    conn.commit()
    conn.close()
# -------------------- INVENTARIO --------------------
# REFACTORIZAR
# def agregar_consumible(user_id, item_id):
#     conn = conectar()
#     cursor = conn.cursor()

#     cursor.execute("SELECT inventario FROM jugadores WHERE user_id = ?", (user_id,))
#     fila = cursor.fetchone()

#     inv = json.loads(fila[0]) if fila else []
#     inv.append(item_id)

#     cursor.execute("UPDATE jugadores SET inventario = ? WHERE user_id = ?", (json.dumps(inv), user_id))
#     conn.commit()
#     conn.close()

# --- inventario / items helpers ---

def agregar_item(user_id: str, item_id: str, cantidad: int = 1):
    conn = conectar()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO inventario (user_id, item_id, cantidad) VALUES (?, ?, ?)"
        " ON CONFLICT(user_id, item_id) DO UPDATE SET cantidad = cantidad + ?",
        (user_id, item_id, cantidad, cantidad)
    )
    conn.commit()
    conn.close()

def obtener_inventario(user_id: str):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("""
        SELECT i.item_id, it.nombre, i.cantidad, it.tipo, it.rareza
        FROM inventario i
        JOIN items it ON it.id = i.item_id
        WHERE i.user_id = ?
    """, (user_id,))
    rows = cur.fetchall()
    conn.close()
    return [{"item_id": r[0], "nombre": r[1], "cantidad": r[2], "tipo": r[3], "rareza": r[4]} for r in rows]

import random

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
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(f"UPDATE jugadores SET {slot} = ? WHERE user_id = ?", (item_id, user_id))
    conn.commit()
    conn.close()

    recalcular_stats(user_id)


# -------------------- ORO / ENERGÍA --------------------
def sumar_oro(user_id, cantidad):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("UPDATE jugadores SET oro = oro + ? WHERE user_id = ?", (cantidad, user_id))
    conn.commit()
    conn.close()


def obtener_energia(user_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT energia FROM jugadores WHERE user_id = ?", (user_id,))
    fila = cursor.fetchone()
    conn.close()
    return fila[0] if fila else None


def gastar_energia(user_id, cantidad=1):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT energia FROM jugadores WHERE user_id = ?", (user_id,))
    fila = cursor.fetchone()

    if fila:
        nueva = max(fila[0] - cantidad, 0)
        cursor.execute("UPDATE jugadores SET energia = ? WHERE user_id = ?", (nueva, user_id))
        conn.commit()

    conn.close()

def energia_max_por_afinidad(afinidad: str) -> int:
    base = 3
    if afinidad.lower() == "arcano":
        return base + 1
    return base

def resetear_todos():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT user_id, vida, vida_max, afinidad FROM jugadores")
    jugadores = cursor.fetchall()

    for jugador in jugadores:
        user_id = jugador["user_id"]
        vida_actual = jugador["vida"]
        vida_max = jugador["vida_max"]
        afinidad = jugador["afinidad"]

        energia_max = energia_max_por_afinidad(afinidad)

        cursor.execute(
            "UPDATE jugadores SET energia = ? WHERE user_id = ?",
            (energia_max, user_id)
        )

        # Recuperar vida como ya tenías
        recuperar = max(1, int(vida_max * 0.20))
        nueva_vida = min(vida_actual + recuperar, vida_max)
        cursor.execute(
            "UPDATE jugadores SET vida = ? WHERE user_id = ?",
            (nueva_vida, user_id)
        )


    conn.commit()
    conn.close()


def resetear_usuario(user_id: str):
    conn = conectar()
    cursor = conn.cursor()

    # Traer datos del usuario
    cursor.execute("""
        SELECT vida, vida_max, afinidad
        FROM jugadores
        WHERE user_id = ?
    """, (user_id,))
    
    jugador = cursor.fetchone()

    # Si no existe, salir
    if not jugador:
        conn.close()
        return False

    vida_actual = jugador["vida"]
    vida_max = jugador["vida_max"]
    afinidad = jugador["afinidad"]

    # Calcular energía máxima según afinidad
    energia_max = energia_max_por_afinidad(afinidad)

    # Resetear energía
    cursor.execute(
        "UPDATE jugadores SET energia = ? WHERE user_id = ?",
        (energia_max, user_id)
    )

    # Recuperar vida
    recuperar = max(1, int(vida_max * 0.10))
    nueva_vida = min(vida_actual + recuperar, vida_max)

    cursor.execute(
        "UPDATE jugadores SET vida = ? WHERE user_id = ?",
        (nueva_vida, user_id)
    )

    conn.commit()
    conn.close()

    return True


def eliminar_jugador(user_id: str):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM jugadores WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()


def obtener_materiales():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM items WHERE tipo='material'")
    items = cursor.fetchall()
    conn.close()
    return items

def obtener_consumibles():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM items WHERE tipo='consumible'")
    items = cursor.fetchall()
    conn.close()
    return items

def obtener_equipables():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM items WHERE tipo IN ('arma','armadura','casco','botas')")
    items = cursor.fetchall()
    conn.close()
    return items


def actualizar_accion(user_id: str, accion: str | None):
    """Actualiza la acción actual del jugador (pescando, etc.)"""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("UPDATE jugadores SET accion_actual = ? WHERE user_id = ?", (accion, user_id))
    conn.commit()
    conn.close()

def obtener_accion_actual(user_id: str) -> str | None:
    """Obtiene la acción actual del jugador (pescando, etc.)"""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT accion_actual FROM jugadores WHERE user_id = ?", (user_id,))
    fila = cursor.fetchone()
    conn.close()
    return fila["accion_actual"] if fila else None

def actualizar_accion_fin(user_id: str, accion_fin: str | None):
    """Actualiza la fecha/hora de finalización de la acción actual del jugador."""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE jugadores SET accion_fin = ? WHERE user_id = ?",
        (accion_fin, user_id)
    )
    conn.commit()
    conn.close()

def obtener_accion_fin(user_id: str) -> str | None:
    """Obtiene la fecha/hora de finalización de la acción actual del jugador."""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT accion_fin FROM jugadores WHERE user_id = ?",
        (user_id,)
    )
    fila = cursor.fetchone()
    conn.close()
    return fila["accion_fin"] if fila else None



def agregar_columna_accion_fin():
    """Agrega la columna 'accion_fin' a la tabla jugadores si no existe."""
    conn = conectar()
    cursor = conn.cursor()

    # Revisar columnas existentes
    cursor.execute("PRAGMA table_info(jugadores)")
    columnas = [col[1] for col in cursor.fetchall()]

    if "accion_fin" not in columnas:
        cursor.execute("ALTER TABLE jugadores ADD COLUMN accion_fin TEXT DEFAULT NULL")
        print("Columna 'accion_fin' agregada correctamente.")
    else:
        print("La columna 'accion_fin' ya existe.")

    conn.commit()
    conn.close()

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