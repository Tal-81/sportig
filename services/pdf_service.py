from io import BytesIO
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    Table, TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT

# ============================================================
#  BRANDING CONSTANTS — edit these to customize your invoice
# ============================================================

COMPANY_NAME      = 'JD SPORTS'
COMPANY_TAGLINE   = 'Premium Sports & Lifestyle'
COMPANY_EMAIL     = 'support@jdsports-clone.com'
COMPANY_WEBSITE   = 'www.jdsports-clone.com'
COMPANY_PHONE     = '+46 8 123 456 78'
COMPANY_ADDRESS   = 'Drottninggatan 1, 111 51 Stockholm, Sweden'

# VAT / Org number shown in footer (leave empty to hide)
COMPANY_VAT_NO    = 'VAT No: SE556123456701'
COMPANY_ORG_NO    = 'Org No: 556123-4567'

# Primary brand color (hex) — used for header bar, table header, totals
PRIMARY_COLOR     = '#111111'

# Footer message
FOOTER_TEXT = (
    'Thank you for shopping with JD Sports!  |  '
    'Delivery: 3–5 business days  |  '
    'Returns accepted within 30 days'
)

# Show VAT line in totals? Set rate e.g. 0.25 for 25%, or None to hide
VAT_RATE = None   # e.g. 0.25

# ============================================================


