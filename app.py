import json
from pathlib import Path
import pandas as pd
import streamlit as st

st.set_page_config(page_title="ShelfVision AI", page_icon="🛒", layout="wide")
st.title("ShelfVision AI")
st.caption("Planogram-aware shelf auditing — prototype dashboard")

st.warning(
    "Prototype note: the starter detector is generic. Object counts are only a zone-level proxy, "
    "not validated SKU-level inventory. Do not treat alerts as ground truth until evaluated."
)

plan_path = Path("data/planogram.json")
audit_path = Path("outputs/audit.csv")
annotated_path = Path("outputs/annotated.jpg")

left, right = st.columns(2)
with left:
    st.subheader("Planogram")
    if plan_path.exists():
        plan = json.loads(plan_path.read_text(encoding="utf-8"))
        st.write(f"Store: {plan.get('store_id', 'demo-store')}")
        st.dataframe(pd.DataFrame(plan.get("zones", [])), use_container_width=True)
    else:
        st.info("Add data/planogram.json.")

with right:
    st.subheader("Latest audit")
    if audit_path.exists():
        audit = pd.read_csv(audit_path)
        high = int((audit["priority"] == "HIGH").sum()) if "priority" in audit else 0
        medium = int((audit["priority"] == "MEDIUM").sum()) if "priority" in audit else 0
        m1, m2, m3 = st.columns(3)
        m1.metric("Zones audited", len(audit))
        m2.metric("High priority", high)
        m3.metric("Medium priority", medium)
        st.dataframe(audit, use_container_width=True)
        st.download_button("Download audit CSV", audit.to_csv(index=False), "shelf_audit.csv", "text/csv")
    else:
        st.info("Run detection and audit scripts to generate outputs/audit.csv.")

if annotated_path.exists():
    st.subheader("Annotated image")
    st.image(str(annotated_path), use_container_width=True)
