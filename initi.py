import os

def crear_estructura_babelcomics(base_path):
    dirs = [
        "entidades",
        "interfaces",
        "helpers",
        "images",
        "repositories",
        "data",
        "data/thumbnails",
        "data/thumbnails/Editoriales",
        "data/thumbnails/Volumenes",
        "data/thumbnails/Comics",
        "resources"
    ]

    for d in dirs:
        print("hola")
        path = os.path.join(base_path, d)
        if not os.path.exists(path):
            os.makedirs(path)
            print(f"Directorio creado: {path}")
        else:
            print(f"Directorio ya existe: {path}")

if __name__ == "__main__":
    base = "."  # Cambiar según necesidad
    crear_estructura_babelcomics(base)
