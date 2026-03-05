Seznam Bulk Contacts Import
A specialized Python utility for bulk-importing contacts into Seznam.cz (including Seznam Profi) via CardDAV. This project provides a core import engine alongside diagnostic tools to navigate the unique resource discovery requirements of Seznam's SznCalDAV server.

The Core Utility
import_contacts.py: The only script required for the actual import process. Once you have your specific address book URL, this script handles the parsing of your .vcf file and the sequential upload of contacts.

Diagnostic & Setup Tools
The following scripts are included to help you identify the correct environment settings. They do not need to be run once your path is configured:

redirect_discovery.py: The primary diagnostic tool. It crawls your account hierarchy to identify the specific folder UUIDs and verify which ones have WRITABLE permissions.

carddav_path_discovery.py: A secondary utility used to test common URL patterns for quick server endpoint verification.

Technical Specifications & References
This implementation is built upon the following official documentation and standards:

Seznam Mail Specification: https://o-seznam.cz/napoveda/email/mohlo-by-se-hodit/postovni-programy-a-aplikace/ - The official guide for Seznam server addresses and connection parameters.

CardDAV Protocol Standards: https://developers.google.com/people/carddav - The reference for resource hierarchy, discovery processes, and REST-based contact management used to develop this tool.

Critical: Credentials Update
To protect your account security, never share or commit files containing your actual email or password to public repositories.

How to Configure Safely:
Remove Hardcoded Credentials: Before pushing code to GitHub, ensure USERNAME and PASSWORD in all scripts are set to placeholders like 'mail@example.com' and 'your_password'.

Update Locally: Open the scripts in your local editor and enter your actual Seznam credentials to perform the discovery or import.

Verify Gitignore: This project includes a .gitignore to ensure your contacts.vcf and sensitive local files are never tracked by Git.

Usage Workflow
1. Discovery (One-time Setup)
Run redirect_discovery.py to find the specific folder in your account that allows uploads. Note the path marked WRITABLE.

2. Configuration
Copy that path into the CARDDAV_URL variable inside import_contacts.py.

3. Execution
Ensure your contacts.vcf (vCard 3.0) is in the project root and run:
python import_contacts.py

License
This project is licensed under the MIT License.