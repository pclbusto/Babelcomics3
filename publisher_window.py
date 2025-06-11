import os
import configparser
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GdkPixbuf
from interfaces.maestro import Maestro
from repositories.publisher_repository import PublisherRepository


class PublisherWindow(Maestro):
    def __init__(self, session=None):
        self.repo = PublisherRepository(session)  # Inicializar el repositorio
        super().__init__(titulo="Publisher Management")
        self.load_publishers()
        
    def create_stack_views(self):
        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.stack.set_transition_duration(300)
        # Table view (Lista)
        self.publisher_store = Gtk.ListStore(str, str, str, str, str)  # Alineado con el modelo Publisher
        self.publisher_treeview = Gtk.TreeView(model=self.publisher_store)
        columns = [("ID", 0), ("Name", 1), ("Deck", 2), ("Description", 3), ("URL Logo", 4)]
        for title, index in columns:
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(title, renderer, text=index)
            self.publisher_treeview.append_column(column)
        scroll_table = Gtk.ScrolledWindow()
        scroll_table.add(self.publisher_treeview)
        self.stack.add_named(scroll_table, "table")

        # Grid view (Grilla con IconView)
        self.icon_store = Gtk.ListStore(GdkPixbuf.Pixbuf, str)  # Pixbuf para imágenes, str para nombres
        self.icon_view = Gtk.IconView(model=self.icon_store)
        self.icon_view.set_pixbuf_column(0)  # Columna para las imágenes
        self.icon_view.set_text_column(1)  # Columna para los nombres
        scroll_grid = Gtk.ScrolledWindow()
        scroll_grid.add(self.icon_view)
        self.stack.add_named(scroll_grid, "grid")

   

    def load_publishers(self):
        # Obtener los publishers desde el repositorio
        publishers = self.repo.obtener_todos_los_publishers()

        # Limpiar las vistas antes de cargar nuevos datos
        self.publisher_store.clear()
        self.icon_store.clear()

        # Cargar datos en la vista de tabla
        for publisher in publishers:
            self.publisher_store.append([
                str(publisher.id_publisher),
                publisher.nombre,
                publisher.deck,
                publisher.descripcion,
                publisher.url_logo
            ])

        # Cargar datos en la vista de grilla
        for publisher in publishers:
            try:
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                    publisher.obtener_nombre_logo(), width=64, height=64, preserve_aspect_ratio=True
                )
            except Exception as e:
                print(f"Error loading image for {publisher.nombre}: {e}")
                pixbuf = None  # Si no se puede cargar la imagen, usa None

            nombre_logo = publisher.obtener_nombre_logo()
            self.icon_store.append([pixbuf, f"{publisher.nombre} ({nombre_logo})"])

    def mostrar_tabla(self):
        """Carga los datos de los publishers en la vista de tabla."""
        self.store.clear()
        publishers = self.repo.obtener_todos_los_publishers()
        for publisher in publishers:
            self.store.append([
                str(publisher.id_publisher),
                publisher.nombre,
                publisher.deck,
                publisher.descripcion,
                publisher.url_logo
            ])

    def mostrar_grilla(self):
        """Carga los datos de los publishers en la vista de grilla."""
        for hijo in self.flowbox.get_children():
            self.flowbox.remove(hijo)

        publishers = self.repo.obtener_todos_los_publishers()
        for publisher in publishers:
            try:
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                    publisher.obtener_nombre_logo(), width=64, height=64, preserve_aspect_ratio=True
                )
            except Exception as e:
                print(f"Error loading image for {publisher.nombre}: {e}")
                pixbuf = None  # Si no se puede cargar la imagen, usa None

            etiqueta = Gtk.Label(label=f"{publisher.nombre}\n{publisher.url_logo or ''}")
            etiqueta.set_justify(Gtk.Justification.CENTER)
            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
            img = Gtk.Image.new_from_pixbuf(pixbuf) if pixbuf else Gtk.Image.new_from_icon_name("image-missing", Gtk.IconSize.DIALOG)
            box.pack_start(img, False, False, 0)
            box.pack_start(etiqueta, False, False, 0)
            frame = Gtk.Frame()
            frame.set_shadow_type(Gtk.ShadowType.IN)
            frame.add(box)
            self.flowbox.add(frame)

        self.flowbox.show_all()

    
    def aplicar_filtros(self, button):
        """Aplica los filtros seleccionados y actualiza la vista."""
        nombre = self.entrada_nombre.get_text().strip()
        editorial = self.combo_editorial.get_active_text()

        if not nombre and editorial == "Todas":
            self.repo.limpiar_filtros()
        else:
            self.repo.filtrar(nombre=nombre if nombre else None,
                              editorial=editorial if editorial != "Todas" else None)
        self.pagina_actual = 0

        if self.stack.get_visible_child_name() == "grilla":
            self.mostrar_grilla()
        else:
            self.mostrar_tabla()
    
    
# Run the application
if __name__ == "__main__":
    from sqlalchemy.orm import sessionmaker
    from entidades import engine
    session = sessionmaker(bind=engine)()
    win = PublisherWindow(session=session)
    win.connect("destroy", Gtk.main_quit)
    Gtk.main()