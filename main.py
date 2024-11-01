import tkinter as tk
import sys
import os
from models import ConfigManager, TemplateManager, DATA_DIR
from views import MainWindow, get_style_config
from controllers import MainController, DEFAULT_CODE

def setup_environment():
    """Configura el entorno de la aplicación"""
    os.makedirs(DATA_DIR, exist_ok=True)
    
    import logging
    logging.basicConfig(
        filename=os.path.join(DATA_DIR, 'app.log'),
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    def handle_exception(exc_type, exc_value, exc_traceback):
        logging.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
    
    sys.excepthook = handle_exception

def main():
    setup_environment()
    
    root = tk.Tk()
    root.title("Tkinter Tester")
    
    try:
        config_manager = ConfigManager(os.path.join(DATA_DIR, 'config.json'))
        template_manager = TemplateManager(os.path.join(DATA_DIR, 'templates.db'))
        
        view = MainWindow(root)
        
        controller = MainController(view, config_manager, template_manager)
        
        root.mainloop()
        
    except Exception as e:
        import logging
        logging.error(f"Error al iniciar la aplicación: {e}")
        raise

if __name__ == '__main__':
    main()