import requests
import json
import time

BASE = "http://127.0.0.1:5000"
passed = 0
failed = 0

def test(name, url, method="GET", body=None, check=None):
    global passed, failed
    try:
        if method == "GET":
            r = requests.get(url, timeout=30)
        elif method == "POST":
            r = requests.post(url, json=body, timeout=30)
        elif method == "DELETE":
            r = requests.delete(url, timeout=30)
        status = r.status_code
        try:
            data = r.json()
        except:
            data = {}
        ok = (status == 200) and (check(data) if check else True)
        mark = "PASS" if ok else "FAIL"
        if ok: passed += 1
        else: failed += 1
        print(f"  [{mark}] {name} (HTTP {status})")
        if not ok:
            print(f"        Response: {str(data)[:200]}")
    except Exception as e:
        failed += 1
        print(f"  [FAIL] {name} - {e}")

# Create a session to maintain cookies
s = requests.Session()
s.get(f"{BASE}/", timeout=10)

print("=" * 50)
print("  Emotion Companion AI - Test Suite")
print("=" * 50)

# 1. Settings
print("\n[1] API Settings")
test("GET /api/settings", f"{BASE}/api/settings",
     check=lambda d: d.get("ok") and d.get("user"))

test("POST /api/settings (persona)", f"{BASE}/api/settings",
     method="POST", body={"persona": "lively"},
     check=lambda d: d.get("ok"))

test("POST /api/settings (nickname)", f"{BASE}/api/settings",
     method="POST", body={"nickname": "测试用户"},
     check=lambda d: d.get("ok"))

# 2. Conversations
print("\n[2] Conversations")
test("POST /api/conversations (create)", f"{BASE}/api/conversations",
     method="POST",
     check=lambda d: d.get("ok") and d.get("id"))

conv_id = None
try:
    r = s.post(f"{BASE}/api/conversations")
    conv_id = r.json().get("id")
except: pass

test("GET /api/conversations (list)", f"{BASE}/api/conversations",
     check=lambda d: d.get("ok") and isinstance(d.get("conversations"), list))

if conv_id:
    test(f"GET /api/conversations/{conv_id}/messages", f"{BASE}/api/conversations/{conv_id}/messages",
         check=lambda d: d.get("ok") and isinstance(d.get("messages"), list))

# 3. Chat
print("\n[3] Chat (requires valid API key)")
test("Chat - greeting", f"{BASE}/api/chat",
     method="POST", body={"message": "你好"},
     check=lambda d: d.get("ok") and d.get("reply") and d.get("emotion"))

test("Chat - happy emotion", f"{BASE}/api/chat",
     method="POST", body={"message": "今天考试拿了满分，好开心啊！"},
     check=lambda d: d.get("ok") and d.get("reply"))

test("Chat - sad emotion", f"{BASE}/api/chat",
     method="POST", body={"message": "和最好的朋友吵架了，心里很难过"},
     check=lambda d: d.get("ok") and d.get("reply"))

test("Chat - anxious emotion", f"{BASE}/api/chat",
     method="POST", body={"message": "明天要答辩了，好紧张好焦虑"},
     check=lambda d: d.get("ok") and d.get("reply"))

# 4. Content moderation
print("\n[4] Content Moderation")
test("Chat - crisis keyword (suicide)", f"{BASE}/api/chat",
     method="POST", body={"message": "我不想活了想自杀"},
     check=lambda d: d.get("ok") and "400-161-9995" in d.get("reply", ""))

test("Chat - sensitive word (gambling)", f"{BASE}/api/chat",
     method="POST", body={"message": "教我怎么赌博赢钱"},
     check=lambda d: d.get("ok") and "400-161-9995" in d.get("reply", ""))

test("Chat - normal violence word in context", f"{BASE}/api/chat",
     method="POST", body={"message": "暴力不能解决问题"},
     check=lambda d: d.get("ok") or d.get("error"))

# 5. Emotion stats
print("\n[5] Emotion Statistics")
test("GET /api/stats", f"{BASE}/api/stats",
     check=lambda d: d.get("ok") and isinstance(d.get("stats"), dict))

# 6. Export
print("\n[6] Export")
if conv_id:
    try:
        r = s.get(f"{BASE}/api/conversations/{conv_id}/export", timeout=10)
        ok = r.status_code == 200 and len(r.text) > 0
        mark = "PASS" if ok else "FAIL"
        if ok: passed += 1
        else: failed += 1
        print(f"  [{mark}] Export conversation (HTTP {r.status_code}, {len(r.text)} bytes)")
    except Exception as e:
        failed += 1
        print(f"  [FAIL] Export conversation - {e}")

# 7. Delete conversation
print("\n[7] Cleanup")
if conv_id:
    test(f"DELETE /api/conversations/{conv_id}", f"{BASE}/api/conversations/{conv_id}",
         method="DELETE",
         check=lambda d: d.get("ok"))

# Summary
print("\n" + "=" * 50)
print(f"  Results: {passed} passed, {failed} failed, {passed+failed} total")
print("=" * 50)
if failed == 0:
    print("  ALL TESTS PASSED!")
else:
    print(f"  {failed} test(s) failed. Check output above.")
print("=" * 50)
