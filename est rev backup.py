import pandas as pd
from pathlib import Path
import sqlite3
import pickle
import numpy as np

# Function to print debug information
def debug_print(message, df=None):
    print(message)
    if df is not None:
        print(df.head())
    print("\n")

# Set the path for the CSV file
file_path = Path('C:\\Users\\serge\\Desktop\\DOV\\2023\\HHA_Dov_2023.csv')

# Define the path for the output CSV file
output_path = Path('C:\\Users\\serge\\Desktop\\DOV\\Dov Revenue Project\\Payments_Adj.csv')

# Read the CSV file into a DataFrame
df = pd.read_csv(file_path, parse_dates=['Date of Service'], low_memory=False)
debug_print("Initial DataFrame loaded:", df)
print("Total Payments Sum after initial load:", df['Total Payments Amount'].sum())

# Rename the columns for ease of use
rename_columns = {
    "Transaction Code (Charge, Payment or Adjustment)": "Transaction_Code",
    "Provider of Service Name": "Provider_of_Service_Name",
    "Location of Service Name": "Location_of_Service_Name",
    "Primary Insurance Carrier Name": "Primary_Insurance_Carrier_Name",
    "Total Payments Amount": "Total_Payments_Amount",
    "Total Adjustments Amount": "Total_Adjustments_Amount",
    "Transaction Amount": "Transaction_Amount"

}
df.rename(columns=rename_columns, inplace=True)
debug_print("Columns renamed:", df)
print("Columns after renaming:", df.columns)


# Ensure 'Units of Service' is numeric
df['Units of Service'] = pd.to_numeric(df['Units of Service'], errors='coerce').fillna(0)
debug_print("Units of Service converted to numeric:", df)
print("Total Payments Sum after renaming and initial cleaning:", df['Total_Payments_Amount'].sum())


# Identify and remove voided transactions
indices_to_remove = set()
negative_units_transactions = df[(df['Units of Service'] < 0) & (df['Total_Payments_Amount'] == 0)]

for index, row in negative_units_transactions.iterrows():
    matching_positives = df[
        (df['Date of Service'] == row['Date of Service']) &
        (df['Transaction_Code'] == row['Transaction_Code']) &
        (df['TRANSACTION AMOUNT'] == -row['TRANSACTION AMOUNT']) &
        (df['Units of Service'] == -row['Units of Service']) &
        (df['Total_Payments_Amount'] == 0)  # Additional condition for zero payment
    ].index
    
    if not matching_positives.empty:
        indices_to_remove.update([index])
        indices_to_remove.update(matching_positives)

df.drop(list(indices_to_remove), inplace=True)

# Debug prints
print("Voided transactions removed. Remaining transaction count:", df.shape[0])
print("Total Payments Sum after removing voided transactions:", df['Total_Payments_Amount'].sum())
debug_print("Voided transactions removed. DataFrame after removal:", df)
print("Total Payments Sum after removing negative units:", df['Total_Payments_Amount'].sum())
print("Count after removal:", df.shape[0])
print("Transactions being removed (Negative Units):")
print(negative_units_transactions.head())
print("Transactions being removed (Matching Positives):")

# Fill missing values in the grouping columns with 'Unknown'
grouping_columns = ['Date of Service', 'Location_of_Service_Name', 
                    'Primary_Insurance_Carrier_Name', 'Provider_of_Service_Name', 
                    'Transaction_Code']

for col in grouping_columns:
    df[col] = df[col].fillna('Unknown')

# Group by the specified columns and aggregate the sums
grouped_df = df.groupby(grouping_columns).agg({
    'Total_Payments_Amount': 'sum'
}).reset_index()

# Rename the columns to reflect the aggregated sums
grouped_df.rename(columns={
    'Total_Payments_Amount': 'Total_Payments_Amount_Sum',
    'Total_Adjustments_Amount': 'Total_Adjustments_Amount_Sum'
}, inplace=True)

# Multiply 'Total_Payments_Amount_Sum' by -1
grouped_df['Total_Payments_Amount_Sum'] *= -1
print("Total Payments Sum after grouping and aggregating:", grouped_df['Total_Payments_Amount_Sum'].sum())

# Save the grouped DataFrame using Pickle
grouped_df.to_pickle('C:\\Users\\serge\\Desktop\\DOV\\Dov Revenue Project\\grouped_df.pkl')

# Print the resulting DataFrame with total sums
debug_print("Total sums of payments and adjustments per specified columns:", grouped_df)

# Save the result to a CSV file
grouped_df.to_csv(output_path, index=False)
print(f"CSV file with total sums has been saved to: {output_path}")
print("Total Payments Sum after grouping and aggregating:", grouped_df['Total_Payments_Amount_Sum'].sum())


