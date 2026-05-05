import requests
import os

BASE_URL = "http://localhost:8000/api/v1"
FILE_PATH = "Apuntes_IA_Prueba.pdf"

def test_upload():
    # 1. Login
    login_data = {
        "username": "test@example.com",
        "password": "password123"
    }
    print(f"Logging in as {login_data['username']}...")
    resp = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    if resp.status_code != 200:
        print(f"Login failed: {resp.status_code} - {resp.text}")
        return

    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Upload PDF
    if not os.path.exists(FILE_PATH):
        print(f"File not found: {FILE_PATH}")
        return

    print(f"Uploading {FILE_PATH}...")
    with open(FILE_PATH, "rb") as f:
        files = {"file": (FILE_PATH, f, "application/pdf")}
        data = {"asignatura": "IA"}
        resp = requests.post(f"{BASE_URL}/documents/upload", headers=headers, files=files, data=data)

    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.text}")

if __name__ == "__main__":
    test_upload()
