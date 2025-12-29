"""
TapQuote PDF Generator
Creates professional invoice PDFs using ReportLab
"""
import io
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT

from config import BUSINESS_NAME, BUSINESS_ADDRESS, BUSINESS_PHONE, BUSINESS_EMAIL, TAX_RATE


def generate_pdf(quote_data: dict) -> bytes:
    """
    Generate a professional PDF invoice from quote data.
    Returns PDF as bytes.
    """
    buffer = io.BytesIO()
    
    # Create document
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20*mm,
        leftMargin=20*mm,
        topMargin=20*mm,
        bottomMargin=20*mm
    )
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1e3a5f'),
        spaceAfter=10,
        alignment=TA_CENTER
    )
    
    header_style = ParagraphStyle(
        'HeaderStyle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#666666'),
        alignment=TA_CENTER
    )
    
    section_style = ParagraphStyle(
        'SectionStyle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1e3a5f'),
        spaceBefore=15,
        spaceAfter=10
    )
    
    normal_style = ParagraphStyle(
        'NormalStyle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#333333')
    )
    
    # Build content
    content = []
    
    # Header - Business Info
    content.append(Paragraph(BUSINESS_NAME, title_style))
    content.append(Paragraph(BUSINESS_ADDRESS, header_style))
    content.append(Paragraph(f"{BUSINESS_PHONE} | {BUSINESS_EMAIL}", header_style))
    content.append(Spacer(1, 15*mm))
    
    # Quote Title & Number
    quote_number = f"Q-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    quote_date = datetime.now().strftime("%d %B %Y")
    
    content.append(Paragraph("QUOTE", ParagraphStyle(
        'QuoteTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.HexColor('#1e3a5f'),
        alignment=TA_LEFT
    )))
    
    # Quote details table
    quote_info = [
        ["Quote Number:", quote_number],
        ["Date:", quote_date],
        ["Customer:", quote_data.get("customer_name", "Customer")],
    ]
    
    quote_info_table = Table(quote_info, colWidths=[80, 200])
    quote_info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#333333')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    content.append(quote_info_table)
    content.append(Spacer(1, 10*mm))
    
    # Job Summary
    content.append(Paragraph("Job Summary", section_style))
    content.append(Paragraph(quote_data.get("job_summary", "N/A"), normal_style))
    content.append(Spacer(1, 10*mm))
    
    # Line Items Table
    content.append(Paragraph("Quote Details", section_style))
    
    # Table header
    table_data = [
        ["Description", "Qty", "Unit Cost", "Labor", "Total"]
    ]
    
    # Add items
    items = quote_data.get("items", [])
    for item in items:
        description = item.get("description", "")
        if item.get("is_estimate", False):
            description += " *"
        
        table_data.append([
            Paragraph(description, ParagraphStyle('ItemDesc', fontSize=9)),
            str(item.get("qty", 1)),
            f"${item.get('unit_material_cost', 0):.2f}",
            f"${item.get('labor_cost', 0):.2f}",
            f"${item.get('line_total', 0):.2f}"
        ])
    
    # Create table
    col_widths = [250, 40, 70, 70, 70]
    items_table = Table(table_data, colWidths=col_widths)
    
    items_table.setStyle(TableStyle([
        # Header row
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a5f')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        
        # Data rows
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        
        # Alternating row colors
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
        
        # Grid
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#1e3a5f')),
    ]))
    
    content.append(items_table)
    content.append(Spacer(1, 5*mm))
    
    # Totals section
    subtotal = quote_data.get("subtotal", 0)
    tax = quote_data.get("tax", 0)
    grand_total = quote_data.get("grand_total", 0)
    
    totals_data = [
        ["", "", "", "Subtotal:", f"${subtotal:.2f}"],
        ["", "", "", f"GST ({TAX_RATE}%):", f"${tax:.2f}"],
        ["", "", "", "TOTAL:", f"${grand_total:.2f}"],
    ]
    
    totals_table = Table(totals_data, colWidths=col_widths)
    totals_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (3, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (3, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (3, -1), (-1, -1), 12),
        ('TEXTCOLOR', (3, -1), (-1, -1), colors.HexColor('#1e3a5f')),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LINEABOVE', (3, -1), (-1, -1), 2, colors.HexColor('#1e3a5f')),
    ]))
    
    content.append(totals_table)
    content.append(Spacer(1, 15*mm))
    
    # Footer notes
    notes_style = ParagraphStyle(
        'Notes',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.HexColor('#666666')
    )
    
    # Check if any estimates
    has_estimates = any(item.get("is_estimate", False) for item in items)
    if has_estimates:
        content.append(Paragraph("* Marked items are estimates only. Actual prices may vary.", notes_style))
        content.append(Spacer(1, 3*mm))
    
    content.append(Paragraph("Terms & Conditions:", ParagraphStyle(
        'TermsHeader',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#333333'),
        fontName='Helvetica-Bold'
    )))
    content.append(Paragraph(
        "• This quote is valid for 30 days from the date of issue.<br/>"
        "• Payment terms: 50% deposit, balance on completion.<br/>"
        "• All work is guaranteed for 12 months.<br/>"
        "• Prices include GST.",
        notes_style
    ))
    
    # Build PDF
    doc.build(content)
    
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    return pdf_bytes


def save_pdf_to_file(quote_data: dict, filepath: str) -> str:
    """
    Generate PDF and save to file.
    """
    pdf_bytes = generate_pdf(quote_data)
    
    with open(filepath, 'wb') as f:
        f.write(pdf_bytes)
    
    return filepath
