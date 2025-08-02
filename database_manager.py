import sqlite3


class DatabaseManager():
    def __init__(self, path):
        self.table = 'produtos'
        self.type_mapping = {'INTEGER': int, 'TEXT': str, 'REAL': float}
        self.path = path
        self.columns = ('name', 'quantity', 'price')

    def create_table_if_not_exists(self):
        try:
            with sqlite3.connect(self.path) as connection:
                cursor = connection.cursor()
                cursor.execute(
                    f'''CREATE TABLE IF NOT EXISTS {self.table} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    price REAL NOT NULL)
                    ''')
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to create table: {e}")
        except Exception as e:
            raise DatabaseError(
                f'An error occurred in the database operation: {e}')

    def add_row(self, values):
        try:
            with sqlite3.connect(self.path) as connection:
                column_names_str = ', '.join(self.columns)
                sql_query = f'''INSERT INTO {self.table} ({column_names_str})
                                 VALUES (?, ?, ?)'''
                cursor = connection.cursor()
                cursor.execute(sql_query, values)
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to add new record: {e}")
        except Exception as e:
            raise DatabaseError(
                f'An error occurred in the database operation: {e}')

    def update_row(self, values, record_id):
        try:
            with sqlite3.connect(self.path) as connection:
                sql_query = f'''UPDATE {self.table}
                                SET name = ?, quantity = ?, price = ?
                                WHERE id = ?'''
                cursor = connection.cursor()
                params = tuple(values) + (record_id,)
                cursor.execute(sql_query, params)
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to update record: {e}")
        except Exception as e:
            raise DatabaseError(
                f'An error occurred in the database operation: {e}')

    def delete_rows(self, ids_to_delete):
        try:
            with sqlite3.connect(self.path) as connection:
                cursor = connection.cursor()
                placeholders = ', '.join('?' for _ in ids_to_delete)
                sql_query = f'''DELETE FROM {self.table}
                                WHERE id IN ({placeholders})'''
                cursor.execute(sql_query, tuple(ids_to_delete))
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to delete records: {e}")
        except Exception as e:
            raise DatabaseError(
                f'An error occurred in the database operation: {e}')

    def get_data(self, search_term=None, order_by_column=None,
                 order_direction='asc'):
        try:
            with sqlite3.connect(self.path) as connection:
                cursor = connection.cursor()
                query = f"SELECT * FROM {self.table}"
                params = []

                if search_term and search_term.strip():
                    search_term = search_term.strip()
                    where_clause, filter_params = self._build_filter_clause(
                        search_term)
                    query += where_clause
                    params.extend(filter_params)

                if order_by_column and order_by_column in self.columns:
                    direction = ('ASC' if order_direction.lower() == 'asc'
                                 else 'DESC')
                    query += f" ORDER BY {order_by_column} {direction}"

                cursor.execute(query, params)
                return cursor.fetchall()
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to retrieve data: {e}")
        except Exception as e:
            raise DatabaseError(
                f'An error occurred in the database operation: {e}')

    def get_column_types(self):
        column_types = {}
        try:
            with sqlite3.connect(self.path) as connection:
                cursor = connection.cursor()
                cursor.execute(f'PRAGMA table_info({self.table})')
                for column_info in cursor.fetchall():
                    column_name = column_info[1]
                    column_type = column_info[2]
                    column_types[column_name] = column_type
                return column_types
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to retrieve column types: {e}")
        except Exception as e:
            raise DatabaseError(
                f'An error occurred in the database operation: {e}')

    def _build_filter_clause(self, search_term):
        conditions = ["name LIKE ?"]
        params = [f"%{search_term}%"]

        try:
            num_search_term = float(search_term)
            conditions.append("quantity = ?")
            params.append(num_search_term)
            conditions.append("price = ?")
            params.append(num_search_term)
        except ValueError:
            pass

        conditions.append("CAST(quantity AS TEXT) LIKE ?")
        params.append(f"%{search_term}%")
        conditions.append("CAST(price AS TEXT) LIKE ?")
        params.append(f"%{search_term}%")

        where_clause = " WHERE " + " OR ".join(conditions)
        return where_clause, params


class DatabaseError(Exception):
    def __init__(self, message='An error occurred in the database operation'):
        self.message = message
        super().__init__(self.message)
