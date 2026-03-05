import requests
import uuid

# --- CONFIGURATION ---
USERNAME = 'mail@example.com'
PASSWORD = 'your_password' 
VCF_FILE_PATH = 'contacts.vcf'
# Ensure this ends with a slash
COLLECTION_URL = 'https://carddav.seznam.cz/{USERNAME}/ab/personal/'

# Create a test vCard following Google's version 3.0 requirement
test_vcard = f"""BEGIN:VCARD
VERSION:3.0
FN:Post Test Entry
N:Entry;Post;;;
EMAIL;TYPE=INTERNET:mail@example.cm
UID:{uuid.uuid4()}
END:VCARD"""

def debug_post_request():
    print(f"Testing POST request to: {COLLECTION_URL}\n")
    
    headers = {
        'Content-Type': 'text/vcard; charset=utf-8'
        }
    
    try:
        # POST to the collection allows the server to create the ID
        response = requests.post(
            COLLECTION_URL,
            data=test_vcard.encode('utf-8'),
            auth=(USERNAME, PASSWORD),
            headers=headers
        )
        
        print(f"HTTP Status Code: {response.status_code}")
        print(f"HTTP Reason: {response.reason}")
        
        if response.status_code in [201, 204]:
            print(f"✅ SUCCESS! New resource created.")
            print(f"Server-assigned location: {response.headers.get('Location')}")
        
        print("\n--- Response Body (XML/Text) ---")
        print(response.text if response.text else "[Empty Response]")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    debug_post_request()