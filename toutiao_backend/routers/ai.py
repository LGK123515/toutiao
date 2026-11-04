import logging
from functools import lru_cache

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from config.db_config import get_db
from config.llm import Myllm
from crud.ai import add_history_messages, create_conversation_id, get_history_messages
from models.ai import AIConversation
from models.users import User
from schemas.ai import UserLLMRequest
from utils.auth import get_current_user
from utils.response import success_response


router = APIRouter(prefix="/api/ai", tags=["ai"])
logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_llm() -> Myllm:
    return Myllm()


async def require_user_conversation(
    conversation_id: int, user_id: int, db: AsyncSession
) -> AIConversation:
    conversation = await db.get(AIConversation, conversation_id)
    if conversation is None or conversation.user_id != user_id:
        raise HTTPException(status_code=404, detail="会话不存在")
    return conversation


@router.post("/chat")
async def llm_chat(
    data: UserLLMRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    question = data.message.strip()
    if not question:
        raise HTTPException(status_code=422, detail="问题不能为空")

    if data.conversation_id is None:
        history = []
    else:
        await require_user_conversation(data.conversation_id, current_user.id, db)
        history = await get_history_messages(data.conversation_id, db)

    try:
        answer = await get_llm().think(history=history, question=question)
    except Exception:
        logger.exception("大模型调用失败")
        raise HTTPException(status_code=502, detail="生成回答失败，请稍后再试")

    if not answer or not answer.strip():
        raise HTTPException(status_code=502, detail="模型未返回有效回答")

    conversation_id = data.conversation_id
    if conversation_id is None:
        conversation_id = await create_conversation_id(current_user.id, db)

    # 同一个数据库事务内保存本轮问题和回答。
    await add_history_messages(conversation_id, "user", question, db)
    await add_history_messages(conversation_id, "assistant", answer, db)

    return success_response(data={"conversationId": conversation_id, "answer": answer})


@router.get("/conversations/{conversation_id}/messages")
async def list_conversation_messages(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await require_user_conversation(conversation_id, current_user.id, db)
    messages = await get_history_messages(conversation_id, db, limit=None)
    return success_response(data={"messages": messages})
