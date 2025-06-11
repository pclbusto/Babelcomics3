import csv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from entidades.volume_model import Volume  # Asegurate que el path sea correcto
from entidades.publisher_model import Publisher  # Asegúrate de que el path sea correcto


def importar_volumenes_desde_csv(db_url='sqlite:////home/pedro/PycharmProjects/Babelcomics3/data/babelcomics.db', csv_path='volumenes.csv'):
    print(db_url)
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            volume = Volume(
                id_volume=int(row.get('id_volume') or row.get('id') or 0),
                nombre=row.get('nombre') or '',
                deck=row.get('deck') or '',
                descripcion=row.get('descripcion') or '',
                url=row.get('url') or '',
                image_url=row.get('image_url') or '',
                id_publisher=row.get('id_publisher') or '',
                publisher_name=row.get('publisher_name') or '',
                anio_inicio=int(row.get('anio_inicio') or 0),
                cantidad_numeros=int(row.get('cantidad_numeros') or 0)
            )
            session.merge(volume)
    session.commit()
    print("Importación completa de volumens.")

def importar_publishers_desde_csv(db_url='sqlite:////home/pedro/PycharmProjects/Babelcomics3/data/babelcomics.db', csv_path='publishers.csv'):
    print(db_url)
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            publisher = Publisher(
                id_publisher=row.get('id_publisher') or '',
                nombre=row.get('nombre') or '',
                deck=row.get('deck') or '',  # Nuevo campo
                descripcion=row.get('descripcion') or '',
                url_logo=row.get('url_logo') or '',  # Campo renombrado
                sitio_web=row.get('sitio_web') or ''
            )
            session.merge(publisher)  # Actualiza si existe, inserta si no
    session.commit()
    print("Importación completa de publishers.")


if __name__ == '__main__':
    print("¿Qué desea importar?")
    print("1. Volumenes")
    print("2. Publishers")  # Nueva opción para importar publishers
    opcion = input("Elija una opción (número): ")

    if opcion == '1':
        importar_volumenes_desde_csv(csv_path='volumenes.csv')
    elif opcion == '2':
        importar_publishers_desde_csv(csv_path='publishers.csv')  # Llama a la nueva función
    else:
        print("Opción no implementada.")
