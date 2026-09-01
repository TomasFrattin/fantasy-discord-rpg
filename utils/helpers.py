from pathlib import Path
from uuid import uuid4

from PIL import Image
from data.canas import CANAS

TEMP_DIR = Path("data/temp")

def canas_ordenadas():
    return sorted(CANAS.items(), key=lambda x: x[1]["tier"])


def ruta_temporal(prefijo: str, ruta_origen: str | Path) -> Path:
    """Devuelve una ruta PNG única para evitar colisiones entre interacciones."""
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    nombre = Path(ruta_origen).stem
    return TEMP_DIR / f"{prefijo}_{nombre}_{uuid4().hex}.png"

def preparar_imagen_mob(ruta, size=(300, 300)):
    img = Image.open(ruta).convert("RGBA")
    img.thumbnail(size, Image.LANCZOS)
    fondo = Image.new("RGBA", size, (0, 0, 0, 0))
    offset = ((size[0] - img.width)//2, (size[1] - img.height)//2)
    fondo.paste(img, offset, img)
    output_path = ruta_temporal("mob", ruta)
    fondo.save(output_path)
    return output_path


def preparar_imagen_npc(ruta, size=(300, 300)):
    img = Image.open(ruta).convert("RGBA")
    img.thumbnail(size, Image.LANCZOS)
    # Reducimos el lienzo vertical a la altura de la imagen + margen mínimo
    new_height = img.height + 20  # por ejemplo, 10px arriba y abajo
    fondo = Image.new("RGBA", (size[0], new_height), (0, 0, 0, 0))
    offset = ((size[0] - img.width)//2, 10)  # 10px arriba
    fondo.paste(img, offset, img)
    output_path = ruta_temporal("npc", ruta)
    fondo.save(output_path)
    return output_path

def preparar_imagen_pez(ruta, size=(300, 300)):
    ruta = Path(ruta)
    if not ruta.is_file():
        ruta = Path("assets/peces") / ruta.name

    if not ruta.exists():
        return None

    img = Image.open(ruta).convert("RGBA")
    img.thumbnail(size, Image.LANCZOS)
    fondo = Image.new("RGBA", size, (0,0,0,0))
    offset = ((size[0]-img.width)//2, (size[1]-img.height)//2)
    fondo.paste(img, offset, img)

    output_path = ruta_temporal("pez", ruta)
    fondo.save(output_path)

    return output_path  # Path, no string

def crear_collage(rutas, tamaño_celda=(128, 128), gap=10):
    if not rutas:
        return None

    cols = min(3, len(rutas))
    filas = (len(rutas) + cols - 1) // cols
    ancho = cols * tamaño_celda[0] + (cols - 1) * gap
    alto = filas * tamaño_celda[1] + (filas - 1) * gap
    collage = Image.new("RGBA", (ancho, alto), (255, 255, 255, 0))

    for idx, ruta in enumerate(rutas):
        img = Image.open(ruta).convert("RGBA").resize(tamaño_celda)
        x = (idx % cols) * (tamaño_celda[0] + gap)
        y = (idx // cols) * (tamaño_celda[1] + gap)
        collage.paste(img, (x, y), img)

    output_path = ruta_temporal("collage", "recoleccion.png")
    collage.save(output_path)
    return output_path
