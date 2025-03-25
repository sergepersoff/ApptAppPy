import traceback
import os
import csv
import json  # ✅ Import JSON to save API structure
from zeep import Client

# ✅ API Credentials
API_KEY = "x35dq92ki47y"  # Same as Customer Key
USERNAME = "sergeypersoff@gmail.com"
PASSWORD = "Spinepain1!"
CUSTOMER_KEY = "x35dq92ki47y"  # Same as API Key
PRACTICE_NAME = "Vivify Medical LLC"

# ✅ SOAP API WSDL URL
WSDL_URL = "https://webservice.kareo.com/services/soap/2.1/KareoServices.svc?singleWsdl"

# ✅ Output File Paths
output_folder = r"C:\Users\serge\Desktop\EDIFY\Python"
os.makedirs(output_folder, exist_ok=True)
debug_file_path = os.path.join(output_folder, "api_response.txt")
debug_structure_path = os.path.join(output_folder, "api_response_structure.txt")
csv_file_path = os.path.join(output_folder, "patient_data.csv")

# ✅ Initialize SOAP Client
client = Client(WSDL_URL)

def get_patient_data():
    """Fetches Last Name and Date of Birth from Tebra API and saves response for debugging."""
    try:
        # ✅ Create Request Header
        RequestHeader = client.get_type("ns0:RequestHeader")(
            CustomerKey=CUSTOMER_KEY,
            User=USERNAME,
            Password=PASSWORD
        )

        # ✅ Define Fields to Return (ONLY Last Name & DOB)
        FieldsToReturn = client.get_type("ns0:PatientFieldsToReturn")(
            LastName=True,  # Last Name
            DOB=True  # Date of Birth
        )

        # ✅ Define Filter Criteria
        PatientFilter = client.get_type("ns0:PatientFilter")(
            PracticeName=PRACTICE_NAME
        )

        # ✅ Create API Request Object
        GetPatientsReq = client.get_type("ns0:GetPatientsReq")(
            RequestHeader=RequestHeader,
            Fields=FieldsToReturn,
            Filter=PatientFilter
        )

        print("🚀 Sending API Request...")

        # ✅ Make API Request
        response = client.service.GetPatients(GetPatientsReq)

        # ✅ Debugging: Check if response is None
        if response is None:
            print("⚠️ API returned an empty response. This may indicate an issue with the request.")
            return None

        # ✅ Debugging: Print response type
        print(f"🔍 API Response Type: {type(response)}")

        # ✅ Save full API response structure to a file
        with open(debug_structure_path, "w", encoding="utf-8") as debug_file:
            json.dump(str(response), debug_file, indent=4)

        print(f"✅ Full API response structure saved to: {debug_structure_path}")

        # ✅ Extract patient data correctly
        if hasattr(response, "Patients") and response.Patients:
            return response.Patients.PatientData if hasattr(response.Patients, "PatientData") else []
        else:
            print("\n⚠️ No 'Patients' key found in API response. Double-check API request parameters.")
            return None

    except Exception as e:
        print("\n❌ API Request Failed! Error Details:")
        traceback.print_exc()  # Prints the full stack trace
        return None

def save_to_csv(data):
    """Saves fetched Last Name and Date of Birth to a CSV file."""
    if not data:
        print("No data available to save.")
        return

    with open(csv_file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Last Name", "Date of Birth"])

        for record in data:
            last_name = getattr(record, "LastName", "N/A")
            dob = getattr(record, "DOB", "N/A")

            # ✅ Fix issue where empty values were written as 'N/A'
            if last_name is None:
                last_name = "N/A"
            if dob is None:
                dob = "N/A"

            writer.writerow([last_name, dob])

    print(f"✅ Data saved to {csv_file_path}")

if __name__ == "__main__":
    patient_data = get_patient_data()
    save_to_csv(patient_data)
