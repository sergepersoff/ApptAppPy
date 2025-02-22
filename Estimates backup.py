import pandas as pd
import sqlite3
from pathlib import Path

# Function to print debug information
def debug_print(message, df=None):
    print(message)
    if df is not None:
        print(df.head())
    print("\n")

# Set the path for the CSV file
file_path = Path('C:\\Users\\serge\\Desktop\\DOV\\2023\\HHA_Dov_2023.csv')

# Define the path for the output CSV file
output_path = Path('C:\\Users\\serge\\Desktop\\DOV\\Dov Revenue Project\\Estimates.csv')

# Read the CSV file into a DataFrame
df = pd.read_csv(file_path, parse_dates=['Date of Service'], low_memory=False)
debug_print("Initial DataFrame loaded:", df)

# Rename the columns for ease of use and ensure all relevant fields are strings for SQL compatibility
rename_columns = {
    "Transaction Code (Charge, Payment or Adjustment)": "Transaction_Code",
    "Provider of Service Name": "Provider_of_Service_Name",
    "Location of Service Name": "Location_of_Service_Name",
    "Primary Insurance Carrier Name": "Primary_Insurance_Carrier_Name",
    "Total Payments Amount": "Total_Payments_Amount",
    "Total Adjustments Amount": "Total_Adjustments_Amount"
}
df.rename(columns=rename_columns, inplace=True)
debug_print("Columns renamed:", df)

# Ensure 'Units of Service' is numeric
df['Units of Service'] = pd.to_numeric(df['Units of Service'], errors='coerce').fillna(0)
debug_print("Units of Service converted to numeric:", df)

# Special handling for transaction codes 'Q4253' and 'Q4248'
special_codes = {'Q4253': 482.00, 'Q4248': 868.44}
for code, price_per_unit in special_codes.items():
    # Filter for the specific code and zero payment amount
    df_special = df[(df['Transaction_Code'] == code) & (df['Total_Payments_Amount'] == 0)]
    
    # Calculate the estimated revenue for these transactions
    df_special['Estimated_Revenue'] = df_special['Units of Service'] * price_per_unit
    
    # Update the main DataFrame with the estimated revenue for these transactions
    df.loc[df_special.index, 'Estimated_Revenue'] = df_special['Estimated_Revenue']

# Identify transactions with negative 'Units of Service'
negative_units_transactions = df[df['Units of Service'] < 0]
debug_print("Negative Units of Service identified:", negative_units_transactions)

# Initialize an empty DataFrame to store indices to remove
indices_to_remove = pd.DataFrame()

# Loop through negative 'Units of Service' transactions
for index, neg_tran in negative_units_transactions.iterrows():
    # Find the corresponding positive transaction
    matching_positives = df[
        (df['Date of Service'] == neg_tran['Date of Service']) &
        (df['Transaction_Code'] == neg_tran['Transaction_Code']) &
        (df['Units of Service'] == -neg_tran['Units of Service'])
    ]
    
    # If match is found, add to indices_to_remove
    if not matching_positives.empty:
        indices_to_remove = indices_to_remove._append(matching_positives)

# Display potential voided transactions before removal
debug_print("Potential voided transactions to remove:", indices_to_remove)

# Drop duplicates from indices_to_remove
indices_to_remove.drop_duplicates(inplace=True)

# Get indices for both positive and negative transactions
indices_to_remove = indices_to_remove.index.union(negative_units_transactions.index)

# Exclude transactions with indices in indices_to_remove
df = df.drop(indices_to_remove)
debug_print("Voided transactions removed. DataFrame after removal:", df)

# Convert to absolute values and fill NaNs where needed
df['Total_Payments_Amount'] = df['Total_Payments_Amount'].fillna(0).abs()
df['Total_Adjustments_Amount'] = df['Total_Adjustments_Amount'].fillna(0).abs()

# Create Day Name column with the actual date
df['Day_Name'] = df['Date of Service'].dt.strftime('%Y-%m-%d')

# Convert all necessary fields to string type
str_columns = ['Transaction_Code', 'Provider_of_Service_Name', 'Location_of_Service_Name', 'Primary_Insurance_Carrier_Name']
for col in str_columns:
    df[col] = df[col].astype(str)
debug_print("Columns converted to string and Day_Name added:", df)

# Establish a database connection and cursor
conn = sqlite3.connect(':memory:')  # Using in-memory database for processing
df.to_sql('transactions', conn, index=False, if_exists='replace')
debug_print("DataFrame loaded into SQLite database.")

# Define hierarchies
hierarchies = [
    ['Day_Name', 'Transaction_Code', 'Provider_of_Service_Name', 'Location_of_Service_Name', 'Primary_Insurance_Carrier_Name'],
    ['Transaction_Code', 'Provider_of_Service_Name', 'Location_of_Service_Name', 'Primary_Insurance_Carrier_Name'],
    ['Transaction_Code', 'Location_of_Service_Name', 'Primary_Insurance_Carrier_Name'],
    ['Transaction_Code', 'Primary_Insurance_Carrier_Name'],
    ['Transaction_Code']
]

# Initialize a DataFrame to hold the results
final_results_df = pd.DataFrame()

