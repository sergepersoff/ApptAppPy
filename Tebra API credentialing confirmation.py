import traceback
from zeep import Client
from zeep.helpers import serialize_object

# ✅ API Credentials
USERNAME = "sergeypersoff@gmail.com"
PASSWORD = "Spinepain1!"
CUSTOMER_KEY = "x35dq92ki47y"

# ✅ SOAP WSDL
WSDL_URL = "https://webservice.kareo.com/services/soap/2.1/KareoServices.svc?singleWsdl"

# ✅ Initialize SOAP Client
client = Client(WSDL_URL)

def get_practices():
    try:
        # ✅ Create Request Header
        RequestHeaderType = client.get_type("ns0:RequestHeader")
        RequestHeader = RequestHeaderType(
            CustomerKey=CUSTOMER_KEY,
            User=USERNAME,
            Password=PASSWORD
        )

        # ✅ Create request wrapper
        GetPracticesReq = client.get_type("ns0:GetPracticesReq")
        request = GetPracticesReq(RequestHeader=RequestHeader)

        print("🚀 Sending GetPractices request...")
        practices_response = client.service.GetPractices(request)

        # ✅ Handle any error
        if practices_response.ErrorResponse and practices_response.ErrorResponse.IsError:
            print("❌ Error:")
            print(f"Message: {practices_response.ErrorResponse.ErrorMessage}")
            return

        # ✅ Check authorization
        security = practices_response.SecurityResponse
        if not security.Authenticated or not security.Authorized:
            print("❌ Authentication or authorization failed.")
            print(f"Security Result: {security.SecurityResult}")
            return

        # ✅ List practices
        practices = practices_response.Practices.Practice
        if not isinstance(practices, list):
            practices = [practices]

        print(f"✅ Retrieved {len(practices)} practice(s):\n")
        for p in practices:
            print(f"- PracticeID: {p.PracticeID}, PracticeName: {p.PracticeName}")

    except Exception as e:
        print("❌ Exception occurred:")
        traceback.print_exc()

if __name__ == "__main__":
    get_practices()
