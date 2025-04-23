from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from backend.db.models import (
    User, FlashcardSet, GeneratedFlashcard,
    ExerciseSet, GeneratedExercise, Simulation, QueryLog
)

# User operations
async def get_user(session: AsyncSession, user_id: int) -> User | None:
    result = await session.get(User, user_id)
    return result

async def create_user(session: AsyncSession, username: str, email: str, password_hash: str) -> User:
    user = User(username=username, email=email, password_hash=password_hash)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

# User lookup by username (for auth)
async def get_user_by_username(session: AsyncSession, username: str) -> User | None:
    result = await session.execute(select(User).filter_by(username=username))
    return result.scalars().first()

# User lookup by email (for Google OAuth)
async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    """Fetch user by email for social login."""
    result = await session.execute(select(User).filter_by(email=email))
    return result.scalars().first()

# Flashcards
async def create_flashcard_set(session: AsyncSession, user_id: int, query: str, flashcards_json: dict) -> FlashcardSet:
    flashcard_set = FlashcardSet(user_id=user_id, query=query, flashcards=flashcards_json)
    session.add(flashcard_set)
    await session.commit()
    await session.refresh(flashcard_set)
    return flashcard_set

# ... additional repository functions for GeneratedFlashcard, exercises, and simulations, similarly structured

async def create_query_log(session: AsyncSession, user_id: int, query_type: str, query: str) -> QueryLog:
    """Log each user query without storing output."""
    log = QueryLog(user_id=user_id, query_type=query_type, query=query)
    session.add(log)
    await session.commit()
    await session.refresh(log)
    return log
