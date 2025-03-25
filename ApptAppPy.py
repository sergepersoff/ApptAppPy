import os
import pandas as pd
import streamlit as st
import plotly.express as px

# ✅ Set the path to the CSV file
csv_path = "appointments_public.csv"  # Make sure this is the correct relative path

def load_data():
    """Load the de-identified public CSV."""
    try:
        df = pd.read_csv(csv_path, parse_dates=['Start Date'])
        df['Start Date'] = pd.to_datetime(df['Start Date'], errors='coerce')
        return df.dropna(subset=['Start Date'])  # Drop rows where 'Start Date' is NaT
    except FileNotFoundError:
        st.error(f"File {csv_path} not found!")
        return pd.DataFrame()  # Return empty DataFrame if file not found

# Load the data
data = load_data()

# Display the data (this can be useful for debugging)
if not data.empty:
    st.write(f"Loaded {len(data)} records.")
else:
    st.write("No data loaded.")

# Filter appointments by status
status_filter = st.selectbox("Select Appointment Status", data['Appointment Status'].unique())

filtered_data = data[data['Appointment Status'] == status_filter]

# Visualizing the filtered appointments per day
appointments_per_day = filtered_data.groupby(filtered_data['Start Date'].dt.date).size().reset_index(name='Appointment Count')

# Plotting the line chart
fig = px.line(appointments_per_day, x='Start Date', y='Appointment Count', title=f"Appointments per Day - {status_filter}")
st.plotly_chart(fig)

# Allow user to zoom in on the chart
st.write("Use the interactive plot above to zoom in and analyze appointments.")
