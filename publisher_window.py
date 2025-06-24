import os
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GdkPixbuf

from interfaces.maestro import Maestro
from repositories.publisher_repository import PublisherRepository


class PublisherWindow(Maestro):
    def __init__(self, session=None):
        super().__init__(titulo="Gestión de Publishers")
        self.repo = PublisherRepository(session)
        self.volumenes_por_pagina = 20
        self.pagina_actual = 0
        self.columna_orden = "nombre"
        self.direccion_orden = "asc"

        # Configurar columnas de la tabla
        self.set_columnas_lista(
            ["ID", "Nombre", "Deck", "Descripción", "Logo"],
            [int, str, str, str, str]
        )

        self.actualizar_vista()

    def mostrar_lista(self):
        self.store_lista.clear()
        publishers = self.repo.obtener_pagina(
            self.pagina_actual,
            self.volumenes_por_pagina,
            orden=self.columna_orden,
            direccion=self.direccion_orden
        )
        for p in publishers:
            self.store_lista.append([
                p.id_publisher,
                p.nombre,
                p.deck,
                p.descripcion,
                p.url_logo
            ])
        self.actualizar_navegacion()

    def mostrar_grilla(self):
        publishers = self.repo.obtener_pagina(
            self.pagina_actual,
            self.volumenes_por_pagina,
            orden=self.columna_orden,
            direccion=self.direccion_orden
        )
        self.construir_grilla(
            publishers,
            get_image_path=lambda p: p.obtener_nombre_logo(),
            get_label_text=lambda p: p.nombre
        )
        self.actualizar_navegacion()

    def aplicar_filtros(self, button):
        # Placeholder para aplicar filtros futuros
        pass


# Run the application
if __name__ == "__main__":
    from sqlalchemy.orm import sessionmaker
    from entidades import engine
    session = sessionmaker(bind=engine)()
    win = PublisherWindow(session=session)
    win.connect("destroy", Gtk.main_quit)
    Gtk.main()
