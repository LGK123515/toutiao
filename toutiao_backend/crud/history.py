from datetime import datetime

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.favorite import Favorite
from models.history import History
from models.news import News




async def get_history(
        db:AsyncSession,
        user_id: int,
        news_id: int
):
    stmt = select(History).where(History.news_id == news_id, History.user_id == user_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

async def add_a_history(
        db:AsyncSession,
        user_id: int,
        news_id: int
):
    res = await get_history(db, user_id, news_id)
    if res:
        res.view_time = datetime.now()
        await db.commit()
        return res
    else:
        history = History(user_id=user_id, news_id=news_id)
        db.add(history)
        await db.commit()
        await db.refresh(history)
        return history


async def get_history_list(
        db: AsyncSession,
        user_id: int,
        page: int,
        page_size: int
):
    count_query = select(func.count()).where(History.user_id == user_id)
    count_result = await db.execute(count_query)
    total = count_result.scalar_one()

    offset = (page - 1) * page_size

    stmt = (select(News, History.id.label("history_id"), History.view_time)
            .join(History, History.news_id == News.id)
            .where(History.user_id == user_id)
            .order_by(History.view_time.desc())
            .offset(offset).limit(page_size)
            )
    result = await db.execute(stmt)
    rows = result.all()

    return total, rows


async def delete_history(
        db: AsyncSession,
        history_id: int,
        user_id: int
):
    stmt = delete(History).where(History.news_id == history_id, History.user_id == user_id)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount > 0
          
async def delete_allhistory(
        db: AsyncSession,
        user_id: int
):
    stmt = delete(History).where(History.user_id == user_id)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount or 0


