import os
import configparser
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GdkPixbuf


class Maestro(Gtk.Window):
    def __init__(self, titulo="Maestro"):
        super().__init__(title=titulo)
        # Configuración para guardar tamaño y posición
        self.config_path = os.path.expanduser("~/.babelcomics.ini")
        self.config = configparser.ConfigParser()
        self.config.read(self.config_path)

        self.restore_window_settings()  # Restaurar tamaño y posición


        self.init_config()
        self.init_variables()
        print("Inicializando init_widgets")
        self.init_widgets()
        self.init_layout()
        self.init_events()
        # Guardar configuración al cerrar la ventana
        self.connect("configure-event", self.save_window_settings)
        with open(self.config_path, "w") as config_file:
            self.config.write(config_file)
        self.show_all()

    def init_widgets(self):
        print("Inicializando stack de vistas")
        self.create_headerbar()
        self.create_stack_views()
        self.create_navigation_bar()

    def create_headerbar(self):
        pass

    def create_stack_views(self):
        pass

    def create_navigation_bar(self):
        pass

    def init_config(self):
        """Inicializa la configuración de la ventana usando el nombre de la ventana como sección."""
        # Obtener el nombre de la ventana como sección
        nombre_ventana = self.get_title().lower().replace(" ", "_")  # Convertir el título en un identificador válido
        self.config_path = os.path.expanduser("~/.babelcomics_config.ini")
        self.config = configparser.ConfigParser()
        self.config.read(self.config_path)

        # Verificar si la sección existe, si no, crearla
        if not self.config.has_section(nombre_ventana):
            self.config.add_section(nombre_ventana)

        # Leer o establecer valores predeterminados
        w = int(self.config.get(nombre_ventana, "ancho", fallback="800"))
        h = int(self.config.get(nombre_ventana, "alto", fallback="600"))
        self.set_default_size(w, h)

        if self.config.has_option(nombre_ventana, "pos_x") and self.config.has_option(nombre_ventana, "pos_y"):
            x = int(self.config.get(nombre_ventana, "pos_x"))
            y = int(self.config.get(nombre_ventana, "pos_y"))
            self.move(x, y)

        # Guardar el nombre de la ventana como sección activa
        self.nombre_ventana = nombre_ventana

    def init_variables(self):
        """Inicializa las variables generales."""
        self.items_por_pagina = 20
        self.pagina_actual = 0
        self.columna_orden = "nombre"
        self.direccion_orden = "asc"

    # def init_widgets(self):
    #     """Inicializa los widgets de la ventana."""
    #     # Crear el TreeView
    #     self.treeview = Gtk.TreeView()

    #     # Inicializar el modelo y las columnas del TreeView
    #     self.init_modelo_treeview()

    #     # Crear la vista de grilla
    #     self.flowbox = Gtk.FlowBox()
    #     self.flowbox.set_max_children_per_line(5)
    #     self.flowbox.set_selection_mode(Gtk.SelectionMode.NONE)

    #     # Crear el stack de vistas
    #     self.stack = Gtk.Stack()
    #     self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
    #     self.stack.set_transition_duration(300)

    #     # Agregar vistas al stack
    #     scroll_tabla = Gtk.ScrolledWindow()
    #     scroll_tabla.add(self.treeview)
    #     self.stack.add_named(scroll_tabla, "tabla")

    #     scroll_grilla = Gtk.ScrolledWindow()
    #     scroll_grilla.add(self.flowbox)
    #     self.stack.add_named(scroll_grilla, "grilla")

    #     # Crear la barra de navegación
    #     self.boton_anterior = Gtk.Button()
    #     self.boton_anterior.set_image(Gtk.Image.new_from_pixbuf(
    #         GdkPixbuf.Pixbuf.new_from_file_at_scale("images/anterior.png", 32, 32, True)))
    #     self.boton_anterior.connect("clicked", self.ir_anterior)

    #     self.boton_siguiente = Gtk.Button()
    #     self.boton_siguiente.set_image(Gtk.Image.new_from_pixbuf(
    #         GdkPixbuf.Pixbuf.new_from_file_at_scale("images/siguiente.png", 32, 32, True)))
    #     self.boton_siguiente.connect("clicked", self.ir_siguiente)

    #     self.label_pagina = Gtk.Label()

    #     self.nav_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
    #     self.nav_box.set_halign(Gtk.Align.CENTER)
    #     self.nav_box.pack_start(self.boton_anterior, False, False, 0)
    #     self.nav_box.pack_start(self.label_pagina, False, False, 0)
    #     self.nav_box.pack_start(self.boton_siguiente, False, False, 0)
    def actualizar_navegacion(self):
        """Actualiza la barra de navegación."""
        total = self.repo.obtener_total()
        max_pagina = (total - 1) // self.items_por_pagina
        self.label_pagina.set_text(f"Página {self.pagina_actual + 1} de {max_pagina + 1}")
        self.boton_anterior.set_sensitive(self.pagina_actual > 0)
        self.boton_siguiente.set_sensitive(self.pagina_actual < max_pagina)

    def ir_anterior(self, button):
        """Navega a la página anterior."""
        self.pagina_actual = max(self.pagina_actual - 1, 0)
        if self.stack.get_visible_child_name() == "grilla":
            self.mostrar_grilla()
        else:
            self.mostrar_tabla()

    def ir_siguiente(self, button):
        """Navega a la página siguiente."""
        self.pagina_actual = self.repo.pagina_siguiente(self.pagina_actual, self.items_por_pagina)
        if self.stack.get_visible_child_name() == "grilla":
            self.mostrar_grilla()
        else:
            self.mostrar_tabla()

    def init_layout(self):
        # Organizar los widgets en la ventana
        container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        container.pack_start(self.stack, True, True, 0)
        container.pack_start(self.nav_box, False, False, 0)
        self.add(container)
        
    def create_navigation_bar(self):
        self.nav_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.nav_box.set_halign(Gtk.Align.CENTER)

        self.prev_button = Gtk.Button(label="Previous")
        self.prev_button.connect("clicked", self.ir_anterior)
        self.nav_box.pack_start(self.prev_button, False, False, 0)

        self.page_label = Gtk.Label(label="Page 1")
        self.nav_box.pack_start(self.page_label, False, False, 0)

        self.next_button = Gtk.Button(label="Next")
        self.next_button.connect("clicked", self.ir_siguiente)
        self.nav_box.pack_start(self.next_button, False, False, 0)

    def toggle_view(self, button):
        # Alternar entre la vista en lista y la vista en grilla
        current_view = self.stack.get_visible_child_name()
        if current_view == "table":
            self.stack.set_visible_child_name("grid")
        else:
            self.stack.set_visible_child_name("table")

    def create_headerbar(self):
        """Crea una barra de encabezado que utiliza el título de la ventana."""
        self.headerbar = Gtk.HeaderBar()
        self.headerbar.set_show_close_button(True)
        self.headerbar.set_title(self.get_title())  # Usar el título dinámico de la ventana
        self.set_titlebar(self.headerbar)

        toggle_view_button = Gtk.Button(label="Toggle View")
        toggle_view_button.connect("clicked", self.toggle_view)
        self.headerbar.pack_end(toggle_view_button)


    def init_layout(self):
        """Organiza los widgets en la ventana."""
        contenedor = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        contenedor.pack_start(self.stack, True, True, 0)
        contenedor.pack_start(self.nav_box, False, False, 5)
        self.add(contenedor)

    def init_events(self):
        """Conecta los eventos de la ventana."""
        self.connect("configure-event", lambda *a: self.guardar_config())

    def guardar_config(self):
        """Guarda la configuración de la ventana en la sección correspondiente."""
        x, y = self.get_position()
        w, h = self.get_size()
        self.config[self.nombre_ventana] = {
            "pos_x": str(x),
            "pos_y": str(y),
            "ancho": str(w),
            "alto": str(h),
            "vista": self.stack.get_visible_child_name()
        }
        with open(self.config_path, "w") as archivo:
            self.config.write(archivo)

    def cambiar_a_lista(self):
        """Cambia a la vista de tabla."""
        self.stack.set_visible_child_name("tabla")

    def cambiar_a_grilla(self):
        """Cambia a la vista de grilla."""
        self.stack.set_visible_child_name("grilla")

    def ir_anterior(self, button):
        """Navega a la página anterior."""
        self.pagina_actual = max(self.pagina_actual - 1, 0)

    def ir_siguiente(self, button):
        """Navega a la página siguiente."""
        self.pagina_actual += 1

    def init_modelo_treeview(self):
        """
        Inicializa el modelo y configura las columnas visibles en el TreeView.
        """
        # Crear el modelo para el TreeView
        self.store = Gtk.ListStore(int, str, str, str, str, str, str, str, int, int)
        self.treeview.set_model(self.store)

        # Configurar las columnas del TreeView
        columnas = [
            ("ID", 0), ("Nombre", 1), ("Deck", 2), ("Descripción", 3),
            ("URL", 4), ("Imagen", 5), ("ID Publisher", 6),
            ("Editorial", 7), ("Año Inicio", 8), ("# Números", 9)
        ]

        # Limpiar columnas existentes
        for columna in self.treeview.get_columns():
            self.treeview.remove_column(columna)

        # Agregar columnas visibles
        for titulo, indice in columnas:
            celda = Gtk.CellRendererText()
            columna = Gtk.TreeViewColumn(titulo, celda, text=indice)
            columna.set_resizable(True)
            self.treeview.append_column(columna)

    def restore_window_settings(self):
        """Restaura el tamaño y la posición de la ventana desde el archivo de configuración usando el nombre de la ventana."""
        nombre_ventana = self.get_title().lower().replace(" ", "_")  # Convertir el título en un identificador válido

        # Leer tamaño y posición desde la sección correspondiente
        width = int(self.config.get(nombre_ventana, "width", fallback="800"))
        height = int(self.config.get(nombre_ventana, "height", fallback="600"))
        self.set_default_size(width, height)

        if self.config.has_option(nombre_ventana, "pos_x") and self.config.has_option(nombre_ventana, "pos_y"):
            pos_x = int(self.config.get(nombre_ventana, "pos_x"))
            pos_y = int(self.config.get(nombre_ventana, "pos_y"))
            self.move(pos_x, pos_y)

    def save_window_settings(self, *args):
        """Guarda el tamaño y la posición de la ventana en el archivo de configuración usando el nombre de la ventana."""
        nombre_ventana = self.get_title().lower().replace(" ", "_")  # Convertir el título en un identificador válido

        # Obtener tamaño y posición actuales
        pos_x, pos_y = self.get_position()
        width, height = self.get_size()

        # Guardar en la sección correspondiente
        if not self.config.has_section(nombre_ventana):
            self.config.add_section(nombre_ventana)

        self.config[nombre_ventana] = {
            "pos_x": str(pos_x),
            "pos_y": str(pos_y),
            "width": str(width),
            "height": str(height),
        }

        # Escribir los cambios en el archivo de configuración
        with open(self.config_path, "w") as archivo:
            self.config.write(archivo)