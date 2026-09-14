"""
What: Helper script to manually create LiveKit agent dispatch rules.
Why: Registers room dispatch rule to route rooms with the configured prefix to interviewer-agent.
Boundaries: One-off administration utility script.
"""

import asyncio
from livekit import api

async def main():
    livekit_api = api.LiveKitAPI("ws://localhost:7880", "devkey", "secret")
    rule = api.RoomDispatchRule(dispatch_rule_room=api.DispatchRuleRoom(room_prefix=""))
    agent_dispatch = api.CreateAgentDispatchRequest(
        agent_name="interviewer-agent",
        room_dispatch=rule,
    )
    res = await livekit_api.agent_dispatch.create_dispatch(agent_dispatch)
    print("Dispatch rule created:", res)
    await livekit_api.aclose()

if __name__ == "__main__":
    asyncio.run(main())