def generate_invoice_pdf(order):
    """Generate a downloadable PDF invoice for a completed order."""
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
    )

    brand_color = colors.HexColor(PRIMARY_COLOR)
    light_gray  = colors.HexColor('#F8F8F8')
    mid_gray    = colors.HexColor('#DDDDDD')
    text_gray   = colors.HexColor('#666666')

    styles = getSampleStyleSheet()

    # ── Custom paragraph styles ──────────────────────────────
    title_style = ParagraphStyle(
        'CompanyTitle',
        parent=styles['Normal'],
        fontSize=26,
        fontName='Helvetica-Bold',
        textColor=brand_color,
        spaceAfter=2,
        leading=28,
    )
    tagline_style = ParagraphStyle(
        'Tagline',
        parent=styles['Normal'],
        fontSize=9,
        textColor=text_gray,
        spaceAfter=0,
    )
    section_label_style = ParagraphStyle(
        'SectionLabel',
        parent=styles['Normal'],
        fontSize=8,
        fontName='Helvetica-Bold',
        textColor=text_gray,
        spaceAfter=4,
        leading=10,
    )
    bold_style = ParagraphStyle(
        'Bold',
        parent=styles['Normal'],
        fontSize=9,
        fontName='Helvetica-Bold',
        textColor=colors.white,
        leading=12,
    )
    normal_style = ParagraphStyle(
        'Normal9',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#222222'),
        leading=13,
    )
    small_style = ParagraphStyle(
        'Small',
        parent=styles['Normal'],
        fontSize=8,
        textColor=text_gray,
        leading=12,
    )
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=text_gray,
        alignment=TA_CENTER,
        leading=12,
    )
    right_style = ParagraphStyle(
        'Right',
        parent=styles['Normal'],
        fontSize=9,
        alignment=TA_RIGHT,
        textColor=colors.HexColor('#222222'),
    )
    right_bold_style = ParagraphStyle(
        'RightBold',
        parent=styles['Normal'],
        fontSize=11,
        fontName='Helvetica-Bold',
        alignment=TA_RIGHT,
        textColor=brand_color,
    )

    story = []

    # ── HEADER ROW: Company info left, Invoice info right ────
    company_block = [
        Paragraph(COMPANY_NAME, title_style),
        Paragraph(COMPANY_TAGLINE, tagline_style),
        Spacer(1, 6),
        Paragraph(COMPANY_ADDRESS, small_style),
        Paragraph(f'{COMPANY_EMAIL}  |  {COMPANY_PHONE}', small_style),
    ]
    if COMPANY_VAT_NO:
        company_block.append(Paragraph(COMPANY_VAT_NO, small_style))

    payment_status_color = (
        colors.HexColor('#16a34a') if order.payment_status == 'completed'
        else colors.HexColor('#dc2626')
    )

    invoice_info_style = ParagraphStyle(
        'InvInfo', parent=styles['Normal'],
        fontSize=9, alignment=TA_RIGHT,
        textColor=colors.HexColor('#333333'), leading=14,
    )
    invoice_number_style = ParagraphStyle(
        'InvNum', parent=styles['Normal'],
        fontSize=20, fontName='Helvetica-Bold',
        alignment=TA_RIGHT, textColor=brand_color,
    )
    status_style = ParagraphStyle(
        'Status', parent=styles['Normal'],
        fontSize=9, fontName='Helvetica-Bold',
        alignment=TA_RIGHT, textColor=payment_status_color,
    )

    invoice_block = [
        Paragraph('INVOICE', invoice_number_style),
        Spacer(1, 4),
        Paragraph(f'<b>Order:</b>  #{order.order_number}', invoice_info_style),
        Paragraph(f'<b>Date:</b>  {order.created_at.strftime("%d %B %Y")}', invoice_info_style),
        Paragraph(f'<b>Order status:</b>  {order.get_status_display()}', invoice_info_style),
        Paragraph(f'Payment: {order.get_payment_status_display().upper()}', status_style),
    ]

    header_table = Table(
        [[company_block, invoice_block]],
        colWidths=['55%', '45%'],
    )
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN',  (1, 0), (1, 0),  'RIGHT'),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 4 * mm))

    # ── DIVIDER ──────────────────────────────────────────────
    story.append(HRFlowable(
        width='100%', thickness=2,
        color=brand_color, spaceAfter=4 * mm,
    ))

    # ── ADDRESSES: Bill To / Ship To ─────────────────────────
    def make_address_cell(title, lines):
        content = [Paragraph(title.upper(), section_label_style)]
        for line in lines:
            if line:
                content.append(Paragraph(line, normal_style))
        return content

    bill_lines = [
        f'{order.shipping_first_name} {order.shipping_last_name}',
        order.shipping_email,
        order.shipping_phone or '',
    ]
    ship_lines = [
        f'{order.shipping_street} {order.shipping_building}'.strip(),
        f'{order.shipping_postal_code} {order.shipping_city}'.strip(),
        order.shipping_country,
    ]

    addr_table = Table(
        [[make_address_cell('Bill To', bill_lines),
          make_address_cell('Ship To', ship_lines)]],
        colWidths=['50%', '50%'],
    )
    addr_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LINEAFTER', (0, 0), (0, -1), 0.5, mid_gray),
        ('LEFTPADDING', (1, 0), (1, -1), 16),
    ]))
    story.append(addr_table)
    story.append(Spacer(1, 5 * mm))

    # ── ITEMS TABLE ──────────────────────────────────────────
    # Columns: Product | Variant | Qty | Unit Price | Total
    # To add a column (e.g. SKU), add a header + value below
    col_headers = [
        Paragraph('<b>Product</b>', bold_style),
        Paragraph('<b>Variant / SKU</b>', bold_style),
        Paragraph('<b>Qty</b>', bold_style),
        Paragraph('<b>Unit Price</b>', bold_style),
        Paragraph('<b>Line Total</b>', bold_style),
    ]
    col_widths = ['34%', '22%', '8%', '18%', '18%']

    items_data = [col_headers]
    for item in order.items.all():
        variant_sku = item.variant_info or ''
        if item.product_sku:
            variant_sku += f'\n{item.product_sku}' if variant_sku else item.product_sku

        items_data.append([
            Paragraph(item.product_name, normal_style),
            Paragraph(variant_sku or '—', small_style),
            Paragraph(str(item.quantity), normal_style),
            Paragraph(f'{item.unit_price:,.2f} kr', normal_style),
            Paragraph(f'{item.line_total:,.2f} kr', right_style),
        ])

    items_table = Table(items_data, colWidths=col_widths)
    items_table.setStyle(TableStyle([
        # Alternating rows for data rows only (row 1 onward)
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [light_gray, colors.white]),
        # Header row — placed AFTER ROWBACKGROUNDS so it takes priority
        ('BACKGROUND', (0, 0), (-1, 0), brand_color),
        ('TEXTCOLOR',  (0, 0), (-1, 0), colors.white),
        ('FONTNAME',   (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE',   (0, 0), (-1, 0), 9),
        # Grid
        ('GRID',       (0, 0), (-1, -1), 0.4, mid_gray),
        # Padding
        ('TOPPADDING',    (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ('LEFTPADDING',   (0, 0), (-1, -1), 8),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 8),
        # Align qty and prices to the right
        ('ALIGN',  (2, 0), (-1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(items_table)
    story.append(Spacer(1, 4 * mm))

    # ── TOTALS ───────────────────────────────────────────────
    def totals_row(label, value, bold=False, color=None):
        lbl_style = ParagraphStyle(
            'TLbl', parent=styles['Normal'],
            fontSize=9 if not bold else 11,
            fontName='Helvetica-Bold' if bold else 'Helvetica',
            textColor=color or colors.HexColor('#444444'),
            alignment=TA_RIGHT,
        )
        val_style = ParagraphStyle(
            'TVal', parent=styles['Normal'],
            fontSize=9 if not bold else 13,
            fontName='Helvetica-Bold' if bold else 'Helvetica',
            textColor=color or (brand_color if bold else colors.HexColor('#222222')),
            alignment=TA_RIGHT,
        )
        return ['', Paragraph(label, lbl_style), Paragraph(value, val_style)]

    totals_data = [
        totals_row('Subtotal:', f'{order.subtotal:,.2f} kr'),
        totals_row('Shipping:', f'{order.shipping_fee:,.2f} kr'),
    ]

    if order.discount_amount and order.discount_amount > 0:
        discount_label = f'Discount ({order.coupon_code}):' if order.coupon_code else 'Discount:'
        totals_data.append(
            totals_row(discount_label, f'-{order.discount_amount:,.2f} kr',
                       color=colors.HexColor('#dc2626'))
        )

    # Optional VAT line
    if VAT_RATE:
        vat_amount = order.subtotal * VAT_RATE
        totals_data.append(
            totals_row(f'VAT ({int(VAT_RATE * 100)}%):', f'{vat_amount:,.2f} kr')
        )

    totals_data.append(
        totals_row('TOTAL:', f'{order.total:,.2f} kr', bold=True)
    )

    totals_table = Table(totals_data, colWidths=['40%', '35%', '25%'])
    totals_table.setStyle(TableStyle([
        ('ALIGN',  (0, 0), (-1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING',    (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LINEABOVE', (1, -1), (-1, -1), 1, brand_color),
        ('TOPPADDING', (0, -1), (-1, -1), 8),
    ]))
    story.append(totals_table)

    # ── NOTES ────────────────────────────────────────────────
    if order.notes:
        story.append(Spacer(1, 4 * mm))
        story.append(HRFlowable(width='100%', thickness=0.5, color=mid_gray))
        story.append(Spacer(1, 2 * mm))
        story.append(Paragraph('<b>Order Notes:</b>', normal_style))
        story.append(Paragraph(order.notes, small_style))

    # ── FOOTER ───────────────────────────────────────────────
    story.append(Spacer(1, 6 * mm))
    story.append(HRFlowable(
        width='100%', thickness=0.5,
        color=mid_gray, spaceAfter=3 * mm,
    ))
    story.append(Paragraph(FOOTER_TEXT, footer_style))
    if COMPANY_ORG_NO or COMPANY_VAT_NO:
        org_line = '  |  '.join(filter(None, [COMPANY_ORG_NO, COMPANY_VAT_NO]))
        story.append(Paragraph(org_line, footer_style))

    doc.build(story)
    buffer.seek(0)

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = (
        f'attachment; filename="invoice-{order.order_number}.pdf"'
    )
    return response
