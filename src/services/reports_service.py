"""
Servicio para generación de reportes de ventas
"""

from datetime import date, datetime, timedelta
from typing import List, Tuple

from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from models_db import (
    LotDetail,
    Person,
    Product,
    ProductPresentation,
    Sale,
    SaleDetail,
)
from schemas.reports import ReportPeriod, TopCustomerItem, TopProductItem


def get_date_range(period: ReportPeriod, reference_date: date) -> Tuple[datetime, datetime]:
    """
    Calcular el rango de fechas según el periodo y fecha de referencia
    
    Args:
        period: Periodo del reporte (daily, weekly, monthly)
        reference_date: Fecha de referencia
        
    Returns:
        Tupla con (fecha_inicio, fecha_fin)
    """
    if period == ReportPeriod.DAILY:
        # Día completo
        start_date = datetime.combine(reference_date, datetime.min.time())
        end_date = datetime.combine(reference_date, datetime.max.time())
        
    elif period == ReportPeriod.WEEKLY:
        # Semana completa (lunes a domingo)
        # Calcular inicio de semana (lunes)
        days_since_monday = reference_date.weekday()
        week_start = reference_date - timedelta(days=days_since_monday)
        week_end = week_start + timedelta(days=6)
        
        start_date = datetime.combine(week_start, datetime.min.time())
        end_date = datetime.combine(week_end, datetime.max.time())
        
    elif period == ReportPeriod.MONTHLY:
        # Mes completo
        # Primer día del mes
        month_start = reference_date.replace(day=1)
        
        # Último día del mes
        if reference_date.month == 12:
            next_month = month_start.replace(year=reference_date.year + 1, month=1)
        else:
            next_month = month_start.replace(month=reference_date.month + 1)
        month_end = next_month - timedelta(days=1)
        
        start_date = datetime.combine(month_start, datetime.min.time())
        end_date = datetime.combine(month_end, datetime.max.time())
    else:
        raise ValueError(f"Periodo no válido: {period}")
        
    return start_date, end_date


def get_sales_metrics(
    db: Session, start_date: datetime, end_date: datetime
) -> dict:
    """
    Obtener métricas generales de ventas para un periodo
    
    Returns:
        dict con total_sales, total_revenue, total_cost, total_items_sold
    """
    # Ventas en el periodo
    sales_query = db.query(Sale).filter(
        and_(
            Sale.sale_date >= start_date,
            Sale.sale_date <= end_date,
            Sale.status != "cancelled"
        )
    )
    
    sales = sales_query.all()
    total_sales = len(sales)
    total_revenue = sum(sale.total for sale in sales)
    
    # Calcular costo total (sumando el costo de cada item vendido)
    cost_query = (
        db.query(func.sum(SaleDetail.quantity * LotDetail.unit_cost).label("total_cost"))
        .join(Sale, SaleDetail.sale_id == Sale.id)
        .outerjoin(LotDetail, SaleDetail.lot_detail_id == LotDetail.id)
        .filter(
            and_(
                Sale.sale_date >= start_date,
                Sale.sale_date <= end_date,
                Sale.status != "cancelled"
            )
        )
    )
    
    total_cost = cost_query.scalar() or 0.0
    
    # Total de items vendidos
    items_query = (
        db.query(func.sum(SaleDetail.quantity).label("total_items"))
        .join(Sale, SaleDetail.sale_id == Sale.id)
        .filter(
            and_(
                Sale.sale_date >= start_date,
                Sale.sale_date <= end_date,
                Sale.status != "cancelled"
            )
        )
    )
    
    total_items_sold = items_query.scalar() or 0
    
    return {
        "total_sales": total_sales,
        "total_revenue": float(total_revenue),
        "total_cost": float(total_cost),
        "total_items_sold": int(total_items_sold),
    }


