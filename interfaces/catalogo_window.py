import os
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GdkPixbuf', '2.0')
from gi.repository import Gtk, GdkPixbuf

from sqlalchemy.orm import sessionmaker
from entidades import engine
from entidades.publisher_model import Publisher
from entidades.setup_model import Setup

# Importar la ventana de volúmenes
from interfaces.volume_window import VolumeWindow
from interfaces.publisher_window import PublisherWindow

Session = sessionmaker(bind=engine)
session = Session()

BASE_IMAGE_PATH = os.path.join(os.path.dirname(__file__), '..', 'images')

class CatalogoWindow:
    def __init__(self):
        self.window = Gtk.Window(title="BabelComics")
        self.window.set_default_size(800, 600)
        self.window.set_border_width(10)

        headerbar = Gtk.HeaderBar()
        headerbar.set_show_close_button(True)
        headerbar.set_title("Catálogo de Cómics")
        self.window.set_titlebar(headerbar)

        menubutton = Gtk.MenuButton()
        popover = Gtk.Popover()
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6, margin=10)

        def boton_con_icono(icon_name, tooltip, callback, popover):
            btn = Gtk.Button()
            ruta_imagen = None
            if icon_name == 'salir':
                ruta_imagen = os.path.join(BASE_IMAGE_PATH, 'salir.png')
            elif icon_name == 'editorial':
                self.abrir_editoriales(None)
                ruta_imagen = os.path.join(BASE_IMAGE_PATH, 'editorial.png')
            elif icon_name == 'volumen':
                ruta_imagen = os.path.join(BASE_IMAGE_PATH, 'volumen.png')
            elif icon_name == 'configurar':
                ruta_imagen = os.path.join(BASE_IMAGE_PATH, 'configurar.png')
            if ruta_imagen and os.path.exists(ruta_imagen):
                pixbuf = GdkPixbuf.Pixbuf.new_from_file(ruta_imagen)
                pixbuf = pixbuf.scale_simple(64, 64, GdkPixbuf.InterpType.BILINEAR)
                image = Gtk.Image.new_from_pixbuf(pixbuf)
            else:
                image = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.BUTTON)
            btn.add(image)
            btn.set_tooltip_text(tooltip)
            btn.connect("clicked", lambda widget: [callback(widget), popover.popdown()])
            return btn

        vbox.pack_start(boton_con_icono("configurar", "Configuración", self.abrir_setup, popover), False, False, 0)
        vbox.pack_start(boton_con_icono("editorial", "Editoriales", self.abrir_editoriales, popover), False, False, 0)
        vbox.pack_start(boton_con_icono("volumen", "Volúmenes", self.abrir_volumenes, popover), False, False, 0)
        vbox.pack_start(boton_con_icono("salir", "Salir", Gtk.main_quit, popover), False, False, 0)

        popover.add(vbox)
        popover.show_all()
        menubutton.set_popover(popover)
        headerbar.pack_end(menubutton)

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.window.add(main_box)

        self.treeview = Gtk.TreeView()
        self.treeview.set_size_request(800, 400)
        self.setup_columns()

        scroll = Gtk.ScrolledWindow()
        scroll.add(self.treeview)
        main_box.pack_start(scroll, True, True, 0)

        button_box = Gtk.ButtonBox()
        button_box.set_layout(Gtk.ButtonBoxStyle.END)

        btn_add = Gtk.Button(label="Agregar")
        btn_add.connect("clicked", self.agregar_comic)
        button_box.pack_start(btn_add, True, True, 0)

        btn_edit = Gtk.Button(label="Editar")
        btn_edit.connect("clicked", self.editar_comic)
        button_box.pack_start(btn_edit, True, True, 0)

        btn_delete = Gtk.Button(label="Eliminar")
        btn_delete.connect("clicked", self.eliminar_comic)
        button_box.pack_start(btn_delete, True, True, 0)

        main_box.pack_start(button_box, False, False, 0)

        self.cargar_comics()
        self.window.connect("destroy", Gtk.main_quit)
        self.window.maximize() 
        self.window.show_all()
        popover.popdown()
    def abrir_volumenes(self, widget):
        win = VolumeWindow(session)
        win.show_all()

    def abrir_setup(self, widget):
        print("Abrir configuración")

    def abrir_editoriales(self, widget):
        win = PublisherWindow(session)
        win.show_all()

    def setup_columns(self):
        cell_renderer_text = Gtk.CellRendererText()
        self.treeview.append_column(Gtk.TreeViewColumn("ID", cell_renderer_text, text=0))
        self.treeview.append_column(Gtk.TreeViewColumn("Nombre", cell_renderer_text, text=1))
        self.treeview.append_column(Gtk.TreeViewColumn("Editorial", cell_renderer_text, text=2))
        self.treeview.append_column(Gtk.TreeViewColumn("Volumen", cell_renderer_text, text=3))
        self.liststore = Gtk.ListStore(str, str, str, str)
        self.treeview.set_model(self.liststore)

    def cargar_comics(self):
        self.liststore.clear()
        # Ejemplo de carga, puedes ajustar para usar la entidad Volume
        from entidades.volume_model import Volume
        comics = session.query(Volume).all()
        for comic in comics:
            self.liststore.append([
                str(comic.id_volume),
                comic.nombre,
                comic.publisher_name,
                comic.publisher_name
            ])

    def agregar_comic(self, widget):
        print("Agregar cómic")

    def editar_comic(self, widget):
        print("Editar cómic")

    def eliminar_comic(self, widget):
        print("Eliminar cómic")

if __name__ == "__main__":
    CatalogoWindow()
    Gtk.main()
