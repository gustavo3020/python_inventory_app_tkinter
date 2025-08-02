import tkinter as tk
import ttkbootstrap as ttk
from database_manager import DatabaseError


class MainWindow(tk.Tk):
    """
    The main application window for the inventory management system.

    This class inherits from `tk.Tk` and sets up the entire graphical user
    interface. It manages all user interactions, delegates data operations
    to the `DatabaseManager`, and handles UI updates and error displays.
    """

    def __init__(self, title, db_manager):
        """
        Initializes the main application window.

        This method sets up the window's title and calls helper methods to
        create all GUI components, including frames, buttons, entry widgets,
        and the Treeview.

        Args:
            title (str): The title to be displayed on the application window.
            db_manager (DatabaseManager): An instance of the DatabaseManager
                to handle all database interactions.
        """
        super().__init__()
        self.db_manager = db_manager
        self.title(title)
        self._create_frames()
        self.info_display = InfoDisplay(self.left_frame)
        self._create_buttons()
        self._create_entrys()
        self._create_search_box()
        self._setup_treeview()

    def request_sorted_data(self, column, direction):
        """
        Requests sorted data from the database and updates the Treeview.

        This method is called by the Treeview's sorting functionality. It
        fetches data using the current search term and the provided sort
        parameters, then refreshes the Treeview with the new data.

        Args:
            column (str): The column name to sort the data by.
            direction (str): The sort direction, either 'asc' or 'desc'.
        """
        self.info_display.clear_text()
        try:
            current_search_term = self.user_entry.get() if hasattr(
                self, 'user_entry') else None

            data = self.db_manager.get_data(
                search_term=current_search_term,
                order_by_column=column,
                order_direction=direction
            )
            self.treeview.update(data)
        except Exception as e:
            self._handle_exception(e)

    def add_row(self):
        """
        Handles adding a new row to the database.

        It validates the entry fields, calls the database manager to insert
        the data, updates the GUI with a success message, and refreshes the
        Treeview.
        """
        columns = self.db_manager.get_column_types()
        values = [entry_box.get() for entry_box in self.entry_box_list]
        try:
            self._validate_entrys(values, columns)
            self.db_manager.add_row(values)
            self.info_display.update_text('Entry added successfully',
                                          foreground='green', duration_ms=3000)
            self._refresh_treeview()
            self._clear_entry_boxes()

        except Exception as e:
            self._handle_exception(e)

    def update_row(self):
        """
        Handles updating a selected row in the database.

        It checks for a selected row, validates the entry fields, and calls
        the database manager to update the record. It then refreshes the
        Treeview and clears the entry boxes.
        """
        columns = self.db_manager.get_column_types()
        values = [entry_box.get() for entry_box in self.entry_box_list]
        try:
            selected_row_iid = self.treeview.selection()
            if not selected_row_iid:
                raise GUIValidationError('Select one row to update!')

            self._validate_entrys(values, columns)
            self.db_manager.update_row(values, selected_row_iid[0])
            self.info_display.update_text('Entry updated successfully',
                                          foreground='green', duration_ms=3000)
            self._refresh_treeview()
            self._clear_entry_boxes()

        except Exception as e:
            self._handle_exception(e)

    def delete_rows(self):
        """
        Handles deleting one or more selected rows from the database.

        It first prompts the user for confirmation and then deletes the
        selected records. The Treeview is refreshed upon successful deletion.
        """
        response = tk.messagebox.askyesno(
            'Confirmation',
            'Are you sure you want to delete the selected entries?')

        if not response:
            return

        try:
            selected_rows_iids = self.treeview.selection()
            if not selected_rows_iids:
                raise GUIValidationError('Select one or more rows to delete!')

            ids_to_delete = [int(iid) for iid in selected_rows_iids]
            self.db_manager.delete_rows(ids_to_delete)
            self.info_display.update_text(
                'Entry(s) deleted successfully', foreground='green',
                duration_ms=3000)
            self._refresh_treeview()

        except Exception as e:
            self._handle_exception(e)

    def _create_frames(self):
        """
        Creates the main frames for the application layout.
        """
        self.frame = Frame(self, side='top')
        self.right_frame = Frame(self.frame, side='right')
        self.left_frame = Frame(
            self.frame, side='left', anchor='n', expand=False)

    def _create_buttons(self):
        """
        Creates the control buttons for the application (Add, Update, Delete).
        """
        button_frame = Frame(
            self.right_frame, text='Options', side='top', anchor='w')
        Button(button_frame, text='Add', command=self.add_row)
        Button(button_frame, text='Update', command=self.update_row)
        Button(button_frame, text='Delete', command=self.delete_rows)

    def _create_entrys(self):
        """
        Creates the input entry boxes for data entry.
        """
        entrys_frame = Frame(self.left_frame, expand=False, side='bottom')
        self.entry_box_list = [Entry(entrys_frame, 'Name'),
                               Entry(entrys_frame, 'Quantity'),
                               Entry(entrys_frame, 'Price')]

    def _create_search_box(self):
        """
        Creates the search input field and links it to the live search
        function.
        """
        search_frame = Frame(self.left_frame, expand=False, side='bottom',
                             text='Search')
        self.user_entry = tk.StringVar()
        Entry(search_frame, textvariable=self.user_entry)
        self.user_entry.trace_add('write', self._on_string_var_change)

    def _setup_treeview(self):
        """
        Initializes the Treeview widget, binds events, and loads initial data.
        """
        self.treeview = Treeview(
            self.right_frame, self.db_manager.columns, self)
        self.treeview.bind('<ButtonRelease-1>', self._fill_entrys)
        try:
            self.treeview.update(self.db_manager.get_data())
        except DatabaseError as e:
            self.info_display.update_text(
                f"Error loading initial data: {e}", foreground='red')
        except Exception as e:
            self.info_display.update_text(
                f'''An unexpected error occurred during initial data loading:
                    {e}''', foreground='red')

    def _refresh_treeview(self):
        """
        Refreshes the Treeview with the latest data from the database,
        respecting the current search and sort parameters.
        """
        current_search_term = self.user_entry.get()
        order_by_column = self.treeview.current_sort_column
        order_direction = self.treeview.sort_direction

        data = self.db_manager.get_data(
            search_term=current_search_term,
            order_by_column=order_by_column,
            order_direction=order_direction
        )
        self.treeview.update(data)

    def _fill_entrys(self, event):
        """
        Populates the entry boxes with data from the selected row in the
        Treeview.
        """
        self.info_display.clear_text()
        self._clear_entry_boxes()
        if self.treeview.selection():
            selected_row_iid = self.treeview.selection()[0]
            data = self.treeview.item(selected_row_iid, 'values')
            for n in range(len(data)):
                self.entry_box_list[n].insert(0, data[n])

    def _validate_entrys(self, values, columns):
        """
        Validates the user input in the entry boxes against the database
        schema.

        Args:
            values (list): The list of values from the entry boxes.
            columns (dict): A dictionary of column names and their data types.

        Raises:
            GUIValidationError: If validation fails (e.g., empty fields,
                incorrect data types).
        """
        column_names = [name for name in columns if name != 'id']
        errors = []
        for i, col_name in enumerate(column_names):
            value = values[i].strip()
            if not value:
                errors.append(f'"{col_name}" cannot be empty.')
                continue

            expected_db_type = columns.get(col_name)
            if expected_db_type:
                type_converter = self.db_manager.type_mapping.get(
                    expected_db_type)
                try:
                    type_converter(value)
                except ValueError:
                    errors.append(f'"{col_name}" must be a valid '
                                  f'{expected_db_type.lower()} number.')
            else:
                errors.append(f'Internal Error: Column "{col_name}" type not '
                              f'found.')
        if errors:
            raise GUIValidationError('\n'.join(errors))

    def _on_string_var_change(self, *args):
        """
        Handles the 'write' event on the search box to trigger live filtering.
        """
        current_text = self.user_entry.get()
        data = self.db_manager.get_data(current_text)
        self.treeview.update(data)

    def _clear_entry_boxes(self):
        """
        Clears the content of all entry boxes.
        """
        for entry in self.entry_box_list:
            entry.delete(0, 'end')

    def _handle_exception(self, error):
        """
        Centralizes the handling of exceptions, displaying a user-friendly
        error message in the InfoDisplay.

        Args:
            error (Exception): The exception object to be handled.
        """
        if isinstance(error, GUIValidationError):
            message = f"Input Error: {error}"
        elif isinstance(error, DatabaseError):
            message = f"Database Error: {error}"
        else:
            message = f"An unexpected error occurred: {error}"

        self.info_display.update_text(message, foreground='red')


