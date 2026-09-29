from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from models.users import User
from schemas.users import UserAuthResponse, UserChangPasswordRequest, UserInfoResponse, UserRequest, UserUpdateRequest
from config.db_config import get_db
from crud import users
from utils.response import success_response
from utils.auth import get_current_user


router = APIRouter(prefix="/api/user", tags=["users"])

@router.post("/register")
async def register(user_data: UserRequest, db: AsyncSession = Depends(get_db)):
    #注册逻辑: 验证用户是否存在 -> 创建用户 -> 生成Token -> 响应结果   (数据库操作)
    existing_user = await users.get_user_by_username(db, user_data.username)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户已存在")
    user = await users.create_user(db, user_data)
    token = await users.create_token(db, user.id)


    response_data = UserAuthResponse(token=token, userInfo=UserInfoResponse.model_validate(user))
    return success_response(message="注册成功", data=response_data)

@router.post("/login")
async def login(user_data: UserRequest, db: AsyncSession = Depends(get_db)):
    #登录逻辑：验证用户是否存在 -> 验证密码 -> 生成Token -> 响应结果
    user = await users.authenticate_user(db, user_data.username, user_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")

    token = await users.create_token(db, user.id)
    response_data = UserAuthResponse(token=token, userInfo=UserInfoResponse.model_validate(user))
    return success_response(message="登录成功",data=response_data)


#根据Token查询用户 -> 封装crud -> 功能整合成一个工具函数 -> 导入路由使用(依赖注入)
@router.get("/info")
async def get_user_info(user: User =Depends(get_current_user)):
    return success_response(message="获取用户信息成功", data=UserInfoResponse.model_validate(user))

#修改用户信息：验证Token -> 更新(用户输入数据 put提交 -> 请求体参数 -> 定义Pydantic模型类) -> 响应结果
@router.put("/update")
async def update_user_info(user_data: UserUpdateRequest, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    user = await users.update_user(db, user.username, user_data)
    return success_response(message="用户信息更新成功", data=UserInfoResponse.model_validate(user))

@router.put("/password")
async def update_password(
    password_data: UserChangPasswordRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    res = await users.change_password(db, user, password_data.old_password, password_data.new_password)
    if not res:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="修改密码失败,请稍后再试")
    return success_response(message="密码修改成功")