# ShelfVision AI

Computer-vision-assisted shelf auditing against a digital planogram.

## Current prototype scope
- Load a shelf image.
- Run a pretrained YOLO detector as a generic-object baseline.
- Save an annotated image and detection table.
- Compare manually configured shelf zones with expected product IDs using a transparent rule-based audit.
- Export findings as CSV.

**Important limitation:** a generic pretrained model does not reliably identify retail SKUs. The starter detector is for pipeline demonstration; reliable SKU-level auditing needs product-specific labels/modeling or another product-identification method. Empty shelf gaps are not directly detected by a generic object detector; this starter uses expected-vs-observed zone counts as a heuristic.

## Quick start
Python 3.10+ recommended.

```bash
python -m venv .venv
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# macOS/Linux:
# source .venv/bin/activate

pip install -r requirements.txt
python src/detect.py --image data/sample_shelf.jpg --output outputs/annotated.jpg
python src/audit.py --planogram data/planogram.json --detections outputs/detections.csv --output outputs/audit.csv
streamlit run app.py
```

Put an authorized shelf image at `data/sample_shelf.jpg`. The repository does not include copyrighted store footage or a dataset.

## Planogram format
`data/planogram.json` contains configured zones. Coordinates are normalized fractions of image width/height. Product IDs are placeholders until a product-specific detector or manual annotation provides SKU identities.

## Pipeline
Image -> YOLO baseline -> zone assignment -> planogram rule checks -> alert CSV/dashboard.

## Evaluation before claiming performance
Use a labeled, held-out set of images. Measure detector precision/recall or mAP where applicable, and alert precision/recall for stockout and displacement. Report latency, failure cases, and data conditions. Do not report simulated numbers as measured results.

## Privacy and responsible use
Use footage only with permission. This project does not perform face recognition. Keep human review for uncertain alerts.
