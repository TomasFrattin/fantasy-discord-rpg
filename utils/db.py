import json
import sqlite3
from config import DB_FILE, ENERGIA_MAX
from datetime import datetime
import random

# -------------------- CONEXIÓN --------------------
def conectar():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn


# -------------------- TABLAS --------------------
def borrar_tabla_jugadores():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS jugadores")
    conn.commit()
    conn.close()

def crear_tabla_jugadores():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(f'''
    CREATE TABLE IF NOT EXISTS jugadores (
        id_usuario TEXT PRIMARY KEY,
        username TEXT,
        afinidad TEXT,
        
        -- stats base
        base_vida INTEGER DEFAULT 100,
        base_damage INTEGER DEFAULT 10,

        -- stats finales
        vida INTEGER DEFAULT 100,
        damage INTEGER DEFAULT 10,

        energia INTEGER DEFAULT 30,

        exploracion INTEGER DEFAULT 0,
        combate INTEGER DEFAULT 0,
        caceria INTEGER DEFAULT 0,

        arma_equipada TEXT,
        armadura_equipada TEXT,
        casco_equipado TEXT,
        botas_equipadas TEXT,

        oro INTEGER DEFAULT 0,
        last_reset TIMESTAMP
    )
    ''')
    conn.commit()
    conn.close()

def crear_tabla_items_consumibles():
    conn = conectar()
    cur = conn.cursor()

    # Crear tabla si no existe
    cur.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id TEXT PRIMARY KEY,
            nombre TEXT NOT NULL,
            tipo TEXT,
            descripcion TEXT,
            rareza TEXT
        );
    """)

    # Insertar ítems base (solo si no existen)
    cur.executemany("""
        INSERT OR IGNORE INTO items (id, nombre, tipo, descripcion, rareza) VALUES 
        (?, ?, ?, ?, ?)
    """, [
        ('hierba_verde', 'Hierba Verde', 'material', 'Hierba común, usada en pociones básicas.', 'comun'),
        ('ramita_seca', 'Ramita Seca', 'material', 'Madera ligera, útil para antorchas y reparaciones simples.', 'comun'),
        ('mineral_rugoso', 'Mineral Rugoso', 'material', 'Mineral de baja calidad para forja inicial.', 'comun'),
        ('petalo_blanco', 'Pétalo Blanco', 'material', 'Pétalo frágil para ungüentos.', 'poco_comun'),
        ('fragmento_cristal', 'Fragmento de Cristal', 'material', 'Brilla con magia leve; sirve para cristalería.', 'raro'),
        ('esencia_arcana', 'Esencia Arcana', 'material', 'Residuos de magia pura. Muy valioso.', 'epico')
    ])

    conn.commit()
    conn.close()

def crear_tabla_inventario():
    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS inventario (
            user_id TEXT NOT NULL,
            item_id TEXT NOT NULL,
            cantidad INTEGER NOT NULL DEFAULT 0,
            PRIMARY KEY (user_id, item_id),
            FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE
        );
    """)

    conn.commit()
    conn.close()
# -------------------- STATS --------------------
def recalcular_stats(id_usuario):
    """Recalcula daño y vida en base al equipamiento."""
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT base_vida, base_damage, 
               arma_equipada, armadura_equipada, casco_equipado, botas_equipadas
        FROM jugadores WHERE id_usuario = ?
    """, (id_usuario,))
    pj = cursor.fetchone()

    if not pj:
        conn.close()
        return

    base_hp = pj["base_vida"]
    base_dmg = pj["base_damage"]

    bonus_hp = 0
    bonus_dmg = 0

    from data_loader import ITEMS_BY_ID  # evita import circular

    # ARMA
    if pj["arma_equipada"]:
        arma = ITEMS_BY_ID.get(pj["arma_equipada"])
        if arma:
            bonus_dmg += arma["stats"].get("ataque", 0)

    # ARMADURA / CASCO / BOTAS
    for slot in ("armadura_equipada", "casco_equipado", "botas_equipadas"):
        if pj[slot]:
            item = ITEMS_BY_ID.get(pj[slot])
            if item:
                bonus_hp += item["stats"].get("vida", 0)

    # actualizar stats finales
    cursor.execute("""
        UPDATE jugadores
        SET vida = ?, damage = ?
        WHERE id_usuario = ?
    """, (base_hp + bonus_hp, base_dmg + bonus_dmg, id_usuario))

    conn.commit()
    conn.close()


def sleep(user_id: str):
    conn = conectar()
    cursor = conn.cursor()

    # Obtener vida actual y máxima
    cursor.execute("SELECT vida, base_vida FROM jugadores WHERE id_usuario = ?", (user_id,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        return None

    vida_actual, vida_max = row["vida"], row["base_vida"]
    recuperar = max(1, int(vida_max * 0.10))  # 10% mínimo 1
    nueva_vida = min(vida_actual + recuperar, vida_max)

    cursor.execute(
        "UPDATE jugadores SET vida = ? WHERE id_usuario = ?",
        (nueva_vida, user_id)
    )
    conn.commit()
    conn.close()

    return nueva_vida, recuperar


# -------------------- JUGADOR --------------------
def registrar_jugador(id_usuario, username, afinidad):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR IGNORE INTO jugadores 
        (id_usuario, username, afinidad, energia, last_reset)
        VALUES (?, ?, ?, ?, ?)
    """, (id_usuario, username, afinidad, ENERGIA_MAX, datetime.now()))
    conn.commit()
    conn.close()


