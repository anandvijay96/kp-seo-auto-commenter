import requests
import json

url = "http://localhost:8500/api/v1/agent/run"
payload = {
    "task": "search_blogs",
    "parameters": {
        "query": "SEO optimization tips",
        "max_results": 5
    }
}

response = requests.post(url, json=payload)
print(json.dumps(response.json(), indent=2))