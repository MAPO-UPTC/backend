# Modelos de Base de Datos MAPO

import uuid
import os
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Uuid,
    func,
    text
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


# Declarative Base
class Base(DeclarativeBase):
    pass


def uuid_default():
    # Si es SQLite, usar uuid.uuid4 en Python. Si es PostgreSQL, usar gen_random_uuid()
    db_url = os.getenv("DATABASE_URL", "sqlite:///")
    if db_url.startswith("sqlite"):
        return uuid.uuid4
    else:
        return text("gen_random_uuid()")


# MODELOS DE INVENTARIO Y LOTES
# =====================

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


class Lot(Base):
    __tablename__ = "lot"
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    supplier_name: Mapped[str] = mapped_column(String, nullable=False)
    purchase_date: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    invoice_number: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    total_cost: Mapped[float] = mapped_column(Float, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(String, nullable=True)


# MODELOS DE PERSONAS Y USUARIOS
# =====================

class Person(Base):
    __tablename__ = "person"
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    last_name: Mapped[str] = mapped_column(String, nullable=False)
    identification: Mapped[str] = mapped_column(String, nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    address: Mapped[Optional[str]] = mapped_column(String, nullable=True)


class User(Base):
    __tablename__ = "user"
    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid_default()
    )
    firebase_uid: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    person_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("person.id"), nullable=False
    )
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class Role(Base):
    __tablename__ = "role"
    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid_default()
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)


class UserRole(Base):
    __tablename__ = "user_role"
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid_default())
    role_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid_default())


# MODELOS DE PRODUCTOS Y CATEGORÍAS
# =====================

class Category(Base):
    __tablename__ = "category"
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)


class Product(Base):
    __tablename__ = "product"
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("category.id"), nullable=False)
    brand: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    base_unit: Mapped[str] = mapped_column(String, nullable=False, default="unidad")


class ProductPresentation(Base):
    __tablename__ = "product_presentation"
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("product.id"), nullable=False)
    presentation_name: Mapped[str] = mapped_column(String, nullable=False)
    unit_quantity: Mapped[float] = mapped_column(Float, nullable=False)
    unit_type: Mapped[str] = mapped_column(String, nullable=False)
    stock: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class BulkConversion(Base):
    __tablename__ = "bulk_conversion"
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    from_presentation_id: Mapped[int] = mapped_column(Integer, ForeignKey("product_presentation.id"), nullable=False)
    to_presentation_id: Mapped[int] = mapped_column(Integer, ForeignKey("product_presentation.id"), nullable=False)
    conversion_factor: Mapped[float] = mapped_column(Float, nullable=False)


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
    notes: Mapped[Optional[str]] = mapped_column(String, nullable=True)


class SaleDetail(Base):
    __tablename__ = "sale_detail"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sale_id: Mapped[int] = mapped_column(Integer, ForeignKey("sale.id"), nullable=False)
    presentation_id: Mapped[int] = mapped_column(Integer, ForeignKey("product_presentation.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[float] = mapped_column(Float, nullable=False)
    discount: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    subtotal: Mapped[float] = mapped_column(Float, nullable=False)