import sys
import os
import asyncio

sys.path.insert(0, os.path.abspath('apps/agents'))
from apps.agents.shared.clients import gemini_flash_lite

try:
    res = gemini_flash_lite.invoke("Hello!")
    print("Success:", res.content)
except Exception as e:
    import traceback
    traceback.print_exc()
