import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import sys
import os   
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import sessionmaker
from entidades import Base, engine
from entidades.setup_model import Setup
from interfaces.setup_visual_config import SetupVisualWindow
from interfaces.catalogo_window import CatalogoWindow  # Importamos la clase CatalogoWindow


def inicializar_base():
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    if not session.query(Setup).first():
        setup = Setup() 
        session.add(setup)
        session.commit()

if __name__ == "__main__":
    inicializar_base()
    # SetupVisualWindow()
    ventana_catalogo = CatalogoWindow()
    Gtk.main()