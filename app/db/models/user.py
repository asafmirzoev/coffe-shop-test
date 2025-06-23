from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column

from app.db.models import BaseDbModel


class UserDbModel(BaseDbModel):
    __tablename__ = 'users'

    email: Mapped[str] = mapped_column(
        unique=True,
        index=True,
    )

    first_name: Mapped[Optional[str]] = mapped_column(default=None)
    last_name: Mapped[Optional[str]] = mapped_column(default=None)

    password: Mapped[str]
    verified: Mapped[bool] = mapped_column(default=False)
    is_admin: Mapped[bool] = mapped_column(default=False)
