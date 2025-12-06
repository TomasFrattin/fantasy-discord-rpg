# tablas.py
from .db import conectar

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

def crear_tabla_items_consumibles():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id TEXT PRIMARY KEY,
            nombre TEXT NOT NULL,
            tipo TEXT,
            descripcion TEXT,
            rareza TEXT
        )
    """)
    cursor.executemany("""
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
