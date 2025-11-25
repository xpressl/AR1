"""
Export Service

Handles data export to various formats (Excel, PDF, CSV)
"""
import os
import csv
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path
import io

try:
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False

from sqlalchemy.ext.asyncio import AsyncSession
from src.models import ExportHistory


class ExportService:
    """Service for exporting data to various formats."""

    def __init__(self, db: AsyncSession, export_dir: str = "/tmp/exports"):
        self.db = db
        self.export_dir = Path(export_dir)
        self.export_dir.mkdir(parents=True, exist_ok=True)

    async def export_to_excel(
        self,
        data: List[Dict[str, Any]],
        sheet_name: str,
        file_name: str,
        user_id: str,
        export_type: str
    ) -> str:
        """
        Export data to Excel (.xlsx) format.

        Args:
            data: List of dictionaries to export
            sheet_name: Name of the Excel sheet
            file_name: Base file name (without extension)
            user_id: User ID performing export
            export_type: Type of export (for tracking)

        Returns:
            Path to generated file
        """
        if not OPENPYXL_AVAILABLE:
            raise ImportError("openpyxl is not installed. Run: pip install openpyxl")

        if not data:
            raise ValueError("No data to export")

        # Create workbook
        wb = Workbook()
        ws = wb.active
        ws.title = sheet_name[:31]  # Excel sheet name limit

        # Get headers from first row
        headers = list(data[0].keys())

        # Style definitions
        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
        header_alignment = Alignment(horizontal="center", vertical="center")
        border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )

        # Write headers
        for col_idx, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_idx)
            cell.value = header.replace('_', ' ').title()
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = header_alignment
            cell.border = border

        # Write data
        for row_idx, row_data in enumerate(data, 2):
            for col_idx, header in enumerate(headers, 1):
                cell = ws.cell(row=row_idx, column=col_idx)
                value = row_data.get(header)

                # Format value
                if isinstance(value, (int, float)):
                    cell.value = value
                    cell.number_format = '#,##0.00' if isinstance(value, float) else '#,##0'
                elif isinstance(value, datetime):
                    cell.value = value
                    cell.number_format = 'yyyy-mm-dd hh:mm:ss'
                else:
                    cell.value = str(value) if value is not None else ''

                cell.border = border

        # Auto-size columns
        for col_idx in range(1, len(headers) + 1):
            col_letter = get_column_letter(col_idx)
            max_length = 0
            for row in ws[col_letter]:
                try:
                    if len(str(row.value)) > max_length:
                        max_length = len(str(row.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)  # Max width 50
            ws.column_dimensions[col_letter].width = adjusted_width

        # Generate file path
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        file_path = self.export_dir / f"{file_name}_{timestamp}.xlsx"

        # Save workbook
        wb.save(str(file_path))

        # Record export in history
        await self._record_export(
            export_type=export_type,
            export_name=file_name,
            file_format="xlsx",
            file_path=str(file_path),
            file_size=os.path.getsize(file_path),
            record_count=len(data),
            user_id=user_id
        )

        return str(file_path)

    async def export_to_csv(
        self,
        data: List[Dict[str, Any]],
        file_name: str,
        user_id: str,
        export_type: str
    ) -> str:
        """
        Export data to CSV format.

        Args:
            data: List of dictionaries to export
            file_name: Base file name (without extension)
            user_id: User ID performing export
            export_type: Type of export (for tracking)

        Returns:
            Path to generated file
        """
        if not data:
            raise ValueError("No data to export")

        # Generate file path
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        file_path = self.export_dir / f"{file_name}_{timestamp}.csv"

        # Get headers from first row
        headers = list(data[0].keys())

        # Write CSV
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()
            writer.writerows(data)

        # Record export in history
        await self._record_export(
            export_type=export_type,
            export_name=file_name,
            file_format="csv",
            file_path=str(file_path),
            file_size=os.path.getsize(file_path),
            record_count=len(data),
            user_id=user_id
        )

        return str(file_path)

    async def export_to_pdf(
        self,
        html_content: str,
        file_name: str,
        user_id: str,
        export_type: str
    ) -> str:
        """
        Export HTML content to PDF format.

        Args:
            html_content: HTML string to convert to PDF
            file_name: Base file name (without extension)
            user_id: User ID performing export
            export_type: Type of export (for tracking)

        Returns:
            Path to generated file

        Note: Requires weasyprint or reportlab
        """
        try:
            from weasyprint import HTML
            WEASYPRINT_AVAILABLE = True
        except ImportError:
            WEASYPRINT_AVAILABLE = False

        if not WEASYPRINT_AVAILABLE:
            raise ImportError("weasyprint is not installed. Run: pip install weasyprint")

        # Generate file path
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        file_path = self.export_dir / f"{file_name}_{timestamp}.pdf"

        # Convert HTML to PDF
        HTML(string=html_content).write_pdf(str(file_path))

        # Record export in history
        await self._record_export(
            export_type=export_type,
            export_name=file_name,
            file_format="pdf",
            file_path=str(file_path),
            file_size=os.path.getsize(file_path),
            record_count=None,  # N/A for PDF
            user_id=user_id
        )

        return str(file_path)

    async def get_export_history(
        self,
        user_id: Optional[str] = None,
        export_type: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get export history with optional filters."""
        from sqlalchemy import select, desc

        query = select(ExportHistory).order_by(desc(ExportHistory.exported_at)).limit(limit)

        if user_id:
            query = query.where(ExportHistory.exported_by == user_id)

        if export_type:
            query = query.where(ExportHistory.export_type == export_type)

        result = await self.db.execute(query)
        exports = result.scalars().all()

        return [export.to_dict() for export in exports]

    async def cleanup_old_exports(self, days: int = 7):
        """
        Delete export files older than specified days.

        Args:
            days: Delete files older than this many days
        """
        from sqlalchemy import select, delete

        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # Find old exports
        query = select(ExportHistory).where(
            ExportHistory.exported_at < cutoff_date
        )

        result = await self.db.execute(query)
        old_exports = result.scalars().all()

        deleted_count = 0
        for export in old_exports:
            # Delete file if it exists
            if export.file_path and os.path.exists(export.file_path):
                try:
                    os.remove(export.file_path)
                    deleted_count += 1
                except Exception as e:
                    print(f"Error deleting {export.file_path}: {e}")

        # Delete database records
        delete_query = delete(ExportHistory).where(
            ExportHistory.exported_at < cutoff_date
        )
        await self.db.execute(delete_query)
        await self.db.commit()

        return {
            'files_deleted': deleted_count,
            'cutoff_date': cutoff_date.isoformat()
        }

    async def _record_export(
        self,
        export_type: str,
        export_name: str,
        file_format: str,
        file_path: str,
        file_size: int,
        record_count: Optional[int],
        user_id: str,
        filters: Optional[Dict] = None
    ):
        """Record export in history."""
        export_history = ExportHistory(
            export_type=export_type,
            export_name=export_name,
            file_format=file_format,
            file_path=file_path,
            file_size=file_size,
            record_count=record_count,
            filters=filters,
            exported_by=user_id,
            status="completed",
            expires_at=datetime.utcnow() + timedelta(days=7)  # Auto-expire in 7 days
        )

        self.db.add(export_history)
        await self.db.commit()


class ExportFormatter:
    """Helper class for formatting data for export."""

    @staticmethod
    def format_customers_for_export(customers: List[Any]) -> List[Dict[str, Any]]:
        """Format customer data for export."""
        return [
            {
                'Customer ID': str(customer.id),
                'Customer Name': customer.name,
                'Status': customer.status,
                'Credit Limit': float(customer.credit_limit or 0),
                'Current Balance': float(customer.balance or 0),
                'Contact Email': customer.contact_email,
                'Contact Phone': customer.contact_phone,
                'Salesperson': customer.salesperson_id or ''
            }
            for customer in customers
        ]

    @staticmethod
    def format_invoices_for_export(invoices: List[Any]) -> List[Dict[str, Any]]:
        """Format invoice data for export."""
        return [
            {
                'Invoice Number': invoice.invoice_number,
                'Customer Name': invoice.customer.name if hasattr(invoice, 'customer') else '',
                'Invoice Date': invoice.invoice_date.strftime('%Y-%m-%d') if invoice.invoice_date else '',
                'Due Date': invoice.due_date.strftime('%Y-%m-%d') if invoice.due_date else '',
                'Total Amount': float(invoice.total_amount),
                'Open Balance': float(invoice.open_balance),
                'Days Overdue': invoice.days_overdue or 0,
                'Status': invoice.status
            }
            for invoice in invoices
        ]

    @staticmethod
    def format_aging_for_export(data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Format aging report data for export."""
        return [
            {
                'Customer Name': invoice['customer_name'],
                'Invoice Number': invoice['invoice_number'],
                'Invoice Date': invoice['invoice_date'],
                'Due Date': invoice['due_date'],
                'Total Amount': invoice['total_amount'],
                'Open Balance': invoice['open_balance'],
                'Days Overdue': invoice['days_overdue'],
                'Aging Bucket': invoice['aging_bucket']
            }
            for invoice in data.get('invoices', [])
        ]
