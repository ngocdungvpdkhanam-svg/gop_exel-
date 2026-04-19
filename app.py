import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="Excel Merger Pro", layout="centered")

st.title("📂 Excel Merger Pro (Bản Python)")
st.write("Tải lên các file Excel để gộp chúng lại thành một.")

uploaded_files = st.file_uploader("Chọn các tệp Excel...", type=["xlsx", "xls"], accept_multiple_files=True)

if uploaded_files:
    combined_df = pd.DataFrame()
    for i, file in enumerate(uploaded_files):
        df = pd.read_excel(file)
        if i == 0:
            combined_df = df
        else:
            combined_df = pd.concat([combined_df, df], ignore_index=True)
            
    st.success(f"Đã gộp thành công {len(uploaded_files)} tệp!")
    st.dataframe(combined_df.head())

    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        combined_df.to_excel(writer, index=False)
    
    st.download_button(
        label="📥 Tải file đã gộp",
        data=output.getvalue(),
        file_name="combined_excel.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
