from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from config.db_config import get_db
from models.users import User
from schemas.history import HistoryAddRequest, HistoryAddResponse, HistorylistResponse
from utils.auth import get_current_user
from utils.response import success_response
from crud import history



router = APIRouter(prefix="/api/history", tags=["history"])


@router.post("/add")
async def add_history(
    data: HistoryAddRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    historys = await history.add_a_history(db, user.id, data.news_id)
    return success_response(message="添加成功", data=HistoryAddResponse.model_validate(historys))


@router.get("/list")
async def get_history_list(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100, alias="pageSize"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    total, rows = await history.get_history_list(db, user.id, page, page_size)
    history_list = [{
        **news.__dict__,
        "history_id": history_id,
        "view_time": view_time
    } for news, history_id, view_time in rows]
    has_more = total > page * page_size    
    data = HistorylistResponse(list=history_list, total=total, has_more=has_more)
    return success_response(message="获取历史列表成功", data=data)


@router.delete("/delete/{history_id}")
async def delete_history(
    history_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    res = await history.delete_history(db, history_id, user.id)
    if not res:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="浏览历史不存在")
    return success_response(message="删除成功")


@router.delete("/clear")
async def clear_history(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    result = await history.delete_allhistory(db, user.id)
    return success_response(message="清空成功")