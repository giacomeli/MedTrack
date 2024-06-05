from PyQt5 import uic, QtWidgets, QtCore
from PyQt5.QtWidgets import QDialog, QMessageBox, QCompleter  # Adicionando QCompleter
from datetime import datetime
import database

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
