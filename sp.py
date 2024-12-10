import sys
import sqlite3
import datetime
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QLabel, QPushButton, QTableWidget, \
    QTableWidgetItem, QComboBox, QHBoxLayout, QFormLayout, QMessageBox, QInputDialog, QStyleFactory, QHeaderView
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QFont, QIcon


# Функции работы с базой данных
def create_db():
    conn = sqlite3.connect("orders.db")
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_name TEXT NOT NULL,
        dishes TEXT NOT NULL,
        status TEXT NOT NULL,
        order_time TEXT NOT NULL,
        total_cost REAL NOT NULL,
        delivery_address TEXT NOT NULL
    )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS menu (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        price REAL NOT NULL
    )''')

    cursor.execute('SELECT COUNT(*) FROM users')
    if cursor.fetchone()[0] == 0:
        cursor.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)', ('admin', 'admin', 'admin'))

    conn.commit()
    conn.close()


def authenticate_user(username, password):
    conn = sqlite3.connect("orders.db")
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    user = cursor.fetchone()
    conn.close()
    return user


def add_order(customer_name, dishes, status, order_time, total_cost, delivery_address):
    conn = sqlite3.connect("orders.db")
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO orders (customer_name, dishes, status, order_time, total_cost, delivery_address)
                      VALUES (?, ?, ?, ?, ?, ?)''',(customer_name, dishes, status, order_time, total_cost, delivery_address))
    conn.commit()
    conn.close()


def get_orders(status_filter=None, search_filter=None):
    conn = sqlite3.connect("orders.db")
    cursor = conn.cursor()
    query = 'SELECT * FROM orders'
    if status_filter:
        query += f" WHERE status = '{status_filter}'"
    if search_filter:
        query += f" AND (customer_name LIKE '%{search_filter}%' OR dishes LIKE '%{search_filter}%')"
    cursor.execute(query)
    orders = cursor.fetchall()
    conn.close()
    return orders


def delete_order(order_id):
    conn = sqlite3.connect("orders.db")
    cursor = conn.cursor()
    cursor.execute('DELETE FROM orders WHERE id = ?', (order_id,))
    conn.commit()
    conn.close()


def update_order(order_id, customer_name, dishes, status, total_cost):
    conn = sqlite3.connect("orders.db")
    cursor = conn.cursor()
    cursor.execute('''UPDATE orders SET customer_name = ?, dishes = ?, status = ?, total_cost = ? 
                      WHERE id = ?''', (customer_name, dishes, status, total_cost, order_id))
    conn.commit()
    conn.close()


def get_menu():
    conn = sqlite3.connect("orders.db")
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM menu')
    menu = cursor.fetchall()
    conn.close()
    return menu


def add_to_cart(dish_name, quantity, cart):
    menu_item = get_menu()
    for item in menu_item:
        if item[1] == dish_name:
            total_price = item[3] * quantity
            cart.append((item[1], quantity, total_price))
            break


