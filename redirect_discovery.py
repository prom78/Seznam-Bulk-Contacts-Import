import requests
from xml.etree import ElementTree

# --- CONFIGURATION ---
USERNAME = 'mail@example.com'
PASSWORD = 'your_password' 
# Ensure this ends with a slash
BASE_URL = 'https://carddav.seznam.cz/'

NS = {'d': 'DAV:', 'c': 'urn:ietf:params:xml:ns:carddav'}

def find_writable_addressbooks():
    print(f"Crawling Seznam for writable address books for {USERNAME}...\n")
    
    # Step 1: Discover Principal Path
    print("1. Discovering Principal...")
    prop_query = '<d:propfind xmlns:d="DAV:"><d:prop><d:current-user-principal/></d:prop></d:propfind>'
    resp = requests.request('PROPFIND', f"{BASE_URL}/", auth=(USERNAME, PASSWORD), headers={'Depth': '0'}, data=prop_query)
    if resp.status_code != 207:
        print(f"Failed to find Principal. Status: {resp.status_code}")
        return

    principal_path = ElementTree.fromstring(resp.content).find('.//d:current-user-principal/d:href', NS).text
    
    # Step 2: Discover Home-Set
    print("2. Discovering Home-Set...")
    home_query = '<d:propfind xmlns:d="DAV:" xmlns:c="urn:ietf:params:xml:ns:carddav"><d:prop><c:addressbook-home-set/></d:prop></d:propfind>'
    resp = requests.request('PROPFIND', f"{BASE_URL}{principal_path}", auth=(USERNAME, PASSWORD), headers={'Depth': '0'}, data=home_query)
    home_set_path = ElementTree.fromstring(resp.content).find('.//c:addressbook-home-set/d:href', NS).text

    # Step 3: List Collections and Check Privileges
    print("3. Listing collections and checking 'WRITE' permissions...")
    # We ask for resourcetype, displayname, and current-user-privilege-set
    priv_query = '''<d:propfind xmlns:d="DAV:">
        <d:prop>
            <d:resourcetype/>
            <d:displayname/>
            <d:current-user-privilege-set/>
        </d:prop>
    </d:propfind>'''
    
    resp = requests.request('PROPFIND', f"{BASE_URL}{home_set_path}", auth=(USERNAME, PASSWORD), headers={'Depth': '1'}, data=priv_query)
    root = ElementTree.fromstring(resp.content)
    
    found_any = False
    for response in root.findall('d:response', NS):
        href = response.find('d:href', NS).text
        displayname = response.find('.//d:displayname', NS)
        name = displayname.text if displayname is not None else "Unnamed Folder"
        
        # Check if it is an address book
        resourcetype = response.find('.//d:resourcetype', NS)
        is_addressbook = resourcetype is not None and resourcetype.find('c:addressbook', NS) is not None
        
        if is_addressbook:
            found_any = True
            # Check for 'write' or 'write-content' or 'all' privileges
            privs = [p.tag.split('}')[-1] for p in response.findall('.//d:privilege/*', NS)]
            is_writable = any(p in ['write', 'write-content', 'all'] for p in privs)
            
            status = "✅ WRITABLE" if is_writable else "❌ READ-ONLY"
            print(f"\nFolder: {name}")
            print(f"Path: {BASE_URL}{href}")
            print(f"Permissions: {', '.join(privs)}")
            print(f"Status: {status}")

    if not found_any:
        print("No address book collections found.")

if __name__ == "__main__":
    find_writable_addressbooks()