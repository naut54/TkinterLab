from .config_manager import ConfigManager
from .template_manager import TemplateManager

__version__ = '1.0.0'
__author__ = 'naut54'

def initialize_data_directory():
    """Inicializa el directorio de datos si no existe"""
    import os
    data_dir = os.path.join(os.path.expanduser('~'), '.tkinter_tester')
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    return data_dir

DATA_DIR = initialize_data_directory()

__all__ = [
    'ConfigManager',
    'TemplateManager',
    'DATA_DIR',
    '__version__',
    '__author__'
]