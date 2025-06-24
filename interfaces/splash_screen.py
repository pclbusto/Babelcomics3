import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GdkPixbuf, Gdk, GLib
import os

class SplashScreen(Gtk.Window):
    def __init__(self, logo_path="images/Babelcomic3.png", tiempo=2000):
        super().__init__(type=Gtk.WindowType.POPUP)

        self.set_app_paintable(True)
        self.set_decorated(False)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_keep_above(True)

        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual and self.is_composited():
            self.set_visual(visual)

        # Fondo transparente
        self.connect("draw", self.dibujar_fondo_transparente)

        # Contenedor y logo
        box = Gtk.Box()
        self.add(box)

        if os.path.exists(logo_path):
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(logo_path, 256, 256, True)
            image = Gtk.Image.new_from_pixbuf(pixbuf)
        else:
            image = Gtk.Image.new_from_icon_name("image-missing", Gtk.IconSize.DIALOG)

        box.pack_start(image, True, True, 0)

        self.show_all()
        GLib.timeout_add(tiempo, self.close)

    def dibujar_fondo_transparente(self, widget, cr):
        cr.set_source_rgba(0, 0, 0, 0)  # completamente transparente
        cr.set_operator(Gdk.cairo.Operator.SOURCE)
        cr.paint()
        cr.set_operator(Gdk.cairo.Operator.OVER)
        return False
