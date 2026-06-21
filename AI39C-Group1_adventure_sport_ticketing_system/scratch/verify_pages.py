import urllib.request
import sys

pages = [
    ("/", "THRILL"),
    ("/gallery", "Gallery"),
    ("/reviews", "Reviews")
]

base_url = "http://127.0.0.1:5000"

print("Checking site pages...")
failed = False

for path, expected_text in pages:
    url = base_url + path
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            html = response.read().decode('utf-8')
            status = response.status
            if status == 200:
                print(f"[OK] {path} - Loaded successfully (Status: {status})")
                if expected_text in html:
                    print(f"   Found expected text: '{expected_text}'")
                else:
                    print(f"   [WARNING] Expected text '{expected_text}' not found in HTML response.")
            else:
                print(f"[ERROR] {path} - Unexpected status code: {status}")
                failed = True
    except Exception as e:
        print(f"[ERROR] {path} - Failed to load. Error: {e}")
        failed = True

if failed:
    print("Verification failed!")
    sys.exit(1)
else:
    print("Verification succeeded! All checked pages loaded successfully.")
    sys.exit(0)
