import os

from dotenv import load_dotenv
import json
import logging
from typing import Any

import redis.asyncio as redis

logger = logging.getLogger(__name__)

load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))

#创建Redis的连接对象
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    decode_responses=True
)

#读取：字符串
async def get_cache(key: str):
    try:
        return await redis_client.get(key)
    except Exception as e:
        logger.warning("获取缓存失败 key=%s: %s", key, e)
        return None

#读取：列表或字典 (因为redis只能存字符串或字符)
async def get_json_cache(key: str):
    try:
        data = await redis_client.get(key)
        if data:
            return json.loads(data)
        return None
    except Exception as e:
        logger.warning("获取json缓存失败 key=%s: %s", key, e)
        return None

#设置缓存 setex(key, expire, value)
async def set_cache(key: str, value: Any, expire: int = 3600):
    try:
        if isinstance(value, (dict, list)):
            #转字符串再存
            value = json.dumps(value, ensure_ascii=False) #中文正常保存
        await redis_client.setex(key, expire, value)
        return True
    except Exception as e:
        logger.warning("设置缓存失败 key=%s: %s", key, e)
        return False