"""
Servicio para manejo de inventario (ingreso de productos)
"""
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from src.models_db import Lot, LotDetail, ProductPresentation
from src.schemas.inventory import LotCreate, LotDetailCreate


def create_lot(db: Session, lot: LotCreate) -> Lot:
    """
    Crear un nuevo lote de compra
    """
    db_lot = Lot(
        supplier_name=lot.supplier_name,
        purchase_date=lot.purchase_date,
        invoice_number=lot.invoice_number,
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
        batch_number=lot_detail.batch_number,
        expiry_date=lot_detail.expiry_date,
        supplier_info=lot_detail.supplier_info
    )
    
    db.add(db_lot_detail)
    db.commit()
    db.refresh(db_lot_detail)
    
    # Actualizar el stock de la presentación
    presentation.stock += lot_detail.quantity_received
    db.commit()
    
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


def get_available_stock_by_presentation(db: Session, presentation_id: int) -> int:
    """
    Obtener el stock disponible total para una presentación específica
    """
    result = db.query(
        db.func.sum(LotDetail.quantity_available)
    ).filter(
        LotDetail.presentation_id == presentation_id
    ).scalar()
    
    return result or 0


def reduce_stock(db: Session, presentation_id: int, quantity: int) -> bool:
    """
    Reducir stock de una presentación usando FIFO (First In, First Out)
    Retorna True si fue exitoso, False si no hay suficiente stock
    """
    # Verificar stock total disponible
    total_available = get_available_stock_by_presentation(db, presentation_id)
    
    if total_available < quantity:
        return False
    
    # Obtener detalles ordenados por fecha de compra (FIFO)
    lot_details = db.query(LotDetail).join(Lot).filter(
        LotDetail.presentation_id == presentation_id,
        LotDetail.quantity_available > 0
    ).order_by(Lot.purchase_date).all()
    
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
    
    # Actualizar también el stock en la presentación
    presentation = db.query(ProductPresentation).filter(
        ProductPresentation.id == presentation_id
    ).first()
    
    if presentation:
        presentation.stock -= quantity
    
    db.commit()
    return True


def get_stock_report(db: Session) -> List[dict]:
    """
    Generar reporte de stock actual por presentación
    """
    query = db.query(
        ProductPresentation.id,
        ProductPresentation.presentation_name,
        ProductPresentation.stock,
        db.func.sum(LotDetail.quantity_available).label("stock_by_lots")
    ).join(LotDetail).group_by(
        ProductPresentation.id,
        ProductPresentation.presentation_name,
        ProductPresentation.stock
    ).all()
    
    return [
        {
            "presentation_id": row.id,
            "presentation_name": row.presentation_name,
            "stock_in_presentation": row.stock,
            "stock_by_lots": row.stock_by_lots or 0,
            "discrepancy": row.stock - (row.stock_by_lots or 0)
        }
        for row in query
    ]