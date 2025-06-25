import os
import configparser
import gi
import threading

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GdkPixbuf, GLib, Gdk


class Maestro(Gtk.Window):
    def __init__(self, titulo="Maestro", thumbnail_manager=None, setup_config=None):
        super().__init__(title=titulo)
        self.set_resizable(True)  # Asegúrate de que la ventana sea redimensionable
        self.set_default_size(800, 600)  # Tamaño inicial de la ventana
        self.thumbnail_manager = thumbnail_manager
        self.setup_config = setup_config
        # Configuración para guardar tamaño y posición
        self.ruta_config = os.path.expanduser("~/.babelcomics.ini")
        self.config = configparser.ConfigParser()
        self.config.read(self.ruta_config)

        # Precargamos el ícono para no tener que leerlo del disco en cada iteración.
        # Si no lo encuentra, no dará error, simplemente no se mostrará.
        try:
            self.classified_icon_pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                "images/clasificado.png", 32, 32, True
            )
        except Exception as e:
            print(f"Advertencia: No se pudo cargar el ícono 'clasificado.png'. {e}")
            self.classified_icon_pixbuf = None

        self.restaurar_configuracion_ventana()  # Restaurar tamaño y posición

        self.inicializar_variables()
        self.inicializar_widgets()
        self.inicializar_distribucion()
        self.inicializar_eventos()

        # Guardar configuración al cerrar la ventana
        self.connect("configure-event", self.guardar_configuracion_ventana)
        self.show_all()

    def construir_grilla(self, items, get_image_path, get_label_text):
        """
        Construye la grilla, superponiendo el ícono de estado directamente sobre la imagen.
        """
        for child in self.flowbox.get_children():
            self.flowbox.remove(child)

        for obj in items:
            # --- Lógica de Lazy Loading (Sin cambios) ---
            stack_imagen = Gtk.Stack()
            stack_imagen.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
            spinner = Gtk.Spinner()
            spinner.start()
            stack_imagen.add_named(spinner, "spinner")
            imagen_widget = Gtk.Image()
            stack_imagen.add_named(imagen_widget, "imagen")

            thread = threading.Thread(
                target=self._cargar_thumbnail_en_hilo,
                args=(get_image_path(obj), imagen_widget, spinner, stack_imagen, obj)
            )
            thread.daemon = True
            thread.start()

            # --- LÓGICA DEL INDICADOR VISUAL CORREGIDA ---

            # 1. El Overlay ahora envuelve SOLAMENTE al Stack de la imagen.
            overlay_imagen = Gtk.Overlay()
            overlay_imagen.add(stack_imagen)
            overlay_imagen.set_halign(Gtk.Align.CENTER)
            # 2. Comprobamos si el objeto está clasificado para añadir el ícono.
            if hasattr(obj, 'is_classified') and obj.is_classified and self.classified_icon_pixbuf:
                icon = Gtk.Image.new_from_pixbuf(self.classified_icon_pixbuf)
                icon.set_halign(Gtk.Align.START)  # <--- 1. De END a START para alinear a la izquierda
                icon.set_valign(Gtk.Align.START)  # <--- Esto se mantiene igual (arriba)
                icon.set_margin_top(3)            # <--- 2. Reducimos el margen superior
                icon.set_margin_start(3)          # <--- 2. Cambiamos margin_end por margin_start y reducimos
             
                # Añadimos el ícono como una capa superpuesta al Overlay.
                overlay_imagen.add_overlay(icon)

            # --- Ensamblado Final ---

            # 3. Creamos un Box vertical para apilar la imagen (con overlay) y la etiqueta.
            
            vbox_celda = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
            
            # Añadimos el overlay que contiene la imagen
            vbox_celda.pack_start(overlay_imagen, False, False, 0)
            
            
            # Añadimos la etiqueta debajo
            etiqueta = Gtk.Label(label=get_label_text(obj))
            etiqueta.set_line_wrap(True)
            etiqueta.set_max_width_chars(20)
            etiqueta.set_justify(Gtk.Justification.CENTER)
            vbox_celda.pack_start(etiqueta, False, False, 0)

            # 4. El Frame principal contiene el Box vertical que ya tiene todo ordenado.
            frame = Gtk.Frame()
            frame.item_data = obj
            frame.add(vbox_celda)
            
            # NOTA: He quitado la línea 'frame.set_size_request(...)' para que GTK
            # calcule el tamaño automáticamente y evite el crecimiento indeseado.
            
            self.flowbox.add(frame)

        self.flowbox.show_all()

    def actualizar_icono_vista(self):
        """Actualiza el ícono del botón de vista según la vista actual."""
        try:
            if self.vista_predeterminada == "lista":
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale("images/vista_lista.png", 24, 24, True)
            else:
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale("images/vista_grilla.png", 24, 24, True)
            self.boton_vista.set_image(Gtk.Image.new_from_pixbuf(pixbuf))
        except:
            self.boton_vista.set_image(Gtk.Image.new_from_icon_name("view-grid-symbolic", Gtk.IconSize.BUTTON))

    def inicializar_variables(self):
        """Inicializa las variables generales."""
        self.items = []
        self.columnas_lista = []
        self.callback_accion = None
        self.callback_child_activated = None # Callback para el FlowBox
        self.last_selected_child_index = -1

    def inicializar_widgets(self):
        """Inicializa los widgets principales."""
        # HeaderBar
        self.headerbar = Gtk.HeaderBar(title=self.get_title())
        self.headerbar.set_show_close_button(True)
        self.set_titlebar(self.headerbar)
    
            # Buscar (a la izquierda)
        self.boton_buscar = Gtk.Button()
        try:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale("images/filtrar.png", 24, 24, True)
            icono_buscar = Gtk.Image.new_from_pixbuf(pixbuf)
        except Exception as e:
            print(f"No se pudo cargar el ícono de filtro: {e}")
            icono_buscar = Gtk.Image.new_from_icon_name("system-search-symbolic", Gtk.IconSize.BUTTON)

        self.boton_buscar.set_image(icono_buscar)
        self.boton_buscar.connect("clicked", self.mostrar_dialogo_busqueda)
        self.headerbar.pack_start(self.boton_buscar)

         # Botón único para alternar vista (a la derecha)
        self.boton_vista = Gtk.Button()
        self.boton_vista.set_image(Gtk.Image.new_from_icon_name("view-grid-symbolic", Gtk.IconSize.BUTTON))
        self.boton_vista.connect("clicked", self.cambiar_vista)
        self.headerbar.pack_end(self.boton_vista)

        # Stack de vistas
        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.stack.set_transition_duration(500)

        # Vista Lista
        self.treeview = Gtk.TreeView()
        self.store_lista = Gtk.ListStore(str, str, str)  # Ajustar columnas según sea necesario
        self.treeview.set_model(self.store_lista)

        # Envolver el TreeView en un ScrolledWindow
        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.scrolled_window.add(self.treeview)

        # Agregar el ScrolledWindow al stack
        self.stack.add_named(self.scrolled_window, "lista")

        # Vista Grilla
        self.flowbox = Gtk.FlowBox()
        self.flowbox.set_selection_mode(Gtk.SelectionMode.MULTIPLE)
        self.flowbox.connect("child-activated", self.on_flowbox_child_activated)

        self.scroll_grilla = Gtk.ScrolledWindow()
        self.scroll_grilla.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.scroll_grilla.add(self.flowbox)

        self.stack.add_named(self.scroll_grilla, "grilla")
        # self.vista_predeterminada = "grilla"  # Configuración inicial de la vista

        # Barra de navegación
        self.crear_barra_navegacion()

    def mostrar_dialogo_busqueda(self, button):
        dialogo = Gtk.Dialog(title="Buscar", transient_for=self, flags=0)
        dialogo.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                            "Limpiar Búsqueda", Gtk.ResponseType.APPLY, # Botón para limpiar
                            Gtk.STOCK_OK, Gtk.ResponseType.OK)

        box = dialogo.get_content_area()
        # Puedes personalizar esta etiqueta si quieres
        box.add(Gtk.Label(label="Buscar por nombre:"))
        
        entry = Gtk.Entry()
        entry.set_activates_default(True) # Permite usar Enter para aceptar
        box.add(entry)
        
        dialogo.set_default_response(Gtk.ResponseType.OK)
        dialogo.show_all()

        respuesta = dialogo.run()
        texto = entry.get_text().strip()
        dialogo.destroy()

        if respuesta == Gtk.ResponseType.OK:
            # Llama al método que la clase hija implementará
            self.realizar_busqueda(texto)
        elif respuesta == Gtk.ResponseType.APPLY:
            # Si se presiona "Limpiar", se realiza una búsqueda con texto vacío
            self.realizar_busqueda("")

    def realizar_busqueda(self, texto):
        """
        Este método será implementado por las clases hijas.
        Se encarga de aplicar el filtro en el repositorio y actualizar la vista.
        """
        # Las clases que heredan de Maestro deben implementar esta lógica
        print("Advertencia: El método 'realizar_busqueda' no ha sido implementado en la clase hija.")
        pass
    
    # def filtrar_items_por_texto(self, texto):
    #     """Filtra usando el repositorio si existe, aplicando el texto sobre el campo 'nombre'."""
    #     if not hasattr(self, "repo"):
    #         print("No hay repositorio definido para aplicar el filtro.")
    #         return

    #     self.pagina_actual = 0
    #     self.repo.filtros = {"nombre": texto}  # Podés ajustar este nombre si el campo se llama diferente
    #     self.actualizar_vista()


    def inicializar_distribucion(self):
        """Organiza los widgets en la ventana."""
        contenedor = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.add(contenedor)

        # Agregar el stack de vistas en el centro
        contenedor.pack_start(self.stack, True, True, 0)

        # Agregar la barra de navegación en la parte inferior
        contenedor.pack_end(self.barra_navegacion, False, False, 0)

    def inicializar_eventos(self):
        """Conecta los eventos de la ventana."""
        # --- AÑADE ESTAS DOS LÍNEAS ---
        self.connect("key-press-event", self.on_maestro_key_press)
        self.flowbox.connect("button-press-event", self.on_maestro_flowbox_button_press)

    def on_maestro_key_press(self, widget, event):
        """
        Manejador de teclado genérico para todas las ventanas Maestro.
        Maneja la tecla Escape para limpiar la selección.
        """
        if event.keyval == Gdk.KEY_Escape:
            # Usamos 'vista_predeterminada' que ya existe en tu código
            if self.vista_predeterminada == 'grilla':
                self.flowbox.unselect_all()
                self.last_selected_child_index = -1
                return True # Evento manejado
            elif self.vista_predeterminada == 'lista':
                selection = self.treeview.get_selection()
                selection.unselect_all()
                return True # Evento manejado
        
        return False # Dejar que el evento se propague si no es Escape

    def on_maestro_flowbox_button_press(self, flowbox, event):
        """
        Manejador de clics genérico para el FlowBox que implementa
        la selección con clic simple y Shift+clic.
        """
        # Solo nos interesa el clic izquierdo
        if event.button != Gdk.BUTTON_PRIMARY:
            return Gdk.EVENT_PROPAGATE

        child = flowbox.get_child_at_pos(event.x, event.y)
        if not child:
            return Gdk.EVENT_PROPAGATE # Clic en espacio vacío
        
        current_index = child.get_index()
        modifiers = Gtk.accelerator_get_default_mod_mask()
        is_shift_pressed = (event.state & modifiers) == Gdk.ModifierType.SHIFT_MASK
        is_ctrl_pressed = (event.state & modifiers) == Gdk.ModifierType.CONTROL_MASK

        # Si se presiona Ctrl, dejamos que GTK haga su magia
        if is_ctrl_pressed:
            self.last_selected_child_index = current_index
            return Gdk.EVENT_PROPAGATE

        # Si se presiona Shift y hay un ancla de selección
        if is_shift_pressed and self.last_selected_child_index != -1:
            start = min(self.last_selected_child_index, current_index)
            end = max(self.last_selected_child_index, current_index)
            
            flowbox.unselect_all()
            all_children = flowbox.get_children()
            for i in range(start, end + 1):
                flowbox.select_child(all_children[i])
            
            return Gdk.EVENT_STOP # Detenemos la propagación, ya lo manejamos

        # Si es un clic simple (sin Shift ni Ctrl)
        flowbox.unselect_all()
        flowbox.select_child(child)
        self.last_selected_child_index = current_index
        return Gdk.EVENT_STOP # Detenemos la propagación
    
    def set_items(self, lista_de_items):
        """Carga o recarga los datos en ambas vistas."""
        self.items = lista_de_items
        self.actualizar_lista()
        self.actualizar_grilla()

    def set_columnas_lista(self, columnas, tipos):
        """Define las columnas visibles en la vista tipo tabla con tipos específicos."""
        self.store_lista = Gtk.ListStore(*tipos)  # Define el modelo con los tipos especificados
        self.treeview.set_model(self.store_lista)

        # Limpiar columnas existentes
        for columna in self.treeview.get_columns():
            self.treeview.remove_column(columna)

        # Agregar nuevas columnas
        for indice, titulo in enumerate(columnas):
            celda = Gtk.CellRendererText()
            columna = Gtk.TreeViewColumn(titulo, celda, text=indice)
            columna.set_resizable(True)
            self.treeview.append_column(columna)

    def set_on_action(self, callback):
        """Define un callback para responder a las acciones del popover."""
        self.callback_accion = callback

    def actualizar_lista(self):
        """Actualiza la vista tipo lista."""
        self.store_lista.clear()
        for item in self.items:
            fila = [item["atributos"].get(col, "") for col in self.columnas_lista]
            self.store_lista.append(fila)

    def actualizar_grilla(self):
        """Actualiza la vista tipo grilla."""
        for child in self.flowbox.get_children():
            self.flowbox.remove(child)

        for item in self.items:
            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
            if "imagen_url" in item:
                try:
                    pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(item["imagen_url"], 128, 128, True)
                    imagen = Gtk.Image.new_from_pixbuf(pixbuf)
                except:
                    imagen = Gtk.Image.new_from_icon_name("image-missing", Gtk.IconSize.DIALOG)
                box.pack_start(imagen, False, False, 0)

            etiqueta = Gtk.Label(label=item["titulo"])
            box.pack_start(etiqueta, False, False, 0)

            boton = Gtk.Button(label="Acciones")
            boton.connect("clicked", self.mostrar_popover, item)
            box.pack_start(boton, False, False, 0)

            self.flowbox.add(box)

        self.flowbox.show_all()

    def mostrar_popover(self, boton, item):
        """Muestra un popover con acciones para un ítem."""
        if not self.callback_accion:
            return

        popover = Gtk.Popover.new(boton)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        for accion in ["Ver", "Actualizar", "Eliminar"]:
            boton_accion = Gtk.Button(label=accion)
            boton_accion.connect("clicked", lambda _, a=accion: self.callback_accion(item, a))
            box.pack_start(boton_accion, False, False, 0)
        popover.add(box)
        popover.show_all()
        popover.popup()

    def cambiar_vista(self, boton):
        if self.vista_predeterminada == "lista":
            self.vista_predeterminada = "grilla"
            self.stack.set_visible_child_name("grilla")
        else:
            self.vista_predeterminada = "lista"
            self.stack.set_visible_child_name("lista")

        self.actualizar_icono_vista()
        self.actualizar_vista()


    def filtrar_items(self, search_entry):
        """Filtra los ítems según el texto ingresado."""
        texto = search_entry.get_text().lower()
        items_filtrados = [item for item in self.items if texto in item["titulo"].lower()]
        self.set_items(items_filtrados)

    # En la clase Maestro en maestro.py

    def restaurar_configuracion_ventana(self):
        """Restaura el tamaño, la posición y la vista de la ventana desde el archivo de configuración."""
        seccion = self.get_title()
        if self.config.has_section(seccion):
            x = int(self.config.get(seccion, "pos_x", fallback="100"))
            y = int(self.config.get(seccion, "pos_y", fallback="100"))
            ancho = int(self.config.get(seccion, "ancho", fallback="800"))
            alto = int(self.config.get(seccion, "alto", fallback="600"))
            self.move(x, y)
            self.set_default_size(ancho, alto)

            # --- LÍNEA AÑADIDA ---
            # Restauramos la vista, con "grilla" como valor por defecto
            self.vista_predeterminada = self.config.get(seccion, "vista", fallback="grilla")
        else:
            self.set_default_size(800, 600)
            self.vista_predeterminada = "grilla" # Valor por defecto si no hay sección

    def guardar_configuracion_ventana(self, *args):
        """Guarda el tamaño, la posición y la vista de la ventana en el archivo de configuración."""
        x, y = self.get_position()
        ancho, alto = self.get_size()
        
        # Obtenemos el nombre de la sección (título de la ventana)
        seccion = self.get_title()
        if not self.config.has_section(seccion):
            self.config.add_section(seccion)

        # Guardamos los valores
        self.config.set(seccion, "pos_x", str(x))
        self.config.set(seccion, "pos_y", str(y))
        self.config.set(seccion, "ancho", str(ancho))
        self.config.set(seccion, "alto", str(alto))
        
        # --- LÍNEA AÑADIDA ---
        # Guardamos la vista actual (lista o grilla)
        self.config.set(seccion, "vista", self.vista_predeterminada)
        print(f"Guardando configuración de la ventana: {seccion} - Posición: ({x}, {y}), Tamaño: ({ancho}, {alto}), Vista: {self.vista_predeterminada}")
        
        with open(self.ruta_config, "w") as archivo:
            self.config.write(archivo)

    def crear_barra_navegacion(self):
        """Crea la barra de navegación."""
        self.barra_navegacion = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)

        # Botón para ir a la página anterior
        try:
            img_prev = GdkPixbuf.Pixbuf.new_from_file_at_scale("images/anterior.png", 24, 24, True)
            self.boton_anterior = Gtk.Button()
            self.boton_anterior.set_image(Gtk.Image.new_from_pixbuf(img_prev))
        except:
            self.boton_anterior = Gtk.Button(label="Anterior")
        self.barra_navegacion.pack_start(self.boton_anterior, False, False, 0)
        self.boton_anterior.connect("clicked", self.ir_anterior)

        # Etiqueta para mostrar la página actual
        self.label_pagina = Gtk.Label(label="Página 1 de 1")
        self.barra_navegacion.pack_start(self.label_pagina, True, True, 0)

        # Botón para ir a la página siguiente
        try:
            img_next = GdkPixbuf.Pixbuf.new_from_file_at_scale("images/siguiente.png", 24, 24, True)
            self.boton_siguiente = Gtk.Button()
            self.boton_siguiente.set_image(Gtk.Image.new_from_pixbuf(img_next))
        except:
            self.boton_siguiente = Gtk.Button(label="Siguiente")
        self.barra_navegacion.pack_start(self.boton_siguiente, False, False, 0)
        self.boton_siguiente.connect("clicked", self.ir_siguiente)

    def actualizar_vista(self):
        """Actualiza la vista actual (tabla o grilla) según la configuración."""
        if getattr(self, "vista_predeterminada", "tabla") == "grilla":
            self.stack.set_visible_child_name("grilla")
            self.mostrar_grilla()
        else:
            self.stack.set_visible_child_name("lista")
            self.mostrar_lista()

    def mostrar_lista(self):
        """Llena la vista tipo tabla con los datos."""
        pass

    def mostrar_grilla(self):
        """Llena la vista tipo grilla con los datos."""
        pass
    
    def ordenar_por_columna(self, column, index, nombre_columna):
        """Ordena los datos según la columna seleccionada."""
        if self.columna_orden == nombre_columna:
            self.direccion_orden = "desc" if self.direccion_orden == "asc" else "asc"
        else:
            self.columna_orden = nombre_columna
            self.direccion_orden = "asc"
        self.pagina_actual = 0
        self.actualizar_vista()
    
    def actualizar_navegacion(self):
        """Actualiza la barra de navegación con la información de la página actual."""
        total = self.repo.obtener_total()
        max_pagina = (total - 1) // self.volumenes_por_pagina
        self.label_pagina.set_text(f"Página {self.pagina_actual + 1} de {max_pagina + 1}")
        self.boton_anterior.set_sensitive(self.pagina_actual > 0)
        self.boton_siguiente.set_sensitive(self.pagina_actual < max_pagina)

    def ir_anterior(self, button):
        """Navega a la página anterior."""
        self.pagina_actual = max(self.pagina_actual - 1, 0)
        if self.stack.get_visible_child_name() == "grilla":
            self.mostrar_grilla()
        else:
            self.mostrar_lista()

    def ir_siguiente(self, button):
        """Navega a la página siguiente."""
        self.pagina_actual = self.repo.pagina_siguiente(self.pagina_actual, self.volumenes_por_pagina)
        if self.stack.get_visible_child_name() == "grilla":
            self.mostrar_grilla()
        else:
            self.mostrar_lista()
   
    def set_on_child_activated(self, callback):
        """
        Permite a la clase hija registrar una función para cuando un
        elemento del FlowBox es activado.
        """
        self.callback_child_activated = callback
        
    def on_flowbox_child_activated(self, flowbox, child):
        """
        Este método se dispara cuando se activa un hijo en el FlowBox.
        """
        # Obtenemos el Frame que está dentro del FlowBoxChild
        frame = child.get_child()
        # Recuperamos el objeto de datos que asociamos previamente
        item = frame.item_data
        
        # Si hay un callback registrado y encontramos el item, lo llamamos
        if self.callback_child_activated and item:
            self.callback_child_activated(item)

    def _cargar_thumbnail_en_hilo(self, ruta_imagen, imagen_widget, spinner, stack, comic_obj):
        """
        Esta función se ejecuta en un hilo separado.
        Ahora también gestiona la cola de carátulas faltantes.
        """

        # Obtenemos el tamaño directamente del objeto de configuración
        # Si no hay configuración, usamos un valor seguro por defecto (ej: 120)
        size = self.setup_config.ancho_thumbnail if self.setup_config else 120


        pixbuf_cargado = None
        if os.path.exists(ruta_imagen):
            # Si el thumbnail ya existe, lo cargamos
            try:
                pixbuf_cargado = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                    ruta_imagen, size, size, True
                )
            except Exception as e:
                print(f"ERROR al cargar thumbnail existente: {ruta_imagen} - {e}")
                # El thumbnail está corrupto, lo añadimos a la cola para regenerar
                if self.thumbnail_manager:
                    self.thumbnail_manager.add_to_queue(comic_obj)
        else:
            # Si el thumbnail NO existe, lo añadimos a la cola
            if self.thumbnail_manager:
                self.thumbnail_manager.add_to_queue(comic_obj)

        # Si no se pudo cargar un pixbuf (sea porque no existe o está corrupto),
        # usamos la imagen genérica como placeholder.
        if not pixbuf_cargado:
            try:
                pixbuf_cargado = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                    "images/Comic_sin_caratula.png", size, size, True
                )
            except:
                pass # Si todo falla, el pixbuf será None

        GLib.idle_add(
            self._actualizar_imagen_en_main_thread,
            pixbuf_cargado,
            imagen_widget,
            spinner,
            stack
        )
    

    def _actualizar_imagen_en_main_thread(self, pixbuf, imagen_widget, spinner, stack):
        """
        Esta función se ejecuta de forma segura en el hilo principal de GTK
        para actualizar la interfaz.
        """
        spinner.stop() # Detenemos el spinner
        if pixbuf:
            imagen_widget.set_from_pixbuf(pixbuf)
        else:
            # Si el pixbuf es None, mostramos un ícono de imagen rota
            imagen_widget.set_from_icon_name("image-missing", Gtk.IconSize.DIALOG)
        
        # Cambiamos la vista del Stack del spinner a la imagen
        stack.set_visible_child_name("imagen")