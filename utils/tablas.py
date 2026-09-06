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

def migrar_accion_fin_a_integer():
    """Migra la columna accion_fin de TEXT a INTEGER si es necesario."""
    conn = conectar()
    cursor = conn.cursor()
    
    try:
        # Verificar si la tabla existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='jugadores'")
        if not cursor.fetchone():
            conn.close()
            return
        
        # Verificar el tipo de accion_fin
        cursor.execute("PRAGMA table_info(jugadores)")
        columnas = cursor.fetchall()
        
        accion_fin_type = None
        for col in columnas:
            if col[1] == "accion_fin":
                accion_fin_type = col[2]
                break
        
        # Si ya es INTEGER, no hacer nada
        if accion_fin_type == "INTEGER":
            conn.close()
            return
        
        # Hacer la migración
        cursor.execute("""
            CREATE TABLE jugadores_migrado AS
            SELECT 
                user_id, username, afinidad,
                vida_base, vida, vida_max,
                base_damage, damage,
                energia, energia_max,
                lvl_recoleccion, exp_recoleccion,
                lvl_caceria, exp_caceria,
                lvl_prestigio, exp_prestigio,
                arma_equipada, armadura_equipada, casco_equipado, botas_equipadas,
                cana_equipada, oro, last_reset,
                accion_actual,
                CASE WHEN accion_fin = '' OR accion_fin IS NULL THEN NULL ELSE CAST(accion_fin AS INTEGER) END as accion_fin
            FROM jugadores
        """)
        
        cursor.execute("DROP TABLE jugadores")
        cursor.execute("ALTER TABLE jugadores_migrado RENAME TO jugadores")
        
        conn.commit()
    except Exception as e:
        print(f"Error en migración de accion_fin: {e}")
    finally:
        conn.close()

def crear_tabla_jugadores():
    # Primero intentar migrar si es necesario
    migrar_accion_fin_a_integer()
    
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
        accion_fin INTEGER DEFAULT NULL
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
    """Crea y sincroniza el catálogo común de materiales y equipables."""
    conn = conectar()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id TEXT PRIMARY KEY,
            nombre TEXT NOT NULL,
            tipo TEXT,
            descripcion TEXT,
            rareza TEXT,
            url TEXT,
            valor_oro INTEGER NOT NULL DEFAULT 0
        )
    """)

    cursor.execute("PRAGMA table_info(items)")
    columnas_items = {columna[1] for columna in cursor.fetchall()}
    if "valor_oro" not in columnas_items:
        cursor.execute(
            "ALTER TABLE items ADD COLUMN valor_oro INTEGER NOT NULL DEFAULT 0"
        )

    catalogos = (
        ("data/materiales.json", "materiales"),
        ("data/equipables.json", "equipables"),
        ("data/consumibles.json", "consumibles"),
        ("data/eventos.json", "items"),
    )

    for ruta, clave in catalogos:
        with open(ruta, "r", encoding="utf-8") as archivo:
            items = json.load(archivo)[clave]

        for item in items:
            cursor.execute(
                """
                INSERT INTO items (id, nombre, tipo, descripcion, rareza, url, valor_oro)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    nombre = excluded.nombre,
                    tipo = excluded.tipo,
                    descripcion = excluded.descripcion,
                    rareza = excluded.rareza,
                    url = excluded.url,
                    valor_oro = excluded.valor_oro
                """,
                (
                    item["id"],
                    item["nombre"],
                    item["tipo"],
                    item["descripcion"],
                    item["rareza"],
                    item.get("url"),
                    item.get("valor_oro", 0),
                ),
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

def crear_tablas_eventos():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS eventos_instancias (
            instance_id TEXT PRIMARY KEY,
            event_id TEXT NOT NULL,
            started_at INTEGER NOT NULL,
            ends_at INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'active'
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS eventos_recompensas (
            instance_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            item_id TEXT NOT NULL,
            obtained_at INTEGER NOT NULL,
            PRIMARY KEY (instance_id, user_id, item_id),
            FOREIGN KEY (instance_id) REFERENCES eventos_instancias(instance_id)
        )
    """)
    conn.commit()
    conn.close()

