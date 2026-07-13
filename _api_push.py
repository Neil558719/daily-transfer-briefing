#!/usr/bin/env python3
"""Push files to GitHub via API"""
import sys, io, json, base64, os, subprocess

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

token = "ghp_Gb…zItD"
username = "Neil558719"
repo = "daily-transfer-briefing"
branch = "master"

def gh_api(method, path, data=None):
    body = json.dumps(data).encode() if data else None
    cmd = ["curl.exe", "-s", "-X", method,
           "-H", f"Authorization: Bearer {token}",
           "-H", "Accept: application/vnd.github.v3+json"]
    if data:
        cmd += ["-H", "Content-Type: application/json", "-d", body]
    cmd += [f"https://api.github.com{path}"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.stdout.strip():
        return result.stdout.strip()
    return ""

# Get current SHA for scraper.py
r = gh_api("GET", f"/repos/{username}/{repo}/contents/src/scraper.py?ref={branch}")
sha_scraper = ""
if r:
    d = json.loads(r)
    sha_scraper = d["sha"]

# Get current SHA for requirements.txt
r2 = gh_api("GET", f"/repos/{username}/{repo}/contents/requirements.txt?ref={branch}")
sha_req = ""
if r2:
    d = json.loads(r2)
    sha_req = d["sha"]

# Read local files
with open("src/scraper.py", "r", encoding="utf-8") as f:
    scraper_content = f.read()
with open("requirements.txt", "r", encoding="utf-8") as f:
    req_content = f.read()

# Update scraper.py
body = {
    "message": "fix: use cloudscraper to bypass 403",
    "content": base64.b64encode(scraper_content.encode()).decode(),
    "sha": sha_scraper,
    "branch": branch,
}
r3 = gh_api("PUT", f"/repos/{username}/{repo}/contents/src/scraper.py", body)
print(f"scraper.py updated: {bool(r3)}")

# Update requirements.txt
body2 = {
    "message": "chore: add cloudscraper dependency",
    "content": base64.b64encode(req_content.encode()).decode(),
    "sha": sha_req,
    "branch": branch,
}
r4 = gh_api("PUT", f"/repos/{username}/{repo}/contents/requirements.txt", body2)
print(f"requirements.txt updated: {bool(r4)}")

os.remove(__file__)