def obtener_jugador(id_usuario):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM jugadores WHERE id_usuario = ?", (id_usuario,))
    row = cursor.fetchone()
    conn.close()
    return row


# -------------------- INVENTARIO --------------------
def agregar_consumible(id_usuario, item_id):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT inventario FROM jugadores WHERE id_usuario = ?", (id_usuario,))
    fila = cursor.fetchone()

    inv = json.loads(fila[0]) if fila else []
    inv.append(item_id)

    cursor.execute("UPDATE jugadores SET inventario = ? WHERE id_usuario = ?", (json.dumps(inv), id_usuario))
    conn.commit()
    conn.close()

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

def recolectar_materiales(user_id: str, zona: str = "colina"):
    """Selecciona materiales, los guarda en inventario y genera texto de salida."""
    pool = [
        ("hierba_verde", 50, 3),
        ("ramita_seca", 40, 2),
        ("mineral_rugoso", 30, 2),
        ("petalo_blanco", 15, 1),
        ("fragmento_cristal", 6, 1),
        ("esencia_arcana", 2, 1)
    ]

    # Cantidad de tipos diferentes a obtener
    n_types = random.choices([1, 2, 3], weights=[60, 30, 10])[0]

    # Elegir items con pesos
    chosen = random.choices(pool, weights=[p[1] for p in pool], k=n_types)

    resultados = []
    for item_id, _, max_q in chosen:
        cantidad = random.randint(1, max_q)
        agregar_item(user_id, item_id, cantidad)  # guardar en inventario
        resultados.append((item_id, cantidad))

    if not resultados:
        return [], "No se encontraron materiales."

    # Obtener nombres de los items
    conn = conectar()
    cur = conn.cursor()
    ids = tuple(r[0] for r in resultados)
    query_marks = ",".join(["?"] * len(ids))
    cur.execute(f"SELECT id, nombre FROM items WHERE id IN ({query_marks})", ids)
    mapping = {row["id"]: row["nombre"] for row in cur.fetchall()}
    conn.close()

    resultados_finales = [(item_id, mapping.get(item_id, item_id), cantidad) for item_id, cantidad in resultados]

    # Texto de flavor
    textos = [
        "Recorrés los senderos polvorientos y apartás unas raíces; algo brilla entre la maleza.",
        "Subís por un risco y el viento deja caer pequeños fragmentos entre las piedras.",
        "Escudriñas bajo unas rocas y hallás tesoros humildes de la naturaleza."
    ]
    descripcion = f"{random.choice(textos)}\nEncontraste: " + ", ".join(
        f"{cantidad}× {nombre}" for _, nombre, cantidad in resultados_finales
    )

    return resultados_finales, descripcion


# -------------------- EQUIPAMIENTO --------------------
def equipar(id_usuario, slot, item_id):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(f"UPDATE jugadores SET {slot} = ? WHERE id_usuario = ?", (item_id, id_usuario))
    conn.commit()
    conn.close()

    recalcular_stats(id_usuario)


# -------------------- ORO / ENERGÍA --------------------
def sumar_oro(id_usuario, cantidad):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("UPDATE jugadores SET oro = oro + ? WHERE id_usuario = ?", (cantidad, id_usuario))
    conn.commit()
    conn.close()


def obtener_energia(id_usuario):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT energia FROM jugadores WHERE id_usuario = ?", (id_usuario,))
    fila = cursor.fetchone()
    conn.close()
    return fila[0] if fila else None


def gastar_energia(id_usuario, cantidad=1):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT energia FROM jugadores WHERE id_usuario = ?", (id_usuario,))
    fila = cursor.fetchone()

    if fila:
        nueva = max(fila[0] - cantidad, 0)
        cursor.execute("UPDATE jugadores SET energia = ? WHERE id_usuario = ?", (nueva, id_usuario))
        conn.commit()

    conn.close()


def resetear_todos():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE jugadores
        SET energia = ?, last_reset = ?
    """, (ENERGIA_MAX, datetime.now()))
    conn.commit()
    conn.close()
