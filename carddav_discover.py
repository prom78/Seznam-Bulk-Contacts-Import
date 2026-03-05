import requests
import uuid
import re
import os
from xml.etree import ElementTree

# --- CONFIGURATION ---
USERNAME = 'mail@example.com'
PASSWORD = 'your_password' 
# Ensure this ends with a slash
BASE_URL = 'https://carddav.seznam.cz/'
VCF_FILE_PATH = 'contacts.vcf'

def discover_addressbook_url():
    """Finds the correct addressbook path automatically to avoid 404 errors."""
    print("Discovering address book path...")
    # Standard CardDAV discovery path
    # discovery_url = f"{BASE_URL}addressbooks/{USERNAME}/"
    discovery_url = f"{BASE_URL}addressbooks/"
    
    try:
        response = requests.request(
            'PROPFIND', discovery_url,
            auth=(USERNAME, PASSWORD),
            headers={'Depth': '1', 'Content-Type': 'text/xml'}
        )
        
        if response.status_code in [200, 207]:
            # Parse the XML to find the first valid addressbook collection
            root = ElementTree.fromstring(response.content)
            for element in root.findall('.//{DAV:}href'):
                path = element.text
                if 'contacts' in path or 'default' in path:
                    return f"https://carddav.seznam.cz{path}"
            return f"{BASE_URL}addressbooks/{USERNAME}/"
        else:
            print(f"Discovery failed (Status {response.status_code}). Check your password.")
            return None
    except Exception as e:
        print(f"Discovery error: {e}")
        return None

def import_from_vcf():
    if not os.path.exists(VCF_FILE_PATH):
        print(f"Error: '{VCF_FILE_PATH}' not found.")
        return

    # 1. Discover the correct URL
    target_collection_url = discover_addressbook_url()
    if not target_collection_url: return
    
    # Ensure URL ends with a slash
    if not target_collection_url.endswith('/'): target_collection_url += '/'
    print(f"Targeting: {target_collection_url}")

    # 2. Load and Process VCF
    with open(VCF_FILE_PATH, 'r', encoding='utf-8') as f:
        data = f.read()

    raw_blocks = re.split(r'(END:VCARD)', data)
    contacts_to_upload = [raw_blocks[i] + raw_blocks[i+1] for i in range(0, len(raw_blocks)-1, 2)]

    seen_emails = set()
    upload_count = 0
    skip_count = 0

    # 3. Upload
    for vcard in contacts_to_upload:
        vcard = vcard.strip()
        if "BEGIN:VCARD" not in vcard: continue
            
        email_match = re.search(r'EMAIL.*?:(.*?)(?:\n|\r)', vcard, re.IGNORECASE)
        email = email_match.group(1).strip().lower() if email_match else "no-email"

        if email != "no-email":
            if email in seen_emails:
                skip_count += 1
                continue
            seen_emails.add(email)

        target_url = f"{target_collection_url}{uuid.uuid4()}.vcf"
        
        try:
            resp = requests.put(
                target_url,
                data=vcard.encode('utf-8'),
                auth=(USERNAME, PASSWORD),
                headers={'Content-Type': 'text/vcard; charset=utf-8'}
            )
            if resp.status_code in [201, 204]:
                upload_count += 1
            else:
                print(f"Failed for {email}: {resp.status_code}")
        except Exception as e:
            print(f"Error: {e}")

    print(f"\n--- Import Finished ---")
    print(f"Uploaded: {upload_count} | Skipped: {skip_count}")

if __name__ == "__main__":
    import_from_vcf()