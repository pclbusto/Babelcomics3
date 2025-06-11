import requests
from bs4 import BeautifulSoup

class ComicVineConnector:
    def __init__(self, api_key, base_url="https://comicvine.gamespot.com/api/"):
        """
        Initialize the ComicVineConnector with API key and base URL.
        :param api_key: Your ComicVine API key.
        :param base_url: Base URL for the ComicVine API.
        """
        self.api_key = "7e4368b71c5a66d710a62e996a660024f6a868d4 "
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
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()

    def scrape_website(self, url):
        """
        Perform web scraping on the ComicVine website.
        :param url: URL to scrape.
        :return: Parsed HTML content.
        """
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup

    def get_comic_details(self, comic_id):
        """
        Get comic details using the API.
        :param comic_id: ID of the comic to fetch details for.
        :return: Comic details as a dictionary.
        """
        endpoint = f"issue/{comic_id}/"
        return self.fetch_from_api(endpoint)

    def scrape_comic_page(self, url):
        """
        Scrape comic details from a specific page.
        :param url: URL of the comic page to scrape.
        :return: Extracted comic details.
        """
        soup = self.scrape_website(url)
        # Example: Extract title and description (adjust selectors as needed)
        title = soup.find('h1', class_='title').text.strip() if soup.find('h1', class_='title') else None
        description = soup.find('div', class_='description').text.strip() if soup.find('div', class_='description') else None
        return {
            'title': title,
            'description': description
        }
    

def main():
    # Configuración inicial
    api_key = "7e4368b71c5a66d710a62e996a660024f6a868d4"  # Reemplaza con tu API key válida
    connector = ComicVineConnector(api_key)

    # ID de la serie a consultar (reemplaza con un ID válido)
    series_id = "4000-1234"  # Ejemplo de ID de una serie en ComicVine

    try:
        # Consulta a la API para obtener detalles de la serie
        print(f"Consultando detalles de la serie con ID: {series_id}")
        series_details = connector.get_comic_details(series_id)

        # Mostrar los detalles obtenidos
        print("Detalles de la serie:")
        for key, value in series_details.items():
            print(f"{key}: {value}")

    except Exception as e:
        print(f"Error al consultar la serie: {e}")

if __name__ == "__main__":
    main()