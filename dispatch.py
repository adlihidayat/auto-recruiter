import asyncio
from livekit import api

async def main():
    livekit_api = api.LiveKitAPI("http://localhost:7880", "devkey", "secret")
    try:
        await livekit_api.agent_dispatch.create_dispatch(
            api.CreateAgentDispatchRequest(
                agent_name="interviewer-agent",
                room="ac75862d-8c1b-40e2-8545-224eb20a1047"
            )
        )
        print("Dispatch successful")
    except Exception as e:
        print(f"Failed to dispatch: {e}")
    finally:
        await livekit_api.aclose()

asyncio.run(main())