# Ensure 'Units of Service' is numeric
df['Units of Service'] = pd.to_numeric(df['Units of Service'], errors='coerce').fillna(0)

# Convert Total Payments Amount to positive values
df['Total_Payments_Amount'] = df['Total_Payments_Amount'] * -1

# New prices effective from October 1, 2023
new_prices = {'Q4253': 333.68, 'Q4248': 822.73}
price_change_date = pd.to_datetime('2023-10-01')

# Special handling for transaction codes 'Q4253' and 'Q4248'
# Original prices before October 1, 2023
special_codes = {'Q4253': 482.00, 'Q4248': 868.44}

# Initialize a column for Estimated_Revenue in the original DataFrame
df['Estimated_Revenue'] = 0.0

# Function to determine the correct price based on the date of service
def get_price(code, date_of_service):
    if date_of_service >= price_change_date:
        return new_prices[code]
    else:
        return special_codes[code]

# Iterate over each special code to calculate Estimated_Revenue
for code in special_codes.keys():
    # Identify the rows for the specific Q code
    condition = df['Transaction_Code'] == code
    
    # Apply the price based on the date of service
    df.loc[condition, 'Price_Per_Unit'] = df.loc[condition, 'Date of Service'].apply(lambda date: get_price(code, date))

    # Calculate the expected payment if all units were paid
    df.loc[condition, 'Expected_Payment'] = df.loc[condition, 'Units of Service'] * df.loc[condition, 'Price_Per_Unit']
    
    # Calculate the revenue that is still expected (owed) due to underpayment
    df.loc[condition, 'Revenue_Owed'] = df.loc[condition, 'Expected_Payment'] - df.loc[condition, 'Total_Payments_Amount']

    # Calculate the Estimated_Revenue for rows with zero payment amount
    zero_payment_condition = condition & (df['Total_Payments_Amount'] == 0)
    df.loc[zero_payment_condition, 'Estimated_Revenue'] = df.loc[zero_payment_condition, 'Units of Service'] * df.loc[zero_payment_condition, 'Price_Per_Unit']

    # Add the owed revenue to the Estimated_Revenue for underpaid units
    condition_owed = condition & (df['Revenue_Owed'] > 0)
    df.loc[condition_owed, 'Estimated_Revenue'] += df.loc[condition_owed, 'Revenue_Owed']

# Remove the temporary columns used for calculations
columns_to_drop = ['Expected_Payment', 'Revenue_Owed', 'Price_Per_Unit']
df.drop(columns=columns_to_drop, inplace=True, errors='ignore')
print("Total Payments Sum after handling special codes:", df['Total_Payments_Amount'].sum())
print("Total Estimated Revenue for Special Codes:", df['Estimated_Revenue'].sum())

# Create a separate q_codes_summary DataFrame
q_codes_summary = df[df['Transaction_Code'].isin(special_codes.keys())].groupby([
    'Date of Service', 'Location_of_Service_Name', 'Primary_Insurance_Carrier_Name',
    'Provider_of_Service_Name', 'Transaction_Code'
]).agg({
    'Estimated_Revenue': 'sum'
}).reset_index()

# Group by the specified columns and aggregate the sums for all codes
grouped_df = df.groupby([
    'Date of Service',
    'Location_of_Service_Name',
    'Primary_Insurance_Carrier_Name',
    'Provider_of_Service_Name',
    'Transaction_Code'
]).agg({
    'Total_Payments_Amount': 'sum',
    'Total_Adjustments_Amount': 'sum',
    'Estimated_Revenue': 'sum'  # Include Estimated_Revenue in aggregation
}).reset_index()

# Rename the columns to reflect the aggregated sums
grouped_df.rename(columns={
    'Total_Payments_Amount': 'Total_Payments_Amount_Sum',
    'Total_Adjustments_Amount': 'Total_Adjustments_Amount_Sum'
}, inplace=True)

# Multiply 'Total_Payments_Amount_Sum' by -1
grouped_df['Total_Payments_Amount_Sum'] *= -1

# Save the grouped DataFrame to a CSV file
grouped_df.to_csv(output_path, index=False)
print(f"CSV file with total sums and estimated revenue has been saved to: {output_path}")
print("Total Payments Sum after handling special codes:", df['Total_Payments_Amount'].sum())
print("Total Estimated Revenue in q_codes_summary:", q_codes_summary['Estimated_Revenue'].sum())

# Print columns in q_codes_summary
print("Columns in q_codes_summary:")
print(q_codes_summary.columns)
# Print the structure of q_codes_summary
print("Structure of q_codes_summary:")
print(q_codes_summary.dtypes)  # This will print the data type of each column

