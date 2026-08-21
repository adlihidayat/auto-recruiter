import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from sqlalchemy import select
from app.core.db import async_session_factory
from app.models.candidate import Candidate

async def f():
    async with async_session_factory() as s:
        res = await s.execute(select(Candidate).where(Candidate.id=='d1833e10-2a32-4fd1-874f-84a948b8bed8'))
        cand = res.scalar_one_or_none()
        print('Status:', cand.status if cand else 'None', 'Score:', cand.composite_score if cand else 'None')

asyncio.run(f())
