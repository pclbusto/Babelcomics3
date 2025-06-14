import os
import configparser
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GdkPixbuf

from repositories.volume_repository import VolumeRepository

class VolumeWindow(Gtk.Window):
    def __init__(self, session):
        self.repo = VolumeRepository(session)
        super().__init__(title="Volúmenes Management")
        self.actualizar_vista()

    def init_variables(self):
        self.volumenes_por_pagina = 20
        self.pagina_actual = 0
        self.columna_orden = "nombre"
        self.direccion_orden = "asc"
        self.pagina_actual = 0

    def init_widgets(self):
        # Crear el modelo para el TreeView
        self.store = Gtk.ListStore(int, str, str, str, str, str, str, str, int, int)
        
        # Crear el TreeView y vincularlo al modelo
        self.treeview = Gtk.TreeView(model=self.store)
        
        # Configurar las columnas del TreeView
        columnas = [
            ("ID", 0), ("Nombre", 1), ("Deck", 2), ("Descripción", 3),
            ("URL", 4), ("Imagen", 5), ("ID Publisher", 6),
            ("Editorial", 7), ("Año Inicio", 8), ("# Números", 9)
        ]
        for titulo, indice in columnas:
            celda = Gtk.CellRendererText()
            columna = Gtk.TreeViewColumn(titulo, celda, text=indice)
            columna.set_resizable(True)
            self.treeview.append_column(columna)
        
        # Llamar a otros métodos de inicialización
        self.crear_headerbar()
        self.crear_filtros_ocultos()
        self.crear_barra_navegacion()
        self.crear_stack_de_vistas()

    def init_layout(self):
        contenedor = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        contenedor.pack_start(self.revealer_filtros, False, False, 0)
        contenedor.pack_start(self.stack, True, True, 0)
        contenedor.pack_start(self.nav_box, False, False, 5)
        self.add(contenedor)

    def init_events(self):
        self.connect("configure-event", lambda *a: self.guardar_config())
        self.connect("key-press-event", self.on_key_press)

    def toggle_filtros(self, button=None):
        visible = self.revealer_filtros.get_reveal_child()
        self.revealer_filtros.set_reveal_child(not visible)

    def crear_headerbar(self):
        self.headerbar = Gtk.HeaderBar()
        self.headerbar.set_show_close_button(True)
        self.headerbar.set_title("Volúmenes")
        self.set_titlebar(self.headerbar)

        boton_lista = Gtk.Button()
        boton_lista.set_image(Gtk.Image.new_from_pixbuf(
            GdkPixbuf.Pixbuf.new_from_file_at_scale("images/vista_lista.png", 24, 24, True)))
        boton_lista.connect("clicked", self.cambiar_a_lista)

        boton_grilla = Gtk.Button()
        boton_grilla.set_image(Gtk.Image.new_from_pixbuf(
            GdkPixbuf.Pixbuf.new_from_file_at_scale("images/vista_grilla.png", 24, 24, True)))
        boton_grilla.connect("clicked", self.cambiar_a_grilla)

        boton_filtro = Gtk.Button()
        boton_filtro.set_image(Gtk.Image.new_from_pixbuf(
            GdkPixbuf.Pixbuf.new_from_file_at_scale("images/filtrar.png", 24, 24, True)))
        boton_filtro.connect("clicked", self.toggle_filtros)

        box_vistas = Gtk.Box(spacing=2)
        box_vistas.pack_start(boton_lista, False, False, 0)
        box_vistas.pack_start(boton_grilla, False, False, 0)

        self.headerbar.pack_start(box_vistas)
        self.headerbar.pack_end(boton_filtro)

    def crear_stack_de_vistas(self):
        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.stack.set_transition_duration(300)

        # Verifica si el TreeView ya está en un contenedor y elimínalo
        if self.treeview.get_parent():
            self.treeview.get_parent().remove(self.treeview)

        # Crear la vista de tabla
        scroll_tabla = Gtk.ScrolledWindow()
        scroll_tabla.add(self.treeview)
        self.stack.add_named(scroll_tabla, "tabla")

        # Crear la vista de grilla
        self.flowbox = Gtk.FlowBox()
        self.flowbox.set_max_children_per_line(5)
        self.flowbox.set_selection_mode(Gtk.SelectionMode.NONE)
        scroll_grilla = Gtk.ScrolledWindow()
        scroll_grilla.add(self.flowbox)
        self.stack.add_named(scroll_grilla, "grilla")

        vista_predeterminada = self.config.get("Vista", "modo", fallback="tabla")
        self.vista_predeterminada = vista_predeterminada

    def crear_barra_navegacion(self):
        self.boton_anterior = Gtk.Button()
        self.boton_anterior.set_image(Gtk.Image.new_from_pixbuf(GdkPixbuf.Pixbuf.new_from_file_at_scale("images/anterior.png", 32, 32, True)))
        self.boton_anterior.connect("clicked", self.ir_anterior)

        self.boton_siguiente = Gtk.Button()
        self.boton_siguiente.set_image(Gtk.Image.new_from_pixbuf(GdkPixbuf.Pixbuf.new_from_file_at_scale("images/siguiente.png", 32, 32, True)))
        self.boton_siguiente.connect("clicked", self.ir_siguiente)

        self.label_pagina = Gtk.Label()

        self.nav_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.nav_box.set_halign(Gtk.Align.CENTER)
        self.nav_box.pack_start(self.boton_anterior, False, False, 0)
        self.nav_box.pack_start(self.label_pagina, False, False, 0)
        self.nav_box.pack_start(self.boton_siguiente, False, False, 0)

    def crear_filtros_ocultos(self):
        self.revealer_filtros = Gtk.Revealer()
        self.revealer_filtros.set_transition_type(Gtk.RevealerTransitionType.SLIDE_DOWN)
        self.revealer_filtros.set_reveal_child(False)

        filtros_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.entrada_nombre = Gtk.Entry()
        self.entrada_nombre.set_placeholder_text("Filtrar por nombre")
        filtros_box.pack_start(self.entrada_nombre, False, False, 0)

        self.combo_editorial = Gtk.ComboBoxText()
        self.combo_editorial.append_text("Todas")
        self.combo_editorial.append_text("DC")
        self.combo_editorial.append_text("Marvel")
        self.combo_editorial.append_text("Image")
        self.combo_editorial.set_active(0)
        filtros_box.pack_start(self.combo_editorial, False, False, 0)

        boton_aplicar = Gtk.Button(label="Aplicar")
        boton_aplicar.connect("clicked", self.aplicar_filtros)
        filtros_box.pack_start(boton_aplicar, False, False, 0)

        self.revealer_filtros.add(filtros_box)

    def cambiar_a_lista(self, button=None):
        self.stack.set_visible_child_name("tabla")
        self.mostrar_tabla()
        self.guardar_config()

    def cambiar_a_grilla(self, button=None):
        self.stack.set_visible_child_name("grilla")
        self.mostrar_grilla()
        self.guardar_config()

    def guardar_config(self):
        x, y = self.get_position()
        w, h = self.get_size()
        self.config["Ventana"] = {
            "pos_x": str(x), "pos_y": str(y),
            "ancho": str(w), "alto": str(h)
        }
        self.config["Vista"] = {"modo": self.stack.get_visible_child_name()}
        with open(self.config_path, "w") as archivo:
            self.config.write(archivo)

    def on_key_press(self, widget, event):
        if event.keyval == Gdk.KEY_Escape:
            if self.revealer_filtros.get_reveal_child():
                self.revealer_filtros.set_reveal_child(False)
                return True
        elif event.keyval == Gdk.KEY_Return:
            self.aplicar_filtros(None)
            return True

        if not self.revealer_filtros.get_reveal_child():
            if (Gdk.KEY_0 <= event.keyval <= Gdk.KEY_9) or (Gdk.KEY_a <= event.keyval <= Gdk.KEY_z):
                self.revealer_filtros.set_reveal_child(True)
                char = chr(Gdk.keyval_to_unicode(event.keyval))
                self.entrada_nombre.set_text(char)
                self.entrada_nombre.set_position(-1)
                self.entrada_nombre.grab_focus()
                return True
        return False

    def ordenar_por_columna(self, column, index, nombre_columna):
        if self.columna_orden == nombre_columna:
            self.direccion_orden = "desc" if self.direccion_orden == "asc" else "asc"
        else:
            self.columna_orden = nombre_columna
            self.direccion_orden = "asc"
        self.pagina_actual = 0
        self.actualizar_vista()

    def actualizar_vista(self):
        if getattr(self, "vista_predeterminada", "tabla") == "grilla":
            self.stack.set_visible_child_name("grilla")
            self.mostrar_grilla()
        else:
            self.stack.set_visible_child_name("tabla")
            self.mostrar_tabla()

    def aplicar_filtros(self, button):
        nombre = self.entrada_nombre.get_text().strip()
        editorial = self.combo_editorial.get_active_text()

        if not nombre and editorial == "Todas":
            self.repo.limpiar_filtros()
        else:
            self.repo.filtrar(nombre=nombre if nombre else None,
                              editorial=editorial if editorial != "Todas" else None)
        self.pagina_actual = 0

        # Respetar la vista actual
        if self.stack.get_visible_child_name() == "grilla":
            self.mostrar_grilla()
        else:
            self.mostrar_tabla()

    def mostrar_tabla(self):
        self.store.clear()
        volumenes = self.repo.obtener_pagina(
            self.pagina_actual,
            self.volumenes_por_pagina,
            orden=self.columna_orden,
            direccion=self.direccion_orden
        )
        print(f"[DEBUG] Tabla: {len(volumenes)} volúmenes")
        for v in volumenes:
            print(f"[DEBUG] Volumen: {v.id_volume}, {v.nombre}, {v.deck}, {v.descripcion}")
            self.store.append([
                v.id_volume, v.nombre, v.deck, v.descripcion,
                v.url, v.image_url, v.id_publisher,
                v.publisher_name, v.anio_inicio, v.cantidad_numeros
            ])
        self.actualizar_navegacion()

    def mostrar_grilla(self):
        for hijo in self.flowbox.get_children():
            self.flowbox.remove(hijo)

        volumenes = self.repo.obtener_pagina(
            self.pagina_actual,
            self.volumenes_por_pagina,
            orden=self.columna_orden,
            direccion=self.direccion_orden
        )
        for v in volumenes:
            path_img = v.obtener_cover(v)
            try:
                if os.path.exists(path_img):
                    pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(path_img, 128, 180, True)
                    img = Gtk.Image.new_from_pixbuf(pixbuf)
                else:
                    raise FileNotFoundError
            except:
                img = Gtk.Image.new_from_icon_name("image-missing", Gtk.IconSize.DIALOG)

            etiqueta = Gtk.Label(label=f"{v.nombre}\n{v.publisher_name or ''}")
            etiqueta.set_justify(Gtk.Justification.CENTER)
            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
            box.pack_start(img, False, False, 0)
            box.pack_start(etiqueta, False, False, 0)
            frame = Gtk.Frame()
            frame.set_shadow_type(Gtk.ShadowType.IN)
            frame.add(box)
            self.flowbox.add(frame)

        self.flowbox.show_all()
        self.actualizar_navegacion()

    def actualizar_navegacion(self):
        total = self.repo.obtener_total()
        max_pagina = (total - 1) // self.volumenes_por_pagina
        self.label_pagina.set_text(f"Página {self.pagina_actual + 1} de {max_pagina + 1}")
        self.boton_anterior.set_sensitive(self.pagina_actual > 0)
        self.boton_siguiente.set_sensitive(self.pagina_actual < max_pagina)

    def ir_anterior(self, button):
        self.pagina_actual = max(self.pagina_actual - 1, 0)
        if self.stack.get_visible_child_name() == "grilla":
            self.mostrar_grilla()
        else:
            self.mostrar_tabla()

    def ir_siguiente(self, button):
        self.pagina_actual = self.repo.pagina_siguiente(self.pagina_actual, self.volumenes_por_pagina)
        if self.stack.get_visible_child_name() == "grilla":
            self.mostrar_grilla()
        else:
            self.mostrar_tabla()
# Run the application
if __name__ == "__main__":
    from sqlalchemy.orm import sessionmaker
    from entidades import engine
    session = sessionmaker(bind=engine)()
    win = VolumeWindow(session=session)
    win.connect("destroy", Gtk.main_quit)
    Gtk.main()