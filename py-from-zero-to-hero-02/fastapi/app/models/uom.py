from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

class UnitOfMeasurement(Base):
    """Unit of measurement entity (e.g., KG, UN, L)."""

    __tablename__ = "unit_of_measurements"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(60), nullable=False, unique=True)    

    # Reverse relationship to all SKUs using this UOM.
    skus = relationship("Sku", back_populates="uom", lazy="selectin")
