import os
import json
import traceback
from zeep import Client
from zeep.helpers import serialize_object

# ✅ API Credentials
API_KEY = "x35dq92ki47y"
USERNAME = "sergeypersoff@gmail.com"
PASSWORD = "Spinepain1!"
CUSTOMER_KEY = "x35dq92ki47y"
PRACTICE_ID = "1"  # ✅ Correct Practice ID

# ✅ SOAP API WSDL URL
WSDL_URL = "https://webservice.kareo.com/services/soap/2.1/KareoServices.svc?singleWsdl"

# ✅ Output File Path
debug_file_path = r"C:\Users\serge\Desktop\EDIFY\Python\api_debug_response_encounters.json"

# ✅ Initialize SOAP Client
client = Client(WSDL_URL)

def get_encounters():
    """Fetch multiple encounters without date filters (only Practice ID)."""
    try:
        # ✅ Create Request Header (MANDATORY)
        RequestHeader = client.get_type("ns0:RequestHeader")(
            CustomerKey=CUSTOMER_KEY,
            User=USERNAME,
            Password=PASSWORD
        )

        # ✅ Define Practice Filter (MANDATORY)
        EncounterPracticeType = client.get_type("ns0:EncounterDetailsPractice")
        EncounterPractice = EncounterPracticeType(PracticeID=PRACTICE_ID)  # ✅ Correctly formatted

        # ✅ Define Encounter Filter (ONLY Practice ID, NO Date Filtering)
        EncounterFilterType = client.get_type("ns0:EncounterDetailsFilter")
        EncounterFilter = EncounterFilterType(
            Practice=EncounterPractice  # ✅ Correct filter without date
        )

        # ✅ Define Fields to Return (MANDATORY)
        EncounterFieldsType = client.get_type("ns0:EncounterDetailsFieldsToReturn")(
            EncounterID=True,
            ServiceStartDate=True
        )

        print(f"🚀 Requesting Encounters for Practice ID: {PRACTICE_ID}...")

        # ✅ Create API Request
        GetEncountersReq = client.get_type("ns0:GetEncounterDetailsReq")(
            RequestHeader=RequestHeader,
            Fields=EncounterFieldsType,
            Filter=EncounterFilter  # ✅ Correct Filter without Date
        )

        print("🚀 Sending API Request...")
        encounter_response = client.service.GetEncounterDetails(GetEncountersReq)

        # ✅ Save API response for debugging
        with open(debug_file_path, "w") as debug_file:
            json.dump(serialize_object(encounter_response), debug_file, indent=4)

        print(f"✅ Debug response saved to: {debug_file_path}")

        # ✅ Handle Response (Multiple Encounters)
        if hasattr(encounter_response, "EncounterDetails") and hasattr(encounter_response.EncounterDetails, "EncounterDetailsData"):
            encounter_list = encounter_response.EncounterDetails.EncounterDetailsData
            if not isinstance(encounter_list, list):
                encounter_list = [encounter_list]  # ✅ Ensure it's a list
            print(f"✅ Retrieved {len(encounter_list)} encounters.")
            return encounter_list

        print("⚠️ No encounters found.")
        return []

    except Exception as e:
        print("❌ API Request Failed! Error Details:")
        traceback.print_exc()
        return []

if __name__ == "__main__":
    print("=== Fetching Multiple Encounters (Practice ID Only) ===")
    get_encounters()
