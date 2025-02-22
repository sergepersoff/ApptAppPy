import pandas as pd
import os
import warnings
warnings.filterwarnings('ignore')

# Paths for input datasets
hha_dov_path = r'C:\Users\serge\Desktop\DOV\2023\HHA_Dov_2023.csv'
dov_est_path = r'C:\Users\serge\Desktop\DOV\Dov Revenue Project\Dov_est.csv'

# Read the input files
hha_dov_df = pd.read_csv(hha_dov_path, parse_dates=['Date of Service'])
dov_est_df = pd.read_csv(dov_est_path, parse_dates=['DATE'])

# Capitalize all string columns in both dataframes
hha_dov_df = hha_dov_df.applymap(lambda s: s.upper() if type(s) == str else s)
dov_est_df = dov_est_df.applymap(lambda s: s.upper() if type(s) == str else s)

# Create 'Full Account Number' in Dov_est
dov_est_df['ACCOUNT'] = dov_est_df['ACCOUNT'].astype(str)
dov_est_df['Full Account Number'] = dov_est_df['Entity'] + "." + dov_est_df['ACCOUNT']

# Outer merge on 'Full Account Number' and 'DATE'
merged_df = pd.merge(hha_dov_df, dov_est_df[['DATE', 'Full Account Number', 'Est. Rev']], 
                     left_on=['PATIENT ACCOUNT NUMBER', 'Date of Service'], 
                     right_on=['Full Account Number', 'DATE'], 
                     how='outer', indicator=True)

# Separate the matched and unmatched records
matched_records = merged_df[merged_df['_merge'] == 'both']
unmatched_records = merged_df[merged_df['_merge'] != 'both']

# Print counts of matched and unmatched records
print(f"Number of matched records: {len(matched_records)}")
print(f"Number of unmatched records: {len(unmatched_records)}")

# Paths for output files
output_directory = r'C:\Users\serge\Desktop\DOV\Dov Revenue Project'
matched_records_path = os.path.join(output_directory, 'merged1.csv')
unmatched_records_path = os.path.join(output_directory, 'unmatched1.csv')

# Save the dataframes to respective CSV files
matched_records.to_csv(matched_records_path, index=False)
unmatched_records.to_csv(unmatched_records_path, index=False)

print("Merged data saved to merged1.csv")
print("Unmatched data saved to unmatched1.csv")
