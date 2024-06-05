import sys
from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow
import database

def main():
    # Cria as tabelas no banco de dados, se ainda não existirem
    database.create_tables()
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()