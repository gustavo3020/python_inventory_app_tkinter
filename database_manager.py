import sqlite3


class DatabaseManager():
    """
    Manages all database interactions for the inventory application.

    This class handles creating the database table, and performing CRUD
    (Create, Read, Update, Delete) operations. It uses the `sqlite3` module
    and provides a layer of abstraction to protect the GUI from direct
    database calls.

    Attributes:
        path (str): The file path to the SQLite database.
        table (str): The name of the table used for product data.
        columns (tuple): A tuple containing the column names for the table.
        type_mapping (dict): A mapping from SQLite types to Python types.
    """

    def __init__(self, path):
        """
        Initializes the DatabaseManager.

        Args:
            path (str): The file path for the SQLite database.
        """
        self.table = 'produtos'
        self.type_mapping = {'INTEGER': int, 'TEXT': str, 'REAL': float}
        self.path = path
        self.columns = ('name', 'quantity', 'price')

    def create_table_if_not_exists(self):
        """
        Creates the 'produtos' table if it does not already exist.

        Raises:
            DatabaseError: If an error occurs during the table creation
            process.
        """
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
        """
        Adds a new row of data to the database.

        Args:
            values (list): A list of values to be inserted into the table.

        Raises:
            DatabaseError: If the database operation fails.
        """
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
        """
        Updates an existing row in the database.

        Args:
            values (list): A list of new values for the row.
            record_id (int): The ID of the record to update.

        Raises:
            DatabaseError: If the database operation fails.
        """
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
        """
        Deletes one or more rows from the database.

        Args:
            ids_to_delete (list): A list of integer IDs of the records to
            delete.

        Raises:
            DatabaseError: If the database operation fails.
        """
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
        """
        Retrieves data from the database, with optional filtering and sorting.

        Args:
            search_term (str, optional): A term to search for in all relevant
            columns.
                Defaults to None.
            order_by_column (str, optional): The column name to sort the
            results by.
                Defaults to None.
            order_direction (str, optional): The direction of sorting, 'asc' or
            'desc'.
                Defaults to 'asc'.

        Returns:
            list[tuple]: A list of tuples, where each tuple represents a row
            from the database.

        Raises:
            DatabaseError: If the database query fails.
        """
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
        """
        Retrieves the column names and their data types from the database
        table.

        Returns:
            dict: A dictionary where keys are column names and values are their
            SQL data types.

        Raises:
            DatabaseError: If the database operation fails.
        """
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
        """
        Builds the SQL WHERE clause and parameters for the search query.

        This method handles searching across multiple columns
        (name, quantity, price) and casting numeric values to text for partial
        matching.

        Args:
            search_term (str): The term to search for.

        Returns:
            tuple: A tuple containing the WHERE clause string and a list of
            parameters.
        """
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
    """
    Custom exception to handle database-related errors.
    """

    def __init__(self, message='An error occurred in the database operation'):
        self.message = message
        super().__init__(self.message)
