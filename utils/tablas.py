# tablas.py
from .db import conectar
import json

# -------------------- TABLAS --------------------

def borrar_tabla_jugadores():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS jugadores")
    conn.commit()
    conn.close()

def crear_tabla_jugadores():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS jugadores (
        id_usuario TEXT PRIMARY KEY,
        username TEXT,
        afinidad TEXT,
        
        -- stats base
        vida_base INTEGER DEFAULT 100,
        base_damage INTEGER DEFAULT 10,

        -- stats actuales
        vida INTEGER DEFAULT 100,
        damage INTEGER DEFAULT 10,
        energia INTEGER DEFAULT 30,

        -- stats máximos
        vida_max INTEGER DEFAULT 100,

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
    """)
    conn.commit()
    conn.close()

def crear_tabla_items():
    conn = conectar()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id TEXT PRIMARY KEY,
            nombre TEXT NOT NULL,
            tipo TEXT,
            descripcion TEXT,
            rareza TEXT,
            url TEXT
        )
    """)

    # Cargar materiales desde JSON
    with open("data/materiales.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    for item in data["materiales"]:
        cursor.execute(
            """
            INSERT OR IGNORE INTO items (id, nombre, tipo, descripcion, rareza, url)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (item["id"], item["nombre"], item["tipo"], item["descripcion"], item["rareza"], item.get("url"))
        )

    conn.commit()
    conn.close()

def crear_tabla_inventario():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS inventario (
            user_id TEXT NOT NULL,
            item_id TEXT NOT NULL,
            cantidad INTEGER NOT NULL DEFAULT 0,
            PRIMARY KEY (user_id, item_id),
            FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE
        )
    """)
    conn.commit()
    conn.close()
