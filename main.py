import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib, Gio

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import sessionmaker
from entidades import Base, engine
from entidades.setup_model import Setup
from interfaces.catalogo_window import CatalogoWindow
from helpers.thumbnail_manager import ThumbnailManager

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RUTA_ICONO = os.path.join(BASE_DIR, 'images', 'Babelcomic3.png')

def inicializar_base():
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    if not session.query(Setup).first():
        setup = Setup() 
        session.add(setup)
        session.commit()

class BabelComicsApp(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="com.babelcomics.app", flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.thumbnail_manager = ThumbnailManager()

    def do_activate(self):
        inicializar_base()

        if os.path.exists(RUTA_ICONO):
            # Gtk.Window.set_default_icon_from_file(RUTA_ICONO)
            Gtk.Window.set_default_icon_name("applications-graphics")

        self.thumbnail_manager.start_background_generator()
        win = CatalogoWindow(application=self, thumbnail_manager=self.thumbnail_manager)
        self.add_window(win)
        win.present()

if __name__ == "__main__":
    app = BabelComicsApp()
    app.run(sys.argv)
