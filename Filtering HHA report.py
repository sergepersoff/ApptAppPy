import pandas as pd


# Read the CSV and suppress the DtypeWarning
df = pd.read_csv(r'C:\OUTGOING\2023 HHA MODS.csv', low_memory=False)

# Filter the dataframe based on given practice codes
filter_practices = ['EVO', 'FFP', 'IPA', 'MFL', 'OFF', 'RDP', 'ICF']
df_filtered = df[df['Practice Code'].isin(filter_practices)].copy()

# Rename the 'Transaction Code (Charge, Payment or Adjustment)' column to 'Transaction Code'
df_filtered.rename(columns={'Transaction Code (Charge, Payment or Adjustment)': 'Transaction Code'}, inplace=True)

# Convert 'Transaction Code' column to string type
df_filtered['Transaction Code'] = df_filtered['Transaction Code'].astype(str)

# Save the cleaned data
output_path = r'C:\Users\serge\Desktop\DOV\2023_HHA_MODS.csv'
df_filtered.to_csv(output_path, index=False)

print("File has been saved successfully!")

