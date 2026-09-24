import asyncio
import sys
import os

# Ensure src/ is in the path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from sqlalchemy import select
from app.core.db import async_session_factory
from app.models.report import CandidateReport
from core_ai_lib.schemas.report import CandidateReportResponse

async def run():
    async with async_session_factory() as session:
        # candidate_id we know from previous run
        candidate_id = "50f40e08-adf4-4b5e-b15b-4e46706364de"
        
        result = await session.execute(
            select(CandidateReport).where(CandidateReport.candidate_id == candidate_id)
        )
        report = result.scalar_one_or_none()
        
        if not report:
            print("Report not found!")
            return
            
        # Pydantic validates and formats it exactly like FastAPI response
        response_model = CandidateReportResponse.model_validate(report)
        print(response_model.model_dump_json(indent=2))

if __name__ == "__main__":
    asyncio.run(run())
