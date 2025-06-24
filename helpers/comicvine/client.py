# filepath: /home/pedro/PycharmProjects/Babelcomics3/helpers/comicvine/client.py

class ComicVineClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://comicvine.gamespot.com/api/"
    
    def get_data(self, endpoint, params=None):
        import requests
        
        if params is None:
            params = {}
        params['api_key'] = self.api_key
        params['format'] = 'json'
        
        response = requests.get(self.base_url + endpoint, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_issue(self, issue_id):
        endpoint = "issue/{}".format(issue_id)
        return self.get_data(endpoint)
    
    def get_volume(self, volume_id):
        endpoint = "volume/{}".format(volume_id)
        return self.get_data(endpoint)
    
    def get_publisher(self, publisher_id):
        endpoint = "publisher/{}".format(publisher_id)
        return self.get_data(endpoint)
    
    def search(self, query):
        endpoint = "search"
        params = {'query': query}
        return self.get_data(endpoint, params)