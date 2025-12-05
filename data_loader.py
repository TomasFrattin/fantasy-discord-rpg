from pathlib import Path
import json
p = Path(__file__).parent / "data" / "items.json"
ITEMS = json.loads(p.read_text(encoding="utf-8"))["items_equipables"]
ITEMS_BY_ID = { item["id"]: item for item in ITEMS }