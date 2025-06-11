from entidades.publisher_model import Publisher
import os

class PublisherRepository:
    def __init__(self, session):
        self.session = session

    def obtener_todos_los_publishers(self):
        return self.session.query(Publisher).all()

    def obtener_publisher_por_id(self, id_publisher):
        return self.session.query(Publisher).filter_by(id_publisher=id_publisher).first()

    def crear_publisher(self, id_publisher, nombre, deck='', descripcion='', url_logo='', sitio_web=''):
        nuevo_publisher = Publisher(
            id_publisher=id_publisher,
            nombre=nombre,
            deck=deck,
            descripcion=descripcion,
            url_logo=url_logo,
            sitio_web=sitio_web
        )
        self.session.add(nuevo_publisher)
        self.session.commit()
        return nuevo_publisher

    def actualizar_publisher(self, id_publisher, nombre=None, deck=None, descripcion=None, url_logo=None, sitio_web=None):
        publisher = self.obtener_publisher_por_id(id_publisher)
        if publisher:
            if nombre is not None:
                publisher.nombre = nombre
            if deck is not None:
                publisher.deck = deck
            if descripcion is not None:
                publisher.descripcion = descripcion
            if url_logo is not None:
                publisher.url_logo = url_logo
            if sitio_web is not None:
                publisher.sitio_web = sitio_web
            self.session.commit()
        return publisher

    def eliminar_publisher(self, id_publisher):
        publisher = self.obtener_publisher_por_id(id_publisher)
        if publisher:
            self.session.delete(publisher)
            self.session.commit()
            return True
        return False

    