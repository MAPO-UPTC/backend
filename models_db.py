from typing import Optional
import uuid

from sqlalchemy import ForeignKeyConstraint, PrimaryKeyConstraint, String, UniqueConstraint, Uuid, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass


class Person(Base):
    __tablename__ = 'person'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='person_pk'),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    name: Mapped[str] = mapped_column(String, nullable=False)
    last_name: Mapped[str] = mapped_column(String, nullable=False)
    document_type: Mapped[str] = mapped_column(String, nullable=False)
    document_number: Mapped[str] = mapped_column(String, nullable=False)

    user: Mapped[list['User']] = relationship('User', back_populates='person')


class Product(Base):
    __tablename__ = 'product'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='product_pk'),
        UniqueConstraint('name', name='product_pk_2')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    category_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)


class Role(Base):
    __tablename__ = 'role'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='role_pk'),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    name: Mapped[str] = mapped_column(String, nullable=False)


class UserRole(Base):
    __tablename__ = 'user_role'
    __table_args__ = (
        PrimaryKeyConstraint('role_id', 'user_id', name='user_role_pk'),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    role_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)


class User(Base):
    __tablename__ = 'user'
    __table_args__ = (
        ForeignKeyConstraint(['person_id'], ['person.id'], name='user_person_id_fk'),
        PrimaryKeyConstraint('id', name='user_pk'),
        UniqueConstraint('email', name='user_pk_2')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    uid: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False)
    person_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)

    person: Mapped['Person'] = relationship('Person', back_populates='user')
