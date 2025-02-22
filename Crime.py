import requests
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import calendar

# Function to map month number to month name
def month_num_to_name(month_num):
    return calendar.month_name[month_num]

# Function to process and plot data for a given city
def process_city_data(city_name, url, headers, params):
    # Make the request
    response = requests.get(url, headers=headers, params=params)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Parse the JSON response
        data = response.json()
        
        # Convert data to DataFrame
        df = pd.DataFrame(data)
        
        # Convert 'month_number' from string to int, then to month name
        df['month_number'] = pd.to_numeric(df['month_number'], errors='coerce')
        df['month_name'] = df['month_number'].apply(month_num_to_name)
        
        # Create a 'Month-Year' column for grouping
        df['Month-Year'] = df['month_name'] + ' ' + df['complaint_year_number'].astype(str)
        
        # Ensure correct ordering for 'Month-Year'
        df['Month-Year'] = pd.to_datetime(df['Month-Year'], format='%B %Y')
        df.sort_values('Month-Year', inplace=True)
        
        # Save the raw data to a CSV file
        csv_file_path = f'C:\\Users\\serge\\Desktop\\EDIFY\\MIsc projects\\{city_name}_Hate_Crimes_Raw_Data.csv'
        df.to_csv(csv_file_path, index=False)
        
        print(f"Raw data for {city_name} successfully saved to", csv_file_path)
        
        # Filter for race-related bias motives
        race_related_biases = ['ANTI-WHITE', 'ANTI-JEWISH', 'ANTI-ARAB']
        race_data = df[df['bias_motive_description'].isin(race_related_biases)]
        
        # Group by 'Month-Year' and 'bias_motive_description'
        grouped_data = race_data.groupby(['Month-Year', 'bias_motive_description']).size().unstack(fill_value=0)
        
        # Plotting as a line chart
        fig, ax = plt.subplots(figsize=(15, 7))
        grouped_data.plot(ax=ax, marker='o')
        
        # Format x-ticks with month names
        ax.xaxis.set_major_locator(mdates.MonthLocator(bymonthday=1, interval=1))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%B %Y'))
        plt.xticks(rotation=90)
        
        plt.xlabel('Month-Year')
        plt.ylabel('Number of Complaints')
        plt.title(f'Trend of Complaints by Month-Year and Bias Motive for {city_name}')
        plt.legend(title='Bias Motive', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(True)
        plt.tight_layout()
        plt.show()
        
    else:
        print(f"Failed to retrieve data for {city_name}: {response.status_code}")

# Calculate the current year and the year 5 years ago
current_year = datetime.now().year
five_years_ago = current_year - 5

# Parameters common to both cities
common_params = {
    '$where': f"complaint_year_number >= '{five_years_ago}'",
    '$limit': 50000  # Adjust the limit as needed
}
headers = {
    'X-App-Token': 'rHSoAD1VIbjeozo2vDNnt1dYu'  # You might need different tokens for different cities
}

# Process New York data
ny_url = "https://data.cityofnewyork.us/resource/bqiq-cu78.json"
process_city_data('New_York', ny_url, headers, common_params)

# Process Chicago data
# You will need the correct endpoint URL for Chicago's dataset
chicago_url = "https://data.cityofchicago.org/resource/ydr8-5enu.json"  # Placeholder URL
process_city_data('Chicago', chicago_url, headers, common_params)
