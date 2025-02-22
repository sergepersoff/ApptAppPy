import pandas as pd

# Define file paths
input_file = r"F:\Download\ABC Billing report through 02112024 by DOS compiled.csv"
output_folder = r"F:\Download\\"  

# Load the CSV file
df = pd.read_csv(input_file)

# Standardize column names
df.columns = [col.strip().replace(" ", "_").lower() for col in df.columns]

if 'paid' in df.columns:
    df['paid'] = df['paid'] * -1

    # Save updated dataset with modified 'paid' values
    df.to_csv(output_folder + "Updated_Billing_Report.csv", index=False)

    print("\n'Paid' values have been negated for aesthetic reasons.")
    print("Updated report saved as: Updated_Billing_Report.csv")

else:
    print("\nWarning: 'paid' column not found. Please check column names in the dataset.")

# 1. Identify Underperforming Insurance Payers
df['reimbursement_ratio'] = df['paid'] / df['allowed']
payer_performance = df.groupby('insurance').agg(
    total_charges=('charge_amount', 'sum'),
    total_allowed=('allowed', 'sum'),
    total_paid=('paid', 'sum'),
    avg_reimbursement=('reimbursement_ratio', 'mean')
).reset_index()

# Identify payers that consistently **underpay** (low reimbursement ratio)
low_payers = payer_performance.sort_values(by='avg_reimbursement').head(5)

# 2. Compare Charge vs. Payment Delays
df['date'] = pd.to_datetime(df['date'])
df['date_paid'] = pd.to_datetime(df['date_paid'])
df['days_to_payment'] = (df['date_paid'] - df['date']).dt.days

payment_speed = df.groupby('insurance').agg(
    avg_days_to_payment=('days_to_payment', 'mean'),
    median_days_to_payment=('days_to_payment', 'median')
).reset_index().sort_values(by='avg_days_to_payment')

# 3. Identify High Deductible & Coinsurance Burden
df['total_patient_liability'] = df['deductible'] + df['coins']
patient_burden = df.groupby('insurance').agg(
    avg_deductible=('deductible', 'mean'),
    avg_coinsurance=('coins', 'mean'),
    avg_patient_liability=('total_patient_liability', 'mean')
).reset_index().sort_values(by='avg_patient_liability', ascending=False)

# 4. Find Procedures with Low Reimbursement
procedure_performance = df.groupby('charge_description').agg(
    total_charges=('charge_amount', 'sum'),
    total_paid=('paid', 'sum'),
    avg_reimbursement_rate=('reimbursement_ratio', 'mean')
).reset_index().sort_values(by='avg_reimbursement_rate')

# Group by Insurance and Procedure to check total charges vs. payments
insurance_procedure_analysis = df.groupby(['insurance', 'charge_description']).agg(
    total_charges=('charge_amount', 'sum'),
    total_paid=('paid', 'sum'),  # Paid is now negative for aesthetics
    total_due=('amount_due', 'sum'),
    num_claims=('charge_amount', 'count')
).reset_index()

# Identify insurers that have **never paid** for certain procedures
unpaid_procedures = insurance_procedure_analysis[insurance_procedure_analysis['total_paid'] == 0]

# Identify **top insurers with the highest unpaid balances**
top_owing_insurers = insurance_procedure_analysis.groupby('insurance').agg(
    total_due=('total_due', 'sum'),
    total_unpaid_procedures=('total_paid', lambda x: (x == 0).sum()),  # Count of procedures never paid
    total_claims=('num_claims', 'sum')
).reset_index().sort_values(by='total_due', ascending=False)

# Identify which insurance pays the most per procedure on average

# Calculate average payment per procedure per insurance
highest_paying_insurers = df.groupby(['insurance', 'charge_description']).agg(
    avg_payment=('paid', 'mean'),  # Paid values are negative for aesthetics
    total_paid=('paid', 'sum'),
    num_claims=('charge_amount', 'count')
).reset_index()

# Sort by highest average payment per procedure
highest_paying_insurers = highest_paying_insurers.sort_values(by='avg_payment', ascending=False)

# Save results to CSV
highest_paying_insurers.to_csv(output_folder + "Highest_Paying_Insurers.csv", index=False)

# Display results on screen
print("\nTop 10 Insurance Companies Paying the Most Per Procedure (on average):")
print(highest_paying_insurers.head(10))

print("\nAnalysis complete! Report saved as: Highest_Paying_Insurers.csv")

# Save results to CSV
insurance_procedure_analysis.to_csv(output_folder + "Insurance_Procedure_Analysis.csv", index=False)
unpaid_procedures.to_csv(output_folder + "Unpaid_Procedures.csv", index=False)
top_owing_insurers.to_csv(output_folder + "Top_Owing_Insurers.csv", index=False)

# Display results on screen
print("\nTop 10 Insurance Companies Owing the Most:")
print(top_owing_insurers.head(10))

print("\nProcedures That Have Never Been Paid By Any Insurer:")
print(unpaid_procedures.head(10))

print("\nAnalysis complete! Reports saved as:")
print("- Insurance_Procedure_Analysis.csv")
print("- Unpaid_Procedures.csv")
print("- Top_Owing_Insurers.csv")


# -------------------- Save Results to CSV --------------------
payer_performance.to_csv(output_folder + "Payer_Performance.csv", index=False)
payment_speed.to_csv(output_folder + "Payment_Speed.csv", index=False)
patient_burden.to_csv(output_folder + "Patient_Liability.csv", index=False)
procedure_performance.to_csv(output_folder + "Procedure_Performance.csv", index=False)

print("\nAnalysis Complete! Results saved in:", output_folder)
print("\nLowest Performing Payers (Avg. Reimbursement Rate):")
print(low_payers)

print("\nTop 5 Fastest Paying Insurance Companies:")
print(payment_speed.head(5))

print("\nTop 5 Slowest Paying Insurance Companies:")
print(payment_speed.tail(5))

print("\nTop 5 Insurance Companies with Highest Patient Liability:")
print(patient_burden.head(5))

print("\nLowest Paid Procedures (Reimbursement Rate):")
print(procedure_performance.head(5))
