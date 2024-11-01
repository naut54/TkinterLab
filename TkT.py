import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import sys
from io import StringIO
import traceback
import re
import json
import sqlite3
import os
from datetime import datetime

class ConfigManager:
    def __init__(self, config_file='config.json'):
        self.config_file = config_file
        self.default_config = {
            'theme': 'light',
            'font_size': 10,
            'window_size': {'width': 800, 'height': 600},
            'last_position': {'x': 100, 'y': 100},
            'recent_files': [],
            'auto_save': True
        }
        self.config = self.load_config()

    def load_config(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            return self.default_config.copy()
        except Exception as e:
            print(f"Error loading config: {e}")
            return self.default_config.copy()

    def save_config(self):
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

    def get(self, key, default=None):
        return self.config.get(key, default)

    def set(self, key, value):
        self.config[key] = value
        self.save_config()

class TemplateManager:
    def __init__(self, db_file='templates.db'):
        self.db_file = db_file
        self.init_db()

    def init_db(self):
        with sqlite3.connect(self.db_file) as conn:
            c = conn.cursor()
            # Tabla para plantillas
            c.execute('''
                CREATE TABLE IF NOT EXISTS templates (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT,
                    code TEXT NOT NULL,
                    category TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            # Tabla para tags de plantillas
            c.execute('''
                CREATE TABLE IF NOT EXISTS template_tags (
                    template_id INTEGER,
                    tag TEXT,
                    FOREIGN KEY (template_id) REFERENCES templates (id),
                    PRIMARY KEY (template_id, tag)
                )
            ''')
            conn.commit()

    def add_template(self, name, code, description="", category="general", tags=None):
        try:
            with sqlite3.connect(self.db_file) as conn:
                c = conn.cursor()
                c.execute('''
                    INSERT INTO templates (name, description, code, category, updated_at)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (name, description, code, category))
                
                template_id = c.lastrowid
                
                if tags:
                    c.executemany('''
                        INSERT INTO template_tags (template_id, tag)
                        VALUES (?, ?)
                    ''', [(template_id, tag) for tag in tags])
                
                conn.commit()
                return template_id
        except sqlite3.IntegrityError:
            raise ValueError("Una plantilla con ese nombre ya existe")

    def get_template(self, template_id):
        with sqlite3.connect(self.db_file) as conn:
            c = conn.cursor()
            c.execute('''
                SELECT t.*, GROUP_CONCAT(tt.tag) as tags
                FROM templates t
                LEFT JOIN template_tags tt ON t.id = tt.template_id
                WHERE t.id = ?
                GROUP BY t.id
            ''', (template_id,))
            return c.fetchone()

    def get_all_templates(self, category=None):
        with sqlite3.connect(self.db_file) as conn:
            c = conn.cursor()
            query = '''
                SELECT t.*, GROUP_CONCAT(tt.tag) as tags
                FROM templates t
                LEFT JOIN template_tags tt ON t.id = tt.template_id
            '''
            params = []
            if category:
                query += ' WHERE t.category = ?'
                params.append(category)
            query += ' GROUP BY t.id'
            c.execute(query, params)
            return c.fetchall()

    def update_template(self, template_id, name=None, code=None, description=None, category=None, tags=None):
        with sqlite3.connect(self.db_file) as conn:
            c = conn.cursor()
            updates = []
            params = []
            if name is not None:
                updates.append("name = ?")
                params.append(name)
            if code is not None:
                updates.append("code = ?")
                params.append(code)
            if description is not None:
                updates.append("description = ?")
                params.append(description)
            if category is not None:
                updates.append("category = ?")
                params.append(category)
            
            if updates:
                updates.append("updated_at = CURRENT_TIMESTAMP")
                query = f"UPDATE templates SET {', '.join(updates)} WHERE id = ?"
                params.append(template_id)
                c.execute(query, params)
                
                if tags is not None:
                    c.execute("DELETE FROM template_tags WHERE template_id = ?", (template_id,))
                    c.executemany('''
                        INSERT INTO template_tags (template_id, tag)
                        VALUES (?, ?)
                    ''', [(template_id, tag) for tag in tags])
                
                conn.commit()

    def delete_template(self, template_id):
        with sqlite3.connect(self.db_file) as conn:
            c = conn.cursor()
            c.execute("DELETE FROM template_tags WHERE template_id = ?", (template_id,))
            c.execute("DELETE FROM templates WHERE id = ?", (template_id,))
            conn.commit()

class TkinterTester:
        def __init__(self, root):
            self.root = root
            self.root.title("Tkinter Code Tester")
            
            # Inicializar gestores de configuración y plantillas
            self.config_manager = ConfigManager()
            self.template_manager = TemplateManager()
            
            # Cargar configuración
            self.load_application_state()
            
            # Variables de tema
            self.is_dark_mode = tk.BooleanVar(value=self.config_manager.get('theme') == 'dark')
            
            # Configurar estilos
            self.style = ttk.Style()
            self.setup_styles()
            
            # Configurar el diseño principal
            self.setup_ui()
            
            # Variable para mantener la ventana de prueba
            self.test_window = None
            
            # Configurar auto-guardado
            if self.config_manager.get('auto_save'):
                self.setup_auto_save()

        def setup_styles(self):
            """Configura los estilos para los temas claro y oscuro"""
            # Colores para el tema claro
            light_bg = '#ffffff'
            light_fg = '#000000'
            light_select = '#0078d7'
            
            # Colores para el tema oscuro
            dark_bg = '#2b2b2b'
            dark_fg = '#ffffff'
            dark_select = '#004c8c'
            
            # Configurar estilos para el tema claro
            self.style.configure('Light.TFrame', background=light_bg)
            self.style.configure('Light.TLabel', background=light_bg, foreground=light_fg)
            self.style.configure('Light.TButton', background=light_bg, foreground=light_fg)
            self.style.map('Light.TButton',
                background=[('active', light_select)],
                foreground=[('active', 'white')])
            
            # Configurar estilos para el tema oscuro
            self.style.configure('Dark.TFrame', background=dark_bg)
            self.style.configure('Dark.TLabel', background=dark_bg, foreground=dark_fg)
            self.style.configure('Dark.TButton', background=dark_bg, foreground=dark_fg)
            self.style.map('Dark.TButton',
                background=[('active', dark_select)],
                foreground=[('active', 'white')])
            
            # Configurar estilos para el Treeview
            self.style.configure('Treeview',
                background=light_bg if not self.is_dark_mode.get() else dark_bg,
                foreground=light_fg if not self.is_dark_mode.get() else dark_fg,
                fieldbackground=light_bg if not self.is_dark_mode.get() else dark_bg)
            
            # Configurar estilos para los menús
            self.style.configure('TMenubutton',
                background=light_bg if not self.is_dark_mode.get() else dark_bg,
                foreground=light_fg if not self.is_dark_mode.get() else dark_fg)

        def toggle_theme(self):
            """Alterna entre tema claro y oscuro"""
            self.is_dark_mode.set(not self.is_dark_mode.get())
            theme = 'dark' if self.is_dark_mode.get() else 'light'
            self.config_manager.set('theme', theme)
            self.setup_styles()
            
            # Actualizar colores de los widgets
            theme_style = 'Dark' if self.is_dark_mode.get() else 'Light'
            bg_color = '#2b2b2b' if self.is_dark_mode.get() else '#ffffff'
            fg_color = '#ffffff' if self.is_dark_mode.get() else '#000000'
            
            # Actualizar el editor y área de salida
            self.code_editor.configure(
                bg=bg_color,
                fg=fg_color,
                insertbackground=fg_color
            )
            self.output_area.configure(
                bg=bg_color,
                fg=fg_color,
                insertbackground=fg_color
            )
            
            # Actualizar frames y botones
            for widget in [self.left_frame, self.right_frame, self.button_frame]:
                widget.configure(style=f'{theme_style}.TFrame')
            
            # Actualizar etiquetas
            for label in [self.code_label, self.output_label]:
                label.configure(style=f'{theme_style}.TLabel')
            
            # Actualizar botones
            for button in [self.run_button, self.clear_output_button, 
                        self.clear_code_button, self.theme_button]:
                button.configure(style=f'{theme_style}.TButton')

        def load_application_state(self):
            # Cargar tamaño y posición de la ventana
            window_size = self.config_manager.get('window_size')
            window_pos = self.config_manager.get('last_position')
            
            if window_size and window_pos:
                geometry = f"{window_size['width']}x{window_size['height']}+{window_pos['x']}+{window_pos['y']}"
                self.root.geometry(geometry)

        def save_application_state(self):
            # Guardar tamaño y posición actual de la ventana
            geometry = self.root.geometry()
            match = re.match(r'(\d+)x(\d+)\+(-?\d+)\+(-?\d+)', geometry)
            if match:
                width, height, x, y = map(int, match.groups())
                self.config_manager.set('window_size', {'width': width, 'height': height})
                self.config_manager.set('last_position', {'x': x, 'y': y})

        def setup_auto_save(self):
            def auto_save():
                if hasattr(self, 'code_editor'):
                    current_code = self.code_editor.get('1.0', tk.END).strip()
                    if current_code:
                        self.config_manager.set('last_code', current_code)
                self.root.after(30000, auto_save)  # Auto-guardar cada 30 segundos
            self.root.after(30000, auto_save)

        def save_template(self):
            current_code = self.code_editor.get('1.0', tk.END).strip()
            if not current_code:
                messagebox.showwarning("Error", "No hay código para guardar")
                return

            # Crear una ventana para los detalles de la plantilla
            dialog = tk.Toplevel(self.root)
            dialog.title("Guardar Plantilla")
            dialog.geometry("400x300")
            
            # Campos del formulario
            ttk.Label(dialog, text="Nombre:").pack(pady=5)
            name_entry = ttk.Entry(dialog, width=40)
            name_entry.pack(pady=5)
            
            ttk.Label(dialog, text="Descripción:").pack(pady=5)
            desc_entry = ttk.Entry(dialog, width=40)
            desc_entry.pack(pady=5)
            
            ttk.Label(dialog, text="Categoría:").pack(pady=5)
            category_entry = ttk.Entry(dialog, width=40)
            category_entry.pack(pady=5)
            
            ttk.Label(dialog, text="Tags (separados por coma):").pack(pady=5)
            tags_entry = ttk.Entry(dialog, width=40)
            tags_entry.pack(pady=5)
            
            def save():
                try:
                    tags = [tag.strip() for tag in tags_entry.get().split(',') if tag.strip()]
                    self.template_manager.add_template(
                        name_entry.get(),
                        current_code,
                        desc_entry.get(),
                        category_entry.get(),
                        tags
                    )
                    messagebox.showinfo("Éxito", "Plantilla guardada correctamente")
                    dialog.destroy()
                except Exception as e:
                    messagebox.showerror("Error", str(e))
            
            ttk.Button(dialog, text="Guardar", command=save).pack(pady=20)

        def load_template(self):
            # Crear ventana de selección de plantilla
            dialog = tk.Toplevel(self.root)
            dialog.title("Cargar Plantilla")
            dialog.geometry("500x400")
            
            # Crear Treeview para mostrar las plantillas
            columns = ('name', 'category', 'updated_at')
            tree = ttk.Treeview(dialog, columns=columns, show='headings')
            
            tree.heading('name', text='Nombre')
            tree.heading('category', text='Categoría')
            tree.heading('updated_at', text='Última actualización')
            
            # Añadir scrollbar
            scrollbar = ttk.Scrollbar(dialog, orient=tk.VERTICAL, command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            
            # Cargar plantillas
            templates = self.template_manager.get_all_templates()
            for template in templates:
                tree.insert('', tk.END, values=(template[1], template[4], template[6]))
            
            def load_selected():
                selection = tree.selection()
                if not selection:
                    return
                
                item = tree.item(selection[0])
                template_name = item['values'][0]
                
                # Buscar la plantilla por nombre
                templates = self.template_manager.get_all_templates()
                template = next((t for t in templates if t[1] == template_name), None)
                
                if template:
                    self.code_editor.delete('1.0', tk.END)
                    self.code_editor.insert('1.0', template[3])  # template[3] es el código
                    dialog.destroy()
            
            # Organizar widgets
            tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            ttk.Button(dialog, text="Cargar", command=load_selected).pack(pady=10)

        def setup_ui(self):
    # Crear menú
            menubar = tk.Menu(self.root)
            self.root.config(menu=menubar)
            
            # Menú Archivo
            file_menu = tk.Menu(menubar, tearoff=0)
            menubar.add_cascade(label="Archivo", menu=file_menu)
            file_menu.add_command(label="Guardar como plantilla", command=self.save_template)
            file_menu.add_command(label="Cargar plantilla", command=self.load_template)
            file_menu.add_separator()
            file_menu.add_command(label="Salir", command=self.root.quit)
            
            # Panel principal
            self.main_panel = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
            self.main_panel.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            # Panel izquierdo para el código (70% del espacio)
            self.left_frame = ttk.Frame(self.main_panel, style='Light.TFrame')
            self.main_panel.add(self.left_frame, weight=7)
            
            # Editor de código
            self.code_label = ttk.Label(self.left_frame, text="Código Tkinter:", style='Light.TLabel')
            self.code_label.pack(pady=(0, 5))
            
            self.code_editor = scrolledtext.ScrolledText(
                self.left_frame, 
                width=50, 
                height=20,
                font=('Consolas', 10)
            )
            self.code_editor.pack(fill=tk.BOTH, expand=True)
    
            # Código de ejemplo por defecto
            default_code = '''import tkinter as tk
from tkinter import ttk

def create_window(root):
    # Tu código aquí
    label = ttk.Label(root, text="¡Hola Mundo!")
    label.pack(padx=20, pady=20)
            '''
            self.code_editor.insert('1.0', default_code)
            
            # Panel derecho para la salida y errores (30% del espacio)
            self.right_frame = ttk.Frame(self.main_panel, style='Light.TFrame')
            self.main_panel.add(self.right_frame, weight=3)
            
            # Área de salida
            self.output_label = ttk.Label(self.right_frame, text="Salida:", style='Light.TLabel')
            self.output_label.pack(pady=(0, 5))
            
            self.output_area = scrolledtext.ScrolledText(
                self.right_frame, 
                width=50, 
                height=8,
                font=('Consolas', 9)
            )
            self.output_area.pack(fill=tk.BOTH, expand=True)
            
            # Marco para botones
            self.button_frame = ttk.Frame(self.root, style='Light.TFrame')
            self.button_frame.pack(fill=tk.X, padx=5, pady=5)
            
            # Botones de acción
            self.run_button = ttk.Button(
                self.button_frame, 
                text="▶ Ejecutar Código",
                command=self.run_code,
                style='Light.TButton'
            )
            self.run_button.pack(side=tk.LEFT, padx=5)
            
            self.clear_output_button = ttk.Button(
                self.button_frame,
                text="🗑 Limpiar Salida",
                command=self.clear_output,
                style='Light.TButton'
            )
            self.clear_output_button.pack(side=tk.LEFT, padx=5)
            
            self.clear_code_button = ttk.Button(
                self.button_frame,
                text="🗑 Limpiar Código",
                command=self.clear_code,
                style='Light.TButton'
            )
            self.clear_code_button.pack(side=tk.LEFT, padx=5)
            
            self.theme_button = ttk.Button(
                self.button_frame,
                text="🌓 Cambiar Tema",
                command=self.toggle_theme,
                style='Light.TButton'
            )
            self.theme_button.pack(side=tk.RIGHT, padx=5)

        def clear_output(self):
            self.output_area.delete('1.0', tk.END)
    
        def clear_code(self):
            self.code_editor.delete('1.0', tk.END)

        def run_code(self):
            # Limpiar la salida anterior
            self.output_area.delete('1.0', tk.END)
            
            try:
                # Obtener el código del editor
                code = self.code_editor.get('1.0', tk.END)
                
                # Verificar la estructura del código
                self.check_create_window(code)
                
                # Cerrar la ventana de prueba anterior si existe
                if self.test_window is not None and self.test_window.winfo_exists():
                    self.test_window.destroy()
                
                # Crear nueva ventana de prueba
                self.test_window = tk.Toplevel(self.root)
                self.test_window.title("Ventana de Prueba")
                
                # Redirigir stdout para capturar la salida
                old_stdout = sys.stdout
                redirected_output = StringIO()
                sys.stdout = redirected_output
                
                # Ejecutar el código
                namespace = {}
                exec(code, namespace)
                
                # Llamar a la función create_window
                namespace['create_window'](self.test_window)
                
                # Restaurar stdout y mostrar la salida
                sys.stdout = old_stdout
                output = redirected_output.getvalue()
                if output:
                    self.output_area.insert(tk.END, "📝 Salida:\n" + output + "\n")
                    
                # Mensaje de éxito
                self.output_area.insert(tk.END, "✅ Código ejecutado correctamente\n", "success")
                self.output_area.tag_configure("success", foreground="green")
                    
            except Exception as e:
                # Formatear el error de manera más amigable
                error_type = type(e).__name__
                error_msg = str(e)
                
                self.output_area.insert(tk.END, f"❌ Error: {error_type}\n", "error_title")
                self.output_area.insert(tk.END, f"📌 {error_msg}\n\n", "error_msg")
                
                # Extraer la información relevante del traceback
                tb = traceback.extract_tb(sys.exc_info()[2])
                for filename, line, func, text in tb:
                    if 'create_window' in func:
                        self.output_area.insert(tk.END, f"📍 Línea {line}: {text}\n", "error_trace")
                
                # Configurar colores para los errores
                self.output_area.tag_configure("error_title", foreground="red")
                self.output_area.tag_configure("error_msg", foreground="dark red")
                self.output_area.tag_configure("error_trace", foreground="gray")
                
                # Cerrar la ventana de prueba si hay un error
                if self.test_window is not None and self.test_window.winfo_exists():
                    self.test_window.destroy()

        def check_create_window(self, code):
            """Verifica si el código contiene la función create_window correctamente definida"""
            if 'create_window' not in code:
                raise SyntaxError("El código debe contener una función llamada 'create_window'")
            
            # Verificar si la función tiene el parámetro root
            pattern = r'def\s+create_window\s*\(\s*(\w+)\s*\)'
            match = re.search(pattern, code)
            if not match:
                raise SyntaxError("La función create_window debe tener un parámetro (normalmente llamado 'root')")

        def on_closing(self):
            """Manejador para cuando se cierra la aplicación"""
            self.save_application_state()
            self.root.destroy()

def main():
    root = tk.Tk()
    root.title("Tkinter Code Tester")
    app = TkinterTester(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)  # Manejar cierre de ventana
    root.mainloop()

if __name__ == '__main__':
    main()