# Print the first few rows to inspect the DataFrame
print("\nFirst few rows of q_codes_summary:")
print(q_codes_summary.head())

# Merge the Q codes summary with grouped_df
grouped_df = grouped_df.merge(q_codes_summary, 
                              on=['Date of Service', 'Location_of_Service_Name', 
                                  'Primary_Insurance_Carrier_Name', 'Provider_of_Service_Name', 
                                  'Transaction_Code'], 
                              how='left')



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

final_results_path = 'C:\\Users\\serge\\Desktop\\DOV\\Dov Revenue Project\\final_results_with_estimated_revenue.csv'


# Calculate the overall average payment per transaction code, location, and insurance company
average_payments = df[df['Total_Payments_Amount'] > 0].groupby(
    ['Transaction_Code', 'Location_of_Service_Name', 'Primary_Insurance_Carrier_Name']
).agg({'Total_Payments_Amount': 'mean'}).rename(columns={'Total_Payments_Amount': 'Average_Payment'})

# If any of the variables are missing for this calculation to take place,
# use a different set of variables limited only to average payment per transaction code.
average_payments_fallback = df[df['Total_Payments_Amount'] > 0].groupby(
    'Transaction_Code'
)['Total_Payments_Amount'].mean().reset_index(name='Average_Payment_Fallback')

# Merge the average payments with the original DataFrame
merged_data = df.merge(average_payments, how='left', 
                       on=['Transaction_Code', 'Location_of_Service_Name', 'Primary_Insurance_Carrier_Name'])

# Where Average_Payment is NaN, fill in with the fallback average payment
merged_data = merged_data.merge(average_payments_fallback, how='left', on='Transaction_Code')
merged_data['Average_Payment'] = merged_data['Average_Payment'].fillna(merged_data['Average_Payment_Fallback'])

# Clean up the columns - no longer needed fallback column
merged_data.drop(columns=['Average_Payment_Fallback'], inplace=True)

# Count the number of zero payments per transaction code, location, insurance company per date of service
zero_payment_counts = df[df['Total_Payments_Amount'] == 0].groupby(
    ['Date of Service', 'Transaction_Code', 'Location_of_Service_Name', 'Primary_Insurance_Carrier_Name']
).size().reset_index(name='Zero_Payment_Count')

# Merge the zero payment counts with the average payments
final_results = merged_data.merge(zero_payment_counts, how='left', 
                                  on=['Date of Service', 'Transaction_Code', 'Location_of_Service_Name', 'Primary_Insurance_Carrier_Name'])

# Fill NaN values in Zero_Payment_Count with 0
final_results['Zero_Payment_Count'] = final_results['Zero_Payment_Count'].fillna(0)

# Update 'Estimated_Revenue_NonQ' where 'Transaction_Code' starts with 'Q'
condition = final_results['Transaction_Code'].str.startswith('Q')
final_results.loc[condition, 'Estimated_Revenue_NonQ'] = final_results.loc[condition, 'Estimated_Revenue']

# Assume the 'final_results_path' variable is defined earlier in your script and points to your desired CSV output path.
final_results.to_csv(final_results_path, index=False)


# Define the path for the output CSV file
final_results_path = 'C:\\Users\\serge\\Desktop\\DOV\\Dov Revenue Project\\final_results_with_estimated_revenue.csv'

# Check for missing Average_Payment after merging
missing_avg_payment = final_results['Average_Payment'].isna()
debug_print("Rows with missing Average_Payment after merging:", final_results[missing_avg_payment])


# Check for missing Average_Payment after merging
missing_avg_payment = final_results['Average_Payment'].isna()
debug_print("Rows with missing Average_Payment after merging:", final_results[missing_avg_payment])

# Output the non-Q code estimated revenue data for review
print("Non-Q Code Estimated Revenue Data:")
print(merged_data.head())

# Define the path for the output CSV file for non-Q code estimated revenue
output_csv_path_non_q = 'C:\\Users\\serge\\Desktop\\DOV\\Dov Revenue Project\\non_q_estimated_revenue.csv'

# Save the non-Q code estimated revenue data to a CSV file
merged_data.to_csv(output_csv_path_non_q, index=False)
print(f"CSV file with non-Q code estimated revenue has been saved to: {output_csv_path_non_q}")

# Output the final DataFrame
print(merged_data.head())

# Save the final DataFrame to a CSV file
merged_data.to_csv('C:\\Users\\serge\\Desktop\\DOV\\Dov Revenue Project\\new_approach_est.csv', index=False)
print("CSV file with estimated revenue for non-Q code transactions has been saved.")

# Output the final merged data
print(final_results.head())

