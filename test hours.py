import pandas as pd

# Read the dataset
path_2023 = r'C:\Users\serge\Documents\My Tableau Prep Repository\Datasources\2023.csv'
df_2023 = pd.read_csv(path_2023, encoding='ISO-8859-1')
df_2023['Date of Service'] = pd.to_datetime(df_2023['Date of Service'])

# Provider and date filters
provider_name = "BRYAN, ROCHELLE"
date_of_service = "07/03/2023"  # Format as mm/dd/yyyy
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

# Ensure that the Transaction Code column is of type string
df_2023['Transaction Code'] = df_2023['Transaction Code'].astype(str)

# Filter the dataset for the specified provider, date, and transaction codes
filtered_data = df_2023[
    (df_2023['Provider of Service Name'] == provider_name) & 
    (df_2023['Date of Service'].dt.strftime('%m/%d/%Y') == date_of_service) & 
    (df_2023['Transaction Code'].isin(transaction_codes))
]

# Calculate total minutes for this provider and date
filtered_data['Minutes'] = filtered_data['Transaction Code'].map(code_to_minutes)

# Group by transaction code and sum the minutes
transaction_code_counts = filtered_data.groupby('Transaction Code')['Minutes'].sum().reset_index()

# Print all transaction codes and their counts
print("All Transaction Codes:")
print(transaction_code_counts)

# Calculate total hours
total_hours = transaction_code_counts['Minutes'].sum() / 60

# Print the total hours
print(f"Total hours for {provider_name} on {date_of_service}: {total_hours:.4f} hours")
