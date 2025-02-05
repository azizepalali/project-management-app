import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

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
        
        # Filtreleme seçenekleri üstte olacak şekilde düzenlendi
        col1, col2, col3 = st.columns(3)
        
        with col1:
            main_domain = st.selectbox("Select Main Domain", ["All"] + sorted(df["Main Domain"].dropna().unique().tolist()))
        with col2:
            sub_domain_options = ["All"] + sorted(df[df["Main Domain"] == main_domain]["Sub Domain"].dropna().unique().tolist()) if main_domain != "All" else ["All"] + sorted(df["Sub Domain"].dropna().unique().tolist())
            sub_domain = st.selectbox("Select Sub Domain", sub_domain_options)
        with col3:
            subject_area_options = ["All"] + sorted(df[df["Sub Domain"] == sub_domain]["Subject Area"].dropna().unique().tolist()) if sub_domain != "All" else ["All"] + sorted(df["Subject Area"].dropna().unique().tolist())
            subject_area = st.selectbox("Select Subject Area", subject_area_options)
        
        # Filtreleme işlemi
        filtered_df = df.copy()
        if main_domain != "All":
            filtered_df = filtered_df[filtered_df["Main Domain"] == main_domain]
        if sub_domain != "All":
            filtered_df = filtered_df[filtered_df["Sub Domain"] == sub_domain]
        if subject_area != "All":
            filtered_df = filtered_df[filtered_df["Subject Area"] == subject_area]
        
        # Gantt şeması oluşturma
        if not filtered_df.empty:
            fig = px.timeline(filtered_df, x_start="Start Date", x_end="End Date", y="Task", color="Subject Area", 
                              title="Filtered Gantt Chart", hover_data=["Main Domain", "Sub Domain", "Subject Area"])
            fig.update_yaxes(categoryorder="total ascending")
            fig.update_layout(
                autosize=True,
                height=900,  # Sayfayı kaplayacak şekilde büyütüldü
                width=1400,
                xaxis_title="Timeline",  # X ekseni başlığı
                xaxis=dict(side="top"),  # Tarihlerin üstte görünmesi
                legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5),  # Legend grafiğin altına alındı
                shapes=[
                    dict(
                        type="rect",
                        xref="x",
                        yref="y",
                        x0=row["Start Date"],
                        x1=row["End Date"],
                        y0=row["Task"],
                        y1=row["Task"],
                        fillcolor="rgba(0, 0, 255, 0.2)",
                        line=dict(width=0)
                    ) for _, row in filtered_df.iterrows()
                ]
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.write("No data available for the selected filters.")
    else:
        st.error("Excel dosyanızda 'Main Domain', 'Sub Domain', 'Subject Area', 'Task', 'Start Date' ve 'End Date' sütunları bulunmalıdır.")
else:
    st.write("Please upload an Excel file to generate the Gantt chart.")