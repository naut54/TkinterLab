# 🚀 TkinterLab - Entorno de Pruebas para Tkinter

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

TkinterLab es un entorno de desarrollo interactivo diseñado específicamente para probar y experimentar con código Tkinter de manera rápida y eficiente. Con características como guardado de plantillas, tema oscuro y seguimiento de errores en tiempo real.

## ✨ Características Principales

- 🎨 **Editor de Código Integrado**
  - Resaltado de sintaxis para Python

- 💾 **Sistema de Plantillas**
  - Guarda tus snippets favoritos
  - Organización por tags
  - Importación/Exportación de plantillas

- 🌙 **Tema Oscuro/Claro**
  - Cambia entre temas con un clic
  - Personalización de colores
  - Diseño moderno y minimalista

- 🐛 **Depuración en Tiempo Real**
  - Terminal integrada para output
  - Resaltado de errores

## 🚀 Instalación

```bash
# Clonar el repositorio
git clone https://github.com/usuario/tkinterlab.git

# Entrar al directorio
cd tkinterlab

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar la aplicación
python main.py
```

## 📖 Uso Básico

1. **Iniciar un Nuevo Proyecto**
   ```python
   # Ejemplo básico de ventana Tkinter
   import tkinter as tk
   
   root = tk.Tk()
   root.title("Mi Aplicación")
   
   label = tk.Label(root, text="¡Hola Mundo!")
   label.pack()
   
   root.mainloop()
   ```

2. **Guardar Plantillas**
   - Ve a `Plantilla` para guardar el código actual como plantilla
   - Asigna un nombre y categoría para fácil acceso
   - Las plantillas se guardan en `templates.db`

3. **Ejecutar Código**
   - Usa `F5` para ejecutar el código actual
   - Los errores aparecerán en la terminal integrada
   - El output se muestra en tiempo real

## 🛠️ Requisitos del Sistema

- Python 3.8 o superior
- Tkinter (incluido en la instalación estándar de Python)
- Sistema operativo: Windows/Linux/MacOS

## 📚 Estructura del Proyecto

```
tkinterlab/
├── main.py
├── __init__.py
├── config.json
├── controllers/
│   ├── __init__.py
│   └── main_controller.py
├── models/
|   ├── __init__.py
|   ├── config_manager.py
|   └── template_manager.py
└── views/
    ├── __init__.py
    ├── main_window.py
    ├── styles.py
    └── template_dialogs.py

```

## 📝 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## 🙏 Agradecimientos

- [Tkinter Documentation](https://docs.python.org/3/library/tkinter.html)
- [Python Community](https://www.python.org/community/)
