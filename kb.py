"""
VARS Knowledge Base (KB) operations.
"""

from typing import List

import requests


class VARSKBClient:
    """
    VARS KB API client.
    """

    def __init__(self, url):
        self._url = url
        self._session = requests.Session()

    @property
    def url(self):
        return self._url

    @property
    def session(self):
        return self._session

    def url_to(self, resource: str) -> str:
        return self.url.rstrip("/") + "/" + resource.lstrip("/")

    def get(self, resource: str, **kwargs) -> requests.Response:
        return self.session.get(self.url_to(resource), **kwargs)

    def get_taxa(self, name: str) -> List[dict]:
        """
        Get a list of taxa for a given name.
        """
        response = self.get(f"phylogeny/taxa/{name}")
        response.raise_for_status()
        return response.json()
