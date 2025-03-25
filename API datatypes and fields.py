from zeep import Client

# ✅ SOAP API WSDL URL
WSDL_URL = "https://webservice.kareo.com/services/soap/2.1/KareoServices.svc?singleWsdl"

# ✅ Initialize SOAP Client
client = Client(WSDL_URL)

# ✅ List available API methods
print("\n=== Available API Methods ===")
for service in client.wsdl.services.values():
    for port in service.ports.values():
        for operation in port.binding._operations.values():  # 🔹 FIX: Use `_operations`
            print(operation.name)

# ✅ List available data types
print("\n=== Available Data Types ===")
for element in client.wsdl.types.elements:  # 🔹 FIX: Iterate over `elements` directly
    print(element)
