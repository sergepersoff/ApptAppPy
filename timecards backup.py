import pandas as pd

# Read the dataset
path_time_cards = r'C:\Users\serge\Desktop\DOV\Time Cards.csv'
df_time_cards = pd.read_csv(path_time_cards, encoding='ISO-8859-1')

# Format the dataset

# Convert 'Date' column to datetime format
df_time_cards['Date'] = pd.to_datetime(df_time_cards['Date'])

# Capitalize the 'Practitioner' column
df_time_cards['Practitioner'] = df_time_cards['Practitioner'].str.upper()

# Renaming the entry
df_time_cards['Practitioner'] = df_time_cards['Practitioner'].replace('LIM, JU HYUN', 'LIM, HYUN')


# Display the first few rows to verify the formatting
print(df_time_cards.head())

# Save the formatted dataset
formatted_output_path = r'C:\Users\serge\Desktop\DOV\Formatted_Time_Cards.csv'
df_time_cards.to_csv(formatted_output_path, index=False, encoding='ISO-8859-1')


# Read the dataset
path_2023 = r'C:\Users\serge\Documents\My Tableau Prep Repository\Datasources\2023.csv'
df_2023 = pd.read_csv(path_2023, encoding='ISO-8859-1')
df_2023['Date of Service'] = pd.to_datetime(df_2023['Date of Service'])

# Providers and transaction codes as provided
providers = ["GAMIDOVA, SOFIA", "SAITTA, ALEXANDER", "LIM, HYUN", "BRYAN, ROCHELLE", "MCDERMOTT, MICHELE"]
transaction_codes = ["99304", "99305", "99306", "99307", "99308", "99309", "99310"]

# Transaction codes to minutes mapping
code_to_minutes = {
    "99304": 25,
    "99305": 35,
    "99306": 45,
    "99307": 10,
    "99308": 15,
    "99309": 30,
    "99310": 45
}

# DOS range
start_date = "2023-07-01"
end_date = "2023-09-30"

# Filter the dataset
filtered_data = df_2023[
    (df_2023['Provider of Service Name'].isin(providers)) & 
    (df_2023['Date of Service'] >= start_date) & 
    (df_2023['Date of Service'] <= end_date) & 
    (df_2023['Transaction Code'].isin(transaction_codes))
]

# Copy the filtered data to prevent warnings
filtered_data = filtered_data.copy()
filtered_data['Hours'] = filtered_data['Transaction Code'].map(code_to_minutes) / 60

# Group by Provider and Date of Service and sum the hours
grouped_data = filtered_data.groupby(['Provider of Service Name', 'Date of Service'])['Hours'].sum().reset_index()

# Save the grouped data
grouped_data.to_csv(r'C:\Users\serge\Desktop\DOV\HHAhours.csv', index=False)


# Read the HHAhours file 
path_hha_hours = r'C:\Users\serge\Desktop\DOV\HHAhours.csv'
df_hha_hours = pd.read_csv(path_hha_hours, encoding='ISO-8859-1')

# Convert both 'Date' columns to datetime format
df_time_cards['Date'] = pd.to_datetime(df_time_cards['Date'])
df_hha_hours['Date of Service'] = pd.to_datetime(df_hha_hours['Date of Service'])

# Create a date range for July 2023 excluding weekends (business days)
date_range = pd.bdate_range(start="2023-07-01", end="2023-09-30")

# Create a new dataframe for BRYAN, ROCHELLE using that date range
data = {
    'Practitioner': ['BRYAN, ROCHELLE'] * len(date_range),
    'Date': date_range,
    'Hours': [8] * len(date_range)
}
rochelle_df = pd.DataFrame(data)

# 3. Append this new dataframe to df_time_cards
df_time_cards = pd.concat([df_time_cards, rochelle_df], ignore_index=True)

# 1. Merge the datasets
merged_data = pd.merge(df_time_cards, df_hha_hours, 
                       left_on=['Date', 'Practitioner'], 
                       right_on=['Date of Service', 'Provider of Service Name'], 
                       how='outer', suffixes=('_timecards', '_hha'))

# 2. Save the merged dataset to an Excel file
merged_output_path_temp = r'C:\Users\serge\Desktop\DOV\Temp_Hours_Analysis.xlsx'
merged_data.to_excel(merged_output_path_temp, index=False, engine='openpyxl')

# 3. Read the Excel file back into a DataFrame
merged_data_readback = pd.read_excel(merged_output_path_temp, engine='openpyxl')

# 4. Print all the column names
print(merged_data_readback.columns)

# Fill missing values in 'Hours_timecards' with values from ' Hours '
merged_data_readback['Hours_timecards'].fillna(merged_data_readback[' Hours '], inplace=True)

# Now, you can perform your calculations
merged_data_readback['Difference'] = merged_data_readback['Hours_timecards'] - merged_data_readback['Hours_hha']
merged_data_readback['Efficiency score'] = merged_data_readback['Hours_hha'] / merged_data_readback['Hours_timecards']

# Save the results again if needed
final_output_path = r'C:\Users\serge\Desktop\DOV\Hours_Analysis.csv'
merged_data_readback.to_csv(final_output_path, index=False, encoding='ISO-8859-1')
