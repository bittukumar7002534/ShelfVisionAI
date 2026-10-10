import argparse
from pathlib import Path
import cv2
import pandas as pd
from ultralytics import YOLO

def main():
    parser = argparse.ArgumentParser(description="Run generic YOLO object detection on a shelf image.")
    parser.add_argument("--image", required=True, help="Path to an authorized shelf image")
    parser.add_argument("--output", default="outputs/annotated.jpg", help="Annotated image output path")
    parser.add_argument("--model", default="yolo11n.pt", help="Ultralytics model weights")
    parser.add_argument("--confidence", type=float, default=0.25)
    args = parser.parse_args()

    image_path = Path(args.image)
    if not image_path.exists():
        raise SystemExit(f"Image not found: {image_path}. Add an image at this path first.")

    model = YOLO(args.model)
    results = model.predict(source=str(image_path), conf=args.confidence, verbose=False)
    result = results[0]
    annotated = result.plot()
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(output_path), annotated)

    rows = []
    names = result.names
    if result.boxes is not None:
        for box in result.boxes:
            x1, y1, x2, y2 = [float(v) for v in box.xyxy[0].tolist()]
            cls_id = int(box.cls[0].item())
            rows.append({
                "detection_id": len(rows) + 1,
                "class_id": cls_id,
                "class_name": names.get(cls_id, str(cls_id)),
                "confidence": float(box.conf[0].item()),
                "x1": x1, "y1": y1, "x2": x2, "y2": y2,
                "center_x": (x1 + x2) / 2, "center_y": (y1 + y2) / 2
            })

    csv_path = output_path.with_name("detections.csv")
    pd.DataFrame(rows, columns=[
        "detection_id", "class_id", "class_name", "confidence",
        "x1", "y1", "x2", "y2", "center_x", "center_y"
    ]).to_csv(csv_path, index=False)
    print(f"Annotated image: {output_path}")
    print(f"Detection table: {csv_path}")
    print("Reminder: generic COCO classes are not retail SKU identities.")

if __name__ == "__main__":
    main()
