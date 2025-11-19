# modules/llm.py
import os
import requests
from typing import List, Dict
import re


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


## Pessoal essa classe faz a mesma coisa q a de cima, depois vejam se precisa ficar!!
class LOCAL_LLM:
    """Classe base simples para chamadas a LLMs localmente."""

    def __init__(self, model: str, endpoint: str = "http://localhost:11434/api/chat/"):
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
        result = result["message"]["content"].strip()
        result = re.sub(r"""['"“”‘’‹›«»‛‟❛❜❝❞⹂]""", "", result)
        print (result)
        return result

