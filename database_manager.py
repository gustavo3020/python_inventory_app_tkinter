import sqlite3


class DatabaseManager():
    table = 'produtos'
    type_mapping = {'INTEGER': int, 'TEXT': str, 'REAL': float}

    def __init__(self, path):
        self.path = path
        self.columns = ('name', 'quantity', 'price')

    def create_table_if_not_exists(self):
        with sqlite3.connect(self.path) as connection:
            cursor = connection.cursor()
            cursor.execute(
                f'''CREATE TABLE IF NOT EXISTS {self.table} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                price REAL NOT NULL)
                ''')

    def add_row(self, values):
        with sqlite3.connect(self.path) as connection:
            cursor = connection.cursor()
            cursor.execute(f'''INSERT INTO {self.table} (name, quantity, price)
                           VALUES (?, ?, ?)''', values)

    def update_row(self, values, id):
        with sqlite3.connect(self.path) as connection:
            cursor = connection.cursor()
            cursor.execute(
                f'''UPDATE {self.table}
                SET name = ?, quantity = ?, price = ?
                WHERE id = ?''',
                (values[0], values[1], values[2], id)
            )

    def delete_row(self, id):
        with sqlite3.connect(self.path) as connection:
            cursor = connection.cursor()
            cursor.execute(f'DELETE FROM {self.table} WHERE id = {id}')

    def get_data(self):
        with sqlite3.connect(self.path) as connection:
            cursor = connection.cursor()
            query = cursor.execute(f'SELECT * FROM {self.table}')
            return query

    def get_column_types(self):
        column_types = {}
        with sqlite3.connect(self.path) as connection:
            cursor = connection.cursor()
            cursor.execute(f'PRAGMA table_info({self.table})')
            for column_info in cursor.fetchall():
                column_name = column_info[1]
                column_type = column_info[2]
                column_types[column_name] = column_type
            return column_types