class Treeview(ttk.Treeview):
    """
    A custom `ttk.Treeview` widget for displaying and managing product data.

    This class configures the columns, handles sorting, and provides methods
    for updating the displayed data. It also manages scrollbars and binds
    events for user interaction.
    """

    def __init__(self, master, columns, main_window):
        """
        Initializes the custom Treeview widget.

        Args:
            master (tk.Widget): The parent widget for the Treeview.
            columns (tuple): A tuple of column names to be displayed.
            main_window (MainWindow): The main application window instance
                to enable communication with the main GUI.
        """
        self.main_window = main_window
        self.frame = Frame(master, text='Summary', side='right')
        super().__init__(self.frame)
        x_scroll = self.create_xscroll()
        y_scroll = self.create_yscroll()

        self.columns = columns
        self.configure(yscrollcommand=y_scroll.set, columns=self.columns,
                       xscrollcommand=x_scroll.set, height=30)
        self.configure_columns()
        self.pack(fill='both', expand=True)

        self.current_sort_column = None
        self.sort_direction = 'asc'

    def configure_columns(self):
        """
        Configures the Treeview columns with headings and sizes.
        """
        self.configure(show="headings")
        for column in self.columns:
            self.heading(column, text=column, anchor='w',
                         command=lambda c=column: self.sort_column(c))
        self.column('#1', width=200, stretch='no')
        self.column('#2', width=120, stretch='no')
        self.column('#3', width=100, stretch='no')

    def sort_column(self, column):
        """
        Toggles the sort direction (ascending/descending) and requests sorted
        data from the main application window.

        Args:
            column (str): The column name on which to perform the sort.
        """
        self.main_window.info_display.clear_text()

        if self.current_sort_column == column:
            self.sort_direction = ('desc' if self.sort_direction == 'asc'
                                   else 'asc')
        else:
            self.current_sort_column = column
            self.sort_direction = 'asc'

        self.main_window.request_sorted_data(column, self.sort_direction)

    def create_xscroll(self):
        """
        Creates and returns a horizontal scrollbar for the Treeview.
        """
        treescroll = ttk.Scrollbar(self.frame, orient='horizontal')
        treescroll.config(command=self.xview)
        treescroll.pack(side='bottom', fill='x')
        return treescroll

    def create_yscroll(self):
        """
        Creates and returns a vertical scrollbar for the Treeview.
        """
        treescroll = ttk.Scrollbar(self.frame, orient='vertical')
        treescroll.config(command=self.yview)
        treescroll.pack(side='right', fill='y')
        return treescroll

    def update(self, data):
        """
        Clears the existing data and inserts new data into the Treeview.

        Args:
            data (list): A list of tuples, where each tuple represents a
                row of data to be inserted.
        """
        self.delete(*self.get_children())
        for row in data:
            self.insert('', 'end', iid=row[0], values=row[1:])