def get_top_products(
    db: Session, start_date: datetime, end_date: datetime, limit: int = 10
) -> List[TopProductItem]:
    """
    Obtener los productos más vendidos en un periodo
    """
    query = (
        db.query(
            SaleDetail.presentation_id,
            Product.name.label("product_name"),
            ProductPresentation.presentation_name,
            func.sum(SaleDetail.quantity).label("total_quantity"),
            func.sum(SaleDetail.line_total).label("total_revenue"),
            func.avg(SaleDetail.unit_price).label("average_price"),
        )
        .join(Sale, SaleDetail.sale_id == Sale.id)
        .join(ProductPresentation, SaleDetail.presentation_id == ProductPresentation.id)
        .join(Product, ProductPresentation.product_id == Product.id)
        .filter(
            and_(
                Sale.sale_date >= start_date,
                Sale.sale_date <= end_date,
                Sale.status != "cancelled"
            )
        )
        .group_by(
            SaleDetail.presentation_id,
            Product.name,
            ProductPresentation.presentation_name,
        )
        .order_by(func.sum(SaleDetail.quantity).desc())
        .limit(limit)
    )
    
    results = query.all()
    
    top_products = []
    for result in results:
        top_products.append(
            TopProductItem(
                presentation_id=result.presentation_id,
                product_name=result.product_name,
                presentation_name=result.presentation_name,
                total_quantity=int(result.total_quantity),
                total_revenue=float(result.total_revenue),
                average_price=float(result.average_price),
            )
        )
    
    return top_products


def get_top_customers(
    db: Session, start_date: datetime, end_date: datetime, limit: int = 10
) -> List[TopCustomerItem]:
    """
    Obtener los mejores clientes en un periodo
    """
    query = (
        db.query(
            Sale.customer_id,
            Person.name,
            Person.last_name,
            Person.document_type,
            Person.document_number,
            func.count(Sale.id).label("total_purchases"),
            func.sum(Sale.total).label("total_spent"),
            func.avg(Sale.total).label("average_purchase"),
        )
        .join(Person, Sale.customer_id == Person.id)
        .filter(
            and_(
                Sale.sale_date >= start_date,
                Sale.sale_date <= end_date,
                Sale.status != "cancelled"
            )
        )
        .group_by(
            Sale.customer_id,
            Person.name,
            Person.last_name,
            Person.document_type,
            Person.document_number,
        )
        .order_by(func.sum(Sale.total).desc())
        .limit(limit)
    )
    
    results = query.all()
    
    top_customers = []
    for result in results:
        customer_name = f"{result.name} {result.last_name}"
        customer_document = f"{result.document_type}: {result.document_number}"
        
        top_customers.append(
            TopCustomerItem(
                customer_id=result.customer_id,
                customer_name=customer_name,
                customer_document=customer_document,
                total_purchases=int(result.total_purchases),
                total_spent=float(result.total_spent),
                average_purchase=float(result.average_purchase),
            )
        )
    
    return top_customers


def generate_sales_report(
    db: Session, period: ReportPeriod, reference_date: date, top_limit: int = 10
) -> dict:
    """
    Generar reporte completo de ventas
    
    Args:
        db: Sesión de base de datos
        period: Periodo del reporte (daily, weekly, monthly)
        reference_date: Fecha de referencia
        top_limit: Límite de items para top productos y clientes
        
    Returns:
        dict con toda la información del reporte
    """
    # Calcular rango de fechas
    start_date, end_date = get_date_range(period, reference_date)
    
    # Obtener métricas generales
    metrics = get_sales_metrics(db, start_date, end_date)
    
    # Obtener productos más vendidos
    top_products = get_top_products(db, start_date, end_date, top_limit)
    
    # Obtener mejores clientes
    top_customers = get_top_customers(db, start_date, end_date, top_limit)
    
    # Calcular ganancia estimada y margen
    estimated_profit = metrics["total_revenue"] - metrics["total_cost"]
    profit_margin = (
        (estimated_profit / metrics["total_revenue"] * 100)
        if metrics["total_revenue"] > 0
        else 0.0
    )
    
    # Calcular valor promedio por venta
    average_sale_value = (
        metrics["total_revenue"] / metrics["total_sales"]
        if metrics["total_sales"] > 0
        else 0.0
    )
    
    return {
        "period": period,
        "start_date": start_date,
        "end_date": end_date,
        "total_sales": metrics["total_sales"],
        "total_revenue": metrics["total_revenue"],
        "estimated_profit": estimated_profit,
        "profit_margin": round(profit_margin, 2),
        "top_products": top_products,
        "top_customers": top_customers,
        "average_sale_value": round(average_sale_value, 2),
        "total_items_sold": metrics["total_items_sold"],
    }
