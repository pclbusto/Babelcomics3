from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from entidades.volume_model import Volume
from helpers.file_utils import get_db_path

# Crear engine y sesión
engine = create_engine(f"sqlite:///{get_db_path()}")
session = Session(bind=engine)

# Lista de volúmenes de prueba
volumenes = [
    {"nombre": "Green Lantern V1", "deck": "Hal Jordan inicia su camino", "descripcion": "Primera etapa clásica", "url": "", "image_url": "green_lantern_v1.jpg", "id_publisher": "dc", "publisher_name": "DC Comics", "anio_inicio": 1960, "cantidad_numeros": 89},
    {"nombre": "Batman V1", "deck": "El caballero oscuro clásico", "descripcion": "Primeros años del detective", "url": "", "image_url": "batman_v1.jpg", "id_publisher": "dc", "publisher_name": "DC Comics", "anio_inicio": 1940, "cantidad_numeros": 713},
    {"nombre": "Batman V2", "deck": "Renacimiento del murciélago", "descripcion": "Era moderna post-Crisis", "url": "", "image_url": "batman_v2.jpg", "id_publisher": "dc", "publisher_name": "DC Comics", "anio_inicio": 2011, "cantidad_numeros": 52},
    {"nombre": "X-Men", "deck": "Mutantes y evolución", "descripcion": "Primera formación de X-Men", "url": "", "image_url": "xmen_v1.jpg", "id_publisher": "marvel", "publisher_name": "Marvel Comics", "anio_inicio": 1963, "cantidad_numeros": 66},
    {"nombre": "The Flash V1", "deck": "Barry Allen corre", "descripcion": "El velocista escarlata", "url": "", "image_url": "flash_v1.jpg", "id_publisher": "dc", "publisher_name": "DC Comics", "anio_inicio": 1959, "cantidad_numeros": 350},
    {"nombre": "Invincible", "deck": "El superhéroe de Kirkman", "descripcion": "Sangre, familia y traición", "url": "", "image_url": "invincible.jpg", "id_publisher": "image", "publisher_name": "Image Comics", "anio_inicio": 2003, "cantidad_numeros": 144},
    {"nombre": "TMNT", "deck": "Tortugas ninja", "descripcion": "Original blanco y negro", "url": "", "image_url": "tmnt.jpg", "id_publisher": "mirage", "publisher_name": "Mirage Studios", "anio_inicio": 1984, "cantidad_numeros": 62},
    {"nombre": "Spawn", "deck": "Oscuridad y redención", "descripcion": "Todd McFarlane's Spawn", "url": "", "image_url": "spawn.jpg", "id_publisher": "image", "publisher_name": "Image Comics", "anio_inicio": 1992, "cantidad_numeros": 300},
    {"nombre": "Saga", "deck": "Espacio y fantasía", "descripcion": "Una ópera espacial moderna", "url": "", "image_url": "saga.jpg", "id_publisher": "image", "publisher_name": "Image Comics", "anio_inicio": 2012, "cantidad_numeros": 54},
    {"nombre": "Watchmen", "deck": "¿Quién vigila a los vigilantes?", "descripcion": "Obra maestra de Alan Moore", "url": "", "image_url": "watchmen.jpg", "id_publisher": "dc", "publisher_name": "DC Comics", "anio_inicio": 1986, "cantidad_numeros": 12},
    {"nombre": "Sandman", "deck": "El señor de los sueños", "descripcion": "Neil Gaiman en su mejor forma", "url": "", "image_url": "sandman.jpg", "id_publisher": "dc", "publisher_name": "DC Comics/Vertigo", "anio_inicio": 1989, "cantidad_numeros": 75},
    {"nombre": "Hellboy", "deck": "Demonio con buen corazón", "descripcion": "Mike Mignola y su universo", "url": "", "image_url": "hellboy.jpg", "id_publisher": "darkhorse", "publisher_name": "Dark Horse", "anio_inicio": 1993, "cantidad_numeros": 60},
    {"nombre": "Ultimate Spider-Man", "deck": "Reinvención moderna", "descripcion": "Peter Parker en siglo XXI", "url": "", "image_url": "ultimate_spiderman.jpg", "id_publisher": "marvel", "publisher_name": "Marvel Comics", "anio_inicio": 2000, "cantidad_numeros": 160},
    {"nombre": "Ms. Marvel", "deck": "Kamala Khan", "descripcion": "Diversidad y juventud", "url": "", "image_url": "msmarvel.jpg", "id_publisher": "marvel", "publisher_name": "Marvel Comics", "anio_inicio": 2014, "cantidad_numeros": 38},
    {"nombre": "Moon Knight", "deck": "El vigilante de la noche", "descripcion": "Marc Spector y sus identidades", "url": "", "image_url": "moonknight.jpg", "id_publisher": "marvel", "publisher_name": "Marvel Comics", "anio_inicio": 1980, "cantidad_numeros": 38},
    {"nombre": "Iron Man", "deck": "Armadura y genio", "descripcion": "Tony Stark desde los 60s", "url": "", "image_url": "ironman.jpg", "id_publisher": "marvel", "publisher_name": "Marvel Comics", "anio_inicio": 1968, "cantidad_numeros": 332},
    {"nombre": "Black Panther", "deck": "El rey de Wakanda", "descripcion": "T'Challa, guerrero y diplomático", "url": "", "image_url": "blackpanther.jpg", "id_publisher": "marvel", "publisher_name": "Marvel Comics", "anio_inicio": 1977, "cantidad_numeros": 15},
    {"nombre": "Wonder Woman", "deck": "La princesa amazona", "descripcion": "Icono femenino de DC", "url": "", "image_url": "wonderwoman.jpg", "id_publisher": "dc", "publisher_name": "DC Comics", "anio_inicio": 1942, "cantidad_numeros": 329},
    {"nombre": "Daredevil", "deck": "El hombre sin miedo", "descripcion": "Justicia desde Hell's Kitchen", "url": "", "image_url": "daredevil.jpg", "id_publisher": "marvel", "publisher_name": "Marvel Comics", "anio_inicio": 1964, "cantidad_numeros": 380},
    {"nombre": "Swamp Thing", "deck": "Horror y naturaleza", "descripcion": "El avatar del verde", "url": "", "image_url": "swampthing.jpg", "id_publisher": "dc", "publisher_name": "DC Comics", "anio_inicio": 1972, "cantidad_numeros": 171}
]

# Insertar
for v in volumenes:
    session.add(Volume(**v))

session.commit()
print("✔ 20 volúmenes de prueba insertados correctamente.")
