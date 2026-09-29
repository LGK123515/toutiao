from fastapi import Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from config.db_config import get_db
from crud import users
from starlette import status


async def get_current_user(
        authorization: str = Header(alias="Authorization"),
        db: AsyncSession = Depends(get_db)
        ):
    token = authorization.replace("Bearer ", "")
    user = await users.get_user_by_token(db, token)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="令牌无效或已过期")
    
    return user