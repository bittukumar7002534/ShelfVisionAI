import argparse
import json
from pathlib import Path
import pandas as pd

def assign_zone(row, zones, image_width, image_height):
    cx = float(row["center_x"]) / image_width
    cy = float(row["center_y"]) / image_height
    for zone in zones:
        x1, y1, x2, y2 = zone["bbox_norm"]
        if x1 <= cx <= x2 and y1 <= cy <= y2:
            return zone["zone_id"]
    return None

def main():
    parser = argparse.ArgumentParser(description="Run a transparent zone-level planogram audit.")
    parser.add_argument("--planogram", default="data/planogram.json")
    parser.add_argument("--detections", default="outputs/detections.csv")
    parser.add_argument("--output", default="outputs/audit.csv")
    args = parser.parse_args()

    plan_path, det_path = Path(args.planogram), Path(args.detections)
    if not plan_path.exists():
        raise SystemExit(f"Planogram not found: {plan_path}")
    if not det_path.exists():
        raise SystemExit(f"Detection CSV not found: {det_path}. Run src/detect.py first.")

    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    detections = pd.read_csv(det_path)
    zones = plan.get("zones", [])
    width = float(plan.get("image_width", 1280))
    height = float(plan.get("image_height", 720))

    if detections.empty:
        detections["zone_id"] = pd.Series(dtype="object")
    else:
        detections["zone_id"] = detections.apply(
            lambda r: assign_zone(r, zones, width, height), axis=1
        )

    rows = []
    for zone in zones:
        zone_dets = detections[detections["zone_id"] == zone["zone_id"]] if not detections.empty else detections
        observed = int(len(zone_dets))
        minimum = int(zone.get("min_facings", 1))
        target = int(zone.get("target_facings", minimum))
        # This is only a baseline proxy: generic detected objects are not necessarily products/SKUs.
        if observed < minimum:
            issue = "POSSIBLE_LOW_STOCK"
            priority = "HIGH" if observed == 0 else "MEDIUM"
            action = f"Inspect and replenish {zone.get('expected_product_id', 'expected product')} in {zone['zone_id']}"
        else:
            issue = "NO_THRESHOLD_ALERT"
            priority = "LOW"
            action = "No immediate action; verify product identity and facings"
        rows.append({
            "zone_id": zone["zone_id"],
            "zone_name": zone.get("name", ""),
            "expected_product_id": zone.get("expected_product_id", ""),
            "observed_object_count_proxy": observed,
            "minimum_threshold": minimum,
            "target_facings": target,
            "issue_type": issue,
            "priority": priority,
            "recommended_action": action,
            "confidence_note": "Heuristic only; generic detections do not establish SKU identity or true on-shelf inventory."
        })

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(out, index=False)
    print(f"Audit report saved: {out}")
    print("This is a baseline zone-level heuristic, not validated SKU-level stock counting.")

if __name__ == "__main__":
    main()
