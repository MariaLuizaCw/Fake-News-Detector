# modules/llm.py
import os
import requests
from typing import List, Dict


class LLM:
    """Classe base simples para chamadas a LLMs via API."""

    def __init__(self, model: str, api_key_env: str, endpoint: str):
        self.model = model
        self.api_key = os.getenv(api_key_env)
        if not self.api_key:
            raise ValueError(f"⚠️ Variável de ambiente {api_key_env} não definida.")
        self.endpoint = endpoint
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def generate(self, prompt: str, temperature: float = 0.0) -> str:
        """Gera texto a partir de um prompt, ignorando SSL."""

        messages = [
            {"role": "system", "content": "You are an assistant for fake news detection."},
            {"role": "user", "content": prompt}
        ]

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature
        }

        resp = requests.post(self.endpoint, headers=self.headers, json=payload, timeout=60, verify=False)
        resp.raise_for_status()
        result = resp.json()
        return result["choices"][0]["message"]["content"].strip()


class LOCAL_LLM:
    """Classe base simples para chamadas a LLMs localmente."""

    def __init__(self, model: str, endpoint: str = "http://localhost:11434/api/chat"):
        self.model = model        
        self.endpoint = endpoint

    def generate(self, prompt: str, temperature: float = 0.0) -> str:
        """Gera texto a partir de um prompt, ignorando SSL."""

        messages = [
            {"role": "system", "content": "You are a multipurpose assistant."},
            {"role": "user", "content": prompt}
        ]

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "stream": False
        }

        resp = requests.post(self.endpoint, json=payload, timeout=60, verify=False)
        resp.raise_for_status()
        
        result = resp.json()
        return result["message"]["content"].strip()


def build_classification_prompt(title_to_check: str, results_filtered: list) -> str:
    """
    Cria prompt 1-shot para classificar uma notícia como 'fake' ou 'true',
    usando um exemplo de notícia verdadeira e um exemplo de notícia falsa.
    """

    # 1-shot examples
    examples = [
        {
            "title": "NASA announces new water discovery on Mars",
            "results": [
                {"title": "NASA confirms water on Mars", "domain": "nasa.gov", "credible": True},
                {"title": "Scientists find traces of water on Mars", "domain": "science.org", "credible": True}
            ],
            "label": "true"
        },
        {
            "title": "Celebrity endorses miracle cure for cancer",
            "results": [
                {"title": "Miracle cure claims debunked by doctors", "domain": "healthnews.com", "credible": True},
                {"title": "Celebrity claims not verified", "domain": "gossipblog.com", "credible": False}
            ],
            "label": "fake"
        }
    ]

    # Convert results_filtered into simple JSON string
    filtered_json = "\n".join([str(r) for r in results_filtered])

    prompt = f"""
        You are an assistant for fake news detection. Classify the news headline as 'fake' or 'true'.

        Example 1:
        Headline: {examples[0]['title']}
        Results:
        {examples[0]['results']}
        Answer: {examples[0]['label']}

        Example 2:
        Headline: {examples[1]['title']}
        Results:
        {examples[1]['results']}
        Answer: {examples[1]['label']}

        Now classify the following headline:
        Headline: {title_to_check}
        Results:
        {filtered_json}

        Answer only 'fake' or 'true'. No explanations.
    """
    return prompt
