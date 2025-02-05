import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from io import StringIO

# Sayfanın tam genişlikte olması için ayar
st.set_page_config(layout="wide", page_title="Product Analytics Gantt Chart Creator 🚀", page_icon="🚀")

# Başlık
st.title("Product Analytics Gantt Chart Creator 🚀")

# Kullanıcıdan veri yükleme (Excel veya kopyala-yapıştır metin)
option = st.radio("Choose data input method:", ("Upload Excel File", "Paste Comma-Separated Data"))

df = None

if option == "Upload Excel File":
    uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx", "xls"])
    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file)

elif option == "Paste Comma-Separated Data":
    pasted_data = st.text_area("Paste your comma-separated data here:")
    if pasted_data:
        try:
            rows = [line.split(",") for line in pasted_data.strip().split("\n")]
            df = pd.DataFrame(rows[1:], columns=rows[0])
        except Exception as e:
            st.error(f"Error parsing data: {e}")

if df is not None:
    # Verinin uygun formatta olduğundan emin ol
    required_columns = {"Main Domain", "Sub Domain", "Subject Area", "Task", "Start Date", "End Date"}
    if required_columns.issubset(df.columns):
        df["Start Date"] = pd.to_datetime(df["Start Date"], errors='coerce').dt.date
        df["End Date"] = pd.to_datetime(df["End Date"], errors='coerce').dt.date
        
        # Veri kümesindeki minimum ve maksimum tarihleri belirle
        min_date = df["Start Date"].min() if not pd.isna(df["Start Date"].min()) else datetime.today().date()
        max_date = df["End Date"].max() if not pd.isna(df["End Date"].max()) else datetime.today().date()
        
        # Varsayılan başlangıç ve bitiş tarihlerini ayarla
        default_start = max(min_date, datetime(2025, 1, 1).date())
        default_end = min(max_date, datetime(2025, 3, 1).date())
        
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Select Start Date", value=default_start, min_value=min_date, max_value=max_date)
        with col2:
            end_date = st.date_input("Select End Date", value=default_end, min_value=min_date, max_value=max_date)
        
        # Seçilen tarih aralığında veriyi filtrele
        df = df[(df["Start Date"] >= start_date) & (df["End Date"] <= end_date)]
        
        # Zaman aralıklarını 7 günlük bölümler halinde göster
        date_range = pd.date_range(start=start_date, end=end_date, freq='7D')
        
        # Ana Domain gruplarına göre sıralama, Task'ları Sub Domain bazında sıralama
        df = df.sort_values(by=["Main Domain", "Sub Domain", "Start Date"])
        
        # Filtreleme seçenekleri üstte olacak şekilde düzenlendi
        col1, col2, col3 = st.columns(3)
        
        with col1:
            main_domain = st.multiselect("Select Main Domain", sorted(df["Main Domain"].dropna().unique().tolist()))
        with col2:
            sub_domain_options = sorted(df[df["Main Domain"].isin(main_domain)]["Sub Domain"].dropna().unique().tolist()) if main_domain else sorted(df["Sub Domain"].dropna().unique().tolist())
            sub_domain = st.multiselect("Select Sub Domain", sub_domain_options)
        with col3:
            subject_area_options = sorted(df[df["Sub Domain"].isin(sub_domain)]["Subject Area"].dropna().unique().tolist()) if sub_domain else sorted(df["Subject Area"].dropna().unique().tolist())
            subject_area = st.multiselect("Select Subject Area", subject_area_options)
        
        # Filtreleme işlemi
        filtered_df = df.copy()
        if main_domain:
            filtered_df = filtered_df[filtered_df["Main Domain"].isin(main_domain)]
        if sub_domain:
            filtered_df = filtered_df[filtered_df["Sub Domain"].isin(sub_domain)]
        if subject_area:
            filtered_df = filtered_df[filtered_df["Subject Area"].isin(subject_area)]
        
        # Data'yı indirme butonu
        
        
        # Her Main Domain için ayrı Gantt Chart oluşturma
        for domain in filtered_df["Main Domain"].unique():
            domain_df = filtered_df[filtered_df["Main Domain"] == domain].sort_values(by=["Sub Domain", "Start Date"])
            st.subheader(f"Gantt Chart for {domain}")
            fig = px.timeline(domain_df, x_start="Start Date", x_end="End Date", y="Task", color="Sub Domain", 
                              title=f"Gantt Chart - {domain}", text="Task", hover_data=["Sub Domain", "Subject Area", "Task"])
            fig.update_traces(marker=dict(line=dict(width=2, color='rgba(0,0,0,0.3)')), textposition='outside')  # Gölge efekti eklendi
            fig.update_yaxes(categoryorder="total ascending", showgrid=True, visible=True)
            fig.update_layout(bargap=0.1, 
                autosize=True,
                height=200,  # Grafiğin dikey boyutunu artırdım
                width=2200,
                xaxis_title="Timeline",
                xaxis=dict(side="top", showgrid=True, tickmode='array', tickvals=date_range, ticktext=[d.strftime('%d %b %Y') for d in date_range]),
                legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5)
            )
            st.plotly_chart(fig, use_container_width=True)

        # Data'yı en sonda gösterme
        st.subheader("Filtered Data")
        st.dataframe(filtered_df)
        st.download_button(label="Download Filtered Data as CSV", data=filtered_df.to_csv(index=False), file_name="filtered_data.csv", mime="text/csv")
    else:
        st.error("Excel dosyanızda 'Main Domain', 'Sub Domain', 'Subject Area', 'Task', 'Start Date' ve 'End Date' sütunları bulunmalıdır.")
