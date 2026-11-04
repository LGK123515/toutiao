from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.ai import AIConversation, AIMessages


async def create_conversation_id(
    user_id: int,
    db: AsyncSession
):
    conversation = AIConversation(user_id=user_id)

    db.add(conversation)
    await db.flush()

    return conversation.id

async def get_history_messages(
    conversation_id: int,
    db: AsyncSession,
    limit: int | None = 30,
):
    stmt = select(AIMessages).where(AIMessages.conversation_id == conversation_id)
    if limit is None:
        stmt = stmt.order_by(AIMessages.id.asc())
    else:
        stmt = stmt.order_by(AIMessages.id.desc()).limit(limit)
    result = await db.execute(stmt)
    messages = result.scalars().all()
    if limit is not None:
        messages = reversed(messages)

    return [{"role": item.role, "content": item.content} for item in messages]

async def add_history_messages(
    conversation_id: int,
    role: str,
    message: str,
    db: AsyncSession
):
    history = AIMessages(conversation_id=conversation_id, role=role, content=message)

    db.add(history)
    await db.flush()

    return history
