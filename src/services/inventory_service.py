"""
Servicio para manejo de inventario (ingreso de productos)
"""
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from src.models_db import Lot, LotDetail, ProductPresentation, Supplier
from src.schemas.inventory import LotCreate, LotDetailCreate, SupplierCreate


def create_lot(db: Session, lot: LotCreate) -> Lot:
    """
    Crear un nuevo lote de compra
    """
    db_lot = Lot(
        lot_code=lot.lot_code,
        supplier_id=lot.supplier_id,
        received_date=lot.received_date,
        expiry_date=lot.expiry_date,
        status=lot.status,
        total_cost=lot.total_cost,
        notes=lot.notes
    )
    db.add(db_lot)
    db.commit()
    db.refresh(db_lot)
    return db_lot


def create_lot_detail(db: Session, lot_detail: LotDetailCreate, lot_id: str) -> LotDetail:
    """
    Crear un detalle de lote (producto específico en un lote)
    """
    # Verificar que la presentación existe
    presentation = db.query(ProductPresentation).filter(
        ProductPresentation.id == lot_detail.presentation_id
    ).first()
    
    if not presentation:
        raise ValueError(f"Presentación con ID {lot_detail.presentation_id} no encontrada")
    
    # Crear el detalle del lote
    db_lot_detail = LotDetail(
        lot_id=lot_id,
        presentation_id=lot_detail.presentation_id,
        quantity_received=lot_detail.quantity_received,
        quantity_available=lot_detail.quantity_received,  # Inicialmente igual a recibido
        unit_cost=lot_detail.unit_cost,
        batch_number=lot_detail.batch_number
    )
    
    db.add(db_lot_detail)
    db.commit()
    db.refresh(db_lot_detail)
    
    return db_lot_detail


def create_lot_with_details(db: Session, lot: LotCreate, lot_details: List[LotDetailCreate]) -> Lot:
    """
    Crear un lote con sus detalles en una sola transacción
    """
    try:
        # Crear el lote
        db_lot = create_lot(db, lot)
        
        # Crear todos los detalles
        for detail in lot_details:
            create_lot_detail(db, detail, str(db_lot.id))
        
        return db_lot
    
    except Exception as e:
        db.rollback()
        raise e


def get_lot_by_id(db: Session, lot_id: str) -> Optional[Lot]:
    """
    Obtener un lote por su ID
    """
    return db.query(Lot).filter(Lot.id == lot_id).first()


def get_lots(db: Session, skip: int = 0, limit: int = 100) -> List[Lot]:
    """
    Obtener lista de lotes con paginación
    """
    return db.query(Lot).offset(skip).limit(limit).all()


def get_lot_details_by_lot(db: Session, lot_id: str) -> List[LotDetail]:
    """
    Obtener todos los detalles de un lote específico
    """
    return db.query(LotDetail).filter(LotDetail.lot_id == lot_id).all()


def get_available_stock_by_presentation(db: Session, presentation_id: str) -> int:
    """
    Obtener el stock disponible total para una presentación específica
    """
    result = db.query(
        func.sum(LotDetail.quantity_available)
    ).filter(
        LotDetail.presentation_id == presentation_id
    ).scalar()
    
    return result or 0


def get_lot_details_by_presentation(db: Session, presentation_id: str, available_only: bool = True) -> List[LotDetail]:
    """
    Obtener todos los detalles de lotes para una presentación específica.
    Ordenados por fecha de recepción (FIFO - First In, First Out).
    
    Args:
        db: Sesión de base de datos
        presentation_id: UUID de la presentación
        available_only: Si True, solo retorna lotes con quantity_available > 0
    
    Returns:
        Lista de LotDetail ordenados por FIFO (más antiguo primero)
    """
    # JOIN explícito con condición ON para evitar ambigüedad
    query = db.query(LotDetail).join(
        Lot, 
        LotDetail.lot_id == Lot.id
    ).filter(
        LotDetail.presentation_id == presentation_id
    )
    
    # Filtrar solo lotes con stock disponible si se solicita
    if available_only:
        query = query.filter(LotDetail.quantity_available > 0)
    
    # Ordenar por fecha de recepción (FIFO) - más antiguo primero
    # Cualificar explícitamente las columnas para evitar ambigüedad
    lot_details = query.order_by(Lot.received_date.asc(), LotDetail.id.asc()).all()
    
    return lot_details


def reduce_stock(db: Session, presentation_id: str, quantity: int) -> bool:
    """
    Reducir stock de una presentación usando FIFO (First In, First Out)
    Retorna True si fue exitoso, False si no hay suficiente stock
    """
    # Verificar stock total disponible
    total_available = get_available_stock_by_presentation(db, presentation_id)
    
    if total_available < quantity:
        return False
    
    # Obtener detalles ordenados por fecha de compra (FIFO)
    # JOIN explícito con condición ON para evitar ambigüedad
    lot_details = db.query(LotDetail).join(
        Lot,
        LotDetail.lot_id == Lot.id
    ).filter(
        LotDetail.presentation_id == presentation_id,
        LotDetail.quantity_available > 0
    ).order_by(Lot.received_date.asc()).all()
    
    remaining_to_reduce = quantity
    
    for detail in lot_details:
        if remaining_to_reduce <= 0:
            break
            
        if detail.quantity_available >= remaining_to_reduce:
            # Este lote tiene suficiente para completar la reducción
            detail.quantity_available -= remaining_to_reduce
            remaining_to_reduce = 0
        else:
            # Usar todo lo disponible de este lote
            remaining_to_reduce -= detail.quantity_available
            detail.quantity_available = 0
    
    db.commit()
    return True


def get_stock_report(db: Session) -> List[dict]:
    """
    Generar reporte de stock actual por presentación
    """
    query = db.query(
        ProductPresentation.id,
        ProductPresentation.presentation_name,
        func.sum(LotDetail.quantity_available).label("stock_available")
    ).outerjoin(LotDetail).group_by(
        ProductPresentation.id,
        ProductPresentation.presentation_name
    ).all()
    
    return [
        {
            "presentation_id": row.id,
            "presentation_name": row.presentation_name,
            "stock_available": row.stock_available or 0,
            "last_updated": datetime.now().isoformat()
        }
        for row in query
    ]


# FUNCIONES PARA PROVEEDORES
# ==========================

def create_supplier(db: Session, supplier: SupplierCreate) -> Supplier:
    """
    Crear un nuevo proveedor
    """
    db_supplier = Supplier(
        name=supplier.name,
        address=supplier.address,
        phone_number=supplier.phone_number,
        email=supplier.email,
        contact_person=supplier.contact_person
    )
    db.add(db_supplier)
    db.commit()
    db.refresh(db_supplier)
    return db_supplier


def get_suppliers(db: Session, skip: int = 0, limit: int = 100) -> List[Supplier]:
    """
    Obtener lista de proveedores
    """
    return db.query(Supplier).offset(skip).limit(limit).all()


def get_supplier_by_id(db: Session, supplier_id: str) -> Optional[Supplier]:
    """
    Obtener un proveedor por su ID
    """
    return db.query(Supplier).filter(Supplier.id == supplier_id).first()