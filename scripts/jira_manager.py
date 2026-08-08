import base64
import json
import os
import sys
import urllib.parse
import urllib.request

URL_BASE = "https://averas-1744767979220.atlassian.net/rest/api/3"
EMAIL = os.getenv("JIRA_EMAIL", "a.veras@gmail.com")
TOKEN = os.getenv("JIRA_TOKEN", "your_token_here")
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
        with urllib.request.urlopen(req) as response:
            res = json.loads(response.read().decode())
            print(f"Created: {res['key']}")
            return res['key']
    except urllib.error.HTTPError as e:
        print(f"Failed: {e.read().decode()}")

if __name__ == "__main__":
    if len(sys.argv) > 2:
        create_issue(sys.argv[1], sys.argv[2])
