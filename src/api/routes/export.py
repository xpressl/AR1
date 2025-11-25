"""
Export API Routes

Data export endpoints for various formats (Excel, PDF, CSV)
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from datetime import date

from src.db.connection import get_db
from src.services.export.export_service import ExportService, ExportFormatter
from src.models import Customer, Invoice
from src.api.dependencies import get_current_user

router = APIRouter(prefix="/api/v1/export", tags=["export"])


@router.get("/customers")
async def export_customers(
    format: str = Query("xlsx", regex="^(xlsx|csv|pdf)$"),
    status: Optional[str] = None,
    salesperson_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Export customer list.

    Formats: xlsx, csv, pdf
    """
    # Query customers
    query = select(Customer)

    if status:
        query = query.where(Customer.status == status)

    if salesperson_id:
        query = query.where(Customer.salesperson_id == salesperson_id)

    result = await db.execute(query)
    customers = result.scalars().all()

    if not customers:
        raise HTTPException(status_code=404, detail="No customers found")

    # Format data for export
    export_data = ExportFormatter.format_customers_for_export(customers)

    # Create export service
    export_service = ExportService(db)

    # Export based on format
    if format == "xlsx":
        file_path = await export_service.export_to_excel(
            data=export_data,
            sheet_name="Customers",
            file_name="customer_list",
            user_id=current_user['id'],
            export_type="customers"
        )
    elif format == "csv":
        file_path = await export_service.export_to_csv(
            data=export_data,
            file_name="customer_list",
            user_id=current_user['id'],
            export_type="customers"
        )
    else:  # pdf
        raise HTTPException(status_code=400, detail="PDF export not yet implemented for customers")

    # Return file
    return FileResponse(
        path=file_path,
        filename=f"customer_list.{format}",
        media_type=f"application/{format}"
    )


@router.get("/invoices")
async def export_invoices(
    format: str = Query("xlsx", regex="^(xlsx|csv|pdf)$"),
    customer_id: Optional[str] = None,
    status: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Export invoice list.

    Formats: xlsx, csv, pdf
    """
    from sqlalchemy.orm import joinedload

    # Query invoices
    query = select(Invoice).options(joinedload(Invoice.customer))

    if customer_id:
        query = query.where(Invoice.customer_id == customer_id)

    if status:
        query = query.where(Invoice.status == status)

    if start_date:
        query = query.where(Invoice.invoice_date >= start_date)

    if end_date:
        query = query.where(Invoice.invoice_date <= end_date)

    result = await db.execute(query)
    invoices = result.scalars().all()

    if not invoices:
        raise HTTPException(status_code=404, detail="No invoices found")

    # Format data for export
    export_data = ExportFormatter.format_invoices_for_export(invoices)

    # Create export service
    export_service = ExportService(db)

    # Export based on format
    if format == "xlsx":
        file_path = await export_service.export_to_excel(
            data=export_data,
            sheet_name="Invoices",
            file_name="invoice_list",
            user_id=current_user['id'],
            export_type="invoices"
        )
    elif format == "csv":
        file_path = await export_service.export_to_csv(
            data=export_data,
            file_name="invoice_list",
            user_id=current_user['id'],
            export_type="invoices"
        )
    else:  # pdf
        raise HTTPException(status_code=400, detail="PDF export not yet implemented for invoices")

    # Return file
    return FileResponse(
        path=file_path,
        filename=f"invoice_list.{format}",
        media_type=f"application/{format}"
    )


@router.get("/aging-report")
async def export_aging_report(
    format: str = Query("xlsx", regex="^(xlsx|csv|pdf)$"),
    customer_id: Optional[str] = None,
    min_balance: Optional[float] = None,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Export detailed aging report.

    Formats: xlsx, csv, pdf
    """
    from src.services.reports.report_service import ReportService

    # Generate aging report
    report_service = ReportService(db)
    report_data = await report_service.get_aging_detail(customer_id, min_balance)

    if not report_data['invoices']:
        raise HTTPException(status_code=404, detail="No data found for aging report")

    # Format data for export
    export_data = ExportFormatter.format_aging_for_export(report_data)

    # Create export service
    export_service = ExportService(db)

    # Export based on format
    if format == "xlsx":
        file_path = await export_service.export_to_excel(
            data=export_data,
            sheet_name="Aging Report",
            file_name="aging_report",
            user_id=current_user['id'],
            export_type="aging_report"
        )
    elif format == "csv":
        file_path = await export_service.export_to_csv(
            data=export_data,
            file_name="aging_report",
            user_id=current_user['id'],
            export_type="aging_report"
        )
    else:  # pdf
        raise HTTPException(status_code=400, detail="PDF export not yet implemented for aging report")

    # Return file
    return FileResponse(
        path=file_path,
        filename=f"aging_report.{format}",
        media_type=f"application/{format}"
    )


@router.get("/history")
async def get_export_history(
    limit: int = Query(50, ge=1, le=200),
    export_type: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get export history for current user.
    """
    export_service = ExportService(db)
    history = await export_service.get_export_history(
        user_id=current_user['id'],
        export_type=export_type,
        limit=limit
    )

    return {
        'exports': history,
        'count': len(history)
    }


@router.post("/cleanup")
async def cleanup_old_exports(
    days: int = Query(7, ge=1, le=90, description="Delete exports older than this many days"),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Cleanup old export files.

    Admin only.
    """
    if current_user.get('role') != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")

    export_service = ExportService(db)
    result = await export_service.cleanup_old_exports(days)

    return {
        'message': f"Cleaned up exports older than {days} days",
        'files_deleted': result['files_deleted'],
        'cutoff_date': result['cutoff_date']
    }
