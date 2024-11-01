from .main_window import MainWindow
from .styles import StyleManager

__version__ = '1.0.0'

DEFAULT_STYLES = {
    'font_family': 'Consolas',
    'code_font_size': 10,
    'output_font_size': 9,
    'light_theme': {
        'bg': '#ffffff',
        'fg': '#000000',
        'select': '#0078d7'
    },
    'dark_theme': {
        'bg': '#2b2b2b',
        'fg': '#ffffff',
        'select': '#004c8c'
    }
}

def get_style_config():
    """Retorna la configuración de estilos"""
    return DEFAULT_STYLES

__all__ = [
    'MainWindow',
    'StyleManager',
    'get_style_config',
    'DEFAULT_STYLES',
    '__version__'
]