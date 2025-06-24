import csv
"""
This script provides functionality to import data from CSV files into a SQLite database using SQLAlchemy ORM models.

Modules:
- csv: Used for reading CSV files.
- sqlalchemy: Used for database connection and ORM functionality.
- entidades.volume_model: Contains the Volume model definition.
- entidades.publisher_model: Contains the Publisher model definition.
- entidades.comicbook_model: Contains the Comicbook model definition.

Functions:
- importar_volumenes_desde_csv(db_url, csv_path):
    Imports volume data from a CSV file into the database.
    Parameters:
        db_url (str): The database connection URL. Defaults to a local SQLite database.
        csv_path (str): The path to the CSV file containing volume data. Defaults to 'volumenes.csv'.
    Notes:
        The CSV file should be created directly using DB Browser.

- importar_publishers_desde_csv(db_url, csv_path):
    Imports publisher data from a CSV file into the database.
    Parameters:
        db_url (str): The database connection URL. Defaults to a local SQLite database.
        csv_path (str): The path to the CSV file containing publisher data. Defaults to 'publishers.csv'.
    Notes:
        The CSV file should be created directly using DB Browser.

Usage:
- Run the script and choose an option to import either volumes or publishers.
- Ensure the CSV files are properly formatted and located at the specified paths.

Example:
1. To import volumes, select option 1 and ensure 'volumenes.csv' exists.
2. To import publishers, select option 2 and ensure 'publishers.csv' exists.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from entidades.volume_model import Volume  # Asegurate que el path sea correcto
from entidades.publisher_model import Publisher  # Asegúrate de que el path sea correcto
from entidades.comicbook_model import Comicbook  # Asegúrate de que el path sea correcto



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

def importar_comicbooks_desde_csv(db_url='sqlite:////home/pedro/PycharmProjects/Babelcomics3/data/babelcomics.db', csv_path='comicbooks.csv'):
    """
    Importa datos de comicbooks desde un archivo CSV a la base de datos.
    
    Args:
        db_url (str): URL de la base de datos.
        csv_path (str): Ruta del archivo CSV.
    """
    print(f"Conectando a la base de datos: {db_url}")
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Validar y asignar valores del CSV al modelo
                comicbook = Comicbook(
                    id_comicbook=int(row.get('id_comicbook') or 0),
                    path=row.get('path') or '',
                    id_comicbook_info=row.get('id_comicbook_info') or '',
                    calidad=int(row.get('calidad') or 0),
                    en_papelera=row.get('en_papelera') == 'True'  # Convertir a booleano
                )
                # Actualiza si existe, inserta si no
                session.merge(comicbook)
        session.commit()
        print("Importación completa de comicbooks.")
    except FileNotFoundError:
        print(f"Error: El archivo {csv_path} no existe.")
    except Exception as e:
        print(f"Error durante la importación: {e}")
    finally:
        session.close()


if __name__ == '__main__':
    print("¿Qué desea importar?")
    print("1. Volumenes")
    print("2. Publishers")
    print("3. Comicbooks")
    opcion = input("Elija una opción (número): ")

    if opcion == '1':
        importar_volumenes_desde_csv(csv_path='volumenes.csv')
    elif opcion == '2':
        importar_publishers_desde_csv(csv_path='publishers.csv')
    elif opcion == '3':
        importar_comicbooks_desde_csv(csv_path='comicbooks.csv')
    else:
        print("Opción no implementada.")
