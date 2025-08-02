import configparser


class ConfigManager():
    """
    Manages reading from and writing to the application's configuration file.

    This class handles the creation of a default config file if one
    does not exist and provides methods to access and update settings.
    """
    _CONFIG_FILE_NAME = 'config.ini'
    default_configs = {
        'Settings': {
            'theme': 'darkly'
        }
    }

    def __init__(self):
        """
        Initializes the ConfigManager by loading or creating the config file.

        This method sets up the ConfigParser object and ensures the config
        file exists with default values if it's the first time running.
        """
        self.config = configparser.ConfigParser()
        self._load_or_create_defaults()

    def get_theme(self):
        """Returns the current theme name."""
        return self.config.get('Settings', 'theme')

    def set_theme(self, theme_name):
        """Sets the theme name and saves the config file."""
        self.config.set('Settings', 'theme', theme_name)
        self._save_configs()

    def _load_or_create_defaults(self):
        """
        Loads the config file. If the file is not found, a new one is created
        with default settings.
        """
        if not self.config.read(self._CONFIG_FILE_NAME):
            for section, values in self.default_configs.items():
                self.config.add_section(section)
                for key, value in values.items():
                    self.config.set(section, key, value)

            self._save_configs()

    def _save_configs(self):
        """
        Writes the current state of the config object to the config file.
        """
        with open(self._CONFIG_FILE_NAME, 'w') as configfile:
            self.config.write(configfile)
