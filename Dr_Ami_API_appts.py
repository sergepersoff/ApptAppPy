import traceback
import os
import csv
import json
import time
import shutil
from datetime import datetime, timedelta
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

# ✅ File Paths
output_folder = r"C:\Users\serge\Desktop\EDIFY\Python"
backup_folder = r"C:\Users\serge\Desktop\Vivify Med"
os.makedirs(output_folder, exist_ok=True)
os.makedirs(backup_folder, exist_ok=True)

csv_file_path = os.path.join(output_folder, "appointments_final.csv")
debug_file_path = os.path.join(output_folder, "api_debug_response.json")

# ✅ Initialize SOAP Client
client = Client(WSDL_URL)

def convert_datetime(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    return obj

def get_month_boundaries(target_month_offset=0):
    today = datetime.utcnow().replace(day=1)
    target_month = today + timedelta(days=target_month_offset * 31)
    start_date = target_month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    next_month = (start_date + timedelta(days=32)).replace(day=1)
    end_date = next_month - timedelta(seconds=1)
    return start_date, end_date

def fetch_appointments_range(start_date, end_date):
    RequestHeader = client.get_type("ns0:RequestHeader")(
        CustomerKey=CUSTOMER_KEY,
        User=USERNAME,
        Password=PASSWORD
    )

    AppointmentFieldsType = client.get_type("ns0:AppointmentFieldsToReturn")(
        ID=True,
        StartDate=True,
        EndDate=True,
        LastModifiedDate=True,
        PatientFullName=True,
        ConfirmationStatus=True,
        ResourceName1=True  # ✅ Include provider name
    )

    AppointmentFilterType = client.get_type("ns0:AppointmentFilter")
    filter_obj = AppointmentFilterType(
        StartDate=start_date.strftime('%Y-%m-%dT00:00:00'),
        EndDate=end_date.strftime('%Y-%m-%dT23:59:59')
    )

    GetAppointmentsReq = client.get_type("ns0:GetAppointmentsReq")(
        RequestHeader=RequestHeader,
        Fields=AppointmentFieldsType,
        Filter=filter_obj
    )

    print(f"📆 Fetching appointments from {start_date.date()} to {end_date.date()}...")
    response = client.service.GetAppointments(GetAppointmentsReq)
    return getattr(response.Appointments, "AppointmentData", []) or []

def get_combined_appointments():
    try:
        current_start, current_end = get_month_boundaries()
        jan_start = datetime(2025, 1, 1)
        feb_end = datetime(2025, 2, 28, 23, 59, 59)

        all_current = fetch_appointments_range(current_start, current_end)
        all_past = fetch_appointments_range(jan_start, feb_end)

        full_set = {str(getattr(a, "ID", "")): a for a in all_past + all_current}

        print(f"✅ Combined total: {len(full_set)} appointments")

        with open(debug_file_path, "w", encoding="utf-8") as debug_file:
            json.dump(serialize_object(list(full_set.values())), debug_file, indent=4, default=convert_datetime)

        return list(full_set.values())

    except Exception as e:
        print("\n❌ API Request Failed! Error Details:")
        traceback.print_exc()
        return []

def backup_csv():
    if os.path.exists(csv_file_path):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(backup_folder, f"appointments_backup_{timestamp}.csv")
        shutil.copy2(csv_file_path, backup_path)
        print(f"🗂️ Backup saved to: {backup_path}")

def update_monthly_snapshot(data):
    if not data:
        print("ℹ️ No data to write. Skipping CSV update.")
        return

    headers = ["Appointment ID", "Start Date", "End Date", "Last Modified Date", "Patient Name", "Appointment Status", "Provider Name"]
    appointments_by_id = {}

    if os.path.exists(csv_file_path):
        with open(csv_file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if None not in row:
                    appt_id = row.get("Appointment ID")
                    if appt_id:
                        appointments_by_id[appt_id] = row

    changes = 0

    for appt in data:
        appt_id = str(getattr(appt, "ID", "N/A"))
        new_row = {
            "Appointment ID": appt_id,
            "Start Date": getattr(appt, "StartDate", "N/A"),
            "End Date": getattr(appt, "EndDate", "N/A"),
            "Last Modified Date": getattr(appt, "LastModifiedDate", "N/A"),
            "Patient Name": getattr(appt, "PatientFullName", "N/A"),
            "Appointment Status": getattr(appt, "ConfirmationStatus", "N/A"),
            "Provider Name": getattr(appt, "ResourceName1", "N/A")
        }

        if appt_id in appointments_by_id:
            old_row = appointments_by_id[appt_id]
            if old_row != new_row:
                print(f"🔄 Updated appointment {appt_id}:")
                for key in headers:
                    if old_row.get(key) != new_row.get(key):
                        print(f"   • {key}: {old_row.get(key)} → {new_row.get(key)}")
                appointments_by_id[appt_id] = new_row
                changes += 1
        else:
            print(f"➕ New appointment added: {appt_id}")
            appointments_by_id[appt_id] = new_row
            changes += 1

    if changes:
        backup_csv()
        with open(csv_file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=headers)
            writer.writeheader()
            for row in appointments_by_id.values():
                cleaned_row = {key: row.get(key, "") for key in headers}
                writer.writerow(cleaned_row)
        print(f"✅ {changes} change(s) saved to CSV.")
    else:
        print("✅ No changes detected.")

if __name__ == "__main__":
    while True:
        print("\n=== Fetching and Syncing Appointments (Current + Jan-Feb) ===")
        appointments = get_combined_appointments()
        update_monthly_snapshot(appointments)
        print("=== Waiting for next refresh... ===")
        time.sleep(7200)  # 2 hours
