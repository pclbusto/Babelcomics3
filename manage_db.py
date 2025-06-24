import argparse
import sys
import os

# Agregamos la ruta del proyecto al path para que Python encuentre el paquete 'entidades'
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine

# --- ¡Importante! Cambios Clave Aquí ---

# 1. Importamos la 'Base' compartida desde el paquete 'entidades'.
#    Todos los modelos se registran en esta Base.
from entidades import Base

# 2. Importamos cada clase de modelo explícitamente.
#    Esto es necesario para que SQLAlchemy sepa que existen y las asocie con la Base.
from entidades.comicbook_model import Comicbook
from entidades.publisher_model import Publisher
from entidades.setup_model import Setup
from entidades.volume_model import Volume
# Si tienes más modelos, añádelos aquí.


# --- Configuración de la Base de Datos ---
DATABASE_URL = 'sqlite:///data/babelcomics.db' # Apunta al archivo de tu base de datos
engine = create_engine(DATABASE_URL)


def create_table(table_name):
    """
    Crea una tabla específica en la base de datos.
    """
    try:
        # Busca la tabla por su nombre en los metadatos de SQLAlchemy
        table_object = Base.metadata.tables[table_name]
        print(f"Creando tabla '{table_name}'...")
        # Usa el método .create() del objeto de la tabla
        table_object.create(bind=engine, checkfirst=True)
        print(f"¡Tabla '{table_name}' creada con éxito (o ya existía)!")
    except KeyError:
        print(f"Error: La tabla '{table_name}' no se encontró. Asegúrate de que el modelo esté importado en manage_db.py.")
        print("Tablas disponibles:", ", ".join(Base.metadata.tables.keys()))
    except Exception as e:
        print(f"Ocurrió un error al crear la tabla '{table_name}': {e}")


def create_all_tables():
    """
    Crea todas las tablas definidas que heredan de Base.
    """
    print("Creando todas las tablas...")
    try:
        # Esto es equivalente a tu inicialización original
        Base.metadata.create_all(engine, checkfirst=True)
        print("¡Todas las tablas fueron creadas con éxito (o ya existían)!")
    except Exception as e:
        print(f"Ocurrió un error al crear todas las tablas: {e}")


def main():
    """
    Función principal para manejar los argumentos de la línea de comandos.
    """
    parser = argparse.ArgumentParser(description="Script para gestionar las tablas de la base de datos de BabelComics.")
    parser.add_argument('command', choices=['create'], help="El comando a ejecutar.")
    parser.add_argument('--table', help="El nombre de la tabla específica a crear (ej: comicbooks).")
    parser.add_argument('--all', action='store_true', help="Aplica el comando a todas las tablas.")

    args = parser.parse_args()

    if args.command == 'create':
        if args.all:
            create_all_tables()
        elif args.table:
            create_table(args.table)
        else:
            print("Error: Debes especificar --table <nombre_tabla> o --all.")
            parser.print_help()


if __name__ == "__main__":
    main()
