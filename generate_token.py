import datetime
import jwt

api_key = "devkey"
api_secret = "secret"
room_name = "mock_room"
participant_identity = "mock_candidate"

grants = {
    "identity": participant_identity,
    "name": "Mock Candidate",
    "video": {
        "roomJoin": True,
        "room": room_name,
        "canPublish": True,
        "canSubscribe": True,
        "canPublishData": True,
    }
}

token = jwt.encode(
    {
        **grants,
        "iss": api_key,
        "nbf": int(datetime.datetime.utcnow().timestamp()),
        "exp": int((datetime.datetime.utcnow() + datetime.timedelta(hours=24)).timestamp()),
        "sub": participant_identity,
    },
    api_secret,
    algorithm="HS256"
)
print("Token:", token)
