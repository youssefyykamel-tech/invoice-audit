import streamlit as st
import pandas as pd
from invoice_reader import read_invoice

st.set_page_config(
    page_title="Medical Invoice Auditor",
    page_icon="🏥",
    layout="wide"
)

st.title("🏥 Medical Invoice Auditor")
st.subheader("نظام مراجعة الفواتير الطبية")

st.write("ارفع الملفات التالية لبدء المراجعة:")

invoice = st.file_uploader(
    "الفاتورة الطبية",
    type=["pdf"]
)

price_list = st.file_uploader(
    "قائمة الأسعار Price List",
    type=["xlsx", "xls", "csv", "pdf"]
)

medical_report = st.file_uploader(
    "التقرير الطبي",
    type=["pdf", "docx"]
)

if st.button("ابدأ المراجعة"):
    if invoice and price_list and medical_report:
        rows, unread = read_invoice(invoice)

        st.success(f"تم استخراج {len(rows)} بند من الفاتورة")

        if rows:
            st.subheader("جميع بنود الفاتورة")
            st.dataframe(rows)

            df = pd.DataFrame(rows)

            duplicates = df.groupby("name").agg(
                عدد_مرات_التكرار=("name", "count"),
                إجمالي_الكمية=("qty", "sum"),
                إجمالي_المبلغ=("total", "sum")
            ).reset_index()

            duplicates = duplicates[
                duplicates["عدد_مرات_التكرار"] > 1
            ]

            st.subheader("البنود المتكررة")
            st.dataframe(duplicates)

    else:
        st.warning("من فضلك ارفع الملفات الثلاثة أولاً")