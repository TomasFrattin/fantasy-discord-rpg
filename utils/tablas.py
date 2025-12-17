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
        user_id TEXT PRIMARY KEY,
        username TEXT,
        afinidad TEXT,
        
        -- vida
        vida_base INTEGER DEFAULT 100,
        vida INTEGER DEFAULT 100,
        vida_max INTEGER DEFAULT 100,
        
        -- daño
        base_damage INTEGER DEFAULT 10,
        damage INTEGER DEFAULT 10,
        
        -- energía
        energia INTEGER DEFAULT 3,
        energia_max INTEGER DEFAULT 3,
        
        -- niveles y experiencia
        lvl_recoleccion INTEGER DEFAULT 1,
        exp_recoleccion INTEGER DEFAULT 0,
        lvl_caceria INTEGER DEFAULT 1,
        exp_caceria INTEGER DEFAULT 0,
        lvl_prestigio INTEGER DEFAULT 1,
        exp_prestigio INTEGER DEFAULT 0,

        -- equipo
        arma_equipada TEXT,
        armadura_equipada TEXT,
        casco_equipado TEXT,
        botas_equipadas TEXT,
        cana_equipada TEXT,     
                        
        -- otros
        oro INTEGER DEFAULT 0,
        last_reset TEXT,

        -- acciones
        accion_actual TEXT DEFAULT NULL,
        accion_fin TEXT DEFAULT NULL
    )
    """)
    conn.commit()
    conn.close()

def crear_tabla_jugadores_nueva():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS jugadores_nueva (
        user_id TEXT PRIMARY KEY,
        username TEXT,
        afinidad TEXT,
        
        -- vida
        vida_base INTEGER DEFAULT 100,
        vida INTEGER DEFAULT 100,
        vida_max INTEGER DEFAULT 100,
        
        -- daño
        base_damage INTEGER DEFAULT 10,
        damage INTEGER DEFAULT 10,
        
        -- energía
        energia INTEGER DEFAULT 3,
        energia_max INTEGER DEFAULT 3,
        
        -- niveles y experiencia
        lvl_recoleccion INTEGER DEFAULT 1,
        exp_recoleccion INTEGER DEFAULT 0,
        lvl_caceria INTEGER DEFAULT 1,
        exp_caceria INTEGER DEFAULT 0,
        lvl_prestigio INTEGER DEFAULT 1,
        exp_prestigio INTEGER DEFAULT 0,

        -- equipo
        arma_equipada TEXT,
        armadura_equipada TEXT,
        casco_equipado TEXT,
        botas_equipadas TEXT,
        cana_equipada TEXT,   -- NUEVA COLUMNA
                    
        -- otros
        oro INTEGER DEFAULT 0,
        last_reset TEXT,

        -- acciones
        accion_actual TEXT DEFAULT NULL,
        accion_fin INTEGER DEFAULT NULL
    )
    """)
    
    # Copiar los datos de la tabla antigua
    cursor.execute("""
    INSERT INTO jugadores_nueva (
        user_id, username, afinidad, vida_base, vida, vida_max, 
        base_damage, damage, energia, energia_max, lvl_recoleccion,
        exp_recoleccion, lvl_caceria, exp_caceria, lvl_prestigio, exp_prestigio,
        arma_equipada, armadura_equipada, casco_equipado, botas_equipadas,
        oro, last_reset, accion_actual, accion_fin
    )
    SELECT user_id, username, afinidad, vida_base, vida, vida_max,
           base_damage, damage, energia, energia_max, lvl_recoleccion,
           exp_recoleccion, lvl_caceria, exp_caceria, lvl_prestigio, exp_prestigio,
           arma_equipada, armadura_equipada, casco_equipado, botas_equipadas,
           oro, last_reset, accion_actual, accion_fin
    FROM jugadores
    """)
    
    # Eliminar la tabla vieja y renombrar la nueva
    cursor.execute("DROP TABLE jugadores")
    cursor.execute("ALTER TABLE jugadores_nueva RENAME TO jugadores")
    
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
