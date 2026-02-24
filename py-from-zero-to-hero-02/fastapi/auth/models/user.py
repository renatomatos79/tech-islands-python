from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from auth.db.base import Base
from auth.enums.roles import Role

class User(Base):
    """User entity"""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(40), nullable=False, unique=False)
    email: Mapped[str] = mapped_column(String(125), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    # just to simplify, let´s start with these roles: "admin" | "user"
    role: Mapped[str] = mapped_column(String(20), nullable=False, default=Role.USER)  
