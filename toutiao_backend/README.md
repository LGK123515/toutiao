# 头条新闻后端

基于 FastAPI + SQLAlchemy + MySQL + Redis 的新闻类应用后端。

## 技术栈

- FastAPI / Pydantic
- SQLAlchemy 2.0 (async) + MySQL
- Redis (缓存)
- JWT / Token 鉴权




## 本地运行

1. 安装依赖：`pip install -r requirements.txt`
2. 复制 `config/.env.example` 为 `config/.env`，填入自己的数据库和 Redis 配置
3. 启动：`uvicorn main:app --reload`
4. 接口文档：http://127.0.0.1:8000/docs

## 功能

- 用户注册 / 登录 / 修改资料 / 修改密码
- 新闻分类、列表、详情
- 收藏、浏览历史
