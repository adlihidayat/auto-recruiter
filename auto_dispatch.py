import asyncio
from livekit import api

async def main():
    print("Auto-dispatcher started. Watching for 'mock_room'...")
    livekit_api = api.LiveKitAPI("http://localhost:7880", "devkey", "secret")
    last_dispatched = False
    
    try:
        while True:
            # Check active rooms
            rooms_resp = await livekit_api.room.list_rooms(api.ListRoomsRequest())
            rooms = rooms_resp.rooms
            mock_room_exists = any(r.name == "mock_room" for r in rooms)
            
            if mock_room_exists:
                # Check participants
                participants_resp = await livekit_api.room.list_participants(api.ListParticipantsRequest(room="mock_room"))
                participants = participants_resp.participants
                has_candidate = any(p.identity == "mock_candidate" for p in participants)
                has_agent = any(p.identity.startswith("agent") for p in participants)
                
                if has_candidate and not has_agent and not last_dispatched:
                    print("Candidate detected in mock_room without an agent! Dispatching agent...")
                    await livekit_api.agent_dispatch.create_dispatch(
                        api.CreateAgentDispatchRequest(
                            agent_name="interviewer-agent",
                            room="mock_room"
                        )
                    )
                    last_dispatched = True
                    print("Dispatch sent!")
                elif not has_candidate and not has_agent:
                    last_dispatched = False
            else:
                last_dispatched = False
                
            await asyncio.sleep(1)
            
    except asyncio.CancelledError:
        pass
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await livekit_api.aclose()

asyncio.run(main())
