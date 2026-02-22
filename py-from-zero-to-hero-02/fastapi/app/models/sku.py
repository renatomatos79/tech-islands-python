from sqlalchemy import String, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

class Sku(Base):
    """SKU entity stored in the `skus` table."""

    __tablename__ = "skus"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(40), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    unit_price: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)

    # FK to unit_of_measurements.id
    uom_id: Mapped[int] = mapped_column(ForeignKey("unit_of_measurements.id"), nullable=False)
    # Eager-load the related UOM in list/read operations.
    uom = relationship("UnitOfMeasurement", back_populates="skus", lazy="selectin") 