# ------------------------
# Crear tabla dungeon
# ------------------------
def crear_tabla_dungeon():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dungeon (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            oro_recompensa INTEGER NOT NULL,
            nivel_recomendado INTEGER NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# ------------------------
# Crear tabla boss
# ------------------------
def crear_tabla_boss():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS boss (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dungeon_id INTEGER NOT NULL,
            nombre TEXT NOT NULL,
            vida INTEGER NOT NULL,
            damage INTEGER NOT NULL,
            FOREIGN KEY (dungeon_id) REFERENCES dungeon(id) ON DELETE CASCADE
        )
    """)
    conn.commit()
    conn.close()

# ------------------------
# Insertar dungeon de ejemplo
# ------------------------
def insertar_dungeons_base():
    dungeons = [
        ("Cripta Antigua", 500, 3),
        ("Abismo del Coloso", 900, 6),
        ("Santuario del Eclipse", 1500, 9),
        ("Trono del Vacío", 2500, 13),
        ("Trono del Apocalipsis", 4000, 18),
    ]

    conn = conectar()
    cursor = conn.cursor()

    for nombre, oro, nivel in dungeons:
        cursor.execute(
            "SELECT id FROM dungeon WHERE nombre = ?",
            (nombre,)
        )
        if cursor.fetchone() is None:
            cursor.execute(
                """
                INSERT INTO dungeon (nombre, oro_recompensa, nivel_recomendado)
                VALUES (?, ?, ?)
                """,
                (nombre, oro, nivel)
            )

    conn.commit()
    conn.close()

# ------------------------
# Insertar bosses de ejemplo
# ------------------------
def insertar_bosses_base():
    bosses_por_dungeon = {
        "Cripta Antigua": [
            ("Guardián Óseo", 150, 25),
            ("Nigromante Caído", 120, 35),
            ("Rey de los Huesos", 200, 40),
            ("Liche Despierto", 260, 45),
        ],
        "Abismo del Coloso": [
            ("Titán de Piedra", 450, 50),
            ("Martillo Viviente", 500, 55),
            ("Coloso Ancestral", 600, 60),
            ("Corazón del Abismo", 750, 70),
        ],
        "Santuario del Eclipse": [
            ("Sacerdote Sombrío", 420, 65),
            ("Avatar del Eclipse", 520, 75),
            ("Vigía Crepuscular", 600, 85),
            ("Señor del Eclipse", 750, 95),
        ],
        "Trono del Vacío": [
            ("Heraldo del Vacío", 700, 90),
            ("Entropía Viva", 850, 105),
            ("Eco del Fin", 1000, 120),
            ("Rey del Vacío", 1200, 140),
        ],
        "Trono del Apocalipsis": [
            ("Destructor Primordial", 1200, 150),
            ("Fragmento del Caos", 1400, 170),
            ("Juicio Final", 1600, 190),
            ("El Innombrable", 2000, 220),
        ],
    }

    conn = conectar()
    cursor = conn.cursor()

    for dungeon_nombre, bosses in bosses_por_dungeon.items():
        cursor.execute(
            "SELECT id FROM dungeon WHERE nombre = ?",
            (dungeon_nombre,)
        )
        fila = cursor.fetchone()
        if not fila:
            continue

        dungeon_id = fila[0]

        for nombre, vida, damage in bosses:
            cursor.execute(
                """
                SELECT id FROM boss
                WHERE dungeon_id = ? AND nombre = ?
                """,
                (dungeon_id, nombre)
            )
            if cursor.fetchone() is None:
                cursor.execute(
                    """
                    INSERT INTO boss (dungeon_id, nombre, vida, damage)
                    VALUES (?, ?, ?, ?)
                    """,
                    (dungeon_id, nombre, vida, damage)
                )

    conn.commit()
    conn.close()

# ------------------------
# Crear tablas de contribuciones
# ------------------------
def crear_tabla_fondos():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fondos (
            id TEXT PRIMARY KEY,
            objetivo INTEGER NOT NULL,
            acumulado INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

def crear_tabla_contribuciones():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contribuciones (
            user_id TEXT NOT NULL,
            fondo_id TEXT NOT NULL,
            cantidad INTEGER NOT NULL,
            PRIMARY KEY (user_id, fondo_id),
            FOREIGN KEY (fondo_id) REFERENCES fondos(id) ON DELETE CASCADE
        )
    """)
    conn.commit()
    conn.close()

# ------------------------
# Función de inicialización completa
# ------------------------
def inicializar_dungeons():
    crear_tabla_dungeon()
    crear_tabla_boss()
    insertar_dungeons_base()
    insertar_bosses_base()
