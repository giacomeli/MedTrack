from PyQt5 import uic, QtWidgets, QtCore
from PyQt5.QtWidgets import QDialog, QMessageBox
import database

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