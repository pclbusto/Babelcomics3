import requests
import time
import math
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

class ComicVineClient:
    BASE_URL = "https://comicvine.gamespot.com/api"
    FORMAT = "json"

    def __init__(self, api_key: str, throttle_delay=1.0, max_threads=1):
        self.api_key = api_key
        self.headers = {
            "User-Agent": "ComicVineConnector/1.0",
            "Accept": "application/json"
        }
        self.throttle_delay = throttle_delay
        self.last_request_time = 0
        self.max_threads = max_threads

    def _throttle(self):
        elapsed = time.time() - self.last_request_time
        if elapsed < self.throttle_delay:
            time.sleep(self.throttle_delay - elapsed)
        self.last_request_time = time.time()

    def _request(self, endpoint: str, params: dict = None, retries=5, backoff_factor=2):
        self._throttle()
        url = f"{self.BASE_URL}/{endpoint}"
        payload = {
            "api_key": self.api_key,
            "format": self.FORMAT
        }
        if params:
            payload.update(params)

        for attempt in range(retries):
            try:
                print(f"Request URL: {url}")
                print(f"Request Params: {payload}")
                response = requests.get(url, headers=self.headers, params=payload, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status_code") == 1:
                        return data
                    else:
                        raise Exception(f"ComicVine error: {data.get('error')}")
                else:
                    raise Exception(f"Error {response.status_code}: {response.text}")
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                if attempt < retries - 1:
                    time.sleep(backoff_factor ** attempt)  # Exponential backoff
                else:
                    raise

    def get_all_paginated(self, endpoint: str, params: dict = None, limit=100):
        """Devuelve una lista con todos los resultados de un endpoint paginado"""
        results = []
        initial = self._request(endpoint, {**(params or {}), "limit": limit, "offset": 0})
        total = initial["number_of_total_results"]
        results.extend(initial["results"])

        # Calcular cuántas páginas faltan
        pages = math.ceil(total / limit)
        if pages <= 1:
            return results

        # Lanzar requests en paralelo para el resto de las páginas
        def fetch_page(page_index):
            offset = page_index * limit
            try:
                res = self._request(endpoint, {**(params or {}), "limit": limit, "offset": offset})
                return res["results"]
            except Exception as e:
                print(f"Error al obtener la página {page_index}: {e}")
                return []  # Devuelve una lista vacía si falla

        with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            futures = [executor.submit(fetch_page, i) for i in range(1, pages)]
            for future in tqdm(futures, desc="Fetching pages"):
                results.extend(future.result())

        return results

if __name__ == "__main__":
    # Reemplaza "tu_api_key" con tu clave de API válida
    api_key = "7e4368b71c5a66d710a62e996a660024f6a868d4"
    client = ComicVineClient(api_key)

    try:
        # Prueba un endpoint, por ejemplo, buscar volúmenes
        print("Obteniendo volúmenes relacionados con 'Spider-Man'...")
        volumes = client.get_all_paginated("search", params={"query": "green lantern corps", "resources": "volume"}, limit=100)
        
        # Imprime los resultados
        for volume in volumes:
            print(f"ID: {volume['id']}, Nombre: {volume['name']}")
    except Exception as e:
        print(f"Error al realizar la solicitud: {e}")
