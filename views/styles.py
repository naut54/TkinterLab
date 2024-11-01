import tkinter as tk
from tkinter import ttk

class StyleManager:
    def __init__(self):
        self.style = ttk.Style()
        self.light_bg = '#ffffff'
        self.light_fg = '#000000'
        self.light_select = '#0078d7'
        self.dark_bg = '#2b2b2b'
        self.dark_fg = '#ffffff'
        self.dark_select = '#004c8c'

    def apply_theme(self, is_dark_mode):
        theme = 'Dark' if is_dark_mode else 'Light'
        bg_color = self.dark_bg if is_dark_mode else self.light_bg
        fg_color = self.dark_fg if is_dark_mode else self.light_fg
        select_color = self.dark_select if is_dark_mode else self.light_select

        self.style.configure(f'{theme}.TFrame', background=bg_color)
        self.style.configure(f'{theme}.TLabel', background=bg_color, foreground=fg_color)
        self.style.configure(f'{theme}.TButton', background=bg_color, foreground=fg_color)
        self.style.map(f'{theme}.TButton',
            background=[('active', select_color)],
            foreground=[('active', 'white')])

        return {
            'theme': theme,
            'bg_color': bg_color,
            'fg_color': fg_color,
            'select_color': select_color
        }