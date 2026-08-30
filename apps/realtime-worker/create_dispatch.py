import asyncio
from livekit import api

async def main():
    livekit_api = api.LiveKitAPI("ws://localhost:7880", "devkey", "secret")
    rule = api.RoomDispatchRule(dispatch_rule_room=api.DispatchRuleRoom(room_prefix=""))
    # Create the agent dispatch rule that routes ANY room to "interviewer-agent"
    agent_dispatch = api.CreateAgentDispatchRequest(
        agent_name="interviewer-agent",
        room_dispatch=rule,
    )
    res = await livekit_api.agent_dispatch.create_dispatch(agent_dispatch)
    print("Dispatch rule created:", res)
    await livekit_api.aclose()

asyncio.run(main())
