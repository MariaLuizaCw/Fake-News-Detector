import http.client
import json
import os
from dotenv import load_dotenv
import requests
from urllib.parse import urlparse
from ddgs import DDGS

# 🔹 Classe base (interface)
class SearchEngine:
    """Interface para mecanismos de busca."""
    
    def search(self, query: str, num_results: int = 5):
        raise NotImplementedError("Subclasses devem implementar este método.")


# 🔹 Implementação concreta para o Google via Serper.dev
class GoogleSearchEngine(SearchEngine):
    """Busca no Google via Serper.dev API."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        if not self.api_key:
            raise ValueError("⚠️ Coloque sua GOOGLE_API_KEY no .env")

    def search(self, query: str, num_results: int = 5):
        conn = http.client.HTTPSConnection("google.serper.dev")

        payload = json.dumps({
            "q": query,
            "num": num_results
        })

        headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }

        conn.request("POST", "/search", payload, headers)
        res = conn.getresponse()
        data = res.read()
        conn.close()

        data_json = json.loads(data.decode("utf-8"))

        # Processa os resultados
        results = []
        for item in data_json.get("organic", [])[:num_results]:
            title = item.get("title")
            snippet = item.get("snippet", "")
            link = item.get("link")
            domain = urlparse(link).netloc.replace("www.", "") if link else ""
            results.append({
                "title": title,
                "snippet": snippet,
                "link": link,
                "domain": domain
            })

        return results
    


class DuckDuckGoSearchEngine(SearchEngine):
    """DuckDuckGo search returning results in Google-like format."""
    
    def __init__(self):
        self.ddgs = DDGS()

    def search(self, query: str, num_results: int = 5):
        results = []
        for r in self.ddgs.text(query, max_results=num_results):
            link = r.get("href") or r.get("url")
            title = r.get("title") or ""
            snippet = r.get("body") or title
            domain = urlparse(link).netloc.replace("www.", "") if link else ""
            results.append({
                "title": title,
                "snippet": snippet,
                "link": link,
                "domain": domain
            })
        return results