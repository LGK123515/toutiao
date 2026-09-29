from fastapi.encoders import jsonable_encoder
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from cache.news_cache import get_cache_news_list, get_cached_categories, set_cache_categories, set_cache_news_list
from models.news import Category, News




async def get_categories(db :AsyncSession , skip : int = 0 , limit: int = 100):
    #先尝试从缓存中获取数据
    cache_categoties = await get_cached_categories()
    if cache_categoties:
        return cache_categoties
    
    stmt = select(Category).offset(skip).limit(limit)
    result = await db.execute(stmt)
    categories = result.scalars().all()   #ORM结果

    #写入缓存
    if categories:
        categories = jsonable_encoder(categories)
        await set_cache_categories(categories)

    return categories

async def get_news_list(db: AsyncSession, category_id: int, skip: int = 0, limit: int = 10):
    #尝试从缓存获取
    page = skip // limit + 1   #页码
    cache_list = await get_cache_news_list(category_id, page, limit)
    if cache_list:
        #要的是ORM数据
        return [News(**item) for item in cache_list]
    #查询指定新闻分类下的所有新闻
    stmt = select(News).where(News.category_id == category_id).offset(skip).limit(limit)
    result = await db.execute(stmt)
    news_list = result.scalars().all()

    #写入缓存
    if news_list:
        #先把ORM数据 转换为 字典 才能写入缓存
        news_list = jsonable_encoder(news_list)
        await set_cache_news_list(category_id, page, limit, news_list)

    return news_list  



async def get_news_cout(db: AsyncSession, category_id: int):
    stmt = select(func.count(News.id)).where(News.category_id == category_id)
    result = await db.execute(stmt)
    return result.scalar_one()

async def get_news_detail(db: AsyncSession, news_id: int):
    stmt = select(News).where(news_id == News.id)
    result =await db.execute(stmt)
    return result.scalar_one_or_none()


async def increase_views(db: AsyncSession, news_id: int):
    stmt = update(News).where(news_id == News.id).values(views=News.views+1)
    result = await db.execute(stmt)

    return result.rowcount > 0

async def get_related_news(db:AsyncSession, news_id, category_id, limit: int = 5):
    stmt =  select(News).where(
        news_id != News.id,
        category_id == News.category_id
    ).order_by(News.views.desc(), News.publish_time.desc()).limit(limit)
    result = await db.execute(stmt)
    related_news = result.scalars().all()
    #列表推导式
    return [{
        "id": news_detail.id,
        "title": news_detail.title,
        "content": news_detail.content,
        "image": news_detail.image,
        "author": news_detail.author,
        "publishTime": news_detail.publish_time,
        "categoryId": news_detail.category_id,
        "views": news_detail.views
    } for news_detail in related_news ]
