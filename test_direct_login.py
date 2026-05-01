import requests

BASE_URL = "http://localhost:8000"

email = "bootstrap_4b933fca@example.com"
password = "BootstrapPass123!@"

print(f"\nTesting login:")
print(f"  Email: {email}")
print(f"  Password: {password}\n")

payload = {"email": email, "password": password}
response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=payload)

print(f"Status: {response.status_code}")
print(f"Response: {response.json()}\n")
