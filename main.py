import pymysql
from PyQt6.uic import loadUiType
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox, QTableWidgetItem
from config import host, user, password, db_name, port

# Загрузка интерфейсов для главного окна и окна администратора
AuthForm, AuthWindow = loadUiType("Authorization.ui")
AdminForm, AdminWindow = loadUiType("AdminWindow.ui")

class UserDatabase:
    """
    Класс для работы с базой данных пользователей.

    Атрибуты:
        connection (pymysql.Connection): Соединение с базой данных.

    Методы:
        execute_query(query: str) -> list: Выполнение SQL-запроса и получение результата в виде списка.
        execute_update(query: str): Выполнение SQL-запроса на обновление данных в базе данных.
    """
    def __init__(self):
        self.connection = pymysql.connect(host=host, user=user, password=password, db=db_name, port=port)

    def execute_query(self, query: str) -> list:
        with self.connection.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()

    def execute_update(self, query: str):
        with self.connection.cursor() as cursor:
            cursor.execute(query)
            self.connection.commit()

class MainWindow(QMainWindow, AuthForm):
    """
    Главное окно приложения для авторизации пользователей.

    Атрибуты:
        loginEnter (QTextEdit): Поле ввода логина.
        passEnter (QTextEdit): Поле ввода пароля.

    Методы:
        auth_button_click(): Обработчик нажатия на кнопку авторизации.
        popup_action(btn: QPushButton): Обработчик действий при всплывающем окне.
        show_error_message(title: str, text: str): Отображение всплывающего окна с ошибкой.
    """
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.authButton.clicked.connect(self.auth_button_click)

    def auth_button_click(self):
        user_db = UserDatabase()
        login = self.loginEnter.toPlainText()
        password = self.passEnter.toPlainText()
        auth_query = f"SELECT * FROM User WHERE User_Login = '{login}' AND User_Password = '{password}';"
        user = user_db.execute_query(auth_query)

        if user:
            print("Здравствуйте!")
            super().close()
            self.admin_window = AdWindow(user_db)
            self.admin_window.show()
        else:
            print("Пользователь не найденъ")
            self.show_error_message("Пользователь не найден", "Ошибка в логине или пароле! Попробуйте снова")

    def popup_action(self, btn):
        if btn.text() == "Ok":
            print("Нажата кнопка Ok")

    def show_error_message(self, title, text):
        error = QMessageBox()
        error.setWindowTitle(title)
        error.setText(text)
        error.setInformativeText("Попробуйте снова")
        error.buttonClicked.connect(self.popup_action)
        error.exec()

