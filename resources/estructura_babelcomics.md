
# 📚 Estructura de Datos de Babelcomics

Este documento describe las tablas principales del sistema **Babelcomics**.

## 🗂️ Diagrama de relaciones

Se puede visualizar con Mermaid:


```mermaid
erDiagram
    SETUPS ||--o{ COMICBOOK : tiene_configuracion
    COMICBOOK ||--|| COMICBOOK_INFO : usa_info
    COMICBOOK_INFO ||--o{ COMICBOOK_INFO_COVER_URL : tiene_portadas
    COMICBOOK_INFO ||--o{ ARCOS_ARGUMENTALES_COMICS_REFERENCE : en_arco
    ARCOS_ARGUMENTALES ||--o{ ARCOS_ARGUMENTALES_COMICS_REFERENCE : tiene_comics
    VOLUMENS ||--o{ COMICS_IN_VOLUME : contiene
    COMICBOOK_INFO ||--o{ COMICS_IN_VOLUME : esta_en
    COMICBOOK ||--o{ COMICBOOK_DETAIL : tiene_paginas
    COMICBOOK_INFO ||--o{ PUBLISHERS : pertenece_a
    VOLUMENS ||--o{ PUBLISHERS : publicado_por

    SETUPS {
        Integer setupkey PK
        String directorioBase
        Integer cantidadComicsPorPagina
    }

    COMICBOOK {
        Integer id_comicbook PK
        String path
        String id_comicbook_info FK
    }

    COMICBOOK_INFO {
        Integer id_comicbook_info PK
        String titulo
        String numero
        String id_volume
    }

    COMICBOOK_INFO_COVER_URL {
        Integer id_comicbook_info PK
        String thumb_url PK
    }

    ARCOS_ARGUMENTALES {
        Integer id_arco_argumental PK
        String nombre
    }

    ARCOS_ARGUMENTALES_COMICS_REFERENCE {
        Integer id_arco_argumental PK
        Integer id_comicbook_info PK
    }

    COMICS_IN_VOLUME {
        Integer id_volume PK
        String numero PK
        String id_comicbook_info
    }

    COMICBOOK_DETAIL {
        Integer comicbook_id PK
        Integer indicePagina PK
    }

    PUBLISHERS {
        Integer id_publisher PK
        String name
    }

    VOLUMENS {
        Integer id_volume PK
        String nombre
        Integer id_publisher
    }
```


---

## 📋 Descripción de Tablas

### `setups`
Contiene configuración global del sistema: carpeta base, cantidad por página, regex de numerado, etc.

### `comicbooks`
Archivos de cómics físicos (cbz/cbr), su path, calidad, y si está en papelera.

### `comicbooks_info`
Metadata del cómic: título, número, volumen, fecha, resumen.

### `comicbooks_info_cover_url`
URLs de portadas adicionales asociadas a un cómic.

### `arcos_argumentales`
Define arcos narrativos (sagas).

### `arcos_argumentales_comics_reference`
Relaciona cómics con arcos narrativos en orden secuencial.

### `comicbooks_detail`
Información por página de archivo: tipo, orden, nombre.

### `comics_in_volume`
Asociación entre cómics y volumen en ComicVine.

### `publishers`
Editoriales de los cómics, con descripción y logos.

### `volumens`
Volúmenes de series: año de inicio, cantidad de números, editorial asociada.

### `setup_directorios`
Directorios definidos para escaneo de archivos.

### `setup_tipos_archivo`
Extensiones válidas para archivos de cómics.

### `setup_vineKeys`
Claves API de ComicVine.

### `setup_vineKeys_status`
Tracking de uso de claves API.

---
