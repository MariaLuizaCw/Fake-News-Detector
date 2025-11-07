# 🔹 Classe base para embedders
from typing import List, Dict
import torch
from transformers import AutoTokenizer, AutoModel
from sklearn.metrics.pairwise import cosine_similarity
from urllib.parse import urlparse



class Embedder:
    """Interface para gerar embeddings de textos."""
    
    def encode(self, texts: List[str]) -> torch.Tensor:
        """Retorna embeddings para uma lista de textos."""
        raise NotImplementedError("Subclasses devem implementar este método.")

# 🔹 Implementação HuggingFace
class HuggingFaceEmbedder(Embedder):
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
    
    def encode(self, texts: List[str]) -> torch.Tensor:
        # Tokenização
        encoded_input = self.tokenizer(
            texts, padding=True, truncation=True, return_tensors="pt"
        )
        # Extraindo embeddings do [CLS]
        with torch.no_grad():
            model_output = self.model(**encoded_input)
            embeddings = model_output.last_hidden_state[:,0,:]  # [CLS] token
        # Normalizando para similaridade coseno
        embeddings = torch.nn.functional.normalize(embeddings, p=2, dim=1)
        return embeddings