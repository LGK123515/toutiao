from pydantic import BaseModel, Field


class UserLLMRequest(BaseModel):
    message: str = Field(min_length=1)
    conversation_id: int | None = Field(default=None, alias="conversationId")
