from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.favorite import Favorite
from models.news import News


async def is_news_favorite(
        db: AsyncSession,
        user_id: int,
        news_id: int
):
    query = select(Favorite).where(Favorite.user_id == user_id , Favorite.news_id == news_id)
    result = await db.execute(query)
    return result.scalar_one_or_none() is not None #目标是返回布尔值

async def add_news_favorite(
        db: AsyncSession,
        user_id: int,
        news_id: int
):
    favorite = Favorite(user_id=user_id, news_id=news_id)
    db.add(favorite)
    await db.commit()
    await db.refresh(favorite)
    return favorite

async def remove_news_favorite(
        db: AsyncSession,
        user_id: int,
        news_id: int
):
    stmt = delete(Favorite).where(Favorite.news_id == news_id, Favorite.user_id == user_id)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount > 0


async def get_favorite_list(
        db:AsyncSession,
        user_id: int,
        page: int,
        page_size: int
):
    #总量 + 新闻收藏列表
    count_query = select(func.count()).where(Favorite.user_id == user_id)
    count_result = await db.execute(count_query)
    total = count_result.scalar_one()

    #收藏列表 - 联表查询 join() + 收藏时间排序
    offset = (page - 1)*page_size
    #select(查询主体模型类).join(联合查询模型类, 联合查询条件).where().order_by().offset().limit()
    #Favorite.create_at.lable("别名") 起别名
    query = (select(News, Favorite.created_at.label("favorite_time"), Favorite.id.label("favorite_id"))
                .join(Favorite, Favorite.news_id == News.id)
                .where(Favorite.user_id == user_id)
                .order_by(Favorite.created_at.desc())
                .offset(offset).limit(page_size)
                )
    result = await db.execute(query)
    rows = result.all()
    return rows, total
    #rows的返回格式：列表里元组
    #[
    #(新闻对象，收藏时间，收藏id)
    #]


async def remove_all_favorite(
        db: AsyncSession,
        user_id: int
):
    stmt = delete(Favorite).where(Favorite.user_id == user_id)
    result = await db.execute(stmt)
    await db.commit()

    #返回删除数量
    return result.rowcount or 0