def add_menu_item(name, description, price):
    conn = sqlite3.connect("orders.db")
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO menu (name, description, price) VALUES (?, ?, ?)''', (name, description, price))
    conn.commit()
    conn.close()


def delete_menu_item(menu_id):
    conn = sqlite3.connect("orders.db")
    cursor = conn.cursor()
    cursor.execute('DELETE FROM menu WHERE id = ?', (menu_id,))
    conn.commit()
    conn.close()


# Функции для работы с пользователями
def get_users():
    conn = sqlite3.connect("orders.db")
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
    conn.close()
    return users


def delete_user(user_id):
    conn = sqlite3.connect("orders.db")
    cursor = conn.cursor()
    cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()


# Экран авторизации
class AuthWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Авторизация")
        self.setGeometry(100, 100, 400, 250)

        self.layout = QVBoxLayout()
        self.layout.setSpacing(10)

        self.username_input = QLineEdit(self)
        self.username_input.setPlaceholderText("Логин")
        self.username_input.setStyleSheet("padding: 10px; font-size: 14px; border: 2px solid #ddd; border-radius: 5px;")

        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText("Пароль")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("padding: 10px; font-size: 14px; border: 2px solid #ddd; border-radius: 5px;")

        self.login_button = QPushButton("Войти", self)
        self.login_button.setStyleSheet(
            "padding: 10px 15px; font-size: 14px; background-color: #4CAF50; color: white; border-radius: 5px;")
        self.login_button.clicked.connect(self.authenticate)

        self.register_button = QPushButton("Зарегистрироваться", self)
        self.register_button.setStyleSheet(
            "padding: 10px 15px; font-size: 14px; background-color: #2196F3; color: white; border-radius: 5px;")
        self.register_button.clicked.connect(self.register)

        self.layout.addWidget(QLabel("Логин"))
        self.layout.addWidget(self.username_input)
        self.layout.addWidget(QLabel("Пароль"))
        self.layout.addWidget(self.password_input)
        self.layout.addWidget(self.login_button)
        self.layout.addWidget(self.register_button)

        self.setLayout(self.layout)

    def authenticate(self):
        username = self.username_input.text()
        password = self.password_input.text()

        user = authenticate_user(username, password)
        if user:
            if user[3] == 'admin':
                self.open_admin_window(user)
            elif user[3] == 'user':
                self.open_menu_window()
            else:
                self.show_message("Ошибка", "Недостаточно прав доступа.")
        else:
            self.show_message("Ошибка", "Неверный логин или пароль.")

    def register(self):
        username = self.username_input.text()
        password = self.password_input.text()
        conn = sqlite3.connect("orders.db")
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
                       (username, password, "user"))
        conn.commit()
        conn.close()
        self.show_message("Успех", "Вы успешно зарегистрировались!")

    def open_admin_window(self, user):
        self.admin_window = AdminWindow(user)
        self.admin_window.show()
        self.close()

    def open_menu_window(self):
        self.menu_window = MenuWindow()
        self.menu_window.show()
        self.close()

    def show_message(self, title, text):
        QMessageBox.information(self, title, text)


# Окно для администраторов
class AdminWindow(QWidget):
    def __init__(self, user):
        super().__init__()
        self.setWindowTitle("Админ Панель")
        self.setGeometry(100, 100, 1000, 600)

        self.layout = QVBoxLayout()

        self.orders_table = QTableWidget(self)
        self.orders_table.setColumnCount(8)
        self.orders_table.setHorizontalHeaderLabels(["ID", "Клиент", "Блюда", "Статус", "Дата", "Стоимость", "Адрес доставки", "Удалить"])
        self.orders_table.horizontalHeader().setStretchLastSection(True)
        self.orders_table.setStyleSheet("""
        QTableWidget {
            font-size: 14px;
            border: 1px solid #ddd;
            background-color: #f9f9f9;
            border-radius: 8px;
        }
        QHeaderView::section {
            background-color: #4CAF50;
            color: white;
            padding: 8px;
            font-size: 14px;
        }
        QTableWidget::item {
            padding: 8px;
        }
        QTableWidget QPushButton {
            background-color: #FF5722;
            color: white;
            border: none;
            padding: 20px 20px;
            border-radius: 5px;
        }
        QTableWidget QPushButton:hover {
            background-color: #FF3D00;
        }
        """)
        self.update_orders()

        self.users_table = QTableWidget(self)
        self.users_table.setColumnCount(4)
        self.users_table.setHorizontalHeaderLabels(["ID", "Логин", "Роль", "Удалить"])
        self.users_table.setStyleSheet("""
        QTableWidget {
            font-size: 14px;
            border: 1px solid #ddd;
            background-color: #f9f9f9;
            padding: 20px 20px;
            padding: 10px;
        }
        QTableWidget::item {
            padding: 8px;
        }
        QTableWidget QHeaderView::section {
            background-color: #4CAF50;
            color: white;
            padding: 8px;
            font-size: 14px;
        }
        QTableWidget QPushButton {
            background-color: #FF5722;
            color: white;
            border: none;
            padding: 20px 20px;
            border-radius: 5px;
        }
        QPushButton:hover {
            background-color: #FF3D00;
        }
     """)

        self.update_users()

        self.add_menu_button = QPushButton("Добавить блюдо")
        self.add_menu_button.setStyleSheet("""
        QPushButton {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 12px 20px;
            border-radius: 8px;
            font-size: 16px;
        }
        QPushButton:hover {
            background-color: #45a049;
        }
        QPushButton:pressed {
            background-color: #388e3c;
        }
    """)
        self.add_menu_button.clicked.connect(self.add_menu_item)

        self.delete_menu_button = QPushButton("Удалить блюдо")
        self.delete_menu_button.setStyleSheet("""
        QPushButton {
            background-color: #f44336;
            color: white;
            border: none;
            padding: 12px 20px;
            border-radius: 8px;
            font-size: 16px;
        }
        QPushButton:hover {
            background-color: #e53935;
        }
        QPushButton:pressed {
            background-color: #d32f2f;
        }
    """)
        self.delete_menu_button.clicked.connect(self.delete_menu_item)

        self.layout.addWidget(QLabel("Заказы"))
        self.layout.addWidget(self.orders_table)
        self.layout.addWidget(QLabel("Пользователи"))
        self.layout.addWidget(self.users_table)
        self.layout.addWidget(self.add_menu_button)
        self.layout.addWidget(self.delete_menu_button)

        self.setLayout(self.layout)

    def update_orders(self):
        orders = get_orders()
        self.orders_table.setRowCount(len(orders))

        for row_idx, order in enumerate(orders):
            self.orders_table.setItem(row_idx, 0, QTableWidgetItem(str(order[0])))  # ID
            self.orders_table.setItem(row_idx, 1, QTableWidgetItem(order[1]))  # Customer
            self.orders_table.setItem(row_idx, 2, QTableWidgetItem(order[2]))  # Dishes
            self.orders_table.setItem(row_idx, 3, QTableWidgetItem(order[3]))  # Status
            self.orders_table.setItem(row_idx, 4, QTableWidgetItem(order[4]))  # Order Time
            self.orders_table.setItem(row_idx, 5, QTableWidgetItem(str(order[5])))  # Total cost
            self.orders_table.setItem(row_idx, 6, QTableWidgetItem(order[6]))  # Delivery Address

            delete_button = QPushButton("Удалить")
            delete_button.clicked.connect(lambda _, order_id=order[0]: self.delete_order(order_id))
            self.orders_table.setCellWidget(row_idx, 7, delete_button)

    def delete_order(self, order_id):
        confirmation = QMessageBox.question(self, "Удалить заказ", f"Вы уверены, что хотите удалить заказ {order_id}?",
                                            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if confirmation == QMessageBox.Yes:
            delete_order(order_id)
            self.update_orders()

    def update_users(self):
        users = get_users()
        self.users_table.setRowCount(len(users))

        for row_idx, user in enumerate(users):
            self.users_table.setItem(row_idx, 0, QTableWidgetItem(str(user[0])))  # ID
            self.users_table.setItem(row_idx, 1, QTableWidgetItem(user[1]))  # Username
            self.users_table.setItem(row_idx, 2, QTableWidgetItem(user[3]))  # Role

            delete_button = QPushButton("Удалить")
            delete_button.clicked.connect(lambda _, user_id=user[0]: self.delete_user(user_id))
            self.users_table.setCellWidget(row_idx, 3, delete_button)

    def delete_user(self, user_id):
        confirmation = QMessageBox.question(self, "Удалить пользователя",
                                            f"Вы уверены, что хотите удалить пользователя {user_id}?",
                                            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if confirmation == QMessageBox.Yes:
            delete_user(user_id)
            self.update_users()

    def add_menu_item(self):
        name, ok = QInputDialog.getText(self, "Добавить блюдо", "Введите название блюда:")
        if ok:
            description, ok = QInputDialog.getText(self, "Добавить описание", "Введите описание блюда:")
            if ok:
                price, ok = QInputDialog.getDouble(self, "Добавить цену", "Введите цену блюда:")
                if ok:
                    add_menu_item(name, description, price)
                    self.show_message("Успех", "Блюдо добавлено в меню!")
                    self.update_orders()

    def delete_menu_item(self):
        item_id, ok = QInputDialog.getInt(self, "Удалить блюдо", "Введите ID блюда для удаления:")
        if ok:
            delete_menu_item(item_id)
            self.show_message("Успех", "Блюдо удалено из меню!")
            self.update_orders()

    def show_message(self, title, text):
        QMessageBox.information(self, title, text)

# Окно для пользователей
class MenuWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Меню")
        self.setGeometry(100, 100, 600, 400)

        self.layout = QVBoxLayout()
        self.cart = []  # Корзина для товаров

        self.menu_table = QTableWidget(self)
        self.menu_table.setColumnCount(4)
        self.menu_table.setHorizontalHeaderLabels(["Блюдо", "Описание", "Цена", "Количество"])
        self.menu_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.update_menu()

        self.add_to_cart_button = QPushButton("Добавить в корзину", self)
        self.add_to_cart_button.setStyleSheet("""
        QPushButton {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 12px 20px;
            border-radius: 8px;
            font-size: 16px;
        }
        QPushButton:hover {
            background-color: #45a049;
        }
        QPushButton:pressed {
            background-color: #388e3c;
        }
    """)
        self.add_to_cart_button.clicked.connect(self.add_to_cart)

        self.checkout_button = QPushButton("Оформить заказ", self)
        self.checkout_button.setStyleSheet("""
        QPushButton {
            background-color: #2196F3;
            color: white;
            border: none;
            padding: 12px 20px;
            border-radius: 8px;
            font-size: 16px;
        }
        QPushButton:hover {
            background-color: #1976D2;
        }
        QPushButton:pressed {
            background-color: #1565C0;
        }
    """)
        self.checkout_button.clicked.connect(self.checkout)

        self.layout.addWidget(self.menu_table)
        self.layout.addWidget(self.add_to_cart_button)
        self.layout.addWidget(self.checkout_button)

        self.setLayout(self.layout)

    def update_menu(self):
        menu_items = get_menu()
        self.menu_table.setRowCount(len(menu_items))

        for row_idx, item in enumerate(menu_items):
            self.menu_table.setItem(row_idx, 0, QTableWidgetItem(item[1]))  # Название блюда
            self.menu_table.setItem(row_idx, 1, QTableWidgetItem(item[2]))  # Описание
            self.menu_table.setItem(row_idx, 2, QTableWidgetItem(str(item[3])))  # Цена
            quantity_item = QTableWidgetItem("1")  # По умолчанию 1 штука
            quantity_item.setFlags(quantity_item.flags() & ~Qt.ItemIsEditable)
            self.menu_table.setItem(row_idx, 3, quantity_item)

    def add_to_cart(self):
        selected_row = self.menu_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите блюдо.")
            return

        dish_name = self.menu_table.item(selected_row, 0).text()
        price = float(self.menu_table.item(selected_row, 2).text())
        quantity = 1  # Количество по умолчанию

        # Проверка, есть ли блюдо уже в корзине
        for item in self.cart:
            if item[0] == dish_name:
                QMessageBox.warning(self, "Ошибка", f"{dish_name} уже добавлено в корзину.")
                return

        # Добавление в корзину
        total_price = price * quantity
        self.cart.append((dish_name, quantity, total_price))
        QMessageBox.information(self, "Успех", f"{dish_name} добавлено в корзину.")

    def checkout(self):
        if not self.cart:
            QMessageBox.warning(self, "Ошибка", "Корзина пуста.")
            return

        customer_name, ok = QInputDialog.getText(self, "Оформить заказ", "Введите имя клиента:")
        if not ok or not customer_name.strip():
            QMessageBox.warning(self, "Ошибка", "Имя клиента не может быть пустым.")
            return

        delivery_address, ok = QInputDialog.getText(self, "Адрес доставки", "Введите адрес доставки:")
        if not ok or not delivery_address.strip():
            QMessageBox.warning(self, "Ошибка", "Адрес доставки не может быть пустым.")
            return

        # Формирование заказа
        dishes = ", ".join([f"{item[0]} x{item[1]}" for item in self.cart])
        total_cost = sum([item[2] for item in self.cart])
        order_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = "Принят"

        # Сохранение заказа в БД
        add_order(customer_name, dishes, status, order_time, total_cost, delivery_address)
        QMessageBox.information(self, "Успех", "Ваш заказ успешно оформлен!")

        # Очистка корзины
        self.cart.clear()



if __name__ == "__main__":
    create_db()
    app = QApplication(sys.argv)
    app.setStyle(QStyleFactory.create("Fusion"))
    window = AuthWindow()
    window.show()
    sys.exit(app.exec_())
