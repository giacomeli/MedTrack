from PyQt5 import uic, QtWidgets, QtCore
from PyQt5.QtWidgets import QDialog, QMessageBox
from datetime import datetime
import database
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
import subprocess
import sys
import os

class ReportDialog(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi('ui/report_dialog.ui', self)

        # Set default dates to today
        today = QtCore.QDate.currentDate()
        self.startDateEdit.setDate(today)
        self.endDateEdit.setDate(today)

        self.generateButton.clicked.connect(self.generate_report)

    def generate_report(self):
        start_date = self.startDateEdit.date().toString('yyyy-MM-dd')
        end_date = self.endDateEdit.date().toString('yyyy-MM-dd')

        if start_date > end_date:
            QMessageBox.warning(self, 'Erro', 'A data inicial deve ser anterior à data final')
            return

        data = database.fetch_withdrawals_by_date_range(start_date, end_date)
        if not data:
            QMessageBox.warning(self, 'Erro', 'Nenhum registro encontrado para o período selecionado')
            return

        file_name = self.create_pdf_report(data, start_date, end_date)
        QMessageBox.information(self, 'Sucesso', 'Relatório gerado com sucesso')

        # Open the PDF file with the default viewer
        self.open_pdf(file_name)

    def create_pdf_report(self, data, start_date, end_date):
        file_name = f'report_{start_date}_{end_date}.pdf'
        doc = SimpleDocTemplate(file_name, pagesize=letter)
        elements = []

        styles = getSampleStyleSheet()
        title_style = styles['Title']
        title_style.alignment = 1  # Center alignment

        # Convert dates to PT-BR format
        start_date_br = datetime.strptime(start_date, '%Y-%m-%d').strftime('%d/%m/%Y')
        end_date_br = datetime.strptime(end_date, '%Y-%m-%d').strftime('%d/%m/%Y')

        title = Paragraph(f'Relatório de Retiradas - {start_date_br} a {end_date_br}', title_style)
        elements.append(title)

        # Table data
        table_data = [['Nome do Item', 'Quantidade Retirada', 'Quantidade em Estoque']]

        grouped_data = {}
        for item in data:
            item_name = item[0]
            quantity = item[1]
            if item_name in grouped_data:
                grouped_data[item_name] += quantity
            else:
                grouped_data[item_name] = quantity

        for item_name, total_quantity in grouped_data.items():
            remaining_quantity = database.fetch_item_quantity(item_name)
            table_data.append([item_name, total_quantity, remaining_quantity])

        # Create table
        table = Table(table_data, colWidths=[3 * inch, 2 * inch, 2 * inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        elements.append(table)
        doc.build(elements)
        return file_name

    def open_pdf(self, file_name):
        try:
            if sys.platform == "win32":
                os.startfile(file_name)
            elif sys.platform == "darwin":
                subprocess.call(["open", file_name])
            else:
                subprocess.call(["xdg-open", file_name])
        except Exception as e:
            QMessageBox.warning(self, 'Erro', f'Não foi possível abrir o arquivo PDF: {str(e)}')
