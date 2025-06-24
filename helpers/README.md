# This is the README for the ComicVine project.

## ComicVine Project

The ComicVine project is designed to provide structured access to the ComicVine API, allowing users to interact with various comic-related data. This project includes models, services, and utilities to facilitate the retrieval and processing of comic information.

### Directory Structure

- `helpers/comicvine/`: Contains the main package for interacting with the ComicVine API.
  - `__init__.py`: Initializes the comicvine package.
  - `client.py`: Provides structured access to the ComicVine API.
  - `models/`: Contains data models representing various entities.
    - `__init__.py`: Initializes the models subpackage.
    - `publisher_comicvine.py`: Represents a publisher entity.
    - `volume_comicvine.py`: Represents a comic volume entity.
    - `issue_comicvine.py`: Represents a comic issue entity.
    - `story_arc_comicvine.py`: Represents a story arc entity.
  - `services/`: Contains services for handling business logic.
    - `__init__.py`: Initializes the services subpackage.
  - `utils/`: Contains utility functions and helpers.
    - `__init__.py`: Initializes the utils subpackage.
  - `scraper/`: Contains components for scraping comic data.
    - `issue_spider.py`: Spider implementation for scraping comic issue details.
    - `pipelines.py`: Data processing pipelines for scraped data.
    - `settings.py`: Settings configuration for the Scrapy project.
  - `data/`: Stores intermediate data.
    - `urls_issues.txt`: URLs for comic issues.
  - `outputs/`: Contains final output data.
    - `publishers.json`: Final output data for publishers.
    - `volumes.json`: Final output data for volumes.
    - `issues.json`: Final output data for issues.
    - `scraped_issues.json`: Final output data for scraped issues.
    - `covers/`: Directory for storing cover images.
  - `main.py`: Main coordinator for the system.

### Installation

To install the necessary dependencies, run:

```
pip install -r requirements.txt
```

### Usage

To run the project, execute:

```
python helpers/comicvine/main.py
```

### Contributing

Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

### License

This project is licensed under the MIT License. See the LICENSE file for details.

# ComicVine Connector / Scrapper

Sistema híbrido para integrar datos de cómics desde la API de ComicVine y enriquecerlos vía scraping. Diseñado para integrarse fácilmente con interfaces GTK y sistemas de análisis de datos.

## 🔧 ¿Qué hace?

- ✅ Obtiene publishers, volúmenes, issues y story arcs desde la API.
- ✅ Extrae sinopsis completas, portadas adicionales, staff y tags desde HTML.
- ✅ Ejecuta scraping y consultas API en paralelo.
- ✅ Exporta resultados en JSON o entidades listas para grillas GTK.

## 📁 Estructura

```
comicvine/
├── api/            # Cliente API ComicVine
├── scraper/        # Scrapy para detalles enriquecidos
├── models/         # Modelos con sufijo _comicvine
├── data/           # URLs y temporales
├── outputs/        # Resultados finales
└── main.py         # Coordinador general
```

## ⚙️ Tecnologías

- Python 3.x
- `requests` para la API
- `Scrapy` para scraping paralelo con AutoThrottle
- `dataclasses` para modelos GTK-ready

## 🚀 Uso

1. Consultar la API para obtener listas básicas.
2. Pasar las URLs de issues al scraper.
3. Recibir datos enriquecidos y estructurados.

## 🛠️ En desarrollo

- [ ] `client.py` con paginado paralelo
- [ ] Módulos: publishers, volumes, issues, arcs
- [ ] `issue_spider.py` con extracción completa
- [ ] Integración final en `main.py`

## 📜 Licencia

MIT — sin restricciones para modificar o usar.