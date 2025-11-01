"""Utility functions for generating CSV and PDF reports"""

import csv
import io
from flask import make_response
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

def generate_csv(data, headers, filename):
    """
    Generate CSV file from data

    Args:
        data: List of dictionaries containing row data
        headers: List of column headers
        filename: Name of the CSV file

    Returns:
        Flask response with CSV file
    """
    si = io.StringIO()
    writer = csv.DictWriter(si, fieldnames=headers)

    writer.writeheader()
    writer.writerows(data)

    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = f"attachment; filename={filename}"
    output.headers["Content-type"] = "text/csv"

    return output

def generate_pdf(title, date_str, data, headers, filename):
    """
    Generate PDF file from data

    Args:
        title: Report title
        date_str: Date string to display
        data: List of lists containing row data
        headers: List of column headers
        filename: Name of the PDF file

    Returns:
        Flask response with PDF file
    """
    buffer = io.BytesIO()

    # Create PDF document
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    # Styles
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    normal_style = styles['Normal']

    # Add title
    title_para = Paragraph(title, title_style)
    elements.append(title_para)
    elements.append(Spacer(1, 0.2*inch))

    # Add date
    date_para = Paragraph(f"Report generated on: {date_str}", normal_style)
    elements.append(date_para)
    elements.append(Spacer(1, 0.3*inch))

    # Create table data (headers + data rows)
    table_data = [headers] + data

    # Create table
    table = Table(table_data)

    # Style the table
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
    ]))

    elements.append(table)

    # Build PDF
    doc.build(elements)

    # Get PDF data
    pdf_data = buffer.getvalue()
    buffer.close()

    # Create response
    response = make_response(pdf_data)
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    response.headers["Content-Type"] = "application/pdf"

    return response
