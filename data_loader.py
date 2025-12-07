from collections import defaultdict
import json
from pathlib import Path

# ---------- CARGA DE ITEMS / INDICES ----------
p = Path(__file__).parent / "data" / "materiales.json"
MATERIALES = json.loads(p.read_text(encoding="utf-8"))["materiales"]

# PARA LAS POCIONES
# p = Path(__file__).parent / "data" / "consumibles.json"
# CONSUMIBLES = json.loads(p.read_text(encoding="utf-8"))["consumibles"]

p = Path(__file__).parent / "data" / "equipables.json"
EQUIPABLES = json.loads(p.read_text(encoding="utf-8"))["equipables"]

EQUIPABLES_BY_ID = {}
EQUIPABLES_BY_TYPE = defaultdict(list)
EQUIPABLES_BY_RARITY = defaultdict(list)

for item in EQUIPABLES:
    EQUIPABLES_BY_ID[item["id"]] = item
    EQUIPABLES_BY_TYPE[item["tipo"]].append(item)
    EQUIPABLES_BY_RARITY[item["rareza"]].append(item)

RARITY_COLORS = {
    "comun": 0xB0B0B0,       # gris
    "raro": 0x3A82F7,        # azul
    "epico": 0xA335EE,       # violeta
    "legendario": 0xFF8000   # naranja
}

