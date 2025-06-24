# ComicVine Scrapper / Connector

## ✨ Objetivo
Desarrollar un sistema híbrido que combine:
- ✉️ **API de ComicVine**: para obtener información estructurada como publishers, series (volúmenes), issues y story arcs.
- 🔍 **Web Scraping** (via Scrapy): para enriquecer los datos con información adicional no expuesta por la API, como sinopsis extendidas, portadas múltiples, staff detallado y etiquetas.

Este sistema se llama **ComicVine Connector/Scrapper** y está diseñado para ser modular, escalable y apto para integrarse con interfaces GTK y otros consumidores de datos.

---

## 🔄 Arquitectura General

```
comicvine/
├── api/                  # Acceso estructurado a la API de ComicVine
│   ├── client.py
│   ├── publishers.py
│   ├── volumes.py
│   ├── issues.py
│   └── arcs.py
│
├── scraper/              # Scrapy: scrapear detalles de cada issue
│   ├── issue_spider.py
│   ├── pipelines.py
│   └── settings.py
│
├── models/               # Entidades estructuradas para GTK u otras UIs
│   ├── publisher_comicvine.py
│   ├── volume_comicvine.py
│   ├── issue_comicvine.py
│   └── story_arc_comicvine.py
│
├── data/                 # Datos intermedios: URLs, resultados parciales
│   └── urls_issues.txt
│
├── outputs/              # Resultados finales (JSON, CSV, imagenes)
│   ├── publishers.json
│   ├── volumes.json
│   ├── issues.json
│   ├── scraped_issues.json
│   └── covers/
│
├── main.py               # Coordinador principal del sistema
└── README.md
```

---

## 🚀 Flujo de Trabajo

### Paso 1: API (ComicVine)
Obtener información estructurada a través de la API REST:
- Lista de publishers y detalles individuales
- Lista de volúmenes (series) y sus detalles
- Issues por volumen
- Story Arcs (arcos argumentales) y detalles

> ⚠️ Cada request puede estar paginado. Se debe hacer una primera request para conocer el total, luego lanzar en paralelo el resto de las páginas usando threads.

### Paso 2: Web Scraping
Dado un listado de issues (`site_detail_url`):
- Scrapy extrae sinopsis extendida, múltiples portadas, staff, tags, y otros detalles específicos del HTML.
- Se controla la concurrencia de requests con AutoThrottle o cantidad fija de threads.

### Paso 3: Modelado / Integración
- Todos los resultados de API y Scrapy se transforman en **entidades estructuradas** (`dataclass`, `dict`) con sufijo `_comicvine`, pensadas para ser utilizadas en interfaces GTK (grillas, formularios, listas).

---

## ⚙️ Detalles técnicos implementados / por implementar

### API Client (modularizado por recurso)
- ✅ Manejo de requests con headers y autenticación por API Key.
- ✅ Soporte de paginado con detección automática de cantidad de páginas.
- ✅ Lanzamiento en paralelo de requests restantes (después de la primera), respetando límite de ComicVine (200/hora).
- ✅ Devuelve entidades listas para interfaz GTK, con sufijo `_comicvine`.

### Scraper (detalles de issues)
- ✅ Usa Scrapy con AutoThrottle para no ser bloqueado.
- ✅ Extrae: título completo, sinopsis (primer párrafo), tags, portada principal y adicionales.
- ✅ Guarda resultados en `scraped_issues.json`.
- ✅ Opcional: descarga de portadas en carpeta local.
- ✅ Soporta procesamiento en paralelo de múltiples issues, configurable.

### Modelos
- ✅ `PublisherComicvine`, `VolumeComicvine`, `IssueComicvine`, `StoryArcComicvine` como `@dataclass`
- ✅ Fácil de serializar a JSON o usar en grillas GTK.

### Concurrencia
- ✅ API: paginado paralelo con `ThreadPoolExecutor`.
- ✅ Scraper: control de concurrencia por configuración de Scrapy o manejo manual.

---

## 📆 Justificación de la arquitectura

| Decisión                          | Justificación                                                                 |
|-----------------------------------|-------------------------------------------------------------------------------|
| Usar API para estructura general  | Provee datos fiables, estructurados y sin necesidad de parsear HTML          |
| Usar Scraping para detalles       | La API de ComicVine está limitada y no incluye sinopsis completa ni múltiples portadas |
| Scrapy con AutoThrottle           | Evita bloqueos por demasiadas requests al servidor ComicVine                 |
| Multithread para paginado         | Mejora velocidad de carga manteniendo control sobre la cuota horaria         |
| Modelos estructurados con sufijo  | Permite distinguir modelos específicos de ComicVine de otros en el sistema   |

---

## 🚀 Próximos pasos sugeridos

- [ ] Implementar `client.py` base con soporte de paginado paralelo
- [ ] Crear `publishers.py` para listar y obtener detalle
- [ ] Definir entidades `PublisherComicvine`, `VolumeComicvine`, `IssueComicvine`, `StoryArcComicvine`
- [ ] Terminar `issue_spider.py` para scrapear detalles completos
- [ ] Integrar flujo API + Scraper en `main.py`

---

Este documento debe mantenerse vivo e irse actualizando con cada avance y decisión implementada en el desarrollo de ComicVine Connector/Scrapper.
