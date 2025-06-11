import os
import configparser
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GdkPixbuf
from repositories.publisher_repository import PublisherRepository  # Importar el repositorio

class PublisherWindow(Gtk.Window):
    def __init__(self, session=None):
        super().__init__(title="Publisher Management")
        self.session = session
        self.repo = PublisherRepository(session)  # Inicializar el repositorio

        # Configuración para guardar tamaño y posición
        self.config_path = os.path.expanduser("~/.babelcomics_publisherwindow.ini")
        self.config = configparser.ConfigParser()
        self.config.read(self.config_path)

        self.restore_window_settings()  # Restaurar tamaño y posición

        self.init_widgets()
        self.init_layout()
        self.load_publishers()
        self.show_all()

        # Guardar configuración al cerrar la ventana
        self.connect("configure-event", self.save_window_settings)

    def restore_window_settings(self):
        """Restaurar tamaño y posición de la ventana desde el archivo de configuración."""
        width = int(self.config.get("Window", "width", fallback="800"))
        height = int(self.config.get("Window", "height", fallback="600"))
        self.set_default_size(width, height)

        if self.config.has_option("Window", "pos_x") and self.config.has_option("Window", "pos_y"):
            pos_x = int(self.config.get("Window", "pos_x"))
            pos_y = int(self.config.get("Window", "pos_y"))
            self.move(pos_x, pos_y)

    def save_window_settings(self, *args):
        """Guardar tamaño y posición de la ventana en el archivo de configuración."""
        pos_x, pos_y = self.get_position()
        width, height = self.get_size()

        self.config["Window"] = {
            "pos_x": str(pos_x),
            "pos_y": str(pos_y),
            "width": str(width),
            "height": str(height),
        }

        with open(self.config_path, "w") as config_file:
            self.config.write(config_file)

    def init_widgets(self):
        self.create_headerbar()
        self.create_stack_views()
        self.create_navigation_bar()

    def init_layout(self):
        # Organizar los widgets en la ventana
        container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        container.pack_start(self.stack, True, True, 0)
        container.pack_start(self.nav_box, False, False, 0)
        self.add(container)

    def create_headerbar(self):
        self.headerbar = Gtk.HeaderBar()
        self.headerbar.set_show_close_button(True)
        self.headerbar.set_title("Publisher Management")
        self.set_titlebar(self.headerbar)

        toggle_view_button = Gtk.Button(label="Toggle View")
        toggle_view_button.connect("clicked", self.toggle_view)
        self.headerbar.pack_end(toggle_view_button)

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

    def create_navigation_bar(self):
        self.nav_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.nav_box.set_halign(Gtk.Align.CENTER)

        self.prev_button = Gtk.Button(label="Previous")
        self.prev_button.connect("clicked", self.go_previous)
        self.nav_box.pack_start(self.prev_button, False, False, 0)

        self.page_label = Gtk.Label(label="Page 1")
        self.nav_box.pack_start(self.page_label, False, False, 0)

        self.next_button = Gtk.Button(label="Next")
        self.next_button.connect("clicked", self.go_next)
        self.nav_box.pack_start(self.next_button, False, False, 0)

    def toggle_view(self, button):
        # Alternar entre la vista en lista y la vista en grilla
        current_view = self.stack.get_visible_child_name()
        if current_view == "table":
            self.stack.set_visible_child_name("grid")
        else:
            self.stack.set_visible_child_name("table")

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

    # Métodos de navegación
    def go_previous(self, button):
        print("Navigating to the previous page...")
        # Aquí puedes implementar la lógica para cargar la página anterior

    def go_next(self, button):
        print("Navigating to the next page...")
        # Aquí puedes implementar la lógica para cargar la página siguiente

# Run the application
if __name__ == "__main__":
    from sqlalchemy.orm import sessionmaker
    from entidades import engine
    session = sessionmaker(bind=engine)()
    win = PublisherWindow(session=session)
    win.connect("destroy", Gtk.main_quit)
    Gtk.main()