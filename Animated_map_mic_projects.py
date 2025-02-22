import pandas as pd
import plotly.express as px
from uszipcode import SearchEngine

# Read the data
df = pd.read_csv(r"C:\Users\serge\Documents\My Tableau Prep Repository\Datasources\2023.csv", low_memory=False)

# Convert 'Date of Service' to a datetime object
df['Date of Service'] = pd.to_datetime(df['Date of Service'])

# Create an instance of SearchEngine
search = SearchEngine()

def get_lat_lng(zipcode):
    result = search.by_zipcode(zipcode)
    if result:
        return result.lat, result.lng
    else:
        return None, None  # Return None if there's no result

df['Lat'], df['Lng'] = zip(*df['Location Zip Code'].astype(str).apply(get_lat_lng))

# Group by 'Date of Service' and other desired columns
grouped = df.groupby(['Date of Service', 'Location Zip Code', 'Location of Service Name', 'Lat', 'Lng'])['PATIENT ACCOUNT NUMBER'].count().reset_index()

# Create a scatter mapbox animation
fig = px.scatter_mapbox(grouped,
                        lat="Lat",
                        lon="Lng",
                        size="PATIENT ACCOUNT NUMBER",
                        hover_name="Location of Service Name",
                        hover_data=["Location Zip Code"],
                        color_discrete_sequence=["fuchsia"],
                        zoom=3,
                        height=300,
                        animation_frame=grouped['Date of Service'].dt.strftime('%Y-%m-%d'), 
                        title='Spread of Patient Volume over Time')

fig.update_layout(mapbox_style="open-street-map")
fig.update_layout(showlegend=False)
fig.show()