# Process each hierarchy level
for level, group in enumerate(hierarchies):
    group_str = ', '.join(f'"{g}"' for g in group)  # Ensure the group names are quoted for SQL
    
    # Exclude the special Q-codes in the WHERE clause
    zeros_query = f'''
        SELECT {group_str}, COUNT(*) as "Number_of_Zero_Payment_Visits"
        FROM transactions
        WHERE "Total_Payments_Amount" = 0 AND "Transaction_Code" NOT IN ('Q4253', 'Q4248')
        GROUP BY {group_str}
    '''
    averages_query = f'''
        SELECT {group_str}, AVG("Total_Payments_Amount") as "Average_Payment_Amount"
        FROM transactions
        WHERE "Total_Payments_Amount" > 0 AND "Transaction_Code" NOT IN ('Q4253', 'Q4248')
        GROUP BY {group_str}
    '''
    merge_query = f'''
        SELECT z.*, a."Average_Payment_Amount"
        FROM ({zeros_query}) z
        LEFT JOIN ({averages_query}) a ON { ' AND '.join(f'z."{g}" = a."{g}"' for g in group) }
    '''
    # Execute the merge query and retrieve the results
    level_results = pd.read_sql(merge_query, conn)
    debug_print(f"Debug Level {level} - Zero Payments with Averages:", level_results)

    # If this is the first level, initialize the final results DataFrame with the current level results
    if final_results_df.empty:
        final_results_df = level_results
    else:
        # Merge the current level results with the final results DataFrame
        final_results_df = final_results_df.merge(level_results, on=group, how='left', suffixes=('', f'_level{level}'))
        # Update the 'Average_Payment_Amount' to the value from the current level if it's not NaN
        final_results_df['Average_Payment_Amount'] = final_results_df.apply(
            lambda row: row[f'Average_Payment_Amount_level{level}'] if not pd.isna(row[f'Average_Payment_Amount_level{level}']) else row['Average_Payment_Amount'],
            axis=1
        )
        # Drop the additional 'Average_Payment_Amount' columns
        final_results_df.drop(columns=[f'Average_Payment_Amount_level{level}'], inplace=True)
    debug_print(f"Debug - Final Results after Level {level} merging:", final_results_df)

# Calculate the estimated revenue payments for non-Q code transactions
final_results_df['Estimated_Revenue_Payments'] = final_results_df['Number_of_Zero_Payment_Visits'] * final_results_df['Average_Payment_Amount']
debug_print("Estimated Revenue Payments calculated for non-Q code transactions:", final_results_df)

# Calculate the total sums of payments and adjustments per day
total_sums_query = '''
    SELECT "Day_Name", SUM("Total_Payments_Amount") as "Total_Payments_Amount", SUM("Total_Adjustments_Amount") as "Total_Adjustments_Amount"
    FROM transactions
    GROUP BY "Day_Name"
'''
total_sums_result = pd.read_sql(total_sums_query, conn)
debug_print("Total sums of payments and adjustments per day:", total_sums_result)

# Merge the estimated revenue with the daily sums
final_results_with_sums = pd.merge(final_results_df, total_sums_result, on='Day_Name', how='left')
final_results_with_sums['Duplicated'] = final_results_with_sums.duplicated(subset='Day_Name', keep='first')

# Only keep the total sums for the first occurrence of each 'Day_Name'
final_results_with_sums.loc[final_results_with_sums['Duplicated'], 'Total_Payments_Amount'] = None
final_results_with_sums.loc[final_results_with_sums['Duplicated'], 'Total_Adjustments_Amount'] = None
final_results_with_sums.drop(columns='Duplicated', inplace=True)

# Filter out the Q codes with the special calculations from the original dataframe
q_codes_df = df[df['Transaction_Code'].isin(special_codes.keys())]

# Since the estimated revenue for Q codes is already calculated in the original dataframe, we just need to select the relevant columns
q_codes_df = q_codes_df[['Day_Name', 'Transaction_Code', 'Provider_of_Service_Name', 'Location_of_Service_Name', 'Primary_Insurance_Carrier_Name', 'Estimated_Revenue']]

# Rename the 'Estimated_Revenue' column to 'Estimated_Revenue_Payments' to match the final_results_with_sums DataFrame
q_codes_df.rename(columns={'Estimated_Revenue': 'Estimated_Revenue_Payments'}, inplace=True)

# Add the Q codes DataFrame to the final results DataFrame
final_results_with_sums = pd.concat([final_results_with_sums, q_codes_df], ignore_index=True)

# Filter out rows where 'Estimated_Revenue_Payments' is zero or NaN
final_results_with_sums = final_results_with_sums[final_results_with_sums['Estimated_Revenue_Payments'].notna() & (final_results_with_sums['Estimated_Revenue_Payments'] != 0)]

# Debug step to check for any NaN or zeros in 'Estimated_Revenue_Payments' before exporting
nan_or_zeros = final_results_with_sums[(final_results_with_sums['Estimated_Revenue_Payments'].isna()) | (final_results_with_sums['Estimated_Revenue_Payments'] == 0)]
if not nan_or_zeros.empty:
    debug_print("Warning: NaN or zero values found in 'Estimated_Revenue_Payments':", nan_or_zeros)
else:
    debug_print("No NaN or zero values in 'Estimated_Revenue_Payments' - Ready to export.")

# Save to CSV
final_results_with_sums.to_csv(output_path, index=False)
print(f"CSV file has been saved to: {output_path}")

# Close the database connection
conn.close()




