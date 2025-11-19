from newspaper import Article
import numpy as np
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


class TitleRefiner:
    def __init__(self, embedder, similarity_threshold: float = 0.85, min_full_len: int = 10):
        """
        embedder: instância do seu HuggingFaceEmbedder (com método .encode)
        similarity_threshold: limiar mínimo de similaridade para aceitar o novo título
        min_full_len: tamanho mínimo do título retornado pelo newspaper
                      (evita casos tipo "MSN" ser aceito)
        """
        self.embedder = embedder
        self.similarity_threshold = similarity_threshold
        self.min_full_len = min_full_len

    def _to_1d(self, v):
        """
        Converte a saída do embedder em um vetor 1D (np.array).
        Funciona com formatos como [[tensor(...), tensor(...), ...]]
        ou já np.array.
        """
        arr = np.array(v, dtype=float)

        # [[x, x, x]] -> (1, D) -> (D,)
        if arr.ndim > 1:
            arr = arr.reshape(-1)

        return arr

    def _cosine_similarity(self, v1, v2) -> float:
        v1 = self._to_1d(v1)
        v2 = self._to_1d(v2)
        denom = (np.linalg.norm(v1) * np.linalg.norm(v2))
        if denom == 0:
            return 0.0
        return float(np.dot(v1, v2) / denom)

    def _fetch_full_title(self, url: str) -> str | None:
        try:
            article = Article(url)
            article.download()
            article.parse()
            full_title = (article.title or "").strip()

            # evita retornar lixo muito curto (ex: "MSN")
            if not full_title or len(full_title) < self.min_full_len:
                return None

            return full_title
        except Exception as e:
            # log simples, se quiser
            return None

    def refine(self, original_title: str, url: str) -> str:
        """
        Se o título tiver "..." tenta completar com newspaper + similaridade.
        Caso contrário, retorna o título original.
        """
        # se não parece truncado, não faz nada
        if "..." not in original_title:
            return original_title

        if not url:
            # sem URL não tem como usar newspaper
            return original_title

        full_title = self._fetch_full_title(url)
        if not full_title:
            return original_title

        # calcula embeddings usando .encode (não existe .embed)
        try:
            emb_original = self.embedder.encode(original_title)
            emb_full = self.embedder.encode(full_title)
        except Exception as e:
            # se der qualquer problema no embedder, não quebra o fluxo
            return original_title

        similarity = self._cosine_similarity(emb_original, emb_full)

        if similarity >= self.similarity_threshold:
            return full_title
        else:
            return original_title
        


class GoogleSearchEngine(SearchEngine):
    """Busca no Google via Serper.dev API, com suporte opcional a TitleRefiner."""

    def __init__(self, api_key: str = None, title_refiner: TitleRefiner | None = None):
        self.api_key = api_key
        if not self.api_key:
            raise ValueError("⚠️ Coloque sua GOOGLE_API_KEY no .env")

        self.title_refiner = title_refiner

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

        results = []
        for item in data_json.get("organic", [])[:num_results]:
            title = item.get("title") or ""
            snippet = item.get("snippet", "")
            link = item.get("link")

            # ✔️ aplica refinamento apenas quando possível
            if self.title_refiner and link:
                refined_title = self.title_refiner.refine(title, link)
            else:
                refined_title = title

            domain = urlparse(link).netloc.replace("www.", "") if link else ""

            results.append({
                "title": title,
                "refined_title": refined_title,
                "snippet": snippet,
                "link": link,
                "domain": domain
            })

        return results


class DuckDuckGoSearchEngine(SearchEngine):
    """DuckDuckGo search returning results in Google-like format."""
    
    def __init__(self, title_refiner: TitleRefiner | None = None):
        self.ddgs = DDGS()
        self.title_refiner = title_refiner  # pode ser None se não quiser usar

    def search(self, query: str, num_results: int = 5):
        results = []
        for r in self.ddgs.text(query, max_results=num_results):
            link = r.get("href") or r.get("url")
            title = r.get("title") or ""

            if self.title_refiner and link:
                refined_title = self.title_refiner.refine(title, link)
            else:
                refined_title = title

            snippet = r.get("body") or title
            domain = urlparse(link).netloc.replace("www.", "") if link else ""
            results.append({
                "title": title,
                "refined_title": refined_title,
                "snippet": snippet,
                "link": link,
                "domain": domain
            })
        return results
    


