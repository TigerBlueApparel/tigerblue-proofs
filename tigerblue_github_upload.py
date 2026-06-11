#!/usr/bin/env python3
"""
TigerBlue GitHub Proof Uploader
Usage: python3 tigerblue_github_upload.py /path/to/proof.png
Config: ~/tigerblue_config.json
Returns: raw GitHub URL on stdout
"""

import sys, base64, json, urllib.request, urllib.error, os

# Load config from home directory
config_path = os.path.expanduser("~/tigerblue_config.json")
with open(config_path, "r") as f:
    cfg = json.load(f)

TOKEN = cfg["github_token"]
USER = cfg["github_user"]
REPO = cfg["github_repo"]

def upload(filepath):
    if not os.path.exists(filepath):
        print(f"ERROR: File not found: {filepath}")
        sys.exit(1)

    filename = os.path.basename(filepath)
    api_url = f"https://api.github.com/repos/{USER}/{REPO}/contents/{filename}"
    raw_url = f"https://raw.githubusercontent.com/{USER}/{REPO}/main/{filename}"

    with open(filepath, "rb") as f:
        content = base64.b64encode(f.read()).decode()

    # Check if file exists (get SHA for update)
    sha = ""
    try:
        req = urllib.request.Request(
            api_url,
            headers={"Authorization": f"token {TOKEN}", "User-Agent": "TigerBlue"}
        )
        with urllib.request.urlopen(req) as r:
            sha = json.loads(r.read()).get("sha", "")
    except urllib.error.HTTPError as e:
        if e.code != 404:
            print(f"ERROR: {e.code}")
            sys.exit(1)

    payload = {"message": f"Upload {filename}", "content": content}
    if sha:
        payload["sha"] = sha

    req = urllib.request.Request(
        api_url,
        data=json.dumps(payload).encode(),
        headers={"Authorization": f"token {TOKEN}", "Content-Type": "application/json", "User-Agent": "TigerBlue"},
        method="PUT"
    )

    try:
        with urllib.request.urlopen(req) as r:
            json.loads(r.read())
            print(raw_url)
    except urllib.error.HTTPError as e:
        print(f"ERROR: {e.code} {e.read().decode()}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("ERROR: No file path provided")
        sys.exit(1)
    upload(sys.argv[1])
