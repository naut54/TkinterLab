from .main_controller import MainController

__version__ = '1.0.0'

DEFAULT_CODE = '''import tkinter as tk
from tkinter import ttk

def create_window(root):
    # Tu código aquí
    label = ttk.Label(root, text="¡Hola Mundo!")
    label.pack(padx=20, pady=20)
'''

ERROR_MESSAGES = {
    'no_create_window': "El código debe contener una función llamada 'create_window'",
    'invalid_parameter': "La función create_window debe tener un parámetro (normalmente llamado 'root')",
    'execution_error': "Error al ejecutar el código: {}"
}

__all__ = [
    'MainController',
    'DEFAULT_CODE',
    'ERROR_MESSAGES',
    '__version__'
]