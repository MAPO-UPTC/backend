"""
Servicio para manejo de ventas
"""
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from src.models_db import Sale, SaleDetail, ProductPresentation
from src.schemas.sales import SaleCreate, CompleteSaleCreate, SalesReportFilter
from src.services import inventory_service


def generate_sale_code() -> str:
    """
    Generar código único para la venta
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"VEN-{timestamp}"


def create_sale(db: Session, sale: CompleteSaleCreate, user_id: int) -> Sale:
    """
    Crear una nueva venta con sus detalles
    """
    # Verificar stock disponible para todos los items
    for item in sale.items:
        available_stock = inventory_service.get_available_stock_by_presentation(
            db, item.presentation_id
        )
        if available_stock < item.quantity:
            raise ValueError(
                f"Stock insuficiente para presentación {item.presentation_id}. "
                f"Disponible: {available_stock}, Solicitado: {item.quantity}"
            )
    
    try:
        # Crear la venta
        db_sale = Sale(
            sale_code=generate_sale_code(),
            sale_date=datetime.now(),
            customer_id=sale.customer_id,
            user_id=user_id,
            total=0.0,  # Se calculará después
            notes=sale.notes
        )
        db.add(db_sale)
        db.flush()  # Para obtener el ID de la venta
        
        total_sale = 0.0
        
        # Crear los detalles de la venta
        for item in sale.items:
            subtotal = (item.quantity * item.unit_price) - (item.discount or 0.0)
            
            db_sale_detail = SaleDetail(
                sale_id=db_sale.id,
                presentation_id=item.presentation_id,
                quantity=item.quantity,
                unit_price=item.unit_price,
                discount=item.discount or 0.0,
                subtotal=subtotal
            )
            db.add(db_sale_detail)
            total_sale += subtotal
            
            # Reducir el stock
            success = inventory_service.reduce_stock(
                db, item.presentation_id, item.quantity
            )
            if not success:
                raise ValueError(f"Error reduciendo stock para presentación {item.presentation_id}")
        
        # Actualizar el total de la venta
        db_sale.total = total_sale
        
        db.commit()
        db.refresh(db_sale)
        return db_sale
        
    except Exception as e:
        db.rollback()
        raise e


def get_sale_by_id(db: Session, sale_id: int) -> Optional[Sale]:
    """
    Obtener una venta por su ID con sus detalles
    """
    return db.query(Sale).filter(Sale.id == sale_id).first()


def get_sale_by_code(db: Session, sale_code: str) -> Optional[Sale]:
    """
    Obtener una venta por su código
    """
    return db.query(Sale).filter(Sale.sale_code == sale_code).first()


def get_sales(db: Session, skip: int = 0, limit: int = 100) -> List[Sale]:
    """
    Obtener lista de ventas con paginación
    """
    return db.query(Sale).offset(skip).limit(limit).all()


def get_sales_by_customer(db: Session, customer_id: int, skip: int = 0, limit: int = 100) -> List[Sale]:
    """
    Obtener ventas de un cliente específico
    """
    return db.query(Sale).filter(
        Sale.customer_id == customer_id
    ).offset(skip).limit(limit).all()


def get_sales_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Sale]:
    """
    Obtener ventas realizadas por un usuario específico
    """
    return db.query(Sale).filter(
        Sale.user_id == user_id
    ).offset(skip).limit(limit).all()


def get_sales_by_date_range(
    db: Session, 
    start_date: datetime, 
    end_date: datetime,
    skip: int = 0, 
    limit: int = 100
) -> List[Sale]:
    """
    Obtener ventas en un rango de fechas
    """
    return db.query(Sale).filter(
        Sale.sale_date >= start_date,
        Sale.sale_date <= end_date
    ).offset(skip).limit(limit).all()


def get_sale_details_by_sale(db: Session, sale_id: int) -> List[SaleDetail]:
    """
    Obtener todos los detalles de una venta específica
    """
    return db.query(SaleDetail).filter(SaleDetail.sale_id == sale_id).all()


def cancel_sale(db: Session, sale_id: int) -> bool:
    """
    Cancelar una venta y restaurar el inventario
    """
    try:
        # Obtener la venta y sus detalles
        sale = db.query(Sale).filter(Sale.id == sale_id).first()
        if not sale:
            return False
        
        sale_details = get_sale_details_by_sale(db, sale_id)
        
        # Restaurar el stock para cada item
        for detail in sale_details:
            presentation = db.query(ProductPresentation).filter(
                ProductPresentation.id == detail.presentation_id
            ).first()
            if presentation:
                presentation.stock += detail.quantity
        
        # Marcar la venta como cancelada (o eliminarla según el negocio)
        db.delete(sale)
        
        db.commit()
        return True
        
    except Exception as e:
        db.rollback()
        raise e


def get_sales_report(db: Session, filters: SalesReportFilter) -> dict:
    """
    Generar reporte de ventas con filtros opcionales
    """
    query = db.query(Sale)
    
    # Aplicar filtros
    if filters.start_date:
        query = query.filter(Sale.sale_date >= filters.start_date)
    if filters.end_date:
        query = query.filter(Sale.sale_date <= filters.end_date)
    if filters.customer_id:
        query = query.filter(Sale.customer_id == filters.customer_id)
    if filters.user_id:
        query = query.filter(Sale.user_id == filters.user_id)
    
    sales = query.all()
    
    # Calcular estadísticas
    total_revenue = sum(sale.total for sale in sales)
    
    return {
        "sales": sales,
        "total_sales": len(sales),
        "total_revenue": total_revenue,
        "period_start": filters.start_date,
        "period_end": filters.end_date
    }


def get_best_selling_products(db: Session, limit: int = 10) -> List[dict]:
    """
    Obtener los productos más vendidos
    """
    query = db.query(
        SaleDetail.presentation_id,
        func.sum(SaleDetail.quantity).label("total_sold"),
        func.sum(SaleDetail.subtotal).label("total_revenue")
    ).group_by(SaleDetail.presentation_id).order_by(
        func.sum(SaleDetail.quantity).desc()
    ).limit(limit)
    
    results = query.all()
    
    products = []
    for result in results:
        presentation = db.query(ProductPresentation).filter(
            ProductPresentation.id == result.presentation_id
        ).first()
        
        products.append({
            "presentation_id": result.presentation_id,
            "presentation_name": presentation.presentation_name if presentation else "Unknown",
            "total_sold": result.total_sold,
            "total_revenue": result.total_revenue
        })
    
    return products


def get_daily_sales_summary(db: Session, date: datetime) -> dict:
    """
    Obtener resumen de ventas para un día específico
    """
    start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = date.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    sales = db.query(Sale).filter(
        Sale.sale_date >= start_of_day,
        Sale.sale_date <= end_of_day
    ).all()
    
    total_sales = len(sales)
    total_revenue = sum(sale.total for sale in sales)
    
    # Obtener total de items vendidos
    total_items = db.query(
        func.sum(SaleDetail.quantity)
    ).join(Sale).filter(
        Sale.sale_date >= start_of_day,
        Sale.sale_date <= end_of_day
    ).scalar() or 0
    
    return {
        "date": date.date(),
        "total_sales": total_sales,
        "total_revenue": total_revenue,
        "total_items_sold": total_items,
        "average_sale_value": total_revenue / total_sales if total_sales > 0 else 0
    }