import asyncio
from livekit import api

async def main():
    livekit_api = api.LiveKitAPI("http://localhost:7880", "devkey", "secret")
    try:
        await livekit_api.agent_dispatch.create_dispatch(
            api.CreateAgentDispatchRequest(
                agent_name="interviewer-agent",
                room="test_dispatch_room"
            )
        )
        print("Dispatch successful on v1.11.0")
    except Exception as e:
        print(f"Failed to dispatch: {e}")
    finally:
        await livekit_api.aclose()

asyncio.run(main())
