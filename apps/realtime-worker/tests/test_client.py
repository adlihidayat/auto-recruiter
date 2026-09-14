"""
What: Integration test script for LiveKit room client connection.
Why: Validates room connection, participant event listening, and track subscription using LiveKit Python RTC SDK.
Boundaries: Manual test script for developer execution; does not run inside worker entrypoint.
"""

import asyncio
import os
from livekit import rtc, api
from dotenv import load_dotenv

env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.env"))
load_dotenv(env_path)

async def main():
    token = api.AccessToken(
        os.getenv("LIVEKIT_API_KEY", "devkey"),
        os.getenv("LIVEKIT_API_SECRET", "secret")
    ).with_identity("test_client").with_name("Test Client").with_grants(
        api.VideoGrants(room_join=True, room="candidate_123")
    ).to_jwt()
    
    room = rtc.Room()
    
    @room.on("participant_connected")
    def on_participant_connected(participant):
        print(f"Participant connected: {participant.identity}")

    @room.on("track_subscribed")
    def on_track_subscribed(track, publication, participant):
        print(f"Track subscribed from {participant.identity}: {track.sid}")

    print("Connecting to room...")
    await room.connect("ws://localhost:7880", token)
    print("Connected! Waiting 5 seconds...")
    await asyncio.sleep(5)
    print("Disconnecting...")
    await room.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
