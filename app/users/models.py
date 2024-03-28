from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy import String, Integer
from typing import TYPE_CHECKING
from app.database import Base
from typing import Optional

if TYPE_CHECKING:
    from app.templates.models import Templates


class Users(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(Integer)
    name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    templates: Mapped[list["Templates"]] = relationship(back_populates="users", cascade="all, delete")
