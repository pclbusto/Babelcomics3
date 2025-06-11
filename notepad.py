import gi
import time
import base64
import hashlib
from cryptography.fernet import Fernet
from threading import Timer
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

class TextEditor(Gtk.Window):
    def __init__(self):
        super().__init__(title="Editor de Texto")
        self.set_default_size(800, 600)

        # Derivar clave fija a partir de la palabra "tanatos"
        key_base = "tanatos".encode()
        key_hash = hashlib.sha256(key_base).digest()
        self.key = base64.urlsafe_b64encode(key_hash[:32])
        self.cipher_suite = Fernet(self.key)

        # Última edición
        self.last_edit_time = time.time()
        self.timer = None

        # Crear área de texto
        self.textview = Gtk.TextView()
        self.textbuffer = self.textview.get_buffer()
        self.textbuffer.connect("changed", self.on_text_changed)

        # Configurar el ajuste automático del texto al tamaño de la ventana
        self.textview.set_wrap_mode(Gtk.WrapMode.WORD)
        self.textview.set_hexpand(True)
        self.textview.set_vexpand(True)
        self.encryption_delay = 10  # segundos

        # Configurar el temporizador para encriptar automáticamente
        self.timer = Timer(self.encryption_delay, self.save_encrypted)

        # Crear barra de herramientas
        toolbar = Gtk.Toolbar()

        # Crear botón para encriptar texto en pantalla
        encrypt_button = Gtk.ToolButton.new_from_stock(Gtk.STOCK_CONVERT)
        encrypt_button.set_label("Encriptar")
        encrypt_button.connect("clicked", self.on_encrypt)
        toolbar.insert(encrypt_button, -1)

        # Crear botón para desencriptar texto
        decrypt_button = Gtk.ToolButton.new_from_stock(Gtk.STOCK_CONVERT)
        decrypt_button.set_label("Desencriptar")
        decrypt_button.connect("clicked", self.on_decrypt)
        toolbar.insert(decrypt_button, -1)

        # Crear diseño
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        vbox.pack_start(toolbar, False, False, 0)
        vbox.pack_start(self.textview, True, True, 0)
        self.add(vbox)

    def on_text_changed(self, buffer):
        self.last_edit_time = time.time()
        if self.timer:
            self.timer.cancel()
        self.timer = Timer(10, self.save_encrypted)
        self.timer.start()

    def save_encrypted(self):
        start_iter = self.textbuffer.get_start_iter()
        end_iter = self.textbuffer.get_end_iter()
        text = self.textbuffer.get_text(start_iter, end_iter, True)
        encrypted_text = self.cipher_suite.encrypt(text.encode())
        with open("encrypted_text.txt", "wb") as file:
            file.write(encrypted_text)
        print("Texto guardado encriptado.")

    def on_encrypt(self, widget):
        start_iter = self.textbuffer.get_start_iter()
        end_iter = self.textbuffer.get_end_iter()
        text = self.textbuffer.get_text(start_iter, end_iter, True)
        encrypted_text = self.cipher_suite.encrypt(text.encode())
        self.textbuffer.set_text(encrypted_text.decode())
        print("Texto encriptado en pantalla.")

    def on_decrypt(self, widget):
        try:
            with open("encrypted_text.txt", "rb") as file:
                encrypted_text = file.read()
            decrypted_text = self.cipher_suite.decrypt(encrypted_text).decode()
            self.textbuffer.set_text(decrypted_text)
            print("Texto desencriptado en pantalla.")
        except Exception as e:
            print("Error al desencriptar:", e)
            print("Asegúrate de que el archivo 'encrypted_text.txt' contiene texto válido y que la clave es correcta.")

if __name__ == "__main__":
    editor = TextEditor()
    editor.connect("destroy", Gtk.main_quit)
    editor.show_all()
    Gtk.main()
