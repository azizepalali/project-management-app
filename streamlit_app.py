import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# Sayfa genişliğini artır
st.set_page_config(layout="wide")

# Başlık
st.title("Interactive Gantt Chart Creator")

# Kullanıcıdan Excel dosyası yükleme
uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx", "xls"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    
    # Verinin uygun formatta olduğundan emin ol
    required_columns = {"Main Domain", "Sub Domain", "Subject Area", "Task", "Start Date", "End Date"}
    if required_columns.issubset(df.columns):
        df["Start Date"] = pd.to_datetime(df["Start Date"])
        df["End Date"] = pd.to_datetime(df["End Date"])
        
        # Zaman aralıklarını 7 günlük bölümler halinde göster
        start_date = datetime(2025, 1, 1)
        end_date = df["End Date"].max()
        date_range = pd.date_range(start=start_date, end=end_date, freq='7D')
        
        # Ana Domain gruplarına göre sıralama, Task'ları Sub Domain bazında sıralama
        df = df.sort_values(by=["Main Domain", "Sub Domain", "Start Date"])
        
        # Filtreleme işlemi
        filtered_df = df.copy()
        
        # Her Main Domain için ayrı Gantt Chart oluşturma
        for domain in filtered_df["Main Domain"].unique():
            domain_df = filtered_df[filtered_df["Main Domain"] == domain].sort_values(by=["Sub Domain", "Start Date"])
            st.subheader(f"Gantt Chart for {domain}")
            fig = px.timeline(domain_df, x_start="Start Date", x_end="End Date", y="Task", color="Sub Domain", 
                              title=f"Gantt Chart - {domain}", text="Task", hover_data=["Sub Domain", "Subject Area", "Task"])
            fig.update_traces(marker=dict(line=dict(width=0)), textposition='inside')
            fig.update_yaxes(categoryorder="total ascending", showgrid=True, visible=False)
            fig.update_layout(
                autosize=True,
                height=600,
                width=1600,
                xaxis_title="Timeline",
                xaxis=dict(side="top", showgrid=True, tickmode='array', tickvals=date_range, ticktext=[d.strftime('%d %b %Y') for d in date_range]),
                legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5)
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("Excel dosyanızda 'Main Domain', 'Sub Domain', 'Subject Area', 'Task', 'Start Date' ve 'End Date' sütunları bulunmalıdır.")
