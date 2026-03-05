import requests
import uuid
import re
import os
import time

# --- CONFIGURATION ---
USERNAME = 'mail@example.com'
PASSWORD = 'your_password' 
VCF_FILE_PATH = 'contacts.vcf'
# Ensure this ends with a slash
CARDDAV_URL = 'https://carddav.seznam.cz/{USERNAME}/ab/personal/'

def import_from_vcf():
    if not os.path.exists(VCF_FILE_PATH):
        print(f"Error: File '{VCF_FILE_PATH}' not found.")
        return

    with open(VCF_FILE_PATH, 'r', encoding='utf-8') as f:
        data = f.read()

    # Individual VCARD blocks
    raw_blocks = re.split(r'(END:VCARD)', data)
    contacts_to_upload = [raw_blocks[i] + raw_blocks[i+1] for i in range(0, len(raw_blocks)-1, 2)]

    seen_emails = set()
    upload_count = 0
    skip_count = 0

    print(f"Processing {len(contacts_to_upload)} contacts...")

    for vcard in contacts_to_upload:
        vcard = vcard.strip()
        if "BEGIN:VCARD" not in vcard:
            continue
            
        email_match = re.search(r'EMAIL.*?:(.*?)(?:\n|\r)', vcard, re.IGNORECASE)
        email = email_match.group(1).strip().lower() if email_match else "no-email"

        if email != "no-email":
            if email in seen_emails:
                skip_count += 1
                continue
            seen_emails.add(email)

        # 1. MIMIC THUNDERBIRD: Servers often block generic Python agents with 403
        # 2. IF-NONE-MATCH: Required by some servers to ensure no overwriting
        headers = {
            'Content-Type': 'text/vcard; charset=utf-8',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Thunderbird/102.15.1',
            'If-None-Match': '*' 
        }

        contact_id = str(uuid.uuid4())
        target_url = f"{CARDDAV_URL}{contact_id}.vcf"
        
        try:
            response = requests.put(
                target_url,
                data=vcard.encode('utf-8'),
                auth=(USERNAME, PASSWORD),
                headers=headers
            )
            
            if response.status_code in [201, 204]:
                upload_count += 1
                # Small delay to prevent rate-limiting/403 (spam protection)
                time.sleep(0.1) 
            elif response.status_code == 412:
                print(f"Precondition failed (likely duplicate UUID) for {email}")
                skip_count += 1
            else:
                print(f"Failed for {email}: Status {response.status_code}")
                # If you see 403 here, Seznam may require an App Password despite 2FA being off
                
        except Exception as e:
            print(f"Error uploading {email}: {e}")

    print(f"\n--- Import Finished ---")
    print(f"Uploaded: {upload_count} | Skipped: {skip_count}")

if __name__ == "__main__":
    import_from_vcf()