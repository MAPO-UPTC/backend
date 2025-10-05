# Modelo para detalle de lote (lot_detail)
# Modelo para lotes de compra
class Lot(Base):
    __tablename__ = "lot"
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    supplier_name: Mapped[str] = mapped_column(String, nullable=False)
    purchase_date: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    invoice_number: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    total_cost: Mapped[float] = mapped_column(Float, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(String, nullable=True)

# Modelo para detalle de lote (lot_detail)

import uuid
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    ForeignKeyConstraint,
    Integer,
    PrimaryKeyConstraint,
    String,
    UniqueConstraint,
    Uuid,
    func,
    text
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


# Declarative Base must be defined before any models that inherit from it
class Base(DeclarativeBase):
    pass


class LotDetail(Base):
    __tablename__ = "lot_detail"
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    lot_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    presentation_id: Mapped[int] = mapped_column(Integer, ForeignKey("product_presentation.id"), nullable=False)
    quantity_received: Mapped[int] = mapped_column(Integer, nullable=False)
    quantity_available: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_cost: Mapped[float] = mapped_column(Float, nullable=False)
    batch_number: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    expiry_date: Mapped[Optional[DateTime]] = mapped_column(DateTime, nullable=True)
    supplier_info: Mapped[Optional[str]] = mapped_column(String, nullable=True)


# Modelo para lotes de compra
class Lot(Base):
    __tablename__ = "lot"
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    supplier_name: Mapped[str] = mapped_column(String, nullable=False)
    purchase_date: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    invoice_number: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    total_cost: Mapped[float] = mapped_column(Float, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(String, nullable=True)
# Modelo para presentaciones de producto
class ProductPresentation(Base):
    __tablename__ = "product_presentation"
    id = mapped_column(Integer, primary_key=True)
    product_id = mapped_column(Uuid, ForeignKey("product.id"))
    presentation_name = mapped_column(String, nullable=False)
    quantity = mapped_column(Float, nullable=False)
    unit = mapped_column(String, nullable=False)
    price = mapped_column(Float, nullable=False)
    sku = mapped_column(String)
    active = mapped_column(Boolean, default=True)

# Modelo para conversión de bultos a granel
class BulkConversion(Base):
    __tablename__ = "bulk_conversion"
    id = mapped_column(Integer, primary_key=True)
    source_lot_detail_id = mapped_column(Integer, ForeignKey("lot_detail.id"))
    target_presentation_id = mapped_column(Integer, ForeignKey("product_presentation.id"))
    converted_quantity = mapped_column(Float)
    remaining_bulk = mapped_column(Float)
    conversion_date = mapped_column(DateTime)
    status = mapped_column(String, default="ACTIVE")



import os

def uuid_default():
    # Si es SQLite, usar uuid.uuid4 en Python. Si es PostgreSQL, usar gen_random_uuid()
    db_url = os.getenv("DATABASE_URL", "sqlite:///")
    if db_url.startswith("sqlite"):
        return uuid.uuid4
    else:
        return text("gen_random_uuid()")

class Person(Base):
    __tablename__ = "person"
    __table_args__ = (PrimaryKeyConstraint("id", name="person_pk"),)

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid_default()
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    last_name: Mapped[str] = mapped_column(String, nullable=False)
    document_type: Mapped[str] = mapped_column(String, nullable=False)
    document_number: Mapped[str] = mapped_column(String, nullable=False)

    user: Mapped[list["User"]] = relationship("User", back_populates="person")



class Product(Base):
    __tablename__ = "product"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="product_pk"),
        UniqueConstraint("name", name="product_pk_2"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid_default()
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    brand: Mapped[Optional[str]] = mapped_column(String)
    base_unit: Mapped[Optional[str]] = mapped_column(String)
    category_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    image_url: Mapped[Optional[str]] = mapped_column(String)


class Category(Base):
    __tablename__ = "category"
    __table_args__ = (PrimaryKeyConstraint("id", name="category_pk"),)

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid_default()
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String)
    active: Mapped[bool] = mapped_column(Boolean, default=True)



class Role(Base):
    __tablename__ = "role"
    __table_args__ = (PrimaryKeyConstraint("id", name="role_pk"),)

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid_default()
    )
    name: Mapped[str] = mapped_column(String, nullable=False)



class UserRole(Base):
    __tablename__ = "user_role"
    __table_args__ = (PrimaryKeyConstraint("role_id", "user_id", name="user_role_pk"),)

    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid_default())
    role_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid_default())




class User(Base):
    __tablename__ = "user"
    __table_args__ = (
        ForeignKeyConstraint(["person_id"], ["person.id"], name="user_person_id_fk"),
        PrimaryKeyConstraint("id", name="user_pk"),
        UniqueConstraint("email", name="user_pk_2"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid_default()
    )
    uid: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False)
    person_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)

    person: Mapped["Person"] = relationship("Person", back_populates="user")

# =====================
# MODELOS DE VENTA
# =====================

class Sale(Base):
    __tablename__ = "sale"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sale_code: Mapped[str] = mapped_column(String, nullable=False)
    sale_date: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    customer_id: Mapped[int] = mapped_column(Integer, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    total: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)

    details = relationship("SaleDetail", back_populates="sale")

class SaleDetail(Base):
    __tablename__ = "sale_detail"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sale_id: Mapped[int] = mapped_column(Integer, ForeignKey("sale.id"), nullable=False)
    presentation_id: Mapped[int] = mapped_column(Integer, ForeignKey("product_presentation.id"), nullable=False)
    bulk_conversion_id: Mapped[int] = mapped_column(Integer, ForeignKey("bulk_conversion.id"), nullable=True)
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    unit_price: Mapped[float] = mapped_column(Float, nullable=False)
    line_total: Mapped[float] = mapped_column(Float, nullable=False)

    sale = relationship("Sale", back_populates="details")
