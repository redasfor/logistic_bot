from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy import JSON, Integer, Float, ForeignKey, DateTime
from datetime import datetime
from typing import TYPE_CHECKING
from app.database import Base

if TYPE_CHECKING:
    from app.users.models import Users


class Templates(Base):
    __tablename__ = "templates"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_name: Mapped[str]
    delivery_country: Mapped[str]
    payment_currency: Mapped[str]
    logistics_cost: Mapped[float] = mapped_column(Float)
    measure_of_weight: Mapped[str]
    unit_price: Mapped[float] = mapped_column(Float)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    parameters: Mapped[list[str, int]] = mapped_column(JSON)
    weight: Mapped[int]
    commission: Mapped[float] = mapped_column(Float, nullable=True)
    users: Mapped["Users"] = relationship(back_populates="templates")
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    date: Mapped[datetime] = mapped_column(DateTime, nullable=True)
