
import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="تحليل أداء السائقين", layout="wide")

st.title("📦 تحليل المرتجعات ونسب الأداء حسب السائق")

st.markdown("**يرجى رفع ملف Excel يحتوي على الأعمدة التالية:**")
st.code("Invoice | Driver | ReturnCode | Delivered", language="markdown")

uploaded_file = st.file_uploader("📤 ارفع ملف Excel", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)

        return_codes = ["DD", "DNF", "DP", "CM", "MD"]
        drivers = ["بشرى", "ارفند", "ارباز", "نيام", "ياسر"]

        df = df[df["Invoice"].str.startswith("SO", na=False)]
        df = df[df["Driver"].isin(drivers)]

        df["Failed"] = df["ReturnCode"].isin(return_codes).astype(int)
        df["Successful"] = (~df["ReturnCode"].isin(return_codes)).astype(int)

        summary = df.groupby("Driver").agg(
            TotalDeliveries=("Delivered", "sum"),
            FailedDeliveries=("Failed", "sum"),
            SuccessfulDeliveries=("Successful", "sum")
        ).reset_index()

        summary["SuccessRate (%)"] = (summary["SuccessfulDeliveries"] / summary["TotalDeliveries"] * 100).round(2)
        summary["FailureRate (%)"] = (summary["FailedDeliveries"] / summary["TotalDeliveries"] * 100).round(2)

        st.success("✅ تم تحليل البيانات بنجاح")
        st.dataframe(summary, use_container_width=True)

        @st.cache_data
        def convert_df(df):
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                df.to_excel(writer, index=False)
            return output.getvalue()

        excel_data = convert_df(summary)

        st.download_button(
            label="📥 تحميل النتيجة كـ Excel",
            data=excel_data,
            file_name="driver_return_summary.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    except Exception as e:
        st.error(f"❌ حدث خطأ أثناء قراءة الملف: {e}")
