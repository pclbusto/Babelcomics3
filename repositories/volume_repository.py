class VolumeRepository:
    def __init__(self, session):
        self.session = session
        self.filtros = {}

    def filtrar(self, nombre=None, editorial=None):
        self.filtros = {}
        if nombre:
            self.filtros['nombre'] = nombre.lower()
        if editorial:
            self.filtros['editorial'] = editorial.lower()

    def limpiar_filtros(self):
        self.filtros = {}

    def obtener_total(self):
        from entidades.volume_model import Volume
        query = self.session.query(Volume)
        if 'nombre' in self.filtros:
            query = query.filter(Volume.nombre.ilike(f"%{self.filtros['nombre']}%"))
        if 'editorial' in self.filtros:
            query = query.filter(Volume.publisher_name.ilike(f"%{self.filtros['editorial']}%"))
        return query.count()

    def obtener_pagina(self, pagina, tamanio, orden="nombre", direccion="asc"):
        from entidades.volume_model import Volume
        query = self.session.query(Volume)
        if 'nombre' in self.filtros:
            query = query.filter(Volume.nombre.ilike(f"%{self.filtros['nombre']}%"))
        if 'editorial' in self.filtros:
            query = query.filter(Volume.publisher_name.ilike(f"%{self.filtros['editorial']}%"))

        if hasattr(Volume, orden):
            campo = getattr(Volume, orden)
            campo = campo.desc() if direccion == "desc" else campo.asc()
            query = query.order_by(campo)

        return query.offset(pagina * tamanio).limit(tamanio).all()

    def pagina_siguiente(self, pagina_actual, tamanio):
        total = self.obtener_total()
        max_pagina = (total - 1) // tamanio
        return min(pagina_actual + 1, max_pagina)

