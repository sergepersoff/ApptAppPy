import pandas as pd

# 1. Load the file with the appropriate encoding
file_path = r'C:\Users\serge\Desktop\DOV\Master_Schedule_Facility_Visits_July.csv'
df = pd.read_csv(file_path, encoding='ISO-8859-1')

# 2. Convert everything to upper case
df = df.applymap(lambda x: x.upper() if isinstance(x, str) else x)

# 3. Reformat 'Practitioner' to 'last name, first name'
def reformat_name(name):
    if not isinstance(name, str):  # Check if the value is not a string
        return name  # Return the original value (could be NaN or something else)
        
    parts = name.split()
    if len(parts) >= 2:
        return f"{parts[-1]}, {' '.join(parts[:-1])}"
    return name

df['Practitioner'] = df['Practitioner'].apply(reformat_name)

# 4. Filter based on the given criteria
df = df[df['Facility'].notna()]  # Filter out all nulls in the 'Facility' column
df = df[df['Specialty'] != 'RETINAL ASSMT.']  # Exclude 'RETINAL ASSMT.' in the 'Specialty' column
df = df[df['Total Provider Cost'] != 0]  # Exclude rows where 'Total Provider Cost' is 0
df = df[df['PT Encounter'] != 0]  # Exclude rows where 'PT Encounter' is 0

# 5. Save the filtered data to a new file
output_path = r'C:\Users\serge\Documents\My Tableau Prep Repository\Datasources\Master.csv'
df.to_csv(output_path, index=False)

print(f"Data has been saved to {output_path}")
