import base64
import json
import os
import sys
import urllib.parse
import urllib.request

URL_BASE = "https://averas-1744767979220.atlassian.net/rest/api/3"
# Sin valores por defecto: con credenciales falsas el script salia a la red igual.
EMAIL = os.getenv("JIRA_EMAIL", "")
TOKEN = os.getenv("JIRA_TOKEN", "")
TIMEOUT_S = 15
PROJECT_KEY = "DM"

def get_auth_header():
    auth_string = f"{EMAIL}:{TOKEN}"
    return "Basic " + base64.b64encode(auth_string.encode("utf-8")).decode("utf-8")

def create_issue(summary, description, issue_type="Task"):
    url = f"{URL_BASE}/issue"
    payload = {
        "fields": {
            "project": {"key": PROJECT_KEY},
            "summary": summary,
            "description": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {"type": "text", "text": description}
                        ]
                    }
                ]
            },
            "issuetype": {"name": issue_type}
        }
    }

    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), method="POST")
    req.add_header("Authorization", get_auth_header())
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json")

    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_S) as response:
            res = json.loads(response.read().decode())
            print(f"Created: {res['key']}")
            return res['key']
    except urllib.error.HTTPError as e:
        print(f"Failed: {e.read().decode()}", file=sys.stderr)
        return None

if __name__ == "__main__":
    if len(sys.argv) <= 2:
        print("usage: jira_manager.py <summary> <description>", file=sys.stderr)
        sys.exit(2)
    if not EMAIL or not TOKEN:
        print("JIRA_EMAIL and JIRA_TOKEN must be set", file=sys.stderr)
        sys.exit(2)
    sys.exit(0 if create_issue(sys.argv[1], sys.argv[2]) else 1)
