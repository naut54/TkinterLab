import tkinter as tk
from tkinter import ttk, messagebox
from io import StringIO
import sys
import traceback
import re

class MainController:
    def __init__(self, view, config_manager, template_manager):
        self.view = view
        self.config_manager = config_manager
        self.template_manager = template_manager
        self.test_window = None
        self.setup_callbacks()
        self.load_initial_state()

    def setup_callbacks(self):
        self.view.file_menu.add_command(label="Guardar como plantilla", command=self.save_template)
        self.view.file_menu.add_command(label="Cargar plantilla", command=self.load_template)
        self.view.file_menu.add_separator()
        self.view.file_menu.add_command(label="Salir", command=self.view.root.quit)

        self.view.run_button.configure(command=self.run_code)
        self.view.clear_output_button.configure(command=self.clear_output)
        self.view.clear_code_button.configure(command=self.clear_code)
        self.view.theme_button.configure(command=self.toggle_theme)

        self.view.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def load_initial_state(self):
        window_size = self.config_manager.get('window_size')
        window_pos = self.config_manager.get('last_position')
        
        if window_size and window_pos:
            geometry = f"{window_size['width']}x{window_size['height']}+{window_pos['x']}+{window_pos['y']}"
            self.view.root.geometry(geometry)

        is_dark_mode = self.config_manager.get('theme') == 'dark'
        self.view.apply_theme(is_dark_mode)

        default_code = '''import tkinter as tk
from tkinter import ttk

def create_window(root):
    # Tu código aquí
    label = ttk.Label(root, text="¡Hola Mundo!")
    label.pack(padx=20, pady=20)
'''
        self.view.code_editor.insert('1.0', default_code)

    def clear_output(self):
        """Limpia el área de salida"""
        self.view.output_area.delete('1.0', tk.END)
    
    def clear_code(self):
        """Limpia el editor de código"""
        self.view.code_editor.delete('1.0', tk.END)

    def run_code(self):
        """Ejecuta el código del editor"""
        self.clear_output()
        
        try:
            code = self.view.code_editor.get('1.0', tk.END)
            
            self.check_create_window(code)
            
            if self.test_window is not None and self.test_window.winfo_exists():
                self.test_window.destroy()
            
            self.test_window = tk.Toplevel(self.view.root)
            self.test_window.title("Ventana de Prueba")
            
            old_stdout = sys.stdout
            redirected_output = StringIO()
            sys.stdout = redirected_output
            
            namespace = {}
            exec(code, namespace)
            
            namespace['create_window'](self.test_window)
            
            sys.stdout = old_stdout
            output = redirected_output.getvalue()
            if output:
                self.view.output_area.insert(tk.END, "📝 Salida:\n" + output + "\n")
                
            self.view.output_area.insert(tk.END, "✅ Código ejecutado correctamente\n", "success")
            self.view.output_area.tag_configure("success", foreground="green")
                
        except Exception as e:
            error_type = type(e).__name__
            error_msg = str(e)
            
            self.view.output_area.insert(tk.END, f"❌ Error: {error_type}\n", "error_title")
            self.view.output_area.insert(tk.END, f"📌 {error_msg}\n\n", "error_msg")
            
            tb = traceback.extract_tb(sys.exc_info()[2])
            for filename, line, func, text in tb:
                if 'create_window' in func:
                    self.view.output_area.insert(tk.END, f"📍 Línea {line}: {text}\n", "error_trace")
            
            self.view.output_area.tag_configure("error_title", foreground="red")
            self.view.output_area.tag_configure("error_msg", foreground="dark red")
            self.view.output_area.tag_configure("error_trace", foreground="gray")
            
            if self.test_window is not None and self.test_window.winfo_exists():
                self.test_window.destroy()

    def check_create_window(self, code):
        """Verifica si el código contiene la función create_window correctamente definida"""
        if 'create_window' not in code:
            raise SyntaxError("El código debe contener una función llamada 'create_window'")
        
        pattern = r'def\s+create_window\s*\(\s*(\w+)\s*\)'
        match = re.search(pattern, code)
        if not match:
            raise SyntaxError("La función create_window debe tener un parámetro (normalmente llamado 'root')")

    def save_template(self):
        """Guarda el código actual como una plantilla"""
        current_code = self.view.code_editor.get('1.0', tk.END).strip()
        if not current_code:
            tk.messagebox.showwarning("Error", "No hay código para guardar")
            return

        dialog = tk.Toplevel(self.view.root)
        dialog.title("Guardar Plantilla")
        dialog.geometry("400x300")
        
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
                tk.messagebox.showinfo("Éxito", "Plantilla guardada correctamente")
                dialog.destroy()
            except Exception as e:
                tk.messagebox.showerror("Error", str(e))
        
        ttk.Button(dialog, text="Guardar", command=save).pack(pady=20)

    def load_template(self):
        """Carga una plantilla existente"""
        dialog = tk.Toplevel(self.view.root)
        dialog.title("Cargar Plantilla")
        dialog.geometry("500x400")
        
        columns = ('name', 'category', 'updated_at')
        tree = ttk.Treeview(dialog, columns=columns, show='headings')
        
        tree.heading('name', text='Nombre')
        tree.heading('category', text='Categoría')
        tree.heading('updated_at', text='Última actualización')
        
        scrollbar = ttk.Scrollbar(dialog, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        templates = self.template_manager.get_all_templates()
        for template in templates:
            tree.insert('', tk.END, values=(template[1], template[4], template[6]))
        
        def load_selected():
            selection = tree.selection()
            if not selection:
                return
            
            item = tree.item(selection[0])
            template_name = item['values'][0]
            
            templates = self.template_manager.get_all_templates()
            template = next((t for t in templates if t[1] == template_name), None)
            
            if template:
                self.view.code_editor.delete('1.0', tk.END)
                self.view.code_editor.insert('1.0', template[3])
                dialog.destroy()
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        ttk.Button(dialog, text="Cargar", command=load_selected).pack(pady=10)

    def toggle_theme(self):
        """Alterna entre tema claro y oscuro"""
        current_theme = self.config_manager.get('theme')
        is_dark_mode = current_theme != 'dark'
        self.config_manager.set('theme', 'dark' if is_dark_mode else 'light')
        self.view.apply_theme(is_dark_mode)

    def on_closing(self):
        """Manejador para cuando se cierra la aplicación"""
        geometry = self.view.root.geometry()
        match = re.match(r'(\d+)x(\d+)\+(-?\d+)\+(-?\d+)', geometry)
        if match:
            width, height, x, y = map(int, match.groups())
            self.config_manager.set('window_size', {'width': width, 'height': height})
            self.config_manager.set('last_position', {'x': x, 'y': y})
        self.view.root.destroy()