class InfoDisplay:
    """
    A class to manage a `ttk.Label` widget for displaying status messages.

    It provides methods to update the text, change its color, and automatically
    clear the message after a set duration.
    """

    def __init__(self, master):
        """
        Initializes the InfoDisplay widget.

        Args:
            master (tk.Widget): The parent widget for the InfoDisplay.
        """
        display_frame = Frame(master, text='Info', side='top', expand=False)
        self.label = ttk.Label(display_frame, text='Display')
        self.label.pack()
        self.clear_job = None

    def update_text(self, text, foreground, duration_ms=None):
        """
        Updates the label with a new message and color.

        Args:
            text (str): The message to be displayed.
            foreground (str): The color of the text.
            duration_ms (int, optional): The duration in milliseconds after
                which the message should be cleared. Defaults to None.
        """
        if self.clear_job:
            self.label.after_cancel(self.clear_job)
            self.clear_job = None

        self.label.config(text=text, foreground=foreground)
        if duration_ms:
            self.clear_job = self.label.after(duration_ms, self._clear_message)

    def clear_text(self):
        """
        Immediately clears the displayed message from the label.
        """
        if self.clear_job:
            self.label.after_cancel(self.clear_job)
            self.clear_job = None
        self.label.config(text='', foreground='black')

    def _clear_message(self):
        """
        Helper method to clear the message after a delay.
        """
        self.label.config(text='', foreground='black')
        self.clear_job = None


class Button(ttk.Button):
    """
    A wrapper class for `ttk.Button` to simplify creation and packing.
    """

    def __init__(self, master, text=None, command=None, side='left', padx=5,
                 pady=5):
        super().__init__(master, text=text, command=command)
        self.pack(side=side, padx=padx, pady=pady)


class Frame(ttk.LabelFrame):
    """
    A wrapper class for `ttk.LabelFrame` to simplify creation and packing.
    """

    def __init__(self, master, text='', side='left', padx=10, pady=10,
                 anchor='center', expand=True, fill='both'):
        super().__init__(master, text=text)
        self.pack(side=side, padx=padx, pady=pady, anchor=anchor,
                  expand=expand, fill=fill)


class Entry(ttk.Entry):
    """
    A wrapper class for `ttk.Entry` to simplify creation and packing.
    """

    def __init__(self, master, text='', side='top', expand=False, width='40',
                 padx=5, pady=5, textvariable=None):
        self.frame = Frame(master, text=text, side=side, expand=expand)
        super().__init__(self.frame, width=width, textvariable=textvariable)
        self.pack(padx=padx, pady=pady)


class GUIValidationError(Exception):
    """
    Custom exception for handling GUI-related validation errors.
    """

    def __init__(self, message="Invalid input provided."):
        self.message = message
        super().__init__(self.message)
