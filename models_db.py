from typing import Optional
import datetime
import uuid

from sqlalchemy import Boolean, Column, DateTime, Double, ForeignKeyConstraint, Integer, PrimaryKeyConstraint, String, Table, Text, UniqueConstraint, Uuid, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass


class Category(Base):
    __tablename__ = 'category'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='category_pk'),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)

    product: Mapped[list['Product']] = relationship('Product', back_populates='category')


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
    sale: Mapped[list['Sale']] = relationship('Sale', back_populates='customer')


class Role(Base):
    __tablename__ = 'role'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='role_pk'),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    name: Mapped[str] = mapped_column(String, nullable=False)


t_sale_detail = Table(
    'sale_detail', Base.metadata,
    Column('id', Uuid, nullable=False, server_default=text('gen_random_uuid()')),
    Column('sale_id', Uuid, nullable=False),
    Column('presentation_id', Uuid, nullable=False),
    Column('lot_detail_id', Uuid),
    Column('bulk_conversion_id', Uuid),
    Column('quantity', Integer, nullable=False),
    Column('unit_price', Double(53), nullable=False),
    Column('line_total', Double(53))
)


class Supplier(Base):
    __tablename__ = 'supplier'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='supplier_pk'),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    name: Mapped[str] = mapped_column(String, nullable=False)
    contact_person: Mapped[str] = mapped_column(String, nullable=False)
    address: Mapped[Optional[str]] = mapped_column(String)
    phone_number: Mapped[Optional[str]] = mapped_column(String)
    email: Mapped[Optional[str]] = mapped_column(String)

    lot: Mapped[list['Lot']] = relationship('Lot', back_populates='supplier')


class Unit(Base):
    __tablename__ = 'unit'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='unit_pk'),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    symbol: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[Optional[str]] = mapped_column(String)
    factor_to_base: Mapped[Optional[float]] = mapped_column(Double(53))


class UserRole(Base):
    __tablename__ = 'user_role'
    __table_args__ = (
        PrimaryKeyConstraint('role_id', 'user_id', name='user_role_pk'),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    role_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)


