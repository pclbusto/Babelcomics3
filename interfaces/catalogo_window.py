import os
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, GLib, Gdk

from sqlalchemy.orm import sessionmaker
from entidades import engine
from interfaces.maestro import Maestro
from entidades.comicbook_model import Comicbook
from repositories.comicbook_repository import ComicbookRepository
from repositories.setup_repository import SetupRepository

# Importamos las otras ventanas para poder abrirlas desde el menú
from interfaces.volume_window import VolumeWindow
from interfaces.publisher_window import PublisherWindow
from interfaces.setup_window import SetupVisualWindow

Session = sessionmaker(bind=engine)
session = Session()

class CatalogoWindow(Maestro):
    def __init__(self, application=None, thumbnail_manager=None):
        # Obtenemos la configuración una sola vez
        setup_repo = SetupRepository(session)
        setup_config = setup_repo.obtener_o_crear_configuracion()
        # El título de la ventana se pasa al constructor de Maestro
        super().__init__(
            titulo="Catálogo de Cómics", 
            thumbnail_manager=thumbnail_manager,
            setup_config=setup_config # <--- ¡Mucho más limpio!
        )
        self.set_name("BabelComics") # Para la integración con el ícono del .desktop
        self.application = application

        # Inicializamos el repositorio específico para Comicbooks
        self.repo = ComicbookRepository(session)
        setup_repo = SetupRepository(session)

        # Parámetros de paginación
        setup_config = setup_repo.obtener_o_crear_configuracion()
        self.items_por_pagina = setup_config.cantidad_comics_por_pagina
        self.pagina_actual = 0
        self.columna_orden = "path" # Ordenar por ruta de archivo por defecto
        self.direccion_orden = "asc"

        # Configurar las columnas para la vista de lista
        self.columnas_visibles = ["id_comicbook", "path", "calidad"]
        self.set_columnas_lista(
            # Títulos de las columnas que verá el usuario
            ["ID", "Ruta del Archivo", "Calidad"],
            # Tipos de datos para el ListStore
            [int, str, int]
        )

        # Reemplazamos el HeaderBar genérico de Maestro por uno personalizado
        self.personalizar_headerbar()
        
        # Cargamos los datos iniciales
        self.actualizar_vista()
        self.actualizar_icono_vista()

        # Registramos nuestro método 'on_comic_activated' para que se llame
        # cuando un hijo del FlowBox sea activado.
        self.set_on_child_activated(self.on_comic_activated)

    def personalizar_headerbar(self):
        """
        Personaliza el HeaderBar existente (creado por Maestro) 
        añadiendo el menú de navegación de la aplicación.
        """
        # 1. Obtenemos el HeaderBar que ya fue creado por la clase base 'Maestro'
        headerbar = self.get_titlebar()

        # Es una buena práctica asegurarse de que sea del tipo correcto
        if not isinstance(headerbar, Gtk.HeaderBar):
            # Si no hay HeaderBar, o no es del tipo esperado, salimos para evitar errores.
            # Podrías crear uno aquí si fuera necesario en tu lógica.
            print("Advertencia: No se encontró un HeaderBar en la ventana base.")
            return

        # 2. El resto del código se enfoca en crear y añadir SÓLO los widgets nuevos.
        #    Los botones de búsqueda y vista ya están en el headerbar.
        
        # --- Menú principal de la aplicación ---
        menubutton = Gtk.MenuButton() # <--- AÑADE label="Menú"
        icono_menu = Gtk.Image.new_from_icon_name(
            "open-menu-symbolic",  # Nombre del ícono estándar de GTK para menús
            Gtk.IconSize.BUTTON
        )
        # Añadimos el ícono al botón para que tenga contenido y se pueda ver.
        menubutton.set_image(icono_menu)
        
        popover = Gtk.Popover.new(menubutton)
        
        # Usamos un Grid para un menú más compacto y moderno
        grid = Gtk.Grid()
        grid.set_column_spacing(10)
        grid.set_row_spacing(10)
        grid.set_margin_top(10)
        grid.set_margin_bottom(10)
        grid.set_margin_start(10)
        grid.set_margin_end(10)

        # Creamos los botones del menú
        btn_volumenes = Gtk.Button(label="Volúmenes", image=Gtk.Image.new_from_icon_name("view-list-symbolic", Gtk.IconSize.BUTTON))
        btn_editoriales = Gtk.Button(label="Editoriales", image=Gtk.Image.new_from_icon_name("business-symbolic", Gtk.IconSize.BUTTON))
        btn_config = Gtk.Button(label="Configuración", image=Gtk.Image.new_from_icon_name("preferences-system-symbolic", Gtk.IconSize.BUTTON))
        btn_salir = Gtk.Button(label="Salir", image=Gtk.Image.new_from_icon_name("application-exit-symbolic", Gtk.IconSize.BUTTON))
        btn_refrescar = Gtk.Button(label="Refrescar", image=Gtk.Image.new_from_icon_name("view-refresh-symbolic", Gtk.IconSize.BUTTON))
    

        # Conectamos las señales
        btn_volumenes.connect("clicked", self.abrir_volumenes, popover)
        btn_editoriales.connect("clicked", self.abrir_editoriales, popover)
        btn_config.connect("clicked", self.abrir_setup, popover)
        btn_salir.connect("clicked", lambda w: self.application.quit())
        btn_refrescar.connect("clicked", self.refrescar_vista, popover)

        self.connect("key-press-event", self.on_key_press)

        # Añadimos los botones al grid
        grid.attach(btn_volumenes, 0, 0, 1, 1)
        grid.attach(btn_editoriales, 1, 0, 1, 1)
        grid.attach(btn_config, 0, 1, 1, 1)
        grid.attach(btn_refrescar, 1, 1, 1, 1) # Lo ponemos al lado de Configuración
        grid.attach(btn_salir, 0, 2, 2, 1) # El botón de salir ahora ocupa todo el ancho de la tercera fila
        
        
        popover.add(grid)
        grid.show_all() 
        menubutton.set_popover(popover)
        
        # 3. Añadimos el nuevo menubutton al HeaderBar existente.
        headerbar.pack_end(menubutton)
        self.show_all()
    # --- Implementación de los métodos abstractos de Maestro ---

    def mostrar_lista(self):
        """
        Llena la vista de lista con los cómics de la página actual.
        """
        self.store_lista.clear()
        comics = self.repo.obtener_pagina(
            self.pagina_actual,
            self.items_por_pagina,
            orden=self.columna_orden,
            direccion=self.direccion_orden,
            columnas=self.columnas_visibles
        )
        for c in comics:
            # Añadimos los datos en el orden de self.columnas_visibles
            self.store_lista.append([c.id_comicbook, c.path, c.calidad])
        self.actualizar_navegacion()

    def mostrar_grilla(self):
        """
        Llena la vista de grilla con las carátulas de los cómics.
        """
        comics = self.repo.obtener_pagina(
            self.pagina_actual,
            self.items_por_pagina,
            orden=self.columna_orden,
            direccion=self.direccion_orden
        )
        # Usamos el método genérico de Maestro para construir la grilla
        self.construir_grilla(
            items=comics,
            # Le decimos cómo obtener la imagen de la carátula para un cómic
            get_image_path=lambda comic: comic.obtener_cover(),
            # Le decimos qué texto mostrar debajo de la carátula
            get_label_text=lambda comic: os.path.basename(comic.path)
        )
        self.actualizar_navegacion()

    def realizar_busqueda(self, texto):
        """
        Filtra los cómics por la ruta del archivo.
        """
        if texto:
            # Filtramos en la BD por el campo 'path'
            self.repo.filtrar(path=texto)
        else:
            self.repo.limpiar_filtros()
        
        self.pagina_actual = 0
        self.actualizar_vista()
    
    def actualizar_navegacion(self):
        """
        Actualiza la barra de navegación con la información de paginación correcta.
        Sobrescribimos para usar self.items_por_pagina.
        """
        total = self.repo.obtener_total()
        if total > 0:
            max_pagina = (total - 1) // self.items_por_pagina
        else:
            max_pagina = 0
        self.label_pagina.set_text(f"Página {self.pagina_actual + 1} de {max_pagina + 1}")
        self.boton_anterior.set_sensitive(self.pagina_actual > 0)
        self.boton_siguiente.set_sensitive(self.pagina_actual < max_pagina)
        
    def ir_siguiente(self, button):
        """Navega a la página siguiente."""
        self.pagina_actual = self.repo.pagina_siguiente(self.pagina_actual, self.items_por_pagina)
        self.actualizar_vista()

    def ir_anterior(self, button):
        """Navega a la página anterior."""
        if self.pagina_actual > 0:
            self.pagina_actual -= 1
        self.actualizar_vista()

    # --- Navegación a otras ventanas ---

    def _abrir_ventana(self, constructor_ventana, popover):
        """Función auxiliar para abrir ventanas y cerrar el popover."""
        win = constructor_ventana(session=session)
        win.show_all()
        GLib.idle_add(popover.popdown) # Descomentar si el popover no se cierra solo

    def abrir_volumenes(self, widget, popover):
        self._abrir_ventana(VolumeWindow, popover)

    def abrir_setup(self, widget, popover):
        print("Abrir configuración visual (funcionalidad pendiente)")
        self._abrir_ventana(SetupVisualWindow, popover)

    def abrir_editoriales(self, widget, popover):
        self._abrir_ventana(PublisherWindow, popover)

    def _ejecutar_refresco(self):
        """
        Contiene la lógica central para recargar la configuración y la vista.
        Solo resetea a la primera página si la paginación ha cambiado.
        """
        print("INFO: Ejecutando lógica de refresco...")
        
        # 1. Guardamos el valor actual antes de recargar
        paginacion_actual = self.items_por_pagina
        
        # 2. Volvemos a consultar la base de datos para obtener la configuración
        from repositories.setup_repository import SetupRepository
        setup_repo = SetupRepository(session)
        setup_config = setup_repo.obtener_o_crear_configuracion()
        
        # 3. Actualizamos el valor de la paginación en nuestra ventana
        self.items_por_pagina = setup_config.cantidad_comics_por_pagina
        
        # 4. Comparamos el valor antiguo con el nuevo
        if paginacion_actual != self.items_por_pagina:
            # Si la cantidad de ítems por página cambió, es seguro volver al inicio
            print(f"INFO: La paginación cambió de {paginacion_actual} a {self.items_por_pagina}. Volviendo a la página 1.")
            self.pagina_actual = 0
        else:
            # Si no cambió, nos mantenemos en la página actual
            print(f"INFO: La paginación no cambió ({self.items_por_pagina}). Se mantiene la página actual.")
            
        # 5. Llamamos al método que ya se encarga de dibujar la vista
        self.actualizar_vista()

    def refrescar_vista(self, widget, popover):
        """
        Este es el manejador de la señal 'clicked' del botón del menú.
        Llama a la lógica de refresco y cierra el popover.
        """
        self._ejecutar_refresco()
        GLib.idle_add(popover.popdown)

    def on_key_press(self, widget, event):
        """
        Manejador de teclado específico para CatalogoWindow.
        """
        # 1. Primero, maneja las teclas que solo le importan a esta ventana (F5).
        if event.keyval == Gdk.KEY_F5:
            print("INFO: F5 presionado.")
            self._ejecutar_refresco()
            return True # Evento manejado, no necesita seguir.

        # 2. Si no fue F5, llama al manejador de la clase padre (Maestro).
        #    Esto es CRUCIAL para que la tecla 'Escape' siga funcionando.
        return super().on_maestro_key_press(widget, event)

    def on_comic_activated(self, comic):
        """
        Este método es llamado por Maestro cuando un cómic en la grilla
        es activado (doble clic).
        """
        print("="*30)
        print(f"Cómic Activado: ID {comic.id_comicbook}")
        print(f"Ruta: {comic.path}")
        print("="*30)
        # Aquí podrías abrir una nueva ventana con los detalles del cómic,
        # o realizar cualquier otra acción.