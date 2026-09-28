import io
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from datetime import datetime

def generate_pdf_report(summary_stats, category_stats, rating_stats, recent_feedbacks):
    """
    Generates a professional PDF report using ReportLab.
    Returns a BytesIO stream containing the generated PDF document.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=22,
        leading=26,
        textColor=colors.HexColor('#1E293B'),
        fontName='Helvetica-Bold',
        spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#64748B'),
        spaceAfter=15
    )
    section_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#0F172A'),
        fontName='Helvetica-Bold',
        spaceBefore=12,
        spaceAfter=6
    )
    cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontSize=9,
        leading=11,
        textColor=colors.HexColor('#334155')
    )
    cell_bold_style = ParagraphStyle(
        'TableCellBold',
        parent=cell_style,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#0F172A')
    )

    story = []

    # Title & Metadata Header
    story.append(Paragraph("Customer Feedback & Analytics Report", title_style))
    generated_on = datetime.now().strftime('%B %d, %Y at %I:%M %p')
    story.append(Paragraph(f"Generated on {generated_on} | Comprehensive Performance Summary", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#4F46E5'), spaceAfter=14))

    # 1. Executive Summary KPIs Table
    story.append(Paragraph("1. Executive Performance Summary", section_style))
    
    kpi_data = [
        [
            Paragraph("<b>Total Feedback</b>", cell_style),
            Paragraph(f"<b>{summary_stats.get('total_feedback', 0)}</b>", cell_bold_style),
            Paragraph("<b>Average Rating</b>", cell_style),
            Paragraph(f"<b>{summary_stats.get('avg_rating', 0.0):.2f} / 5.0</b>", cell_bold_style)
        ],
        [
            Paragraph("<b>Positive Feedback</b>", cell_style),
            Paragraph(f"<b>{summary_stats.get('positive_count', 0)} ({summary_stats.get('positive_pct', 0)}%)</b>", cell_style),
            Paragraph("<b>Neutral Feedback</b>", cell_style),
            Paragraph(f"<b>{summary_stats.get('neutral_count', 0)} ({summary_stats.get('neutral_pct', 0)}%)</b>", cell_style)
        ],
        [
            Paragraph("<b>Negative Feedback</b>", cell_style),
            Paragraph(f"<b>{summary_stats.get('negative_count', 0)} ({summary_stats.get('negative_pct', 0)}%)</b>", cell_style),
            Paragraph("<b>Received Today</b>", cell_style),
            Paragraph(f"<b>{summary_stats.get('today_count', 0)}</b>", cell_style)
        ]
    ]

    t_kpi = Table(kpi_data, colWidths=[130, 135, 130, 135])
    t_kpi.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#E2E8F0')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(t_kpi)
    story.append(Spacer(1, 14))

    # 2. Category Performance Table
    story.append(Paragraph("2. Category-Wise Breakdown", section_style))
    cat_headers = [
        Paragraph("<b>Category</b>", cell_bold_style),
        Paragraph("<b>Total Responses</b>", cell_bold_style),
        Paragraph("<b>Share (%)</b>", cell_bold_style),
        Paragraph("<b>Avg Rating</b>", cell_bold_style),
        Paragraph("<b>Positive %</b>", cell_bold_style)
    ]
    cat_rows = [cat_headers]
    for cat in category_stats:
        cat_rows.append([
            Paragraph(cat['category'], cell_style),
            Paragraph(str(cat['count']), cell_style),
            Paragraph(f"{cat['percentage']}%", cell_style),
            Paragraph(f"{cat['avg_rating']:.2f} ⭐", cell_style),
            Paragraph(f"{cat['positive_pct']}%", cell_style)
        ])

    t_cat = Table(cat_rows, colWidths=[120, 105, 95, 105, 105])
    t_cat.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#EEF2FF')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(t_cat)
    story.append(Spacer(1, 14))

    # 3. Rating Distribution
    story.append(Paragraph("3. Star Rating Distribution", section_style))
    rate_headers = [
        Paragraph("<b>Rating Score</b>", cell_bold_style),
        Paragraph("<b>Count</b>", cell_bold_style),
        Paragraph("<b>Percentage</b>", cell_bold_style)
    ]
    rate_rows = [rate_headers]
    for r in rating_stats:
        rate_rows.append([
            Paragraph(f"{r['stars']} Stars ({'★' * r['stars']})", cell_style),
            Paragraph(str(r['count']), cell_style),
            Paragraph(f"{r['percentage']}%", cell_style)
        ])

    t_rate = Table(rate_rows, colWidths=[200, 160, 170])
    t_rate.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FEF3C7')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#CBD5E1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(t_rate)
    story.append(Spacer(1, 14))

    # 4. Recent Customer Entries Summary
    if recent_feedbacks:
        story.append(Paragraph("4. Recent Feedback Log (Sample)", section_style))
        recent_headers = [
            Paragraph("<b>Customer</b>", cell_bold_style),
            Paragraph("<b>Category</b>", cell_bold_style),
            Paragraph("<b>Rating</b>", cell_bold_style),
            Paragraph("<b>Sentiment</b>", cell_bold_style),
            Paragraph("<b>Date</b>", cell_bold_style)
        ]
        recent_rows = [recent_headers]
        for f in recent_feedbacks[:6]:
            date_str = str(f.get('created_at', ''))[:10]
            recent_rows.append([
                Paragraph(f.get('customer_name', 'Anonymous'), cell_style),
                Paragraph(f.get('category', 'General'), cell_style),
                Paragraph(f"{f.get('rating', 0)} / 5", cell_style),
                Paragraph(f.get('sentiment', 'Neutral'), cell_style),
                Paragraph(date_str, cell_style)
            ])
        t_recent = Table(recent_rows, colWidths=[130, 100, 80, 100, 120])
        t_recent.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F1F5F9')),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#CBD5E1')),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
            ('PADDING', (0, 0), (-1, -1), 5),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(t_recent)

    doc.build(story)
    buffer.seek(0)
    return buffer
