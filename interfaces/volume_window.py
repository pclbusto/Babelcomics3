import os
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GdkPixbuf

from interfaces.maestro import Maestro  # Importa la clase Maestro
from repositories.volume_repository import VolumeRepository


class VolumeWindow(Maestro):
    def __init__(self, session):
        super().__init__(titulo="Gestión de Volúmenes")
        self.repo = VolumeRepository(session)
        self.volumenes_por_pagina = 20
        self.pagina_actual = 0
        self.columna_orden = "nombre"
        self.direccion_orden = "asc"
        # self.titulo_columna = ["ID", "Nombre", "Deck", "Descripción", "URL", "Imagen", "ID Publisher", "Editorial", "Año Inicio", "# Números"]
        self.titulo_columna = ["id_volume", "nombre", "publisher_name", "anio_inicio", "cantidad_numeros"]
        # Configurar las columnas de la tabla
        self.set_columnas_lista(
            self.titulo_columna,
            [int, str, str, int, int]
        )
        # # Actualizar la vista inicial
        self.actualizar_vista()
        self.actualizar_icono_vista()  

    def realizar_busqueda(self, texto):
        """
        Aplica el filtro de búsqueda en el repositorio de Volumes y
        actualiza la vista.
        """
        if texto:
            # Filtra por el campo 'nombre' en la base de datos
            self.repo.filtrar(nombre=texto)
        else:
            # Si el texto está vacío, limpia los filtros
            self.repo.limpiar_filtros()
        
        # Vuelve a la primera página para mostrar los resultados desde el inicio
        self.pagina_actual = 0
        
        # Actualiza la vista para reflejar los resultados de la búsqueda
        self.actualizar_vista()


    def mostrar_lista(self):
        """Llena la vista tipo tabla con los datos."""
        self.store_lista.clear()
        volumenes = self.repo.obtener_pagina(
            self.pagina_actual,
            self.volumenes_por_pagina,
            orden=self.columna_orden,
            direccion=self.direccion_orden,
            columnas=self.titulo_columna

        )
        for v in volumenes:
            self.store_lista.append([
                v.id_volume, v.nombre, v.publisher_name, v.anio_inicio, v.cantidad_numeros
            ])
        self.actualizar_navegacion()


    def mostrar_grilla(self):
        print("Mostrando grilla de volúmenes")
        volumenes = self.repo.obtener_pagina(
            self.pagina_actual,
            self.volumenes_por_pagina,
            orden=self.columna_orden,
            direccion=self.direccion_orden
        )

        self.construir_grilla(
            volumenes,
            get_image_path=lambda v: v.obtener_cover(),
            get_label_text=lambda v: v.nombre
        )

        self.actualizar_navegacion()

    

    def aplicar_filtros(self, button):
        # """Aplica los filtros seleccionados en la barra de filtros."""
        # nombre = self.entrada_nombre.get_text().strip()
        # editorial = self.combo_editorial.get_active_text()

        # if not nombre and editorial == "Todas":
        #     self.repo.limpiar_filtros()
        # else:
        #     self.repo.filtrar(nombre=nombre if nombre else None,
        #                       editorial=editorial if editorial != "Todas" else None)
        # self.pagina_actual = 0

        # # Respetar la vista actual
        # if self.stack.get_visible_child_name() == "grilla":
        #     self.mostrar_grilla()
        # else:
        #     self.mostrar_tabla()
        pass

    

    
# Run the application
if __name__ == "__main__":
    from sqlalchemy.orm import sessionmaker
    from entidades import engine
    session = sessionmaker(bind=engine)()
    win = VolumeWindow(session=session)
    win.connect("destroy", Gtk.main_quit)
    Gtk.main()