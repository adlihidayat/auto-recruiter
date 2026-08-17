"""
What: Seed script for creating a mock admin user.
Why: Populates the local database with an initial user for frontend login testing.
Boundaries: Standalone script, not imported by the main application.
"""

import asyncio
import sys
import os

# Ensure src/ is in the path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from sqlalchemy import select
from app.core.db import async_session_factory
from app.core.security import get_password_hash
from app.models.user import User

async def seed_user():
    email = "admin@example.com"
    password = "password123"
    
    async with async_session_factory() as session:
        # Check if user already exists
        result = await session.execute(select(User).where(User.email == email))
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            print(f"User {email} already exists!")
            return
            
        print(f"Creating mock user: {email}")
        
        new_user = User(
            email=email,
            hashed_password=get_password_hash(password)
        )
        
        session.add(new_user)
        await session.commit()
        
        print("Successfully created mock user!")

if __name__ == "__main__":
    asyncio.run(seed_user())
