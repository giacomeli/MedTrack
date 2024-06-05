from PyQt5 import uic, QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QCompleter
from dialogs.add_item_dialog import AddItemDialog
from dialogs.withdraw_item_dialog import WithdrawItemDialog
from dialogs.report_dialog import ReportDialog
import database
from utils.helpers import load_product_names_from_csv

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('ui/main_window.ui', self)
        self.setMinimumSize(800, 600)

        # Load product names from CSV
        self.product_names = load_product_names_from_csv('assets/DADOS_ABERTOS_MEDICAMENTOS.csv')

        self.addButton.clicked.connect(self.open_add_item_dialog)
        self.reportButton.clicked.connect(self.open_report_dialog)

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

    def open_report_dialog(self):
        dialog = ReportDialog()
        dialog.exec_()

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
        self.stockTable.setColumnCount(5)  # Adjust to 5 columns
        self.stockTable.setHorizontalHeaderLabels(['Id', 'Item Name', 'Quantity', 'Created At', 'Updated At'])  # Set column headers
        for row_number, row_data in enumerate(data):
            self.stockTable.insertRow(row_number)
            for column_number, cell_data in enumerate(row_data):  # Do not skip the first column (ID)
                self.stockTable.setItem(row_number, column_number, QtWidgets.QTableWidgetItem(str(cell_data)))

        # Set column widths
        self.stockTable.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        self.stockTable.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        self.stockTable.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        self.stockTable.horizontalHeader().setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
        self.stockTable.horizontalHeader().setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)

    def set_font_size(self):
        font = QtGui.QFont()
        font.setPointSize(14)
        self.searchInput.setFont(font)
        self.searchInput.setMinimumHeight(40)
        self.addButton.setFont(font)
        self.reportButton.setFont(font)

    def eventFilter(self, source, event):
        if source is self.searchInput and event.type() == QtCore.QEvent.KeyPress:
            key_actions = {
                QtCore.Qt.Key_Up: self.navigate_up,
                QtCore.Qt.Key_Down: self.navigate_down,
                QtCore.Qt.Key_Return: self.select_item,
                QtCore.Qt.Key_Enter: self.select_item,
                QtCore.Qt.Key_Delete: self.delete_item,
            }
            action = key_actions.get(event.key())
            if action:
                action()
                return True
        return super().eventFilter(source, event)

    def navigate_up(self):
        current_row = self.stockTable.currentRow()
        if current_row > 0:
            self.stockTable.selectRow(current_row - 1)

    def navigate_down(self):
        current_row = self.stockTable.currentRow()
        if current_row < self.stockTable.rowCount() - 1:
            self.stockTable.selectRow(current_row + 1)

    def select_item(self):
        selected_row = self.stockTable.currentRow()
        if selected_row >= 0:
            item_name = self.stockTable.item(selected_row, 1).text()
            item_quantity = int(self.stockTable.item(selected_row, 2).text())
            self.open_withdraw_item_dialog(item_name, item_quantity)

    def delete_item(self):
        selected_row = self.stockTable.currentRow()
        if selected_row >= 0:
            item_id = self.stockTable.item(selected_row, 0).text()
            item_name = self.stockTable.item(selected_row, 1).text()
            if item_id and item_name:
                reply = QMessageBox.question(self, 'Confirmação', f'Tem certeza que deseja remover o item "{item_name}"?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
                if reply == QMessageBox.Yes:
                    database.delete_item(int(item_id))
                    self.load_data()
                    self.update_completer()
                    QMessageBox.information(self, 'Sucesso', 'Item removido do estoque')