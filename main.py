from gui_manager import MainWindow
from database_manager import DatabaseManager

db_manager = DatabaseManager('inventory.db')
db_manager.create_table_if_not_exists()

root = MainWindow('Inventory App', db_manager)

root.mainloop()
