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
    presentation_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("product_presentation.id"), nullable=False)
    quantity_received: Mapped[int] = mapped_column(Integer, nullable=False)
    quantity_available: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_cost: Mapped[float] = mapped_column(Float, nullable=False)
    batch_number: Mapped[str] = mapped_column(String, nullable=False)


class Lot(Base):
    __tablename__ = "lot"
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    lot_code: Mapped[str] = mapped_column(String, nullable=False)
    supplier_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("supplier.id"), nullable=False)
    expiry_date: Mapped[Optional[DateTime]] = mapped_column(DateTime, nullable=True)
    received_date: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    total_cost: Mapped[float] = mapped_column(Float, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, nullable=False, default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, nullable=False, default=func.now(), onupdate=func.now())


class Supplier(Base):
    __tablename__ = "supplier"
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False)
    address: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    phone_number: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    contact_person: Mapped[Optional[str]] = mapped_column(String, nullable=True)


# MODELOS DE PERSONAS Y USUARIOS
# =====================

class Person(Base):
    __tablename__ = "person"
    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    last_name: Mapped[str] = mapped_column(String, nullable=False)
    document_type: Mapped[str] = mapped_column(String, nullable=False)
    document_number: Mapped[str] = mapped_column(String, nullable=False)
    
    # Relación con User
    user: Mapped[Optional["User"]] = relationship("User", back_populates="person")


class User(Base):
    __tablename__ = "user"
    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid_default()
    )
    uid: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String, nullable=False)
    person_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("person.id"), nullable=False
    )
    firebase_uid: Mapped[str] = mapped_column(String, nullable=False)
    
    # Relación con Person
    person: Mapped["Person"] = relationship("Person", back_populates="user")


class Role(Base):
    __tablename__ = "role"
    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid_default()
    )
    name: Mapped[str] = mapped_column(String, nullable=False)


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
    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    category_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid, ForeignKey("category.id"), nullable=True)
    image_url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    brand: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    base_unit: Mapped[str] = mapped_column(String, nullable=False)
    
    # Relación con presentaciones
    presentations: Mapped[list["ProductPresentation"]] = relationship("ProductPresentation", back_populates="product")


class ProductPresentation(Base):
    __tablename__ = "product_presentation"
    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    product_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("product.id"), nullable=False)
    presentation_name: Mapped[str] = mapped_column(String, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit: Mapped[str] = mapped_column(String, nullable=False)
    sku: Mapped[str] = mapped_column(String, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, nullable=False, default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, nullable=False, default=func.now(), onupdate=func.now())
    price: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    
    # Relación con producto
    product: Mapped["Product"] = relationship("Product", back_populates="presentations")


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
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    sale_code: Mapped[str] = mapped_column(String, nullable=False)
    sale_date: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    customer_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("person.id"), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("user.id"), nullable=False)
    total: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)


class SaleDetail(Base):
    __tablename__ = "sale_detail"
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    sale_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("sale.id"), nullable=False)
    presentation_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("product_presentation.id"), nullable=False)
    lot_detail_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("lot_detail.id"), nullable=False)
    bulk_conversion_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("bulk_conversion.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[float] = mapped_column(Float, nullable=False)
    line_total: Mapped[float] = mapped_column(Float, nullable=False)