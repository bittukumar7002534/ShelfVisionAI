import json
from pathlib import Path

def test_planogram_has_zones():
    plan = json.loads(Path("data/planogram.json").read_text(encoding="utf-8"))
    assert plan["zones"]
    for zone in plan["zones"]:
        assert len(zone["bbox_norm"]) == 4
        assert 0 <= zone["min_facings"] <= zone["target_facings"]
