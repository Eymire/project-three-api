from datetime import UTC, datetime

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, declarative_base, mapped_column


Base = declarative_base()


class UserModel(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    hashed_password: Mapped[bytes]
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now(UTC),
    )

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'hashed_password': self.hashed_password,
            'created_at': self.created_at,
        }
