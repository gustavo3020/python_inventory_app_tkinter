from gui_manager import MainWindow
from database_manager import DatabaseManager
from config_manager import ConfigManager

db_manager = DatabaseManager('inventory.db')
db_manager.create_table_if_not_exists()

config_manager = ConfigManager()

root = MainWindow('Inventory App', db_manager, config_manager)

root.mainloop()
