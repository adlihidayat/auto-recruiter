import jwt
import time
import json

api_key = "devkey"
api_secret = "secret"
room_name = "test_browser_room"
identity = "test_candidate_1"

payload = {
    "sub": identity,
    "iss": api_key,
    "nbf": int(time.time()),
    "exp": int(time.time()) + 3600,
    "name": "Test Browser Candidate",
    "video": {
        "roomJoin": True,
        "room": room_name,
        "canPublish": True,
        "canSubscribe": True,
        "canPublishData": True
    }
}
token = jwt.encode(payload, api_secret, algorithm="HS256")
print(f"http://localhost:3000/interview?token={token}")
