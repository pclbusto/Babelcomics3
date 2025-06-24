# helpers/thumbnail_manager.py

import os
import threading
import time
import zipfile
from unrar import rarfile
from PIL import Image

class ThumbnailManager:
    THUMBNAIL_DIR = "data/thumbnails/comics"
    QUEUE_FILE = "data/missing_thumbnails.txt"
    SEPARATOR = "::" # Separador para el ID y la ruta en el archivo

    def __init__(self):
        os.makedirs(os.path.dirname(self.QUEUE_FILE), exist_ok=True)
        os.makedirs(self.THUMBNAIL_DIR, exist_ok=True)
        self.queue = self._load_queue()
        self.queue_lock = threading.Lock()
        self.stop_event = threading.Event()

    def _load_queue(self):
        """Carga la cola desde el archivo de texto (formato: ID::Ruta)."""
        queue_set = set()
        if not os.path.exists(self.QUEUE_FILE):
            return queue_set
        with open(self.QUEUE_FILE, 'r') as f:
            for line in f:
                if self.SEPARATOR in line:
                    parts = line.strip().split(self.SEPARATOR, 1)
                    if len(parts) == 2:
                        try:
                            # Guardamos como tupla (id, path)
                            queue_set.add((int(parts[0]), parts[1]))
                        except ValueError:
                            print(f"ADVERTENCIA: Línea malformada en la cola: {line.strip()}")
        return queue_set

    def add_to_queue(self, comic_obj):
        """Añade un cómic (ID y ruta) a la cola si no está ya presente."""
        if not comic_obj or not comic_obj.id_comicbook:
            return

        item_tuple = (comic_obj.id_comicbook, comic_obj.path)
        with self.queue_lock:
            if item_tuple not in self.queue:
                self.queue.add(item_tuple)
                with open(self.QUEUE_FILE, 'a') as f:
                    f.write(f"{item_tuple[0]}{self.SEPARATOR}{item_tuple[1]}\n")
                print(f"INFO: Añadido a la cola: ID {item_tuple[0]}")

    def start_background_generator(self):
        # ... (este método no cambia)
        thread = threading.Thread(target=self._process_queue)
        thread.daemon = True
        thread.start()
        print("INFO: Hilo generador de thumbnails iniciado.")

    def stop_generator(self):
        # ... (este método no cambia)
        self.stop_event.set()

    def _process_queue(self):
        """Bucle principal del hilo: procesa la cola continuamente."""
        while not self.stop_event.is_set():
            item_tuple = None
            with self.queue_lock:
                if self.queue:
                    item_tuple = self.queue.pop()

            if item_tuple:
                comic_id, comic_path = item_tuple
                print(f"INFO: Procesando thumbnail para ID: {comic_id}")
                if self._generate_thumbnail(comic_id, comic_path):
                    self._remove_from_file(comic_id, comic_path)
            else:
                time.sleep(5)
    
    def _get_file_type(self, file_path):
        # ... (este método no cambia)
        try:
            with open(file_path, 'rb') as f:
                header = f.read(4)
                if header.startswith(b'PK'): return 'zip'
                elif header.startswith(b'Rar!'): return 'rar'
                return 'unknown'
        except Exception:
            return 'error'

    def _generate_thumbnail(self, comic_id, comic_path):
        """Lógica central para generar una única carátula usando el ID."""
        if not os.path.exists(comic_path):
            return True

        file_type = self._get_file_type(comic_path)
        first_image_data = None

        try:
            if file_type == 'zip':
                with zipfile.ZipFile(comic_path, 'r') as zf:
                    image_files = sorted([f for f in zf.namelist() if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')) and not f.startswith('__MACOSX')])
                    if image_files: first_image_data = zf.read(image_files[0])
            elif file_type == 'rar':
                with rarfile.RarFile(comic_path, 'r') as rf:
                    image_files = sorted([f.filename for f in rf.infolist() if f.filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp'))])
                    if image_files: first_image_data = rf.read(image_files[0])
            else:
                return True

            if first_image_data:
                from io import BytesIO
                img = Image.open(BytesIO(first_image_data))
                if img.mode in ('RGBA', 'P'): img = img.convert('RGB')
                img.thumbnail((128, 128))

                output_path = os.path.join(self.THUMBNAIL_DIR, f"{comic_id}.jpg") # <-- Cambiar a .jpg

                # Guardamos como JPEG con una calidad del 85% (un buen balance)
                img.save(output_path, "JPEG", quality=85) # <-- Cambiar a JPEG y añadir calidad

                print(f"INFO: Thumbnail generado en: {output_path}")
                return True
        except Exception as e:
            print(f"ERROR: No se pudo generar thumbnail para ID {comic_id}: {e}")
            return False
            
        return True

    def _remove_from_file(self, comic_id, comic_path):
        """Elimina una línea específica del archivo de cola."""
        line_to_remove = f"{comic_id}{self.SEPARATOR}{comic_path}"
        with self.queue_lock:
            with open(self.QUEUE_FILE, 'r') as f_read:
                lines = [line.strip() for line in f_read if line.strip() != line_to_remove]
            with open(self.QUEUE_FILE, 'w') as f_write:
                for line in lines:
                    f_write.write(f"{line}\n")