from typing import List, Dict
from sklearn.metrics.pairwise import cosine_similarity
from help import load_credible_domains  # se você também modularizar o carregamento de domínios
from transformers import pipeline

def prefilter_results(
    results: List[Dict],
    original_title: str,
    embedder,
    credible_domains_file: str = "./data/credible_sources.txt"
) -> List[Dict]:

    credible_domains = load_credible_domains(credible_domains_file)

    valid_items = []
    valid_titles = []

    for r in results:
        t = r.get("refined_title")
        if isinstance(t, str) and t.strip() != "":
            valid_items.append(r)
            valid_titles.append(t.strip())

    if not valid_items:
        return []

    embeddings = embedder.encode(valid_titles)
    original_emb = embedder.encode([original_title])
    
    sim_scores = cosine_similarity(original_emb, embeddings)[0]

    filtered_results = []

    for i, score in enumerate(sim_scores):
        r = valid_items[i].copy()
        r["similarity"] = float(score)
        r["credible"] = r["domain"] in credible_domains
        filtered_results.append(r)
    
    return filtered_results