print("Final Total Payments Sum:", final_results['Total_Payments_Amount'].sum())
# Check if 'Estimated_Revenue' exists in final_results before merging
if 'Estimated_Revenue' in final_results.columns:
    print("Estimated_Revenue column exists in final_results.")
else:
    print("Estimated_Revenue column does not exist in final_results. Please check your calculations.")

# Merge the Q codes summary with final_results
final_results = final_results.merge(
    q_codes_summary, 
    on=['Date of Service', 'Location_of_Service_Name', 'Primary_Insurance_Carrier_Name', 
        'Provider_of_Service_Name', 'Transaction_Code'], 
    how='left'
)

# Calculate 'Estimated_Revenue_NonQ' for each row
final_results['Estimated_Revenue_NonQ'] = final_results['Zero_Payment_Count'] * final_results['Average_Payment']

# Identify duplicates in the specified combination of variables, excluding 'Estimated_Revenue_NonQ'
duplicate_mask = final_results.duplicated(subset=['Date of Service', 'Transaction_Code', 
                                                  'Location_of_Service_Name', 'Primary_Insurance_Carrier_Name'], 
                                          keep='first')

# Replace only the 'Estimated_Revenue_NonQ' of duplicates with NaN
final_results.loc[duplicate_mask, 'Estimated_Revenue_NonQ'] = np.nan

# Calculate the total of 'Estimated_Revenue_NonQ' after handling duplicates
total_estimated_revenue_nonq = final_results['Estimated_Revenue_NonQ'].sum()
print("Total Estimated Revenue (Non-Q):", total_estimated_revenue_nonq)

# Output a preview of the final DataFrame
print(final_results.head())

# Save the final DataFrame to a CSV file
final_output_csv_path = 'C:\\Users\\serge\\Desktop\\DOV\\Dov Revenue Project\\final_results_with_estimated_revenue.csv'
final_results.to_csv(final_output_csv_path, index=False)
print(f"CSV file with final results including estimated revenue (duplicates handled) has been saved to: {final_output_csv_path}")

# Assuming 'final_results_path' is the path to your CSV file and is defined earlier in your script
final_results_path = 'C:\\Users\\serge\\Desktop\\DOV\\Dov Revenue Project\\final_results_with_estimated_revenue.csv'

# Load the final results to make sure we have the most up-to-date data
final_results = pd.read_csv(final_results_path)

# Verify that 'Estimated_Revenue_y' exists in the DataFrame
if 'Estimated_Revenue_y' not in final_results.columns:
    print("Column 'Estimated_Revenue_y' does not exist in the DataFrame. Please check the CSV file or prior steps in the script.")
else:
    # Update 'Estimated_Revenue_NonQ' where 'Transaction_Code' starts with 'Q'
    condition = final_results['Transaction_Code'].str.startswith('Q')
    final_results.loc[condition, 'Estimated_Revenue_NonQ'] = final_results.loc[condition, 'Estimated_Revenue_y']

    # Save the updated final results
    final_results.to_csv(final_results_path, index=False)
    print(f"CSV file with updated estimated revenue has been saved to: {final_results_path}")

# Load the final results to make sure we have the most up-to-date data
final_results_path = 'C:\\Users\\serge\\Desktop\\DOV\\Dov Revenue Project\\final_results_with_estimated_revenue.csv'
final_results = pd.read_csv(final_results_path)

# Select only the specified fields
final_columns = [
    'Date of Service',
    'Date of Batch',
    'Transaction_Code',
    'Modifier Codes',
    'Units of Service',
    'TRANSACTION AMOUNT',
    'Provider_of_Service_Name',
    'Location_of_Service_Name',
    'Primary_Insurance_Carrier_Name',
    'Action Code',
    'Primary Insurance Deductible',
    'Primary Insurance Coinsurance',
    'Action Code Description',
    'Practice Code',
    'Practice Name',
    'Due total: Patient + Insurance',
    'Total_Payments_Amount',
    'Total_Adjustments_Amount',
    'Average_Payment',
    'Zero_Payment_Count',
    'Estimated_Revenue_NonQ'  # This will be renamed in the next step
]

# Filter the DataFrame to include only the specified columns
final_results = final_results[final_columns]

# Rename the 'Estimated_Revenue_NonQ' column to 'Net_AR_Revenue'
final_results.rename(columns={'Estimated_Revenue_NonQ': 'Net_AR_Revenue'}, inplace=True)

# Save the final DataFrame to a CSV file
final_output_csv_path = 'C:\\Users\\serge\\Desktop\\DOV\\Dov Revenue Project\\final_results_with_estimated_revenue.csv'
final_results.to_csv(final_output_csv_path, index=False)
print(f"CSV file with final results including Net AR Revenue has been saved to: {final_output_csv_path}")
