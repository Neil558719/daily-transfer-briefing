#!/usr/bin/env python3
"""Update files on GitHub via API using curl.exe"""
import sys, io, json, base64, os, subprocess

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

token = "ghp_Gb…zItD"
username = "Neil558719"
repo = "daily-transfer-briefing"

def curl(method, path, data=None):
    cmd = ["curl.exe", "-s", "-X", method,
           "-H", f"Authorization: Bearer {token}",
           "-H", "Accept: application/vnd.github.v3+json"]
    if data:
        cmd += ["-H", "Content-Type: application/json", "-d", json.dumps(data)]
    cmd += [f"https://api.github.com{path}"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    out = result.stdout.strip()
    if out:
        try:
            return json.loads(out)
        except:
            return out
    return True  # empty response = success (204)

# Test token
test = curl("GET", "/user")
if isinstance(test, dict) and "login" in test:
    print(f"Token OK: {test['login']}")
else:
    print(f"Token invalid: {str(test)[:100]}")
    sys.exit(1)

# Get current SHA for scraper.py
info = curl("GET", f"/repos/{username}/{repo}/contents/src/scraper.py")
sha_scraper = info.get("sha", "")
print(f"scraper.py SHA: {sha_scraper[:12]}...")

# Get current SHA for requirements.txt
info2 = curl("GET", f"/repos/{username}/{repo}/contents/requirements.txt")
sha_req = info2.get("sha", "")
print(f"requirements.txt SHA: {sha_req[:12]}...")

# Read local files
with open("src/scraper.py", "r", encoding="utf-8") as f:
    scraper_content = f.read()
with open("requirements.txt", "r", encoding="utf-8") as f:
    req_content = f.read()

# Update scraper.py
print("\nUpdating scraper.py...")
r = curl("PUT", f"/repos/{username}/{repo}/contents/src/scraper.py", {
    "message": "fix: use cloudscraper to bypass Transfermarkt 403",
    "content": base64.b64encode(scraper_content.encode()).decode(),
    "sha": sha_scraper,
})
print(f"  scraper.py: {'OK' if r else 'Failed'}")

# Update requirements.txt
print("Updating requirements.txt...")
r2 = curl("PUT", f"/repos/{username}/{repo}/contents/requirements.txt", {
    "message": "chore: add cloudscraper dependency",
    "content": base64.b64encode(req_content.encode()).decode(),
    "sha": sha_req,
})
print(f"  requirements.txt: {'OK' if r2 else 'Failed'}")

# Trigger workflow
import time
time.sleep(3)
print("\nTriggering workflow...")
r3 = curl("POST", f"/repos/{username}/{repo}/actions/workflows/daily-briefing.yml/dispatches",
          {"ref": "master"})
print(f"  Workflow: {'Triggered' if r3 else 'Failed'}")

print("\nDone! Check https://github.com/Neil558719/daily-transfer-briefing/actions")
os.remove(__file__)
