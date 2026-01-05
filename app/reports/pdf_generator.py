"""
PDF Report Generator for Microfinance MIS
Generates professional PDF reports for statements, receipts, and compliance
"""
from decimal import Decimal
from datetime import date
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT

from clients.models import Client
from loans.models import Loan
from repayments.models import Repayment


class PDFReportGenerator:
    """Generate professional PDF reports."""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles."""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#366092'),
            spaceAfter=30,
            alignment=TA_CENTER,
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#366092'),
            spaceAfter=12,
        ))
    
    def generate_loan_statement(self, loan_id):
        """Generate a detailed loan statement PDF."""
        try:
            loan = Loan.objects.select_related('client', 'product').get(loan_id=loan_id)
        except Loan.DoesNotExist:
            return None
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        
        # Title
        title = Paragraph(f"LOAN STATEMENT", self.styles['CustomTitle'])
        story.append(title)
        story.append(Spacer(1, 0.2*inch))
        
        # Loan Information
        loan_info_data = [
            ['Loan ID:', loan.loan_id],
            ['Client:', loan.client.full_name],
            ['Client ID:', loan.client.client_id],
            ['Product:', loan.product.name if loan.product else 'N/A'],
            ['Principal:', f'GHS {loan.principal:,.2f}'],
            ['Interest Rate:', f'{loan.interest_rate}% per annum'],
            ['Interest Method:', loan.get_interest_method_display()],
            ['Term:', f'{loan.term_months} months'],
            ['Repayment Frequency:', loan.get_repayment_frequency_display()],
            ['Disbursed Date:', loan.disbursed_date.strftime('%d %B %Y') if loan.disbursed_date else 'N/A'],
            ['Maturity Date:', loan.maturity_date.strftime('%d %B %Y') if loan.maturity_date else 'N/A'],
            ['Status:', loan.get_status_display()],
            ['Classification:', loan.get_classification_display()],
        ]
        
        loan_info_table = Table(loan_info_data, colWidths=[2*inch, 4*inch])
        loan_info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E8E8E8')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        
        story.append(loan_info_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Financial Summary
        outstanding = loan.get_outstanding_balance()
        total_paid = loan.total_repayable - outstanding
        
        summary_heading = Paragraph("Financial Summary", self.styles['CustomHeading'])
        story.append(summary_heading)
        
        summary_data = [
            ['Item', 'Amount (GHS)'],
            ['Total Repayable', f'{loan.total_repayable:,.2f}'],
            ['Total Paid', f'{total_paid:,.2f}'],
            ['Outstanding Balance', f'{outstanding:,.2f}'],
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#366092')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Payment History
        payments = loan.repayments.filter(status='confirmed').order_by('paid_on')
        
        if payments.exists():
            payment_heading = Paragraph("Payment History", self.styles['CustomHeading'])
            story.append(payment_heading)
            
            payment_data = [['Date', 'Receipt #', 'Amount', 'Method', 'Principal', 'Interest']]
            
            for payment in payments:
                payment_data.append([
                    payment.paid_on.strftime('%d/%m/%Y'),
                    payment.receipt_number,
                    f'{payment.amount:,.2f}',
                    payment.get_method_display(),
                    f'{payment.principal_paid:,.2f}',
                    f'{payment.interest_paid:,.2f}',
                ])
            
            payment_table = Table(payment_data, colWidths=[1*inch, 1.5*inch, 1*inch, 1.2*inch, 1*inch, 1*inch])
            payment_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#366092')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            ]))
            
            story.append(payment_table)
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    def generate_payment_receipt(self, receipt_number):
        """Generate a payment receipt PDF."""
        try:
            repayment = Repayment.objects.select_related(
                'loan', 'loan__client', 'received_by'
            ).get(receipt_number=receipt_number)
        except Repayment.DoesNotExist:
            return None
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        
        # Title
        title = Paragraph(f"PAYMENT RECEIPT", self.styles['CustomTitle'])
        story.append(title)
        story.append(Spacer(1, 0.2*inch))
        
        # Receipt Info
        receipt_data = [
            ['Receipt Number:', repayment.receipt_number],
            ['Date:', repayment.paid_on.strftime('%d %B %Y')],
            ['Time:', repayment.received_on.strftime('%H:%M:%S')],
            ['', ''],
            ['Client Name:', repayment.loan.client.full_name],
            ['Client ID:', repayment.loan.client.client_id],
            ['Loan ID:', repayment.loan.loan_id],
            ['', ''],
            ['Amount Paid:', f'GHS {repayment.amount:,.2f}'],
            ['Payment Method:', repayment.get_method_display()],
            ['Reference:', repayment.reference or 'N/A'],
            ['', ''],
            ['Principal Paid:', f'GHS {repayment.principal_paid:,.2f}'],
            ['Interest Paid:', f'GHS {repayment.interest_paid:,.2f}'],
            ['Penalty Paid:', f'GHS {repayment.penalty_paid:,.2f}'],
            ['', ''],
            ['Received By:', repayment.received_by.username if repayment.received_by else 'N/A'],
            ['Status:', repayment.get_status_display()],
        ]
        
        receipt_table = Table(receipt_data, colWidths=[2.5*inch, 3.5*inch])
        receipt_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E8E8E8')),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        
        story.append(receipt_table)
        story.append(Spacer(1, 0.5*inch))
        
        # Outstanding balance after payment
        outstanding = repayment.loan.get_outstanding_balance()
        
        balance_text = Paragraph(
            f"<b>Outstanding Balance After Payment: GHS {outstanding:,.2f}</b>",
            self.styles['Normal']
        )
        story.append(balance_text)
        
        story.append(Spacer(1, 0.5*inch))
        
        # Footer
        footer_text = Paragraph(
            "<i>This is a computer-generated receipt and does not require a signature.</i>",
            self.styles['Normal']
        )
        story.append(footer_text)
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    def generate_portfolio_summary(self):
        """Generate portfolio summary PDF report."""
        from dashboard.analytics import PortfolioAnalytics
        
        analytics = PortfolioAnalytics()
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []
        
        # Title
        title = Paragraph(
            f"PORTFOLIO SUMMARY REPORT<br/>{date.today().strftime('%B %Y')}",
            self.styles['CustomTitle']
        )
        story.append(title)
        story.append(Spacer(1, 0.3*inch))
        
        # Portfolio Metrics
        portfolio = analytics.get_portfolio_summary()
        
        metrics_heading = Paragraph("Portfolio Overview", self.styles['CustomHeading'])
        story.append(metrics_heading)
        
        metrics_data = [
            ['Metric', 'Value'],
            ['Total Portfolio (GHS)', f'{portfolio["total_portfolio_value"]:,.2f}'],
            ['Outstanding Balance (GHS)', f'{portfolio["total_outstanding"]:,.2f}'],
            ['Active Loans', f'{portfolio["active_loans_count"]:,}'],
            ['Collection Rate', f'{portfolio["collection_rate"]:.2f}%'],
        ]
        
        metrics_table = Table(metrics_data, colWidths=[3*inch, 2.5*inch])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#366092')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        
        story.append(metrics_table)
        story.append(Spacer(1, 0.3*inch))
        
        # BoG Classification
        classification_heading = Paragraph("BoG Loan Classification", self.styles['CustomHeading'])
        story.append(classification_heading)
        
        classification = analytics.get_bog_classification()
        
        class_data = [['Classification', 'Count', 'Value (GHS)']]
        for key, data in classification.items():
            class_data.append([
                key.title(),
                f'{data["count"]:,}',
                f'{data["value"]:,.2f}',
            ])
        
        class_table = Table(class_data, colWidths=[2*inch, 1.5*inch, 2*inch])
        class_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#366092')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        
        story.append(class_table)
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    def generate_profit_loss_pdf(self):
        """Generate Profit & Loss statement PDF."""
        from loans.models import Loan
        from repayments.models import Repayment
        from django.db.models import Sum
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        
        # Title
        title = Paragraph(
            f"PROFIT & LOSS STATEMENT<br/>{date.today().strftime('%B %Y')}", 
            self.styles['CustomTitle']
        )
        story.append(title)
        story.append(Spacer(1, 0.3*inch))
        
        # Calculate revenue
        interest_income = Repayment.objects.filter(
            status='confirmed'
        ).aggregate(total=Sum('interest_paid'))['total'] or 0
        
        processing_fees = Loan.objects.filter(
            status__in=['active', 'closed']
        ).aggregate(total=Sum('processing_fee'))['total'] or 0
        
        insurance_fees = Loan.objects.filter(
            status__in=['active', 'closed']
        ).aggregate(total=Sum('insurance_fee'))['total'] or 0
        
        penalty_income = Repayment.objects.filter(
            status='confirmed'
        ).aggregate(total=Sum('penalty_paid'))['total'] or 0
        
        total_revenue = float(interest_income + processing_fees + insurance_fees + penalty_income)
        
        # Revenue section
        revenue_heading = Paragraph("REVENUE", self.styles['CustomHeading'])
        story.append(revenue_heading)
        
        revenue_data = [
            ['Item', 'Amount (GHS)'],
            ['Interest Income', f'{float(interest_income):,.2f}'],
            ['Processing Fees', f'{float(processing_fees):,.2f}'],
            ['Insurance Fees', f'{float(insurance_fees):,.2f}'],
            ['Penalty Income', f'{float(penalty_income):,.2f}'],
            ['TOTAL REVENUE', f'{total_revenue:,.2f}'],
        ]
        
        revenue_table = Table(revenue_data, colWidths=[3*inch, 2.5*inch])
        revenue_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#366092')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#E8E8E8')),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        
        story.append(revenue_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Expenses section (placeholder)
        expenses_heading = Paragraph("EXPENSES", self.styles['CustomHeading'])
        story.append(expenses_heading)
        
        total_expenses = 0
        
        expense_data = [
            ['Item', 'Amount (GHS)'],
            ['Staff Salaries', '0.00'],
            ['Operating Expenses', '0.00'],
            ['Administrative Costs', '0.00'],
            ['Loan Loss Provisions', '0.00'],
            ['TOTAL EXPENSES', f'{total_expenses:,.2f}'],
        ]
        
        expense_table = Table(expense_data, colWidths=[3*inch, 2.5*inch])
        expense_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#366092')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#E8E8E8')),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        
        story.append(expense_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Net Profit
        net_profit = total_revenue - total_expenses
        profit_color = colors.green if net_profit >= 0 else colors.red
        
        profit_data = [
            ['NET PROFIT/LOSS', f'GHS {net_profit:,.2f}'],
        ]
        
        profit_table = Table(profit_data, colWidths=[3*inch, 2.5*inch])
        profit_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#E8E8E8')),
            ('TEXTCOLOR', (0, 0), (-1, -1), profit_color),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 14),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        
        story.append(profit_table)
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    def generate_board_report_pdf(self):
        """Generate Board Executive Summary PDF."""
        from loans.models import Loan
        from clients.models import Client
        from django.db.models import Sum
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        
        # Title
        title = Paragraph(
            f"BOARD EXECUTIVE SUMMARY<br/>{date.today().strftime('%B %Y')}", 
            self.styles['CustomTitle']
        )
        story.append(title)
        story.append(Spacer(1, 0.3*inch))
        
        # Portfolio Overview
        overview_heading = Paragraph("PORTFOLIO OVERVIEW", self.styles['CustomHeading'])
        story.append(overview_heading)
        
        active_loans = Loan.objects.filter(status='active')
        total_portfolio = active_loans.aggregate(total=Sum('principal'))['total'] or 0
        total_outstanding = sum(loan.get_outstanding_balance() for loan in active_loans)
        active_clients = Client.objects.filter(status='active').count()
        
        overview_data = [
            ['Metric', 'Value'],
            ['Total Active Loans', f'{active_loans.count():,}'],
            ['Total Portfolio Value', f'GHS {float(total_portfolio):,.2f}'],
            ['Total Outstanding', f'GHS {float(total_outstanding):,.2f}'],
            ['Active Clients', f'{active_clients:,}'],
        ]
        
        overview_table = Table(overview_data, colWidths=[3*inch, 2.5*inch])
        overview_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#366092')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        
        story.append(overview_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Portfolio Quality
        quality_heading = Paragraph("PORTFOLIO QUALITY", self.styles['CustomHeading'])
        story.append(quality_heading)
        
        par_30_loans = active_loans.filter(days_in_arrears__gte=30)
        par_30_value = sum(loan.get_outstanding_balance() for loan in par_30_loans)
        par_30_rate = (par_30_value / total_outstanding * 100) if total_outstanding > 0 else 0
        
        quality_data = [
            ['Metric', 'Value'],
            ['PAR 30 Rate', f'{par_30_rate:.2f}%'],
            ['Loans in Arrears', f'{par_30_loans.count():,}'],
            ['Arrears Value', f'GHS {float(par_30_value):,.2f}'],
        ]
        
        quality_table = Table(quality_data, colWidths=[3*inch, 2.5*inch])
        quality_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#366092')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        
        story.append(quality_table)
        story.append(Spacer(1, 0.3*inch))
        
        # BoG Classification
        classification_heading = Paragraph("LOAN CLASSIFICATION (BoG)", self.styles['CustomHeading'])
        story.append(classification_heading)
        
        classifications = {
            'Current (0-30 days)': active_loans.filter(days_in_arrears__lt=31).count(),
            'Substandard (31-90 days)': active_loans.filter(days_in_arrears__gte=31, days_in_arrears__lte=90).count(),
            'Doubtful (91-180 days)': active_loans.filter(days_in_arrears__gte=91, days_in_arrears__lte=180).count(),
            'Loss (180+ days)': active_loans.filter(days_in_arrears__gt=180).count(),
        }
        
        class_data = [['Classification', 'Count']]
        for classification, count in classifications.items():
            class_data.append([classification, f'{count:,}'])
        
        class_table = Table(class_data, colWidths=[3*inch, 2.5*inch])
        class_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#366092')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        
        story.append(class_table)
        story.append(Spacer(1, 0.2*inch))
        
        # Footer
        footer_text = Paragraph(
            f"<i>Report Generated: {date.today().strftime('%d %B %Y')}</i>",
            self.styles['Normal']
        )
        story.append(footer_text)
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
