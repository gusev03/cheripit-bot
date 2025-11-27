import os
import enum
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import BigInteger, Text, Enum, DateTime, event
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class ActionType(enum.Enum):
    """Enum for bot message action types."""
    WORDLE = "wordle"
    CONNECTIONS = "connections"
    STRANDS = "strands"
    MENTION = "mention"
    GIF = "gif"
    HAMSTERDLE = "hamsterdle"
    SET_PROMPT = "set_prompt"
    SHOW_PROMPT = "show_prompt"


class Base(DeclarativeBase):
    pass


class BotMessage(Base):
    """Model for storing bot message interactions for analytics."""
    __tablename__ = "bot_messages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    guild_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    guild_name: Mapped[str] = mapped_column(Text, nullable=False)
    channel_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    channel_name: Mapped[str] = mapped_column(Text, nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    user_name: Mapped[str] = mapped_column(Text, nullable=False)
    user_display_name: Mapped[str] = mapped_column(Text, nullable=False)
    user_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    bot_response: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    action_type: Mapped[ActionType] = mapped_column(
        Enum(ActionType, name="action_type_enum"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


class ServerPrompt(Base):
    """Model for storing per-server Grok system prompts."""
    __tablename__ = "server_prompts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    guild_id: Mapped[int] = mapped_column(BigInteger, nullable=False, unique=True)
    guild_name: Mapped[str] = mapped_column(Text, nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    user_name: Mapped[str] = mapped_column(Text, nullable=False)
    user_display_name: Mapped[str] = mapped_column(Text, nullable=False)
    system_prompt: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )


# Database engine and session factory (initialized lazily)
_engine = None
_async_session_factory = None


def _get_database_url() -> str:
    """Get the database URL, converting to async format if needed."""
    url = os.getenv("DATABASE_URL", "")
    # Convert postgresql:// to postgresql+asyncpg:// for async driver
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


async def init_db() -> None:
    """Initialize the database connection and create tables."""
    global _engine, _async_session_factory
    
    try:
        database_url = _get_database_url()
        if not database_url:
            print("Warning: DATABASE_URL not set, database features disabled")
            return
        
        _engine = create_async_engine(database_url, echo=False)
        _async_session_factory = async_sessionmaker(_engine, expire_on_commit=False)
        
        # Create tables if they don't exist
        async with _engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        print("Database initialized successfully")
    except Exception as e:
        print(f"Error initializing database: {e}")
        _engine = None
        _async_session_factory = None


async def close_db() -> None:
    """Close the database connection."""
    global _engine
    if _engine:
        await _engine.dispose()
        _engine = None


def _get_session() -> Optional[AsyncSession]:
    """Get a new async session if database is available."""
    if _async_session_factory is None:
        return None
    return _async_session_factory()


async def log_message(
    guild_id: int,
    guild_name: str,
    channel_id: int,
    channel_name: str,
    user_id: int,
    user_name: str,
    user_display_name: str,
    action_type: ActionType,
    user_message: Optional[str] = None,
    bot_response: Optional[str] = None,
) -> bool:
    """
    Log a bot message interaction to the database.
    
    Returns True if successful, False otherwise.
    Gracefully handles database errors without crashing.
    """
    session = _get_session()
    if session is None:
        return False
    
    try:
        async with session:
            message = BotMessage(
                guild_id=guild_id,
                guild_name=guild_name,
                channel_id=channel_id,
                channel_name=channel_name,
                user_id=user_id,
                user_name=user_name,
                user_display_name=user_display_name,
                user_message=user_message,
                bot_response=bot_response,
                action_type=action_type,
            )
            session.add(message)
            await session.commit()
            return True
    except Exception as e:
        print(f"Error logging message to database: {e}")
        return False


async def upsert_server_prompt(
    guild_id: int,
    guild_name: str,
    user_id: int,
    user_name: str,
    user_display_name: str,
    system_prompt: str,
) -> bool:
    """
    Insert or update a server's system prompt.
    
    Returns True if successful, False otherwise.
    Gracefully handles database errors without crashing.
    """
    session = _get_session()
    if session is None:
        return False
    
    try:
        async with session:
            from sqlalchemy import select
            
            # Check if prompt exists for this guild
            stmt = select(ServerPrompt).where(ServerPrompt.guild_id == guild_id)
            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()
            
            if existing:
                # Update existing prompt
                existing.guild_name = guild_name
                existing.user_id = user_id
                existing.user_name = user_name
                existing.user_display_name = user_display_name
                existing.system_prompt = system_prompt
                existing.updated_at = datetime.now(timezone.utc)
            else:
                # Create new prompt
                new_prompt = ServerPrompt(
                    guild_id=guild_id,
                    guild_name=guild_name,
                    user_id=user_id,
                    user_name=user_name,
                    user_display_name=user_display_name,
                    system_prompt=system_prompt,
                )
                session.add(new_prompt)
            
            await session.commit()
            return True
    except Exception as e:
        print(f"Error upserting server prompt: {e}")
        return False


async def get_server_prompt(guild_id: int) -> Optional[str]:
    """
    Get the system prompt for a server.
    
    Returns the prompt string if found, None otherwise.
    Gracefully handles database errors without crashing.
    """
    session = _get_session()
    if session is None:
        return None
    
    try:
        async with session:
            from sqlalchemy import select
            
            stmt = select(ServerPrompt.system_prompt).where(
                ServerPrompt.guild_id == guild_id
            )
            result = await session.execute(stmt)
            prompt = result.scalar_one_or_none()
            return prompt
    except Exception as e:
        print(f"Error getting server prompt: {e}")
        return None

