import sys
from PyQt5 import uic, QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QCompleter, QDialog
from datetime import datetime
import database
from add_item_dialog import load_product_names_from_csv

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
            current_datetime = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            database.insert_item(item_name, quantity, current_datetime, current_datetime)
            self.accept()
        else:
            QMessageBox.warning(self, 'Erro', 'Preencha todos os campos')

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('ui/main_window.ui', self)
        self.setMinimumSize(800, 600)

        # Load product names from CSV
        self.product_names = load_product_names_from_csv('assets/DADOS_ABERTOS_MEDICAMENTOS.csv')

        self.addButton.clicked.connect(self.open_add_item_dialog)
        self.refreshButton.clicked.connect(self.load_data)

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

    def open_add_item_dialog(self):
        dialog = AddItemDialog(self.product_names)
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
        self.stockTable.setColumnCount(5)  # Ensure there are 5 columns
        self.stockTable.setHorizontalHeaderLabels(['Id', 'Item Name', 'Quantity', 'Created At', 'Updated At'])  # Set column headers
        for row_number, row_data in enumerate(data):
            self.stockTable.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.stockTable.setItem(row_number, column_number, QtWidgets.QTableWidgetItem(str(data)))

    def set_font_size(self):
        font = QtGui.QFont()
        font.setPointSize(14)
        self.searchInput.setFont(font)
        self.addButton.setFont(font)
        self.refreshButton.setFont(font)

    def eventFilter(self, source, event):
        if event.type() == QtCore.QEvent.KeyPress and event.key() == QtCore.Qt.Key_Delete:
            if source is self.stockTable:
                selected_row = self.stockTable.currentRow()
                if selected_row >= 0:
                    item_id = self.stockTable.item(selected_row, 0).text()
                    item_name = self.stockTable.item(selected_row, 1).text()
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