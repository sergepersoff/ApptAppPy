import pandas as pd

# Create the provider dictionary from the HHA_Dov_2023.csv file
def create_provider_dict(file_path):
    df = pd.read_csv(file_path, low_memory=False)
    provider_data = df[["Provider of Service", "Provider of Service Name"]].drop_duplicates().dropna()
    return dict(zip(provider_data["Provider of Service"], provider_data["Provider of Service Name"]))

# Paths for the datasets
dov_est_path = r'C:\Users\serge\Desktop\DOV\Dov Revenue Project\Dov_est.csv'
hha_dov_path = r'C:\Users\serge\Desktop\DOV\2023\HHA_Dov_2023.csv'

# Create the dictionary
provider_dict_cleaned = create_provider_dict(hha_dov_path)

# Read the Dov_est dataset
dov_est_df = pd.read_csv(dov_est_path, parse_dates=['DATE'], low_memory=False)

# Capitalize string columns (if needed)
dov_est_df['LOCATION'] = dov_est_df['LOCATION'].str.upper()
dov_est_df['PROVIDER'] = dov_est_df['PROVIDER'].str.upper()

# Convert the "Est. Rev" column to numeric
dov_est_df['Est. Rev'] = pd.to_numeric(dov_est_df['Est. Rev'], errors='coerce')

# Aggregate the data
agg_dov_est = dov_est_df.groupby(['DATE', 'LOCATION', 'PROVIDER']).agg({
    'Est. Rev': 'sum'
}).reset_index()

# Using the dictionary to map "PROVIDER" to "Provider of Service Name"
agg_dov_est['Provider of Service Name'] = agg_dov_est['PROVIDER'].map(provider_dict_cleaned)

# Save the aggregated data to the specified path
agg_dov_est.to_csv(r'C:\Users\serge\Desktop\DOV\Dov Revenue Project\aggregated.csv', index=False)

# Paths for the datasets
matched_path = r'C:\Users\serge\Desktop\DOV\matched.csv'  
aggregated_path = r'C:\Users\serge\Desktop\DOV\Dov Revenue Project\aggregated.csv'

# Read the datasets
matched_df = pd.read_csv(matched_path, parse_dates=['Date of Service'])
agg_dov_est = pd.read_csv(aggregated_path, parse_dates=['DATE'])

# Merge the dataframes using specified criteria
merged_df = pd.merge(matched_df, agg_dov_est, 
                     left_on=['Date of Service', 'Location of Service', 'Provider of Service Name'], 
                     right_on=['DATE', 'LOCATION', 'Provider of Service Name'], 
                     how='outer', 
                     indicator=True)

print(merged_df['_merge'].value_counts())

merged_df.to_csv(r'C:\Users\serge\Desktop\DOV\merged_result.csv', index=False)