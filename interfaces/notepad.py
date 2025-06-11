import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk

class BlockSelectEditor(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="Editor con Selección en Bloque (ALT + arrastrar)")
        self.set_default_size(800, 600)

        self.textview = Gtk.TextView()
        self.textbuffer = self.textview.get_buffer()
        self.textview.set_monospace(True)

        self.scrolled = Gtk.ScrolledWindow()
        self.scrolled.add(self.textview)
        self.add(self.scrolled)

        self.start_iter = None
        self.block_coords = None  # (start_line, end_line, start_offset, end_offset)

        # Crear el tag visual para la selección en bloque
        self.tag_block = self.textbuffer.create_tag("block_select", background="#add8e6")

        # Agregar eventos del mouse
        self.textview.add_events(
            Gdk.EventMask.BUTTON_PRESS_MASK |
            Gdk.EventMask.BUTTON_RELEASE_MASK |
            Gdk.EventMask.POINTER_MOTION_MASK
        )
        self.textview.connect("button-press-event", self.on_button_press)
        self.textview.connect("motion-notify-event", self.on_mouse_motion)
        self.textview.connect("button-release-event", self.on_button_release)
        self.textview.connect("key-press-event", self.on_key_press)

    def get_iter_at_coords(self, x, y):
        bx, by = self.textview.window_to_buffer_coords(Gtk.TextWindowType.TEXT, x, y)
        iter, _ = self.textview.get_iter_at_location(bx, by)
        return iter

    def on_button_press(self, widget, event):
        if event.button == 1 and event.state & Gdk.ModifierType.MOD1_MASK:  # Alt + click
            self.textbuffer.remove_tag(self.tag_block, self.textbuffer.get_start_iter(), self.textbuffer.get_end_iter())
            self.start_iter = self.get_iter_at_coords(int(event.x), int(event.y))
            return True
        return False

    def on_mouse_motion(self, widget, event):
        if event.state & Gdk.ModifierType.BUTTON1_MASK and event.state & Gdk.ModifierType.MOD1_MASK:
            if not self.start_iter:
                return False

            end_iter = self.get_iter_at_coords(int(event.x), int(event.y))
            if not isinstance(end_iter, Gtk.TextIter):
                return False

            start_line = min(self.start_iter.get_line(), end_iter.get_line())
            end_line = max(self.start_iter.get_line(), end_iter.get_line())
            start_offset = min(self.start_iter.get_line_offset(), end_iter.get_line_offset())
            end_offset = max(self.start_iter.get_line_offset(), end_iter.get_line_offset())

            self.block_coords = (start_line, end_line, start_offset, end_offset)

            self.textbuffer.remove_tag(self.tag_block, self.textbuffer.get_start_iter(), self.textbuffer.get_end_iter())

            for line in range(start_line, end_line + 1):
                line_iter = self.textbuffer.get_iter_at_line(line)
                line_start = line_iter.copy()
                line_start.forward_chars(start_offset)
                line_end = line_iter.copy()
                line_end.forward_chars(end_offset)
                self.textbuffer.apply_tag(self.tag_block, line_start, line_end)
            return True
        return False

    def on_button_release(self, widget, event):
        self.start_iter = None
        return False

    def on_key_press(self, widget, event):
        ctrl = event.state & Gdk.ModifierType.CONTROL_MASK
        shift = event.state & Gdk.ModifierType.SHIFT_MASK
        keyval = Gdk.keyval_name(event.keyval)

        if ctrl and shift and keyval == 'c':
            self.copy_block_selection()
            return True
        return False

    def copy_block_selection(self):
        if not self.block_coords:
            return

        start_line, end_line, start_offset, end_offset = self.block_coords
        copied_lines = []

        for line in range(start_line, end_line + 1):
            iter_line = self.textbuffer.get_iter_at_line(line)
            start = iter_line.copy()
            end = iter_line.copy()

            start.forward_chars(start_offset)
            end.forward_chars(end_offset)

            text = self.textbuffer.get_text(start, end, False)
            copied_lines.append(text)

        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        clipboard.set_text('\n'.join(copied_lines), -1)

win = BlockSelectEditor()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
