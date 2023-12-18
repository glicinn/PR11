
from PyQt6 import QtWidgets, QtSql

class Data:
    def __init__(self):
        super(Data, self).__init__()

    def create_connection(self):
        db = QtSql.QSqlDatabase.addDatabase('QSQLITE')
        db.setDatabaseName('exspense_db.db') # Название базы данных

        # Проверка на подключение к бд
        if not db.open():
            QtWidgets.QMessageBox.critical(None, 'Cannot open database',
                                           "Click Cancel to exit.", QtWidgets.QMessageBox.Cancel)
            return False