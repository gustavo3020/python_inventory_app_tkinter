import tkinter as tk
import ttkbootstrap as ttk


class MainWindow(tk.Tk):
    def __init__(self, title, db_manager):
        super().__init__()
        self.title(title)
        self.db_manager = db_manager
        self.frame = Frame(self, side='top')
        self.right_frame = Frame(self.frame, side='right')
        self.left_frame = Frame(self.frame, side='left', anchor='n')

        self.info_display = InfoDisplay(self.left_frame)
        self.create_buttons()
        self.create_entrys()
        self.treeview = Treeview(self.right_frame, self.db_manager.columns)
        self.treeview.bind("<ButtonRelease-1>", self.fill_entrys)
        self.treeview.update(self.db_manager.get_data())

    def create_buttons(self):
        button_frame = Frame(
            self.right_frame, text='Options', side='top', anchor='w')
        Button(button_frame, text='Add', command=self.add_row)
        Button(button_frame, text='Update', command=self.update_row)
        Button(button_frame, text='Delete', command=self.delete_row)

    def create_entrys(self):
        entrys_frame = Frame(self.left_frame)
        self.entry_box_list = [Entry(entrys_frame, 'Name'),
                               Entry(entrys_frame, 'Quantity'),
                               Entry(entrys_frame, 'Price')]

    def add_row(self):
        column_types = self.db_manager.get_column_types()
        column_names = self.db_manager.columns
        values = [entry_box.get() for entry_box in self.entry_box_list]
        if self.validate_entrys(column_types, column_names, values) == 3:
            self.db_manager.add_row(values)
            self.info_display.update_text(
                'Entry added successfully', foreground='green')
            self.treeview.update(self.db_manager.get_data())
            for entry in self.entry_box_list:
                entry.delete(0, 'end')

    def update_row(self):
        selected_row = self.treeview.selection()
        if not selected_row:
            self.info_display.update_text(
                'Select a row to update!', foreground='red')
            return

        values = [entry_box.get() for entry_box in self.entry_box_list]
        self.db_manager.update_row(values, selected_row[0])
        self.treeview.update(self.db_manager.get_data())

    def delete_row(self):
        selected_rows = self.treeview.selection()
        if not selected_rows:
            self.info_display.update_text(
                'Select a row to delete!', foreground='red')
            return

        for row_id in selected_rows:
            self.db_manager.delete_row(row_id)
        self.info_display.update_text(
            'Entry deleted successfully', foreground='green')
        self.treeview.update(self.db_manager.get_data())

    def fill_entrys(self, event):
        for entry in self.entry_box_list:
            entry.delete(0, 'end')
        selected_row = self.treeview.selection()[0]
        data = self.treeview.item(selected_row, 'values')
        for n in range(len(data)):
            self.entry_box_list[n].insert(0, data[n])

    def validate_entrys(self, column_types, column_names, values):
        mapping = self.db_manager.type_mapping
        tests = 3
        for n in range(0, len(column_names)):
            try:
                column_name = column_names[n]
                column_type = column_types[column_name]
                type = mapping[column_type]
                type(values[n])
            except ValueError:
                self.info_display.update_text(
                    f'{column_name} must be {column_type} number!',
                    foreground="red")
                tests -= 1
        return tests


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
        self.pack()

    def configure_columns(self):
        for column in self.columns:
            self.heading(column, text=column, anchor='w')
        self.column('#0', width=0, stretch='no')
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
    def __init__(self, master, foreground=None):
        display_frame = Frame(master, text='Info', side='top')
        self.label = ttk.Label(display_frame, text='Display')
        self.label.pack()

    def update_text(self, text, foreground):
        self.label.config(text=text, foreground=foreground)


class Button(ttk.Button):
    def __init__(self, master, text=None, command=None):
        super().__init__(master, text=text, command=command)
        self.pack(side='left')


class Frame(ttk.LabelFrame):
    def __init__(self, master, text='', side='left', anchor='center'):
        super().__init__(master, text=text)
        self.pack(side=side, anchor=anchor)


class Entry(ttk.Entry):
    def __init__(self, master, text=''):
        self.frame = Frame(master, text=text, side='top')
        super().__init__(self.frame, width='40')
        self.pack()
