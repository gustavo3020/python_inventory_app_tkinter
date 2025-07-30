import tkinter as tk
import ttkbootstrap as ttk
from database_manager import DatabaseError


class MainWindow(tk.Tk):
    def __init__(self, title, db_manager):
        super().__init__()
        self.title(title)
        self.create_frames()
        self.info_display = InfoDisplay(self.left_frame)
        self.create_buttons()
        self.create_entrys()

        self.db_manager = db_manager
        self.treeview = Treeview(self.right_frame, self.db_manager.columns)
        self.treeview.bind('<ButtonRelease-1>', self.fill_entrys)
        try:
            self.treeview.update(self.db_manager.get_data())
        except DatabaseError as e:
            self.info_display.update_text(
                f"Error loading initial data: {e}", foreground='red')
        except Exception as e:
            self.info_display.update_text(
                f'''An unexpected error occurred during initial data loading:
                    {e}''', foreground='red')

    def create_frames(self):
        self.frame = Frame(self, side='top')
        self.right_frame = Frame(self.frame, side='right')
        self.left_frame = Frame(
            self.frame, side='left', anchor='n', expand=False)

    def create_buttons(self):
        button_frame = Frame(
            self.right_frame, text='Options', side='top', anchor='w')
        Button(button_frame, text='Add', command=self.add_row)
        Button(button_frame, text='Update', command=self.update_row)
        Button(button_frame, text='Delete', command=self.delete_row)

    def create_entrys(self):
        entrys_frame = Frame(self.left_frame, expand=False, side='bottom')
        self.entry_box_list = [Entry(entrys_frame, 'Name'),
                               Entry(entrys_frame, 'Quantity'),
                               Entry(entrys_frame, 'Price')]

    def add_row(self):
        columns = self.db_manager.get_column_types()
        values = [entry_box.get() for entry_box in self.entry_box_list]
        try:
            self.validate_entrys(values, columns)
            self.db_manager.add_row(values)
            self.info_display.update_text('Entry added successfully',
                                          foreground='green', duration_ms=3000)
            self.treeview.update(self.db_manager.get_data())
            for entry in self.entry_box_list:
                entry.delete(0, 'end')

        except GUIValidationError as e:
            self.info_display.update_text(
                f"Input Error:\n{e}", foreground='red')
        except DatabaseError as e:
            self.info_display.update_text(
                f"Database Error:\n{e}", foreground='red')
        except Exception as e:
            self.info_display.update_text(
                f"An unexpected error occurred:\n{e}", foreground='red')

    def update_row(self):
        columns = self.db_manager.get_column_types()
        values = [entry_box.get() for entry_box in self.entry_box_list]
        try:
            selected_row_iid = self.treeview.selection()
            if not selected_row_iid:
                raise GUIValidationError('Select one row to update!')

            self.validate_entrys(values, columns)
            self.db_manager.update_row(values, selected_row_iid[0])
            self.treeview.update(self.db_manager.get_data())
            for entry in self.entry_box_list:
                entry.delete(0, 'end')
        except GUIValidationError as e:
            self.info_display.update_text(
                f"Selection Error: {e}", foreground='red')
        except DatabaseError as e:
            self.info_display.update_text(
                f"Database Error: {e}", foreground='red')
        except Exception as e:
            self.info_display.update_text(
                f"An unexpected error occurred: {e}", foreground='red')

    def delete_row(self):
        try:
            selected_rows_iids = self.treeview.selection()
            if not selected_rows_iids:
                raise GUIValidationError('Select one or more rows to delete!')

            ids_to_delete = [int(iid) for iid in selected_rows_iids]
            self.db_manager.delete_rows(ids_to_delete)
            self.info_display.update_text(
                'Entry(s) deleted successfully', foreground='green')
            self.treeview.update(self.db_manager.get_data())

        except GUIValidationError as e:
            self.info_display.update_text(
                f"Selection Error: {e}", foreground='red')
        except DatabaseError as e:
            self.info_display.update_text(
                f"Database Error: {e}", foreground='red')
        except Exception as e:
            self.info_display.update_text(
                f"An unexpected error occurred: {e}", foreground='red')

    def fill_entrys(self, event):
        self.info_display.clear_text()
        for entry in self.entry_box_list:
            entry.delete(0, 'end')
        if self.treeview.selection():
            selected_row_iid = self.treeview.selection()[0]
            data = self.treeview.item(selected_row_iid, 'values')
            for n in range(len(data)):
                self.entry_box_list[n].insert(0, data[n])

    def validate_entrys(self, values, columns):
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


class Treeview(ttk.Treeview):
    def __init__(self, master, columns):
        self.frame = Frame(master, text='Summary', side='right')
        super().__init__(self.frame)
        x_scroll = self.create_xscroll()
        y_scroll = self.create_yscroll()

        self.columns = columns
        self.configure(yscrollcommand=y_scroll.set, columns=self.columns,
                       xscrollcommand=x_scroll.set, height=30)
        self.configure_columns()
        self.pack(fill='both', expand=True)

    def configure_columns(self):
        self.configure(show="headings")
        for column in self.columns:
            self.heading(column, text=column, anchor='w')
        self.column('#1', width=200, stretch='no')
        self.column('#2', width=120, stretch='no')
        self.column('#3', width=100, stretch='no')

    def create_xscroll(self):
        treescroll = ttk.Scrollbar(self.frame, orient='horizontal')
        treescroll.config(command=self.xview)
        treescroll.pack(side='bottom', fill='x')
        return treescroll

    def create_yscroll(self):
        treescroll = ttk.Scrollbar(self.frame, orient='vertical')
        treescroll.config(command=self.yview)
        treescroll.pack(side='right', fill='y')
        return treescroll

    def update(self, data):
        self.delete(*self.get_children())
        for row in data:
            self.insert('', 'end', iid=row[0], values=row[1:])


class InfoDisplay:
    def __init__(self, master):
        display_frame = Frame(master, text='Info', side='top', expand=False)
        self.label = ttk.Label(display_frame, text='Display')
        self.label.pack()
        self.clear_job = None

    def update_text(self, text, foreground, duration_ms=None):
        if self.clear_job:
            self.label.after_cancel(self.clear_job)
            self.clear_job = None

        self.label.config(text=text, foreground=foreground)
        if duration_ms:
            self.clear_job = self.label.after(duration_ms, self._clear_message)

    def clear_text(self):
        if self.clear_job:
            self.label.after_cancel(self.clear_job)
            self.clear_job = None
        self.label.config(text='', foreground='black')

    def _clear_message(self):
        self.label.config(text='', foreground='black')
        self.clear_job = None


class Button(ttk.Button):
    def __init__(self, master, text=None, command=None):
        super().__init__(master, text=text, command=command)
        self.pack(side='left', padx=5, pady=5)


class Frame(ttk.LabelFrame):
    def __init__(self, master, text='', side='left', anchor='center',
                 expand=True, fill='both'):
        super().__init__(master, text=text)
        self.pack(side=side, anchor=anchor, padx=10, pady=10, expand=expand,
                  fill=fill)


class Entry(ttk.Entry):
    def __init__(self, master, text=''):
        self.frame = Frame(master, text=text, side='top', expand=False)
        super().__init__(self.frame, width='40')
        self.pack(padx=5, pady=5)


class GUIValidationError(Exception):
    def __init__(self, message="Invalid input provided."):
        self.message = message
        super().__init__(self.message)
