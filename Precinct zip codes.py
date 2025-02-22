import pandas as pd
from geopy.geocoders import Nominatim
import time

# Load the data
file_path = 'C:\\Users\\serge\\Desktop\\EDIFY\\MIsc projects\\Precinct adresses.xlsx'
data = pd.read_excel(file_path)

# Initialize the geocoder
geolocator = Nominatim(user_agent="my_geocoder", scheme="http")

# Function to get zip code from address
def get_zip_code(address):
    try:
        location = geolocator.geocode(f"{address}, New York, NY")
        if location:
            return location.address.split(',')[-2].strip()
        else:
            return "Not Found"
    except Exception as e:
        print(f"Error geocoding {address}: {e}")
        return "Error"

# Apply the function to your DataFrame
data['Zip Code'] = data['Address'].apply(get_zip_code)

# Save the amended data
data.to_csv('C:\\Users\\serge\\Desktop\\EDIFY\\MIsc projects\\amended_data_with_zip_codes.csv', index=False)
