import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from sqlalchemy.orm import sessionmaker
from entidades import engine
from entidades.setup_model import Setup
from repositories.setup_repository import SetupRepository

Session = sessionmaker(bind=engine)
session = Session()

# CAMBIO 1: La clase ahora hereda de Gtk.Window
class SetupVisualWindow(Gtk.Window):
    def __init__(self, session):
        # CAMBIO 2: Llamamos al constructor de la clase padre (Gtk.Window)
        super().__init__(title="Configuración de Babelcomics")
        
        # Ya no usamos 'self.window', ahora usamos 'self' directamente
        self.set_default_size(400, 300)
        self.set_border_width(10)

        # Crear el HeaderBar y asignarlo como la titlebar
        headerbar = Gtk.HeaderBar()
        headerbar.set_show_close_button(True)
        headerbar.set_title("Configuración")
        self.set_titlebar(headerbar) # <-- Se usa 'self'

        # Crear el contenedor principal (GtkBox)
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.add(main_box) # <-- Se usa 'self'

        # Usamos el repositorio
        self.repo = SetupRepository(session)
        self.config = self.repo.obtener_o_crear_configuracion()

        # ... (El resto de la creación de widgets no cambia)
        btn_guardar = Gtk.Button(label="Guardar")
        btn_guardar.connect("clicked", self.guardar_configuracion)
        headerbar.pack_end(btn_guardar)

        # ... (Creación de los Gtk.Entry, Gtk.SpinButton, etc. no cambia)
        directorio_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        label_directorio = Gtk.Label(label="Directorio base:")
        self.entry_directorio_base = Gtk.Entry()
        self.entry_directorio_base.set_placeholder_text("Directorio base")
        directorio_box.pack_start(label_directorio, False, False, 0)
        directorio_box.pack_start(self.entry_directorio_base, True, True, 0)
        main_box.pack_start(directorio_box, False, False, 0)

        ancho_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        label_ancho = Gtk.Label(label="Ancho de thumbnail:")
        self.spin_ancho_thumbnail = Gtk.SpinButton()
        adjustment1 = Gtk.Adjustment(lower=10, upper=1000, step_increment=10, page_increment=100, value=120)
        self.spin_ancho_thumbnail.set_adjustment(adjustment1)
        ancho_box.pack_start(label_ancho, False, False, 0)
        ancho_box.pack_start(self.spin_ancho_thumbnail, True, True, 0)
        main_box.pack_start(ancho_box, False, False, 0)

        pagina_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        label_pagina = Gtk.Label(label="Cómiques por página:")
        self.spin_comics_por_pagina = Gtk.SpinButton()
        adjustment2 = Gtk.Adjustment(lower=1, upper=1000, step_increment=1, page_increment=5, value=18)
        self.spin_comics_por_pagina.set_adjustment(adjustment2)
        pagina_box.pack_start(label_pagina, False, False, 0)
        pagina_box.pack_start(self.spin_comics_por_pagina, True, True, 0)
        main_box.pack_start(pagina_box, False, False, 0)

        self.chk_modo_oscuro = Gtk.CheckButton(label="Modo oscuro")
        main_box.pack_start(self.chk_modo_oscuro, False, False, 0)

        self.chk_actualizar_metadata = Gtk.CheckButton(label="Actualizar metadata automáticamente")
        main_box.pack_start(self.chk_actualizar_metadata, False, False, 0)

        self.cargar_configuracion()

        # CAMBIO 3: Ya no necesitamos Gtk.main_quit ni show_all aquí.
        # El que abre la ventana se encargará de eso.
        # self.connect("destroy", Gtk.main_quit) # Esto cerraría toda la app
        # self.show_all() # El que la crea la mostrará
    
    # ... (cargar_configuracion y guardar_configuracion no cambian)
    def cargar_configuracion(self):
        self.entry_directorio_base.set_text(self.config.directorio_base)
        self.spin_ancho_thumbnail.set_value(self.config.ancho_thumbnail)
        self.spin_comics_por_pagina.set_value(self.config.cantidad_comics_por_pagina)
        self.chk_modo_oscuro.set_active(self.config.modo_oscuro)
        self.chk_actualizar_metadata.set_active(self.config.actualizar_metadata)

    def guardar_configuracion(self, button):
        self.config.directorio_base = self.entry_directorio_base.get_text()
        self.config.ancho_thumbnail = int(self.spin_ancho_thumbnail.get_value())
        self.config.cantidad_comics_por_pagina = int(self.spin_comics_por_pagina.get_value())
        self.config.modo_oscuro = self.chk_modo_oscuro.get_active()
        self.config.actualizar_metadata = self.chk_actualizar_metadata.get_active()
        self.repo.guardar_configuracion(self.config)
        # Es una buena práctica cerrar la ventana de config al guardar
        self.destroy()

# El bloque if __name__ == "__main__" ya no es necesario o puede adaptarse para testeo
# if __name__ == "__main__":
#     win = SetupVisualWindow()
#     win.connect("destroy", Gtk.main_quit)
#     win.show_all()
#     Gtk.main()