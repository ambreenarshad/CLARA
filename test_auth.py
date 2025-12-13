"""Quick authentication test script."""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def check_server():
    """Check if server is running and responding."""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        if response.status_code == 200:
            print("✓ Server is running and healthy")
            return True
        else:
            print(f"✗ Server returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ Server is not running")
        return False
    except Exception as e:
        print(f"✗ Error checking server: {e}")
        return False

def test_auth_flow():
    """Test complete authentication flow."""

    print("=" * 60)
    print("Testing Authentication System")
    print("=" * 60)
    
    # Check server first
    print("\n0. Checking Server Status...")
    if not check_server():
        print("\nPlease start the server first:")
        print("  python -m uvicorn src.api.main:app --reload")
        return

    # 1. Register a new user
    print("\n1. Testing User Registration...")
    # Use a unique username with timestamp to avoid conflicts
    timestamp = str(int(time.time()))
    register_data = {
        "email": f"test{timestamp}@example.com",
        "username": f"testuser{timestamp}",
        "password": "testpass123",
        "full_name": "Test User"
    }

    response = requests.post(f"{BASE_URL}/api/v1/auth/register", json=register_data)
    print(f"   Status: {response.status_code}")
    if response.status_code == 201:
        print(f"   ✓ User registered successfully")
        user_response = response.json()
        print(f"   User ID: {user_response['id']}")
        print(f"   Username: {user_response['username']}")
    else:
        try:
            error_data = response.json()
            print(f"   ✗ Error: {error_data}")
        except:
            print(f"   ✗ Error (raw): {response.text}")
        print("\n   Server may need to be restarted to load the latest code changes.")
        print("   Please restart: python -m uvicorn src.api.main:app --reload")
        return

    # 2. Login
    print("\n2. Testing Login...")
    login_data = {
        "username": f"testuser{timestamp}",
        "password": "testpass123"
    }
    login_data = {
        "username": "testuser",
        "password": "testpass123"
    }

    response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=login_data)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data["access_token"]
        print(f"   ✓ Login successful")
        print(f"   Token expires in: {token_data['expires_in']} minutes")
    else:
        print(f"   ✗ Login failed: {response.json()}")
        return

    # 3. Get current user info
    print("\n3. Testing Get Current User (/me)...")
    headers = {"Authorization": f"Bearer {access_token}"}

    response = requests.get(f"{BASE_URL}/api/v1/auth/me", headers=headers)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        user_data = response.json()
        print(f"   ✓ User info retrieved")
        print(f"   Username: {user_data['username']}")
        print(f"   Email: {user_data['email']}")
    else:
        print(f"   ✗ Failed: {response.json()}")

    # 4. Upload feedback (authenticated)
    print("\n4. Testing Authenticated Feedback Upload...")
    feedback_data = {
        "feedback": [
            "This product is amazing! I love it!",
            "Terrible experience, very disappointed.",
            "It's okay, nothing special but works fine."
        ],
        "batch_name": "Test Batch",
        "description": "Testing authentication"
    }

    response = requests.post(
        f"{BASE_URL}/api/v1/upload",
        json=feedback_data,
        headers=headers
    )
    print(f"   Status: {response.status_code}")
    if response.status_code == 201:
        upload_result = response.json()
        feedback_id = upload_result["feedback_id"]
        print(f"   ✓ Feedback uploaded successfully")
        print(f"   Feedback ID: {feedback_id}")
        print(f"   Count: {upload_result['count']}")
        print(f"   Batch Name: {upload_result.get('batch_name')}")
    else:
        print(f"   ✗ Upload failed: {response.json()}")
        return

    # 5. Get user statistics
    print("\n5. Testing User Statistics...")
    response = requests.get(f"{BASE_URL}/api/v1/statistics", headers=headers)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        stats = response.json()["statistics"]
        print(f"   ✓ Statistics retrieved")
        print(f"   Total Batches: {stats['total_batches']}")
        print(f"   Total Feedback: {stats['total_feedback']}")
        print(f"   Total Analyses: {stats['total_analyses']}")
    else:
        print(f"   ✗ Failed: {response.json()}")

    # 6. Logout
    print("\n6. Testing Logout...")
    response = requests.post(f"{BASE_URL}/api/v1/auth/logout", headers=headers)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print(f"   ✓ Logout successful")
    else:
        print(f"   Response: {response.json()}")

    # 7. Try to access protected endpoint without token
    print("\n7. Testing Unauthorized Access...")
    response = requests.get(f"{BASE_URL}/api/v1/statistics")
    print(f"   Status: {response.status_code}")
    if response.status_code == 401:
        print(f"   ✓ Correctly rejected unauthorized request")
    else:
        print(f"   ✗ Should have returned 401")

    print("\n" + "=" * 60)
    print("Authentication Test Complete!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        test_auth_flow()
    except requests.exceptions.ConnectionError:
        print("\n✗ Error: Could not connect to API server")
        print("  Make sure the server is running: python -m uvicorn src.api.main:app --reload")
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
