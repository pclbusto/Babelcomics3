import requests
import os
import math
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

class ComicVineAPI:
    # ... (el resto de la clase: __init__, _make_request, etc., se mantiene igual)
    BASE_URL = "https://comicvine.gamespot.com/api"

    def __init__(self, api_key):
        if not api_key:
            raise ValueError("La API key no puede estar vacía.")
        self.api_key = api_key
        self.default_params = {"api_key": self.api_key, "format": "json"}

    def _make_request(self, endpoint, params=None):
        # (Este método no cambia)
        url = self.BASE_URL + endpoint
        request_params = self.default_params.copy()
        if params:
            request_params.update(params)
        try:
            response = requests.get(url, params=request_params, headers={'User-Agent': 'MiAppDeComicsPython'})
            response.raise_for_status()
            json_response = response.json()
            if json_response.get("error") != "OK":
                print(f"Error en la respuesta de la API: {json_response.get('error')}")
                return None
            return json_response
        except requests.exceptions.RequestException as e:
            # En un entorno con hilos, es mejor no imprimir tanto para no saturar la consola
            return None # Devolvemos None para que el llamador maneje el error
        except ValueError:
            return None

    # --- NUEVO MÉTODO CON HILOS EN PARALELO ---
    def search_all_volumes_parallel(self, name, max_workers=4):
        """
        Busca todos los volúmenes en paralelo usando un pool de hilos.
        
        Args:
            name (str): El nombre del volumen a buscar.
            max_workers (int): El número máximo de hilos a usar en paralelo.
        """
        print(f"\n--- Buscando TODOS los volúmenes para: '{name}' (en PARALELO) ---")
        start_time = time.time()

        # 1. Petición Inicial para descubrir el total de resultados
        print("Realizando petición inicial para determinar el trabajo total...")
        initial_params = {"query": name, "resources": "volume", "limit": 1}
        initial_data = self._make_request("/search", initial_params)
        
        if not initial_data or initial_data.get("number_of_total_results", 0) == 0:
            print("No se encontraron resultados para esta búsqueda.")
            return []

        total_results = int(initial_data["number_of_total_results"])
        limit_per_page = 100
        total_pages = math.ceil(total_results / limit_per_page)
        print(f"Se encontraron {total_results} resultados en total. Se necesitarán {total_pages} peticiones.")

        # 2. Calcular todos los offsets necesarios
        offsets = [i * limit_per_page for i in range(total_pages)]
        
        all_results = []
        
        # 3. Usar ThreadPoolExecutor para paralelizar
        # El 'with' se asegura de que todos los hilos terminen antes de salir
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Creamos un futuro para cada petición de página
            # Un 'futuro' es un objeto que representa un trabajo que se está haciendo en otro hilo
            future_to_offset = {executor.submit(self._fetch_page, name, offset, limit_per_page): offset for offset in offsets}
            
            print(f"Lanzando {len(offsets)} peticiones en paralelo con hasta {max_workers} hilos...")
            
            # 4. Recolectar resultados a medida que se completan
            for future in as_completed(future_to_offset):
                offset = future_to_offset[future]
                try:
                    page_data = future.result()
                    if page_data:
                        all_results.extend(page_data)
                        # print(f"  Página con offset {offset} completada.") # Descomentar para ver progreso
                except Exception as exc:
                    print(f'Página con offset {offset} generó una excepción: {exc}')

        end_time = time.time()
        print("\n--- Búsqueda en paralelo completada ---")
        print(f"Se obtuvieron {len(all_results)} de {total_results} resultados.")
        print(f"Tiempo total: {end_time - start_time:.2f} segundos.")
        
        return all_results

    def _fetch_page(self, name, offset, limit):
        """Función auxiliar que cada hilo ejecutará para obtener una página."""
        params = {
            "query": name,
            "resources": "volume",
            "limit": limit,
            "offset": offset,
            "field_list": "id,name,start_year,publisher"
        }
        data = self._make_request("/search", params=params)
        return data.get("results") if data else []


def main():
    api_key = os.getenv("COMICVINE_API_KEY")
    if not api_key:
        api_key = input("Por favor, ingresa tu API Key de Comic Vine: ").strip()

    try:
        api = ComicVineAPI(api_key)
        # Una búsqueda como "Batman" o "Spider-Man" es ideal para probar esto
        resultados_paralelos = api.search_all_volumes_parallel("Batman")
        
        # Opcional: Imprimir algunos de los resultados obtenidos
        print("\nMostrando los primeros 15 resultados encontrados:")
        for volume in resultados_paralelos:
             publisher_name = volume.get('publisher', {}).get('name', 'N/A')
             print(f"  ID: {volume['id']} | {volume['name']} ({volume.get('start_year', 'N/A')}) | Editorial: {publisher_name}")

    except ValueError as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()