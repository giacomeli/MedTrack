import sys
from PyQt5 import uic, QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QCompleter, QDialog
from datetime import datetime
import database
from add_item_dialog import load_product_names_from_csv

# Ensure tables are created
database.create_tables()

class AddItemDialog(QDialog):
    def __init__(self, product_names):
        super().__init__()
        uic.loadUi('ui/add_item_dialog.ui', self)
        self.saveButton.clicked.connect(self.save_item)

        # Set up the completer for item names
        self.completer = QCompleter(product_names, self)
        self.completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.itemNameInput.setCompleter(self.completer)

    def save_item(self):
        item_name = self.itemNameInput.text()
        quantity = self.quantityInput.value()
        if item_name and quantity:
            if database.item_exists(item_name):
                QMessageBox.warning(self, 'Erro', 'Item com este nome já existe')
            else:
                current_datetime = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
                database.insert_item(item_name, quantity, current_datetime, current_datetime)
                self.accept()
        else:
            QMessageBox.warning(self, 'Erro', 'Preencha todos os campos')

class WithdrawItemDialog(QDialog):
    def __init__(self, item_name, item_quantity):
        super().__init__()
        uic.loadUi('ui/withdraw_item_dialog.ui', self)
        self.itemNameInput.setText(item_name)
        self.quantityInput.setMaximum(item_quantity)
        self.dateTimeInput.setDateTime(QtCore.QDateTime.currentDateTime())
        self.withdrawButton.clicked.connect(self.withdraw_item)

    def withdraw_item(self):
        item_name = self.itemNameInput.text()
        quantity = self.quantityInput.value()
        observations = self.observationInput.toPlainText()
        date_time = self.dateTimeInput.dateTime().toString('dd/MM/yyyy HH:mm:ss')
        if quantity > 0:
            database.withdraw_item(item_name, quantity)
            database.log_withdrawal(item_name, quantity, observations, date_time)
            self.accept()
        else:
            QMessageBox.warning(self, 'Erro', 'A quantidade de saída deve ser maior que zero')

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('ui/main_window.ui', self)
        self.setMinimumSize(800, 600)

        # Load product names from CSV
        self.product_names = load_product_names_from_csv('assets/DADOS_ABERTOS_MEDICAMENTOS.csv')

        self.addButton.clicked.connect(self.open_add_item_dialog)

        # Set up the completer for item names in the search input
        self.completer = QCompleter(self)
        self.searchInput.setCompleter(self.completer)
        self.update_completer()

        # Connect search input signals to update_completer function
        self.searchInput.textChanged.connect(self.update_completer)
        self.completer.activated.connect(self.update_completer)

        self.load_data()

        # Set font size
        self.set_font_size()

        # Enable item deletion with Delete key
        self.stockTable.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.stockTable.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.stockTable.installEventFilter(self)

        # Connect key press events for navigation and selection
        self.searchInput.installEventFilter(self)

    def open_add_item_dialog(self):
        dialog = AddItemDialog(self.product_names)
        if dialog.exec_():
            self.load_data()
            self.update_completer()

    def open_withdraw_item_dialog(self, item_name, item_quantity):
        dialog = WithdrawItemDialog(item_name, item_quantity)
        if dialog.exec_():
            self.load_data()
            self.update_completer()

    def load_data(self):
        data = database.fetch_all()
        self.populate_table(data)

    def update_completer(self):
        search_text = self.searchInput.text().lower()
        item_names = database.fetch_item_names()
        completer_model = QtCore.QStringListModel(item_names, self.completer)
        self.completer.setModel(completer_model)
        
        # Update the table based on the search text
        data = database.search_items(search_text)
        self.populate_table(data)

    def populate_table(self, data):
        self.stockTable.setRowCount(0)
        self.stockTable.setColumnCount(4)  # Adjust to 4 columns
        self.stockTable.setHorizontalHeaderLabels(['Item Name', 'Quantity', 'Created At', 'Updated At'])  # Set column headers
        for row_number, row_data in enumerate(data):
            self.stockTable.insertRow(row_number)
            for column_number, cell_data in enumerate(row_data[1:]):  # Skip the first column (ID)
                self.stockTable.setItem(row_number, column_number, QtWidgets.QTableWidgetItem(str(cell_data)))
        
        # Set column widths
        self.stockTable.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.stockTable.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        self.stockTable.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        self.stockTable.horizontalHeader().setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)

    def set_font_size(self):
        font = QtGui.QFont()
        font.setPointSize(14)
        self.searchInput.setFont(font)
        self.addButton.setFont(font)

    def eventFilter(self, source, event):
        if source is self.searchInput:
            if event.type() == QtCore.QEvent.KeyPress:
                if event.key() == QtCore.Qt.Key_Up:
                    current_row = self.stockTable.currentRow()
                    if current_row > 0:
                        self.stockTable.selectRow(current_row - 1)
                elif event.key() == QtCore.Qt.Key_Down:
                    current_row = self.stockTable.currentRow()
                    if current_row < self.stockTable.rowCount() - 1:
                        self.stockTable.selectRow(current_row + 1)
                elif event.key() == QtCore.Qt.Key_Return or event.key() == QtCore.Qt.Key_Enter:
                    selected_row = self.stockTable.currentRow()
                    if selected_row >= 0:
                        item_name = self.stockTable.item(selected_row, 0).text()
                        item_quantity = int(self.stockTable.item(selected_row, 1).text())
                        self.open_withdraw_item_dialog(item_name, item_quantity)
                elif event.key() == QtCore.Qt.Key_Delete:
                    selected_row = self.stockTable.currentRow()
                    if selected_row >= 0:
                        item_id = self.stockTable.item(selected_row, 0).text()
                        item_name = self.stockTable.item(selected_row, 0).text()
                        if item_id and item_name:
                            reply = QMessageBox.question(self, 'Confirmação', f'Tem certeza que deseja remover o item "{item_name}"?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                            if reply == QMessageBox.Yes:
                                database.delete_item(item_id)
                                self.load_data()
                                self.update_completer()
                                QMessageBox.information(self, 'Sucesso', 'Item removido do estoque')
        return super().eventFilter(source, event)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())