import requests
import re

# --- CONFIGURATION ---
USERNAME = 'mail@example.com'
PASSWORD = 'your_password' 
# Ensure this ends with a slash
BASE_URL = 'https://carddav.seznam.cz'

# List of common path patterns to test
PATHS_TO_TEST = [
    f"/"
    f"/addressbooks/{USERNAME}/default/",
    f"/addressbooks/{USERNAME}/contacts/",
    f"/addressbooks/{USERNAME}/kontakty/",
    f"/addressbooks/{USERNAME}/carddav/",
    f"/addressbooks/{USERNAME}/",
    f"/principals/users/{USERNAME}/",
    f"/dav/addressbooks/users/{USERNAME}/contacts/",
    f"/.well-known/carddav", # Standard redirect path
    f"/addressbooks/{USERNAME.replace('@', '%40')}/default/", # URL encoded version
]

def test_paths():
    print(f"Testing paths for {USERNAME}...\n")
    
    for path in PATHS_TO_TEST:
        url = f"{BASE_URL}{path}"
        print(f"Checking: {url}")
        
        try:
            # PROPFIND is the standard way to ask a DAV server if a folder exists
            response = requests.request(
                'PROPFIND', url,
                auth=(USERNAME, PASSWORD),
                headers={'Depth': '0', 'Content-Type': 'text/xml'},
                # Minimal XML to check resource type
                data='<d:propfind xmlns:d="DAV:"><d:prop><d:resourcetype/></d:prop></d:propfind>'
            )
            
            if response.status_code in [200, 207]:
                print(f"✅ FOUND! Success at: {url}")
                return url
            elif response.status_code == 401:
                print("❌ 401 Unauthorized: The password was rejected.")
            elif response.status_code == 404:
                print("❌ 404: Path not found.")
            else:
                print(f"❓ {response.status_code}: Unexpected response.")
                
        except Exception as e:
            print(f"⚠️ Error testing {path}: {e}")
    
    print("\nNo valid paths found. Double check if 2FA is active or if the username is correct.")
    return None

if __name__ == "__main__":
    working_url = test_paths()
    if working_url:
        print(f"\nUse this URL in your main import script: {working_url}")