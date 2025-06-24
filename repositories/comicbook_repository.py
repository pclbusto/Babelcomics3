# repositories/comicbook_repository.py

from entidades.comicbook_model import Comicbook
from .base_repository import BaseRepository

class ComicbookRepository(BaseRepository):
    """
    Repositorio para gestionar las operaciones de la base de datos
    para la entidad Comicbook.
    """
    def __init__(self, session):
        super().__init__(session)

    def obtener_total(self, modelo=None):
        """
        Obtiene el número total de cómics, aplicando los filtros actuales.
        """
        return super().obtener_total(Comicbook)

    def obtener_pagina(self, pagina, tamanio, orden="path", direccion="asc", columnas=None):
        """
        Obtiene una página de cómics de la base de datos, aplicando filtros,
        ordenación y paginación.
        """
        return super().obtener_pagina(Comicbook, pagina, tamanio, orden, direccion, columnas)

    def pagina_siguiente(self, pagina_actual, tamanio):
        """
        Calcula el número de la página siguiente para la paginación de cómics.
        """
        return super().pagina_siguiente(pagina_actual, tamanio, Comicbook)
        def pagina_anterior(self, pagina_actual, tamanio):
            """
            Calcula el número de la página anterior para la paginación de cómics.
            """
            return super().pagina_anterior(pagina_actual, tamanio, Comicbook)