class Lot(Base):
    __tablename__ = 'lot'
    __table_args__ = (
        ForeignKeyConstraint(['supplier_id'], ['supplier.id'], name='lot_supplier_id_fk'),
        PrimaryKeyConstraint('id', name='lot_pk')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    lot_code: Mapped[str] = mapped_column(String, nullable=False)
    supplier_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    expiry_date: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    total_cost: Mapped[float] = mapped_column(Double(53), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    received_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    status: Mapped[Optional[str]] = mapped_column(String)
    notes: Mapped[Optional[str]] = mapped_column(String)

    supplier: Mapped['Supplier'] = relationship('Supplier', back_populates='lot')
    lot_detail: Mapped[list['LotDetail']] = relationship('LotDetail', back_populates='lot')


class Product(Base):
    __tablename__ = 'product'
    __table_args__ = (
        ForeignKeyConstraint(['category_id'], ['category.id'], name='product_category_id_fk'),
        PrimaryKeyConstraint('id', name='product_pk')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    category_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    brand: Mapped[str] = mapped_column(String, nullable=False)
    is_bulk: Mapped[bool] = mapped_column('is_bulk ', Boolean, nullable=False, server_default=text('false'))
    base_unit: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    image_url: Mapped[Optional[str]] = mapped_column(String)

    category: Mapped['Category'] = relationship('Category', back_populates='product')
    product_presentation: Mapped[list['ProductPresentation']] = relationship('ProductPresentation', back_populates='product')


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
    sale: Mapped[list['Sale']] = relationship('Sale', back_populates='user')
    inventory_movement: Mapped[list['InventoryMovement']] = relationship('InventoryMovement', back_populates='user')


class ProductPresentation(Base):
    __tablename__ = 'product_presentation'
    __table_args__ = (
        ForeignKeyConstraint(['product_id'], ['product.id'], name='product_presentation_product_id_fk'),
        PrimaryKeyConstraint('id', name='product_presentation_pk')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    product_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    presentation_name: Mapped[str] = mapped_column(String, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit: Mapped[str] = mapped_column(String, nullable=False)
    sku: Mapped[str] = mapped_column(String, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('true'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('now()'))

    product: Mapped['Product'] = relationship('Product', back_populates='product_presentation')
    lot_detail: Mapped[list['LotDetail']] = relationship('LotDetail', back_populates='presentation')
    bulk_conversion: Mapped[list['BulkConversion']] = relationship('BulkConversion', back_populates='target_presentation')
    inventory_movement: Mapped[list['InventoryMovement']] = relationship('InventoryMovement', back_populates='presentation')


class Sale(Base):
    __tablename__ = 'sale'
    __table_args__ = (
        ForeignKeyConstraint(['customer_id'], ['person.id'], name='sale_person_id_fk'),
        ForeignKeyConstraint(['user_id'], ['user.id'], name='sale___fk'),
        PrimaryKeyConstraint('id', name='sale_pk')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    sale_code: Mapped[str] = mapped_column(String, nullable=False)
    sale_date: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    customer_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    total: Mapped[Optional[float]] = mapped_column(Double(53))

    customer: Mapped['Person'] = relationship('Person', back_populates='sale')
    user: Mapped['User'] = relationship('User', back_populates='sale')


class LotDetail(Base):
    __tablename__ = 'lot_detail'
    __table_args__ = (
        ForeignKeyConstraint(['lot_id'], ['lot.id'], name='lot_detail_lot_id_fk'),
        ForeignKeyConstraint(['presentation_id'], ['product_presentation.id'], name='lot_detail_product_presentation_id_fk'),
        PrimaryKeyConstraint('id', name='lot_detail_pk')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    lot_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    presentation_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    quantity_received: Mapped[int] = mapped_column(Integer, nullable=False)
    quantity_available: Mapped[int] = mapped_column('quantity_available ', Integer, nullable=False)
    unit_cost: Mapped[float] = mapped_column(Double(53), nullable=False)
    batch_number: Mapped[str] = mapped_column(String, nullable=False)

    lot: Mapped['Lot'] = relationship('Lot', back_populates='lot_detail')
    presentation: Mapped['ProductPresentation'] = relationship('ProductPresentation', back_populates='lot_detail')
    bulk_conversion: Mapped[list['BulkConversion']] = relationship('BulkConversion', back_populates='source_lot_detail')
    inventory_movement: Mapped[list['InventoryMovement']] = relationship('InventoryMovement', back_populates='lot_detail')


class BulkConversion(Base):
    __tablename__ = 'bulk_conversion'
    __table_args__ = (
        ForeignKeyConstraint(['source_lot_detail_id'], ['lot_detail.id'], name='bulk_conversion___fk'),
        ForeignKeyConstraint(['target_presentation_id'], ['product_presentation.id'], name='bulk_conversion___fk_2'),
        PrimaryKeyConstraint('id', name='bulk_conversion_pk')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    source_lot_detail_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    target_presentation_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    converted_quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    remaining_bulk: Mapped[int] = mapped_column(Integer, nullable=False)
    conversion_date: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    status: Mapped[Optional[str]] = mapped_column(String)

    source_lot_detail: Mapped['LotDetail'] = relationship('LotDetail', back_populates='bulk_conversion')
    target_presentation: Mapped['ProductPresentation'] = relationship('ProductPresentation', back_populates='bulk_conversion')
    inventory_movement: Mapped[list['InventoryMovement']] = relationship('InventoryMovement', back_populates='bulk_conversion')


class InventoryMovement(Base):
    __tablename__ = 'inventory_movement'
    __table_args__ = (
        ForeignKeyConstraint(['bulk_conversion_id'], ['bulk_conversion.id'], name='inventory_movement_bulk_conversion_id_fk'),
        ForeignKeyConstraint(['lot_detail_id'], ['lot_detail.id'], name='inventory_movement___fk'),
        ForeignKeyConstraint(['presentation_id'], ['product_presentation.id'], name='inventory_movement_product_presentation_id_fk'),
        ForeignKeyConstraint(['user_id'], ['user.id'], name='inventory_movement_user_id_fk'),
        PrimaryKeyConstraint('id', name='inventory_movement_pk')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'))
    presentation_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    lot_detail_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    bulk_conversion_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    type: Mapped[Optional[str]] = mapped_column(String)
    quantity: Mapped[Optional[float]] = mapped_column(Double(53))
    reason: Mapped[Optional[str]] = mapped_column(String)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)

    bulk_conversion: Mapped[Optional['BulkConversion']] = relationship('BulkConversion', back_populates='inventory_movement')
    lot_detail: Mapped[Optional['LotDetail']] = relationship('LotDetail', back_populates='inventory_movement')
    presentation: Mapped[Optional['ProductPresentation']] = relationship('ProductPresentation', back_populates='inventory_movement')
    user: Mapped[Optional['User']] = relationship('User', back_populates='inventory_movement')
