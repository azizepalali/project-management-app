import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Başlık
st.title("Gantt Chart Creator")

# Kullanıcıdan Excel dosyası yükleme
uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx", "xls"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    
    # Verinin uygun formatta olduğundan emin ol
    if set(["Task", "Start", "End", "Category"]).issubset(df.columns):
        df["Start"] = pd.to_datetime(df["Start"])
        df["End"] = pd.to_datetime(df["End"])
        
        # Gantt şeması oluşturma
        fig = px.timeline(df, x_start="Start", x_end="End", y="Task", color="Category", title="Gantt Chart")
        fig.update_yaxes(categoryorder="total ascending")
        st.plotly_chart(fig)
    else:
        st.error("Excel dosyanızda 'Task', 'Start', 'End' ve 'Category' sütunları bulunmalıdır.")
else:
    st.write("Please upload an Excel file to generate the Gantt chart.")

