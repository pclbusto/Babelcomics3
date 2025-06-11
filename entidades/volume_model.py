from entidades import Base
from sqlalchemy import Column, Integer, String

class Volume(Base):
    __tablename__ = 'volumens'
    id_volume = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False, default='')
    deck = Column(String, nullable=False, default='')
    descripcion = Column(String, nullable=False, default='')
    url = Column(String, nullable=False, default='')
    image_url = Column(String, nullable=False, default='')
    id_publisher = Column(String, nullable=False, default='')
    publisher_name = Column(String, nullable=False, default='')
    anio_inicio = Column(Integer, nullable=False, default=0)
    cantidad_numeros = Column(Integer, nullable=False, default=0)

    def __repr__(self):
        return f"<volumens(id_volume={self.id_volume}, nombre='{self.nombre}', deck='{self.deck}', descripcion='{self.descripcion}', url='{self.url}', image_url='{self.image_url}', id_publisher='{self.id_publisher}', publisher_name='{self.publisher_name}', anio_inicio={self.anio_inicio}, cantidad_numeros={self.cantidad_numeros})>"
    
    def obtener_cover(self, volumen):
        import os
        if volumen.image_url:
            nombre_archivo = volumen.image_url.rsplit("/", 1)[-1]
            ruta = os.path.join("data", "thumbnails", "volumenes", nombre_archivo)
            if os.path.exists(ruta):
                return ruta
        return "images/Volumen_sin_caratula.png"
