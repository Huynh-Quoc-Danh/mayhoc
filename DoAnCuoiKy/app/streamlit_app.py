"""Web demo phân loại ngành hàng từ tiêu đề sản phẩm – Nhóm 06.
Chạy (từ thư mục DoAnCuoiKy):  streamlit run app/streamlit_app.py
"""
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / "src"))
from common import clean_title  # cùng hàm làm sạch lúc huấn luyện

MODEL_PATH = ROOT / "models" / "final_svc_hybrid24_C3.joblib"


@st.cache_resource
def nap_mo_hinh():
    return joblib.load(MODEL_PATH)


st.set_page_config(page_title="Phân loại sản phẩm – Nhóm 06", page_icon="🛒")
st.title("Phân loại ngành hàng từ tiêu đề sản phẩm")
st.caption("Mô hình cuối: TF-IDF word (1,2) + char (2,4), LinearSVC C=3 – Test Macro-F1 0.9929")

if not MODEL_PATH.exists():
    st.error(f"Chưa có file mô hình {MODEL_PATH.name}. Chạy mục 8 notebook 05 để tạo file trước.")
    st.stop()
pipe = nap_mo_hinh()

tieu_de = st.text_input("Nhập tiêu đề sản phẩm", "bosch kgn39vwea fridge freezer 366l a++ white")
if tieu_de.strip():
    X = pd.DataFrame({"clean": [clean_title(tieu_de)], "merchant_id": [0]})
    nganh = pipe.predict(X)[0]
    st.success(f"Ngành dự đoán: **{nganh}**")

    # LinearSVC không có xác suất: dùng điểm quyết định để xếp hạng 3 ngành gần nhất
    diem = pipe.decision_function(X)[0]
    top = np.argsort(diem)[::-1][:3]
    st.subheader("3 ngành có điểm cao nhất")
    st.table(pd.DataFrame({"Ngành": pipe.classes_[top], "Điểm quyết định": diem[top].round(3)}))
    st.caption(f"Tiêu đề sau khi làm sạch: `{X.clean[0]}`")