import requests

API_KEY = "sk-146c2d82f69645f5b1f73ec3ac00c479"
API_BASE = "https://api.deepseek.com/v1"

url = f"{API_BASE}/chat/completions"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}",
}
payload = {
    "model": "deepseek-chat",
    "messages": [{"role": "user", "content": "你好"}],
    "max_tokens": 100,
}

print(f"Testing: {url}")
try:
    resp = requests.post(url, headers=headers, json=payload, timeout=30)
    print(f"Status: {resp.status_code}")
    print(f"Response: {resp.text[:500]}")
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")