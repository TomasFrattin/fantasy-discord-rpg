from collections import defaultdict
import json
from pathlib import Path

# ---------- CARGA DE ITEMS / INDICES ----------
p = Path(__file__).parent / "data" / "materiales.json"
MATERIALES = json.loads(p.read_text(encoding="utf-8"))["materiales"]

p = Path(__file__).parent / "data" / "peces.json"
PECES = json.loads(p.read_text(encoding="utf-8"))["peces"]

p = Path(__file__).parent / "data" / "mobs.json"
MOBS = json.loads(p.read_text(encoding="utf-8"))["mobs"]

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


