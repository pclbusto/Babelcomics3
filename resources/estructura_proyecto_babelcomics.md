# 📁 Estructura del Proyecto Babelcomics

```text
babelcomics/
│
├── main.py                       # Script principal que lanza la app
├── config/                       # Configuraciones generales o setups
│   └── setup.py                  # Clase Setup y carga inicial
│
├── data/                         # Archivos persistentes generados por el sistema
│   ├── babelcomics.db            # Base de datos SQLite
│   └── thumbnails/               # Carátulas extraídas automáticamente
│
├── entidades/                    # Modelos de base de datos (SQLAlchemy)
│   ├── __init__.py
│   └── comic.py                  # Ej: Comic, Serie, Editorial, etc.
│
├── helpers/                      # Funciones utilitarias
│   ├── file_utils.py             # Ej: extracción de portada, lectura de archivos
│   ├── regex_utils.py            # Para manejo de expresiones regulares
│   └── api_client.py             # Comunicación con ComicVine u otros servicios
│
├── interfaces/                   # Scripts que usan Gtk.Builder + lógica
│   ├── __init__.py
│   ├── catalogador.py            # Pantalla principal
│   ├── editor_metadata.py        # Edición de metadata
│   └── setup_window.py           # Configuración general
│
├── glade/                        # Archivos `.ui` de Glade
│   ├── main_window.ui
│   ├── setup_window.ui
│   └── metadata_editor.ui
│
├── images/                       # Recursos gráficos estáticos (íconos, logos, etc.)
│   └── icono.svg
│
└── resources/                    # Archivos extras, plantillas, documentación interna
    └── sample_comic.cbz
```