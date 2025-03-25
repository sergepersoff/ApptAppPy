import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# ✅ Load the de-identified public CSV
def load_data():
    csv_path = r"C:\Users\serge\Desktop\EDIFY\Python\appointments_public.csv"
    df = pd.read_csv(csv_path, parse_dates=['Start Date'])
    df['Start Date'] = pd.to_datetime(df['Start Date'], errors='coerce')
    return df.dropna(subset=['Start Date'])

# ✅ Group data by day and status
def prepare_daily_counts(df):
    df['Date'] = df['Start Date'].dt.date
    status_group = df.groupby(['Date', 'Appointment Status']).size().reset_index(name='Count')
    return status_group

# ✅ Build interactive chart
def render_chart(df):
    fig = px.line(
        df,
        x='Date',
        y='Count',
        color='Appointment Status',
        title='📊 Appointments Per Day by Status',
        markers=True
    )
    fig.update_layout(xaxis=dict(rangeslider=dict(visible=True)), height=600)
    st.plotly_chart(fig, use_container_width=True)

# ✅ Streamlit layout
st.set_page_config(page_title="Appointment Dashboard", layout="wide")
st.title("📅 Appointment Dashboard")
st.markdown("Visualizing daily appointments by status (Cancelled, No Show, Checked Out, etc.)")

# ✅ Load and display data
data = load_data()
st.write(f"Loaded {len(data)} records.")

# ✅ Prepare and visualize
daily_counts = prepare_daily_counts(data)
render_chart(daily_counts)