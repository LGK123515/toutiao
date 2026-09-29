from fastapi import APIRouter,Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from config.db_config import get_db
from crud import news, news_cache

#创建APIRouter实例
router = APIRouter(prefix="/api/news" , tags=["news"])

@router.get("/categories")
async def get_cate(db: AsyncSession= Depends(get_db), skip: int=0,limit: int=100):
    categories= await news_cache.get_categories(db, skip, limit)
    return {
        "code":200,
        "message":"获取新闻分类成功",
        "data":categories
    }

@router.get("/list")
async def get_news_lists(
    category_id: int = Query(alias="categoryId"),
    page: int = 1,
    page_size: int = Query(alias="pageSize",le=100),
    db:AsyncSession = Depends(get_db)
):
    offset = (page - 1) * page_size
    new_list = await news_cache.get_news_list(db, category_id, offset, page_size)
    new_count = await news.get_news_cout(db, category_id)
    has_more = (offset + len(new_list)) < new_count
    return {
        "code": 200,
        "message": "获取新闻列表成功",
        "data": {
            "list": new_list,
            "total": new_count,
            "hasMore": has_more 
        }
    }

@router.get("/detail")
async def get_new_detail(new_id: int = Query(alias="id"), db: AsyncSession = Depends(get_db)):
    #获取新闻详情 + 浏览量加一 + 相关新闻
    news_detail = await news.get_news_detail(db, new_id)
    if not news_detail:
        raise HTTPException(status_code=404, detail="新闻不存在")
    #浏览量加一
    views_res = await news.increase_views(db, news_detail.id)
    if not views_res:
        raise HTTPException(status_code=404, detail="新闻不存在")
    
    #相关新闻
    related_news = await news.get_related_news(db, news_detail.id, news_detail.category_id)

    return {
        "code": 200,
        "message": "success",
        "data": {
        "id": news_detail.id,
        "title": news_detail.title,
        "content": news_detail.content,
        "image": news_detail.image,
        "author": news_detail.author,
        "publishTime": news_detail.publish_time,
        "categoryId": news_detail.category_id,
        "views": news_detail.views,
        "relatedNews": related_news
        }
    }


