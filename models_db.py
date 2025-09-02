from typing import Optional
import uuid

from sqlalchemy import PrimaryKeyConstraint, String, Uuid, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'user'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='user_pk'),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    first_name: Mapped[str] = mapped_column(String, nullable=False)
    last_name: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[str] = mapped_column(String, nullable=False, server_default=text("'USER'::character varying"))
    email: Mapped[str] = mapped_column(String, nullable=False)
    second_first_name: Mapped[Optional[str]] = mapped_column(String)
    second_last_name: Mapped[Optional[str]] = mapped_column(String)
    uid: Mapped[Optional[str]] = mapped_column(String)
    phone_code: Mapped[Optional[str]] = mapped_column(String)
    phone_number: Mapped[Optional[str]] = mapped_column(String)
