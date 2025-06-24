from entidades.volume_model import Volume
from .base_repository import BaseRepository

class VolumeRepository(BaseRepository):
    def __init__(self, session):
        super().__init__(session)

    def obtener_total(self, modelo=None):
        return super().obtener_total(modelo or Volume)

    def obtener_pagina(self, pagina, tamanio, orden="nombre", direccion="asc", columnas=None):
        return super().obtener_pagina(Volume, pagina, tamanio, orden, direccion, columnas)

    def pagina_siguiente(self, pagina_actual, tamanio):
        print("Llamando a pagina_siguiente en VolumeRepository")
        return super().pagina_siguiente(pagina_actual, tamanio, Volume)
