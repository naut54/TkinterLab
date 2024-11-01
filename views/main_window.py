import tkinter as tk
from tkinter import ttk, scrolledtext
from .styles import StyleManager

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.style_manager = StyleManager()
        self.setup_ui()

    def setup_ui(self):
        self.setup_menu()
        
        self.setup_main_panels()
        
        self.setup_buttons()

    def setup_menu(self):
        self.menubar = tk.Menu(self.root)
        self.file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Archivo", menu=self.file_menu)
        self.root.config(menu=self.menubar)

    def setup_main_panels(self):
        self.main_panel = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self.main_panel.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.setup_editor_panel()

        self.setup_output_panel()

    def setup_editor_panel(self):
        self.left_frame = ttk.Frame(self.main_panel)
        self.main_panel.add(self.left_frame, weight=7)

        self.code_label = ttk.Label(self.left_frame, text="Código Tkinter:")
        self.code_label.pack(pady=(0, 5))

        self.code_editor = scrolledtext.ScrolledText(
            self.left_frame,
            width=50,
            height=20,
            font=('Consolas', 10)
        )
        self.code_editor.pack(fill=tk.BOTH, expand=True)

    def setup_output_panel(self):
        self.right_frame = ttk.Frame(self.main_panel)
        self.main_panel.add(self.right_frame, weight=3)

        self.output_label = ttk.Label(self.right_frame, text="Salida:")
        self.output_label.pack(pady=(0, 5))

        self.output_area = scrolledtext.ScrolledText(
            self.right_frame,
            width=50,
            height=8,
            font=('Consolas', 9)
        )
        self.output_area.pack(fill=tk.BOTH, expand=True)

    def setup_buttons(self):
        self.button_frame = ttk.Frame(self.root)
        self.button_frame.pack(fill=tk.X, padx=5, pady=5)

        self.run_button = ttk.Button(
            self.button_frame,
            text="▶ Ejecutar Código"
        )
        self.run_button.pack(side=tk.LEFT, padx=5)

        self.clear_output_button = ttk.Button(
            self.button_frame,
            text="🗑 Limpiar Salida"
        )
        self.clear_output_button.pack(side=tk.LEFT, padx=5)

        self.clear_code_button = ttk.Button(
            self.button_frame,
            text="🗑 Limpiar Código"
        )
        self.clear_code_button.pack(side=tk.LEFT, padx=5)

        self.theme_button = ttk.Button(
            self.button_frame,
            text="🌓 Cambiar Tema"
        )
        self.theme_button.pack(side=tk.RIGHT, padx=5)

    def apply_theme(self, is_dark_mode):
        theme_config = self.style_manager.apply_theme(is_dark_mode)
        
        for frame in [self.left_frame, self.right_frame, self.button_frame]:
            frame.configure(style=f'{theme_config["theme"]}.TFrame')

        for editor in [self.code_editor, self.output_area]:
            editor.configure(
                bg=theme_config['bg_color'],
                fg=theme_config['fg_color'],
                insertbackground=theme_config['fg_color']
            )