class AdWindow(QMainWindow, AdminForm):
    """
    Окно администратора для управления данными.

    Атрибуты:
        user_db (UserDatabase): Объект для работы с базой данных пользователей.

    Методы:
        load_users(): Загрузка пользователей из базы данных и отображение в таблице.
        display_users(users: list): Отображение пользователей в таблице.
        add_users(): Добавление пользователя в базу данных.
        update_users(): Обновление данных пользователя в базе данных.
        delete_users(): Удаление пользователя из базы данных.
    """
    def __init__(self, user_db):
        super().__init__()
        self.setWindowTitle("Окно администратора")
        self.setupUi(self)
        self.user_db = user_db
        self.users_add_button.clicked.connect(self.add_users)
        self.users_edit_button.clicked.connect(self.update_users)
        self.users_delete_button.clicked.connect(self.delete_users)
        self.table_widget.itemSelectionChanged.connect(self.on_item_selection_changed_users)
        self.load_users()

    def load_users(self):
        query = "SELECT * FROM User"
        users = self.user_db.execute_query(query)
        self.display_users(users)

    def display_users(self, users):
        row_index = len(users)
        column_index = len(users[0]) if users else 0

        self.table_widget.setRowCount(row_index)
        self.table_widget.setColumnCount(column_index)

        columns = [column[0] for column in users.description[1:]]
        self.table_widget.setHorizontalHeaderLabels(columns)

        for row_index, row_data in enumerate(users):
            for column_index, data in enumerate(row_data):
                item = QTableWidgetItem(str(data))
                self.table_widget.setItem(row_index, column_index, item)

    def add_users(self):
        try:
            with self.user_db.connection.cursor() as cursor:
                query = "SELECT COUNT(*) FROM User;"
                cursor.execute(query)
                str_num = cursor.fetchone()
                str_num = str_num['COUNT(*)']
                str_num += 1

                login = self.user_login_line_edit.text()
                password = self.user_password_line_edit.text()
                email = self.user_email_line_edit.text()
                balance = self.user_balance_line_edit.text()
                role = self.user_role_combobox.currentText()
                benefit = self.user_benefit_combobox.currentText()

                if login and password and email and balance and role and benefit is not None:
                    try:
                        query = f"INSERT INTO User(User_Login, User_Password, Email, Balance, Role, Benefit_ID) " \
                                f"VALUES ('{login}', '{password}', '{email}', '{balance}', '{role}', {benefit});"
                        cursor.execute(query)
                        self.load_users()

                    except pymysql.Error as e:
                        self.show_error_message("Добавление не удалось", "Ошибка формата данных")

                else:
                    self.show_error_message("Добавление не удалось", "Не все поля заполнены")

        finally:
            None

    def update_users(self):
        try:
            with self.user_db.connection.cursor() as cursor:
                selected_items = self.table_widget.selectedItems()
                if selected_items:
                    selected_row = selected_items[0].row() + 1

                    login = self.user_login_line_edit.text()
                    password = self.user_password_line_edit.text()
                    email = self.user_email_line_edit.text()
                    balance = self.user_balance_line_edit.text()
                    role = self.user_role_combobox.currentText()
                    benefit = self.user_benefit_combobox.currentText()

                    if login and password and email and balance and role is not None:
                        try:
                            query = f"UPDATE User " \
                                    f"SET User_Login = '{login}', User_Password = '{password}', " \
                                    f"Email = '{email}', Balance = '{balance}', " \
                                    f"Role = '{role}', Benefit_ID = {benefit} " \
                                    f"WHERE ID_User = {selected_row};"
                            cursor.execute(query)
                            self.load_users()

                        except pymysql.Error as e:
                            self.show_error_message("Обновление не удалось", "Ошибка формата данных")

                    else:
                        self.show_error_message("Обновление не удалось", "Не все поля заполнены")

        finally:
            None

    def delete_users(self):
        try:
            with self.user_db.connection.cursor() as cursor:
                selected_items = self.table_widget.selectedItems()
                if selected_items:
                    selected_row = selected_items[0].row() + 1

                    try:
                        query = f"DELETE FROM User WHERE ID_User = {selected_row};"
                        cursor.execute(query)
                        self.load_users()

                    except pymysql.Error as e:
                        self.show_error_message("Удаление не удалось", "Объект не выбран")

                else:
                    self.show_error_message("Удаление не удалось", "Объект не выбран")

        finally:
            None

        # ------------------------ Отзывы --------------------------------

        # Функция вывода отзывов в TableWidget
        def load_feedbacks(self):
            """
            Загружает отзывы из базы данных и отображает их в таблице.
            """
            try:
                with connection.cursor() as cursor:
                    # SQL-запрос для подсчета количества столбцов в таблице
                    sql_query = "SELECT COUNT(*) FROM information_schema.columns WHERE table_schema = %s AND table_name = %s"
                    connection.commit()
                    # Указание имени базы данных и таблицы
                    database_name = db_name
                    table_name = 'Feedback'
                    # Выполнение запроса с передачей параметров
                    cursor.execute(sql_query, (database_name, table_name))
                    # Получение результата запроса
                    row_index = cursor.fetchone()
                    row_index = row_index['COUNT(*)']
                    row_index -= 1
                    print(row_index)
            finally:
                # Закрытие соединения
                None

            try:
                with connection.cursor() as cursor:
                    # SQL-запрос для выборки всех записей из таблицы
                    sql_query = "SELECT * FROM Feedback"
                    connection.commit()
                    # Выполнение запроса
                    cursor.execute(sql_query)
                    # Извлечение всех записей из результата запроса в виде списка словарей
                    feedbacks = []
                    # Получение имен столбцов, начиная с первого столбца
                    columns = [column[0] for column in cursor.description[1:]]
                    print(columns)

                    # SQL-запрос для подсчета всех записей из таблицы
                    sql_query2 = "SELECT COUNT(*) FROM Feedback;"
                    connection.commit()
                    # Выполнение запроса
                    cursor.execute(sql_query2)
                    str_num = cursor.fetchone()
                    str_num = str_num['COUNT(*)']
                    print(str_num)

                    for i in range(str_num):
                        feedback = {}
                        for column in columns:
                            sql_query3 = f"SELECT {column} FROM Feedback WHERE ID_Feedback = {i + 1};"
                            cursor.execute(sql_query3)
                            result = cursor.fetchone()  # Получаем одну строку из результата запроса
                            if result:
                                print(result)
                                feedback[column] = result[column]  # Первый элемент кортежа - это значение столбца
                            else:
                                feedback[column] = None
                        feedbacks.append(feedback)

                    # Теперь переменная entities содержит все сущности из вашей таблицы в виде списка словарей
                    print(feedbacks)
            finally:
                # Закрытие соединения
                # connection.close()
                None

            # tableWidget - название поля
            self.feedbacks_table_widget.setRowCount(str_num)  # Кол-во строк
            self.feedbacks_table_widget.setColumnCount(row_index)  # Кол-во столбцов

            # Заголовки столбцов
            self.feedbacks_table_widget.setHorizontalHeaderLabels(['Текст', 'Код пользователя', 'Код товара'])

            # Ширина столбцов (индекс, ширина)
            for i in range(row_index):
                self.feedbacks_table_widget.setColumnWidth(i, 230)

            # Заполнение QtTableWidget
            for row_index, row_data in enumerate(feedbacks):
                for column_index, data in enumerate(row_data.values()):
                    item = QTableWidgetItem(str(data))
                    self.feedbacks_table_widget.setItem(row_index, column_index, item)

        # ------------------------ Заказы --------------------------------

        # Функция вывода заказов в TableWidget
        def load_orders(self):
            """
            Загружает заказы из базы данных и отображает их в таблице.
            """
            try:
                with connection.cursor() as cursor:
                    # SQL-запрос для подсчета количества столбцов в таблице
                    sql_query = "SELECT COUNT(*) FROM information_schema.columns WHERE table_schema = %s AND table_name = %s"
                    connection.commit()
                    # Указание имени базы данных и таблицы
                    database_name = db_name
                    table_name = 'Ordering'
                    # Выполнение запроса с передачей параметров
                    cursor.execute(sql_query, (database_name, table_name))
                    # Получение результата запроса
                    row_index = cursor.fetchone()
                    row_index = row_index['COUNT(*)']
                    row_index -= 1
                    print(row_index)
            finally:
                # Закрытие соединения
                None

            try:
                with connection.cursor() as cursor:
                    # SQL-запрос для выборки всех записей из таблицы
                    sql_query = "SELECT * FROM Ordering"
                    connection.commit()
                    # Выполнение запроса
                    cursor.execute(sql_query)
                    # Извлечение всех записей из результата запроса в виде списка словарей
                    orders = []
                    # Получение имен столбцов, начиная с первого столбца
                    columns = [column[0] for column in cursor.description[1:]]
                    print(columns)

                    # SQL-запрос для подсчета всех записей из таблицы
                    sql_query2 = "SELECT COUNT(*) FROM Ordering;"
                    connection.commit()
                    # Выполнение запроса
                    cursor.execute(sql_query2)
                    str_num = cursor.fetchone()
                    str_num = str_num['COUNT(*)']
                    print(str_num)

                    for i in range(str_num):
                        order = {}
                        for column in columns:
                            sql_query3 = f"SELECT {column} FROM Ordering WHERE ID_Ordering = {i + 1};"
                            cursor.execute(sql_query3)
                            result = cursor.fetchone()  # Получаем одну строку из результата запроса
                            if result:
                                print(result)
                                order[column] = result[column]  # Первый элемент кортежа - это значение столбца
                            else:
                                order[column] = None
                        orders.append(order)

                    # Теперь переменная entities содержит все сущности из вашей таблицы в виде списка словарей
                    print(orders)
            finally:
                # Закрытие соединения
                # connection.close()
                None

            # tableWidget - название поля
            self.orders_table_widget.setRowCount(str_num)  # Кол-во строк
            self.orders_table_widget.setColumnCount(row_index)  # Кол-во столбцов

            # Заголовки столбцов
            self.orders_table_widget.setHorizontalHeaderLabels(
                ['Номер', 'Итоговая стоимость', 'Код пользователя', 'Код товара'])

            # Ширина столбцов (индекс, ширина)
            for i in range(row_index):
                self.orders_table_widget.setColumnWidth(i, 180)

            # Заполнение QtTableWidget
            for row_index, row_data in enumerate(orders):
                for column_index, data in enumerate(row_data.values()):
                    item = QTableWidgetItem(str(data))
                    self.orders_table_widget.setItem(row_index, column_index, item)

    if __name__ == "__main__":
        app = QApplication([])
        connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=db_name,
            cursorclass=pymysql.cursors.DictCursor
        )
        cursor = connection.cursor()
        cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED")
        window = MainWindow()
        window.show()
        app.exec()






