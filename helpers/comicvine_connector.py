import requests
from bs4 import BeautifulSoup
from scrapy.crawler import CrawlerProcess
from scrapy import Spider
from scrapy.settings import Settings


class ComicVineConnector:
    def __init__(self, api_key, base_url="https://comicvine.gamespot.com/api/"):
        """
        Initialize the ComicVineConnector with API key and base URL.
        :param api_key: Your ComicVine API key.
        :param base_url: Base URL for the ComicVine API.
        """
        self.api_key = api_key
        self.base_url = base_url

    def fetch_from_api(self, endpoint, params=None):
        """
        Fetch data from the ComicVine API.
        :param endpoint: API endpoint to call.
        :param params: Additional parameters for the API request.
        :return: JSON response from the API.
        """
        if params is None:
            params = {}
        params['api_key'] = self.api_key
        params['format'] = 'json'
        url = f"{self.base_url}{endpoint}"
        headers = {
            "User-Agent": "Babelcomics3/1.0 (https://github.com/pclbusto/Babelcomics3)"
        }
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()

    def search_volumes(self, query, limit=None):
        """
        Search for volumes using the API.
        :param query: Search query for volumes.
        :param limit: Number of results to return. If None, fetch the maximum allowed by the API.
        :return: List of volumes.
        """
        endpoint = "search/"
        params = {
            "query": query,
            "resources": "volume",
            "limit": limit if limit is not None else 100  # Usa 100 como límite máximo permitido por la API
        }
        return self.fetch_from_api(endpoint, params)

    def search_publishers(self, query, limit=10):
        """
        Search for publishers using the API.
        :param query: Search query for publishers.
        :param limit: Number of results to return.
        :return: List of publishers.
        """
        endpoint = "search/"
        params = {
            "query": query,
            "resources": "publisher",
            "limit": limit
        }
        return self.fetch_from_api(endpoint, params)

    def get_comic_details(self, series_id):
        """
        Fetch details of a specific comic series using the API.
        :param series_id: ID of the comic series to fetch details for.
        :return: Dictionary with series details.
        """
        endpoint = f"volume/{series_id}/"
        params = {}
        response = self.fetch_from_api(endpoint, params)
        return response.get("results", {})

    def get_issue_details(self, issue_id):
        """
        Fetch details of a specific comic issue using the API.
        :param issue_id: ID of the comic issue to fetch details for.
        :return: Dictionary with issue details.
        """
        endpoint = f"issue/{issue_id}/"
        params = {}
        response = self.fetch_from_api(endpoint, params)
        return response.get("results", {})

    def scrape_issue_details(self, url):
        """
        Scrape issue details from a specific page using Scrapy.
        :param url: URL of the issue page to scrape.
        :return: Extracted issue details.
        """
        process = CrawlerProcess(settings={
            "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "AUTOTHROTTLE_ENABLED": True,
            "AUTOTHROTTLE_START_DELAY": 1,
            "AUTOTHROTTLE_MAX_DELAY": 10,
            "AUTOTHROTTLE_TARGET_CONCURRENCY": 1.0,
            "LOG_LEVEL": "ERROR",
            "DOWNLOAD_DELAY": 2.0  # Agregar un retraso entre solicitudes
        })

        class IssueSpider(Spider):
            name = "issue_spider"
            start_urls = [url]

            def parse(self, response):
                # Imprimir el contenido HTML de la página para verificar que se descargó correctamente
                print("Contenido HTML descargado:")
                print(response.text[:1000])  # Muestra los primeros 1000 caracteres del HTML

                # Ajusta los selectores CSS según la estructura actual del sitio
                title = response.css("h1.title::text").get()
                description = response.css("div.description::text").get()
                yield {
                    "title": title.strip() if title else None,
                    "description": description.strip() if description else None
                }

        results = []

        def collect_results(item, response, spider):
            results.append(item)

        # Conectar la señal para recolectar resultados
        from scrapy import signals
        from pydispatch import dispatcher
        dispatcher.connect(collect_results, signal=signals.item_scraped)

        process.crawl(IssueSpider)
        process.start()
        return results[0] if results else {}


def main():
    connector = ComicVineConnector(api_key="tu_api_key")

    # Usar web scraping
    try:
        url = "https://comicvine.gamespot.com/green-lantern-1-the-planet-of-doomed-men-menace-of/4000-4869/"
        issue_details_scraping = connector.scrape_issue_details(url)
        print("Detalles obtenidos desde web scraping:")
        print(issue_details_scraping)
    except Exception as e:
        print(f"Error al realizar web scraping: {e}")


if __name__ == "__main__":
    main()