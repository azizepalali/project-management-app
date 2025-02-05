import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# Sayfanın tam genişlikte olması için ayar
st.set_page_config(layout="wide", page_title="Product Analytics Gantt Chart Creator 🚀", page_icon="🚀")

# Başlık
st.title("Product Analytics Gantt Chart Creator 🚀")

# Kullanıcıdan veri yükleme (Excel veya kopyala-yapıştır metin)
option = st.radio("Choose data input method:", ("Upload Excel File", "Paste Data"))

df = None

if option == "Upload Excel File":
    uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx", "xls"])
    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file)

elif option == "Paste Data":
    pasted_data = st.text_area("Paste your tab-separated data here:")
    if pasted_data:
        try:
            from io import StringIO
df = pd.read_csv(StringIO(pasted_data), sep="	")
        except Exception as e:
            st.error(f"Error parsing data: {e}")

if df is not None:
    # Verinin uygun formatta olduğundan emin ol
    required_columns = {"Main Domain", "Sub Domain", "Subject Area", "Task", "Start Date", "End Date"}
    if required_columns.issubset(df.columns):
        df["Start Date"] = pd.to_datetime(df["Start Date"], format="%Y-%m-%d").dt.date
        df["End Date"] = pd.to_datetime(df["End Date"], format="%Y-%m-%d").dt.date
        
        # Veri kümesindeki minimum ve maksimum tarihleri belirle
        min_date = df["Start Date"].min()
        max_date = df["End Date"].max()
        
        # Varsayılan başlangıç ve bitiş tarihlerini ayarla
        default_start = max(min_date, datetime(2025, 1, 1).date())
        default_end = min(max_date, datetime(2025, 3, 1).date())
        
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.selectbox("Select Start Date", sorted(df["Start Date"].unique()), index=sorted(df["Start Date"].unique()).index(default_start) if default_start in df["Start Date"].unique() else 0)
        with col2:
            available_end_dates = sorted(df[df["Start Date"] >= start_date]["End Date"].unique())
            end_date = st.selectbox("Select End Date", available_end_dates, index=available_end_dates.index(default_end) if default_end in available_end_dates else len(available_end_dates) - 1)
        
        # Seçilen tarih aralığında veriyi filtrele
        df = df[(df["Start Date"] >= start_date) & (df["End Date"] <= end_date)]
        
        # Zaman aralıklarını 7 günlük bölümler halinde göster
        date_range = pd.date_range(start=start_date, end=end_date, freq='7D')
        
        # Ana Domain gruplarına göre sıralama, Task'ları Sub Domain bazında sıralama
        df = df.sort_values(by=["Main Domain", "Sub Domain", "Start Date"])
        
        # Filtreleme seçenekleri üstte olacak şekilde düzenlendi
        col1, col2, col3 = st.columns(3)
        
        with col1:
            main_domain = st.multiselect("Select Main Domain", sorted(df["Main Domain"].dropna().unique().tolist()), default=[])
        with col2:
            sub_domain_options = sorted(df[df["Main Domain"].isin(main_domain)]["Sub Domain"].dropna().unique().tolist()) if main_domain else sorted(df["Sub Domain"].dropna().unique().tolist())
            sub_domain = st.multiselect("Select Sub Domain", sub_domain_options, default=[])
        with col3:
            subject_area_options = sorted(df[df["Sub Domain"].isin(sub_domain)]["Subject Area"].dropna().unique().tolist()) if sub_domain else sorted(df["Subject Area"].dropna().unique().tolist())
            subject_area = st.multiselect("Select Subject Area", subject_area_options, default=[])
        
        # Filtreleme işlemi
        filtered_df = df.copy()
        if main_domain:
            filtered_df = filtered_df[filtered_df["Main Domain"].isin(main_domain)]
        if sub_domain:
            filtered_df = filtered_df[filtered_df["Sub Domain"].isin(sub_domain)]
        if subject_area:
            filtered_df = filtered_df[filtered_df["Subject Area"].isin(subject_area)]
        
        # Data'yı kopyala yapıştır ile almak için gösterme
        st.subheader("Filtered Data")
        st.dataframe(filtered_df)
        st.text_area("Copy/Paste Data", filtered_df.to_csv(index=False, sep='\t'))
        
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
                height=1000,  # Grafiğin dikey boyutunu artırdım
                width=2200,
                xaxis_title="Timeline",
                xaxis=dict(side="top", showgrid=True, tickmode='array', tickvals=date_range, ticktext=[d.strftime('%d %b %Y') for d in date_range]),
                legend=dict(orientation="h", yanchor="top", y=1.2, xanchor="center", x=0.5)
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("Excel dosyanızda 'Main Domain', 'Sub Domain', 'Subject Area', 'Task', 'Start Date' ve 'End Date' sütunları bulunmalıdır.")
