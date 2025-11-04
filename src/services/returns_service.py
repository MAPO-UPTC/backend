"""
Servicio para manejo de devoluciones
"""

from datetime import datetime
from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from models_db import (
    BulkConversion,
    LotDetail,
    Person,
    Product,
    ProductPresentation,
    Return,
    ReturnDetail,
    Sale,
    SaleDetail,
    User,
)
from schemas.returns import ReturnCreate, ReturnUpdateStatus


def generate_return_code() -> str:
    """
    Generar código único para la devolución
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"DEV-{timestamp}"


def create_return(db: Session, return_data: ReturnCreate, user_id: str) -> Return:
    """
    Crear una nueva devolución.

    Args:
        db: Sesión de base de datos
        return_data: Datos de la devolución
        user_id: ID del usuario que procesa la devolución

    Returns:
        Return: Objeto de devolución creado

    Raises:
        ValueError: Si hay errores de validación
    """
    try:
        # Verificar que la venta existe
        sale = db.query(Sale).filter(Sale.id == return_data.sale_id).first()
        if not sale:
            raise ValueError(f"Venta con ID {return_data.sale_id} no encontrada")

        # Verificar que la venta no esté cancelada
        if sale.status == "cancelled":
            raise ValueError("No se puede crear una devolución de una venta cancelada")

        # Verificar que el usuario existe
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"Usuario con ID {user_id} no encontrado")

        # Validar cada item de la devolución
        total_refund = 0.0
        validated_items = []

        for item in return_data.items:
            # Verificar que el sale_detail existe y pertenece a la venta
            sale_detail = (
                db.query(SaleDetail)
                .filter(SaleDetail.id == item.sale_detail_id)
                .first()
            )

            if not sale_detail:
                raise ValueError(
                    f"Detalle de venta {item.sale_detail_id} no encontrado"
                )

            if sale_detail.sale_id != return_data.sale_id:
                raise ValueError(
                    f"El detalle de venta {item.sale_detail_id} no pertenece a la venta {return_data.sale_id}"
                )

            # Calcular cantidad ya devuelta de este sale_detail
            already_returned = (
                db.query(func.sum(ReturnDetail.quantity_returned))
                .join(Return)
                .filter(
                    ReturnDetail.sale_detail_id == item.sale_detail_id,
                    Return.status != "rejected",  # No contar rechazadas
                )
                .scalar()
                or 0
            )

            # Verificar que no se devuelva más de lo comprado
            available_to_return = sale_detail.quantity - already_returned
            if item.quantity_returned > available_to_return:
                raise ValueError(
                    f"No se puede devolver {item.quantity_returned} unidades. "
                    f"Cantidad comprada: {sale_detail.quantity}, "
                    f"Ya devuelta: {already_returned}, "
                    f"Disponible para devolver: {available_to_return}"
                )

            # Calcular el monto de reembolso
            refund_amount = item.quantity_returned * sale_detail.unit_price
            total_refund += refund_amount

            validated_items.append(
                {
                    "sale_detail": sale_detail,
                    "quantity_returned": item.quantity_returned,
                    "condition": item.condition,
                    "refund_amount": refund_amount,
                }
            )

        # Crear la devolución principal
        db_return = Return(
            return_code=generate_return_code(),
            return_date=datetime.now(),
            sale_id=return_data.sale_id,
            customer_id=sale.customer_id,
            processed_by_user_id=user_id,
            reason=return_data.reason,
            total_refund=total_refund,
            status="pending",
            notes=return_data.notes,
        )
        db.add(db_return)
        db.flush()  # Para obtener el ID

        # Crear los detalles de la devolución
        for item_data in validated_items:
            sale_detail = item_data["sale_detail"]

            db_return_detail = ReturnDetail(
                return_id=db_return.id,
                sale_detail_id=sale_detail.id,
                presentation_id=sale_detail.presentation_id,
                quantity_returned=item_data["quantity_returned"],
                unit_price=sale_detail.unit_price,
                refund_amount=item_data["refund_amount"],
                condition=item_data["condition"],
                restocked=False,
                lot_detail_id=sale_detail.lot_detail_id,
                bulk_conversion_id=sale_detail.bulk_conversion_id,
            )
            db.add(db_return_detail)

        db.commit()
        db.refresh(db_return)
        return db_return

    except ValueError:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise ValueError(f"Error creando devolución: {str(e)}")


def get_return_by_id(db: Session, return_id: str) -> Optional[Return]:
    """
    Obtener una devolución por su ID con sus detalles
    """
    return db.query(Return).filter(Return.id == return_id).first()


def get_return_by_code(db: Session, return_code: str) -> Optional[Return]:
    """
    Obtener una devolución por su código
    """
    return db.query(Return).filter(Return.return_code == return_code).first()


def get_returns(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> List[Return]:
    """
    Obtener lista de devoluciones con paginación y filtros

    Args:
        db: Sesión de base de datos
        skip: Registros a omitir
        limit: Límite de resultados
        status: Filtrar por estado (opcional)
        start_date: Fecha de inicio (opcional)
        end_date: Fecha de fin (opcional)

    Returns:
        Lista de devoluciones
    """
    query = db.query(Return)

    # Aplicar filtros
    if status:
        query = query.filter(Return.status == status)
    if start_date:
        query = query.filter(Return.return_date >= start_date)
    if end_date:
        query = query.filter(Return.return_date <= end_date)

    # Ordenar de más reciente a más antigua
    return query.order_by(Return.return_date.desc()).offset(skip).limit(limit).all()


def get_returns_by_sale(db: Session, sale_id: str) -> List[Return]:
    """
    Obtener todas las devoluciones de una venta específica
    """
    return (
        db.query(Return)
        .filter(Return.sale_id == sale_id)
        .order_by(Return.return_date.desc())
        .all()
    )


def get_returns_by_customer(
    db: Session, customer_id: str, skip: int = 0, limit: int = 100
) -> List[Return]:
    """
    Obtener devoluciones de un cliente específico
    """
    return (
        db.query(Return)
        .filter(Return.customer_id == customer_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def update_return_status(
    db: Session, return_id: str, status_data: ReturnUpdateStatus, user_id: str
) -> Return:
    """
    Actualizar el estado de una devolución

    Args:
        db: Sesión de base de datos
        return_id: ID de la devolución
        status_data: Nuevo estado y notas
        user_id: ID del usuario que hace el cambio

    Returns:
        Return: Devolución actualizada

    Raises:
        ValueError: Si hay errores de validación
    """
    try:
        return_record = get_return_by_id(db, return_id)
        if not return_record:
            raise ValueError(f"Devolución con ID {return_id} no encontrada")

        # Validar transiciones de estado
        current_status = return_record.status
        new_status = status_data.status

        # Reglas de transición de estado
        valid_transitions = {
            "pending": ["approved", "rejected"],
            "approved": ["completed", "rejected"],
            "rejected": [],  # No se puede cambiar desde rechazado
            "completed": [],  # No se puede cambiar desde completado
        }

        if new_status not in valid_transitions.get(current_status, []):
            raise ValueError(
                f"No se puede cambiar de estado '{current_status}' a '{new_status}'"
            )

        # Actualizar estado
        return_record.status = new_status
        if status_data.notes:
            return_record.notes = (
                f"{return_record.notes or ''}\n[{datetime.now()}] {status_data.notes}"
            )

        db.commit()
        db.refresh(return_record)
        return return_record

    except ValueError:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise ValueError(f"Error actualizando estado: {str(e)}")


def process_return_to_inventory(db: Session, return_id: str) -> Return:
    """
    Procesar una devolución aprobada y devolver el stock al inventario.
    Solo se reintegran productos en condición 'good'.

    Args:
        db: Sesión de base de datos
        return_id: ID de la devolución

    Returns:
        Return: Devolución procesada

    Raises:
        ValueError: Si hay errores de validación
    """
    try:
        return_record = get_return_by_id(db, return_id)
        if not return_record:
            raise ValueError(f"Devolución con ID {return_id} no encontrada")

        # Verificar que esté aprobada
        if return_record.status != "approved":
            raise ValueError(
                f"La devolución debe estar aprobada para procesarla. Estado actual: {return_record.status}"
            )

        # Procesar cada item
        for return_detail in return_record.items:
            # Solo reintegrar productos en buen estado
            if return_detail.condition == "good":
                # Si vino de un lote empaquetado
                if return_detail.lot_detail_id:
                    lot_detail = (
                        db.query(LotDetail)
                        .filter(LotDetail.id == return_detail.lot_detail_id)
                        .first()
                    )
                    if lot_detail:
                        lot_detail.quantity_available += return_detail.quantity_returned
                        return_detail.restocked = True

                # Si vino de stock a granel
                elif return_detail.bulk_conversion_id:
                    bulk_conv = (
                        db.query(BulkConversion)
                        .filter(BulkConversion.id == return_detail.bulk_conversion_id)
                        .first()
                    )
                    if bulk_conv:
                        bulk_conv.remaining_bulk += return_detail.quantity_returned
                        # Reactivar si estaba completado
                        if bulk_conv.status == "COMPLETED":
                            bulk_conv.status = "ACTIVE"
                        return_detail.restocked = True
            else:
                # Productos dañados o vencidos no se reintegran
                return_detail.restocked = False

        # Cambiar estado a completado
        return_record.status = "completed"
        return_record.notes = f"{return_record.notes or ''}\n[{datetime.now()}] Devolución procesada y stock reintegrado"

        db.commit()
        db.refresh(return_record)
        return return_record

    except ValueError:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise ValueError(f"Error procesando devolución: {str(e)}")


def get_return_details_by_return(db: Session, return_id: str) -> List[ReturnDetail]:
    """
    Obtener todos los detalles de una devolución específica
    """
    return db.query(ReturnDetail).filter(ReturnDetail.return_id == return_id).all()


def get_return_full_details(db: Session, return_id: str) -> dict:
    """
    Obtener detalles completos de una devolución incluyendo:
    - Información de la devolución
    - Información del cliente
    - Información del usuario que procesó
    - Información de la venta original
    - Detalles de items con nombre del producto

    Returns:
        dict con toda la información o None si no existe
    """
    return_record = get_return_by_id(db, return_id)
    if not return_record:
        return None

    # Obtener información del cliente
    customer = db.query(Person).filter(Person.id == return_record.customer_id).first()

    # Obtener información del usuario que procesó
    processor_user = (
        db.query(User).filter(User.id == return_record.processed_by_user_id).first()
    )
    processor_person = (
        db.query(Person).filter(Person.id == processor_user.person_id).first()
        if processor_user
        else None
    )

    # Obtener información de la venta
    sale = db.query(Sale).filter(Sale.id == return_record.sale_id).first()

    # Obtener detalles con información de productos
    return_details = (
        db.query(
            ReturnDetail,
            Product.name.label("product_name"),
            ProductPresentation.presentation_name,
        )
        .join(
            ProductPresentation, ReturnDetail.presentation_id == ProductPresentation.id
        )
        .join(Product, ProductPresentation.product_id == Product.id)
        .filter(ReturnDetail.return_id == return_id)
        .all()
    )

    # Construir items extendidos
    items_extended = []
    for detail, product_name, presentation_name in return_details:
        items_extended.append(
            {
                "id": str(detail.id),
                "return_id": str(detail.return_id),
                "sale_detail_id": str(detail.sale_detail_id),
                "presentation_id": str(detail.presentation_id),
                "quantity_returned": detail.quantity_returned,
                "unit_price": float(detail.unit_price),
                "refund_amount": float(detail.refund_amount),
                "condition": detail.condition,
                "restocked": detail.restocked,
                "product_name": product_name,
                "presentation_name": presentation_name,
            }
        )

    # Construir respuesta completa
    return {
        "id": str(return_record.id),
        "return_code": return_record.return_code,
        "return_date": return_record.return_date,
        "sale_id": str(return_record.sale_id),
        "sale_code": sale.sale_code if sale else None,
        "customer_id": str(return_record.customer_id),
        "customer_name": (
            f"{customer.name} {customer.last_name}"
            if customer
            else "Cliente desconocido"
        ),
        "customer_document": (
            f"{customer.document_type}: {customer.document_number}"
            if customer
            else "N/A"
        ),
        "processed_by_user_id": str(return_record.processed_by_user_id),
        "processed_by_name": (
            f"{processor_person.name} {processor_person.last_name}"
            if processor_person
            else "Usuario desconocido"
        ),
        "reason": return_record.reason,
        "total_refund": float(return_record.total_refund),
        "status": return_record.status,
        "notes": return_record.notes,
        "created_at": return_record.created_at,
        "updated_at": return_record.updated_at,
        "items": items_extended,
    }


def get_return_statistics(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> dict:
    """
    Obtener estadísticas de devoluciones

    Args:
        db: Sesión de base de datos
        start_date: Fecha de inicio (opcional)
        end_date: Fecha de fin (opcional)

    Returns:
        dict con estadísticas
    """
    query = db.query(Return)

    # Aplicar filtros de fecha
    if start_date:
        query = query.filter(Return.return_date >= start_date)
    if end_date:
        query = query.filter(Return.return_date <= end_date)

    returns = query.all()

    # Calcular estadísticas por estado
    returns_by_status = {}
    for status in ["pending", "approved", "rejected", "completed"]:
        count = len([r for r in returns if r.status == status])
        returns_by_status[status] = count

    # Calcular estadísticas por condición
    all_details = []
    for ret in returns:
        all_details.extend(ret.items)

    returns_by_condition = {}
    for condition in ["good", "damaged", "expired"]:
        count = len([d for d in all_details if d.condition == condition])
        returns_by_condition[condition] = count

    # Calcular total reembolsado
    total_refunded = sum(r.total_refund for r in returns if r.status == "completed")

    # Productos más devueltos
    product_returns = {}
    for detail in all_details:
        presentation = (
            db.query(ProductPresentation)
            .filter(ProductPresentation.id == detail.presentation_id)
            .first()
        )
        if presentation:
            product = (
                db.query(Product).filter(Product.id == presentation.product_id).first()
            )
            if product:
                key = f"{product.name} - {presentation.presentation_name}"
                if key not in product_returns:
                    product_returns[key] = {
                        "product_name": key,
                        "total_returned": 0,
                        "total_refund": 0.0,
                    }
                product_returns[key]["total_returned"] += detail.quantity_returned
                product_returns[key]["total_refund"] += float(detail.refund_amount)

    # Ordenar productos más devueltos
    most_returned = sorted(
        product_returns.values(), key=lambda x: x["total_returned"], reverse=True
    )[:10]

    return {
        "total_returns": len(returns),
        "total_refunded": float(total_refunded),
        "returns_by_status": returns_by_status,
        "returns_by_condition": returns_by_condition,
        "most_returned_products": most_returned,
    }
