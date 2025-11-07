from typing import List, Dict
from sklearn.metrics.pairwise import cosine_similarity
from .help import load_credible_domains  # se você também modularizar o carregamento de domínios


def prefilter_results(
    results: List[Dict],
    original_title: str,
    embedder,
    credible_domains_file: str = "./data/credible_sources.txt"
) -> List[Dict]:
    """
    Filtra resultados de busca com base em similaridade semântica e credibilidade da fonte,
    usando thresholds dinâmicos conforme o artigo.
    """

    credible_domains = load_credible_domains(credible_domains_file)
    
    # Embeddings
    titles = [r["title"] for r in results]
    embeddings = embedder.encode(titles)
    original_emb = embedder.encode([original_title])

    # Similaridade coseno
    sim_scores = cosine_similarity(original_emb, embeddings)[0]

    # Thresholds dinâmicos
    thresholds = [0.85, 0.80, 0.70]
    filtered_results = []

    for threshold in thresholds:
        filtered_results = []
        for i, score in enumerate(sim_scores):
            if score >= threshold:
                r = results[i].copy()
                r["similarity"] = float(score)
                r["credible"] = r["domain"] in credible_domains
                filtered_results.append(r)
        if filtered_results:
            break  # Sai do loop assim que encontrar resultados

    # Se não encontrar nada acima de 0.70, retorna todos os resultados com campos adicionais
    if not filtered_results:
        filtered_results = []
        for i, score in enumerate(sim_scores):
            r = results[i].copy()
            r["similarity"] = float(score)
            r["credible"] = r["domain"] in credible_domains
            filtered_results.append(r)

    return filtered_results