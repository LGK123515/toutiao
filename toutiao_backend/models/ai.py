from datetime import datetime

from sqlalchemy import BigInteger, Enum, Text, Index, Integer, ForeignKey, DateTime
from sqlalchemy.dialects.mysql import INTEGER as MYSQL_INTEGER
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from models.users import User


class Base(DeclarativeBase):
    pass



class AIConversation(Base):
    __tablename__ = 'ai_conversations'
    __table_args__ = (
        Index("idx_ai_conversations_user_id", "user_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        MYSQL_INTEGER(unsigned=True), ForeignKey(User.id, ondelete="CASCADE"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)

class AIMessages(Base):
    __tablename__ = "ai_messages"
    __table_args__ = (
        Index("idx_ai_messages_conversation_id_id", "conversation_id", "id"),
    )

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )
    conversation_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(AIConversation.id, ondelete="CASCADE"), nullable=False
    )
    role: Mapped[str] = mapped_column(
        Enum("user", "assistant"), nullable=False
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, nullable=False
    )

    


