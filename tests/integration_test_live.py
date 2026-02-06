import sys
import os

# Ensure src is in python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.network.auth_service import AuthService

def test_live_server():
    server_ip = "47.109.184.107"
    port = "8080"
    base_url = f"http://{server_ip}:{port}"

    print(f"Testing connection to {base_url}...")

    auth_service = AuthService(base_url)

    # 1. Test Health Check
    import requests
    try:
        print("\n[1] Testing /health endpoint...")
        # Increased timeout to 30s
        resp = requests.get(f"{base_url}/health", timeout=30)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text}")
    except Exception as e:
        print(f"Health check failed: {e}")

    # 1.5 Test Login endpoint with raw requests
    print("\n[1.5] Testing /login with raw requests...")
    try:
        import time
        import hashlib
        user = "admin"
        pwd = "123456" # User said they registered an admin account, assuming default or provided password
        timestamp = str(int(time.time()))
        salt = "abc123xyz"
        raw = f"{user}{timestamp}{pwd}{salt}"
        sign = hashlib.md5(raw.encode('utf-8')).hexdigest().lower()

        params = {
            'user': user,
            'time': timestamp,
            'salt': salt,
            'sign': sign
        }
        print(f"Sending raw request to {base_url}/login with params: {params}")
        resp = requests.get(f"{base_url}/login", params=params, timeout=30)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text}")
    except Exception as e:
        print(f"Raw login request failed: {e}")

    # 2. Test Login with AuthService (with increased timeout)
    print("\n[2] Testing /login via AuthService with 'admin' / '123456'...")
    # Re-instantiate with longer timeout
    auth_service = AuthService(base_url, timeout=30)
    result = auth_service.login("admin", "123456")

    print("\n[2] Testing /login with 'testuser' / '123456'...")
    result = auth_service.login("testuser", "123456")
    print(f"Success: {result.success}")
    if result.success:
        print(f"Token: {result.token}")
        print(f"User ID: {result.user_id}")
    else:
        print(f"Error Code: {result.error_code}")
        print(f"Error Msg: {result.error_msg}")

    # 3. Test Login with 'admin' / '123456'
    print("\n[3] Testing /login with 'admin' / '123456'...")
    result = auth_service.login("admin", "123456")
    print(f"Success: {result.success}")
    if result.success:
        print(f"Token: {result.token}")
        print(f"User ID: {result.user_id}")
    else:
        print(f"Error Code: {result.error_code}")
        print(f"Error Msg: {result.error_msg}")

if __name__ == "__main__":
    test_live_server()
