from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

from schemas.base import NewsItemBase




class HistoryAddRequest(BaseModel):
    #id: int
    #user_id: int = Field(...,alias="userId")
    news_id: int = Field(...,alias="newsId")
    #view_time: datetime = Field(...,alias="viewTime")

    model_config = ConfigDict(
            populate_by_name=True,
            from_attributes=True
        )


class HistoryAddResponse(BaseModel):
    id: int
    user_id: int = Field(...,alias="userId")
    news_id: int = Field(...,alias="newsId")
    view_time: datetime = Field(...,alias="viewTime")

    model_config = ConfigDict(
            populate_by_name=True,
            from_attributes=True
        )


class HistoryItemResponse(NewsItemBase):
    history_id: int = Field(alias="historyId")
    view_time: datetime = Field(alias="viewTime")

    model_config = ConfigDict(
            populate_by_name=True,
            from_attributes=True
        )

#历史列表响应模型类
class HistorylistResponse(BaseModel):
    list: list[HistoryItemResponse]
    total: int
    has_more: bool = Field(alias="hasMore")

    model_config = ConfigDict(
            populate_by_name=True,
            from_attributes=True
        )
