import traceback
import os
import csv
import json
from datetime import datetime
from zeep import Client
from zeep.helpers import serialize_object

# ✅ API Credentials
API_KEY = "x35dq92ki47y"
USERNAME = "sergeypersoff@gmail.com"
PASSWORD = "Spinepain1!"
CUSTOMER_KEY = "x35dq92ki47y"
PRACTICE_NAME = "Vivify Medical LLC"

# ✅ SOAP API WSDL URL
WSDL_URL = "https://webservice.kareo.com/services/soap/2.1/KareoServices.svc?singleWsdl"

# ✅ Output File Paths
output_folder = r"C:\Users\serge\Desktop\EDIFY\Python"
os.makedirs(output_folder, exist_ok=True)
csv_file_path = os.path.join(output_folder, "appointments_final.csv")
debug_file_path = os.path.join(output_folder, "api_debug_response.json")

# ✅ Initialize SOAP Client
client = Client(WSDL_URL)

def convert_datetime(obj):
    """Convert datetime objects to string before saving to JSON."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    return obj

def get_appointments_jan_feb_2025():
    """Fetch all appointments for January & February 2025, including Patient Name."""
    try:
        # ✅ Create Request Header
        RequestHeader = client.get_type("ns0:RequestHeader")(
            CustomerKey=CUSTOMER_KEY,
            User=USERNAME,
            Password=PASSWORD
        )

        # ✅ Fixed Date Range for Jan 1 - Feb 28, 2025
        start_date_str = "2025-01-01T00:00:00"
        end_date_str = "2025-02-28T23:59:59"

        # ✅ Define API-Approved Fields (Including Patient Name)
        AppointmentFieldsType = client.get_type("ns0:AppointmentFieldsToReturn")(
            ID=True,
            StartDate=True,
            EndDate=True,
            PatientFullName=True  # ✅ Keeping Patient Name
        )

        # ✅ Define Required Filters (Date Range)
        AppointmentFilter = client.get_type("ns0:AppointmentFilter")(
            StartDate=start_date_str,
            EndDate=end_date_str
        )

        print(f"🚀 Requesting Appointments from {start_date_str} to {end_date_str}...")

        # ✅ Create API Request
        GetAppointmentsReq = client.get_type("ns0:GetAppointmentsReq")(
            RequestHeader=RequestHeader,
            Fields=AppointmentFieldsType,
            Filter=AppointmentFilter
        )

        print("🚀 Sending API Request...")
        appointment_response = client.service.GetAppointments(GetAppointmentsReq)

        # ✅ Save Full API Response for Debugging (convert datetime fields)
        with open(debug_file_path, "w", encoding="utf-8") as debug_file:
            response_dict = serialize_object(appointment_response)
            response_dict = json.loads(json.dumps(response_dict, default=convert_datetime))
            json.dump(response_dict, debug_file, indent=4)

        print(f"✅ Debug response saved to: {debug_file_path}")

        # ✅ Debug Response Structure
        print(f"Response Type: {type(appointment_response)}")
        if hasattr(appointment_response, "Appointments"):
            print(f"Appointments Type: {type(appointment_response.Appointments)}")
            if hasattr(appointment_response.Appointments, "AppointmentData"):
                print(f"AppointmentData Type: {type(appointment_response.Appointments.AppointmentData)}")

        # ✅ Check if SecurityResponse exists before accessing
        if hasattr(appointment_response, 'SecurityResponse'):
            security_response = appointment_response.SecurityResponse
            if hasattr(security_response, 'SecurityResultSuccess') and not security_response.SecurityResultSuccess:
                print(f"❌ Security Error: {security_response.SecurityResult}")
                return []

        # ✅ Check for API errors
        if hasattr(appointment_response, 'ErrorResponse') and appointment_response.ErrorResponse.IsError:
            print(f"❌ API Error: {appointment_response.ErrorResponse.ErrorMessage}")
            return []

        # ✅ Extract Appointments
        if (hasattr(appointment_response, "Appointments") and 
            appointment_response.Appointments and 
            hasattr(appointment_response.Appointments, "AppointmentData")):
            
            data = appointment_response.Appointments.AppointmentData
            print(f"✅ Retrieved {len(data) if isinstance(data, list) else '1'} appointment(s)")
            return data if isinstance(data, list) else [data]

        print("⚠️ No appointments found in the response.")
        return []

    except Exception as e:
        print("\n❌ API Request Failed! Error Details:")
        traceback.print_exc()
        return []

def save_appointments_to_csv(data):
    """Saves fetched appointment details to a CSV file."""
    if not data:
        print("ℹ️ No data available to save. Creating empty CSV.")
        with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["Appointment ID", "Start Date", "End Date", "Patient Name"])
        return

    with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Appointment ID", "Start Date", "End Date", "Patient Name"])

        for record in data:
            writer.writerow([
                getattr(record, "ID", "N/A") or "N/A",
                getattr(record, "StartDate", "N/A") or "N/A",
                getattr(record, "EndDate", "N/A") or "N/A",
                getattr(record, "PatientFullName", "N/A") or "N/A"
            ])

    print(f"✅ All appointments saved to {csv_file_path}")

if __name__ == "__main__":
    print("=== Fetching All Appointments for Jan & Feb 2025 ===")
    appointment_data = get_appointments_jan_feb_2025()
    save_appointments_to_csv(appointment_data)
    print("=== Process Completed ===")
