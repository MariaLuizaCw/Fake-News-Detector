
def build_classification_prompt_test1(title_to_check: str, results_filtered: list) -> str:
    """
    Cria prompt compacto no formato "toon" para classificar fake/true,
    sem JSON, apenas cada resultado em linha | refined_title | original_title | domain | credibility
    """

    # 1-shot examples compactos
    examples = [
        {
            "title": "NASA announces new water discovery on Mars",
            "results": [
                {
                    "refined_title": "NASA confirms water on Mars after new satellite analysis",
                    "original_title": "NASA confirms water on Mars...",
                    "domain": "nasa.gov",
                    "credible": True
                },
                {
                    "refined_title": "Scientists find traces of water on Mars beneath the surface",
                    "original_title": "Scientists find traces of water on Mars...",
                    "domain": "science.org",
                    "credible": True
                }
            ],
            "label": "real"
        },
        {
            "title": "Celebrity endorses miracle cure for cancer",
            "results": [
                {
                    "refined_title": "Miracle cure claims debunked by doctors",
                    "original_title": "Miracle cure claims debunked by doctors",
                    "domain": "healthnews.com",
                    "credible": True
                },
                {
                    "refined_title": "Celebrity claims not verified",
                    "original_title": "Celebrity claims not verified",
                    "domain": "gossipblog.com",
                    "credible": False
                }
            ],
            "label": "fake"
        }
    ]

    # Formatar exemplos no estilo “linha única” e sem indicar campos
    def format_example(ex):
        lines = [f"Headline: {ex['title']}"]
        for r in ex['results']:
            lines.append(
                f"- {r['refined_title']} | {r['original_title']} | {r['domain']} | {'credible' if r['credible'] else 'credibility unknown'}"
            )
        lines.append(f"Answer: {ex['label']}")
        return "\n".join(lines)

    examples_text = "\n\n".join([format_example(e) for e in examples])

    # Formatar resultados filtrados do título atual
    filtered_text = "\n".join([
        f"- {r.get('refined_title')} | {r.get('original_title')} | {r.get('domain')} | {'credible source' if r['credible'] else 'credibility unknown'}"
        for r in results_filtered
    ])

    prompt = f"""
Classify the news headline as 'fake' or 'real'.

Examples (each line shows refined_title | original_title | domain | credibility):

{examples_text}

Now classify the following headline:
Headline: {title_to_check}

Results from web search (each line shows refined_title | original_title | domain | credibility):
{filtered_text}

Answer only 'fake' or 'real'. Do not explain.
    """
    return prompt



def build_classification_prompt_test2(title_to_check: str, results_filtered: list) -> str:
    """
    Cria prompt compacto no formato "toon" para classificar fake/true,
    sem JSON, apenas cada resultado em linha | refined_title | original_title | domain | credibility
    """

    # 1-shot examples compactos
    examples = [
        {
            "title": "NASA announces new water discovery on Mars",
            "results": [
                {
                    "refined_title": "NASA confirms water on Mars after new satellite analysis",
                    "original_title": "NASA confirms water on Mars...",
                    "domain": "nasa.gov",
                    "credible": True
                },
                {
                    "refined_title": "Scientists find traces of water on Mars beneath the surface",
                    "original_title": "Scientists find traces of water on Mars...",
                    "domain": "science.org",
                    "credible": True
                }
            ],
            "label": "real"
        },
        {
            "title": "Celebrity endorses miracle cure for cancer",
            "results": [
                {
                    "refined_title": "Miracle cure claims debunked by doctors",
                    "original_title": "Miracle cure claims debunked by doctors",
                    "domain": "healthnews.com",
                    "credible": True
                },
                {
                    "refined_title": "Celebrity claims not verified",
                    "original_title": "Celebrity claims not verified",
                    "domain": "gossipblog.com",
                    "credible": False
                }
            ],
            "label": "fake"
        },
        {
            "title": "Study proves that coffee doubles lifespan",
            "results": [
                {
                    "refined_title": "Coffee linked to longer lifespan according to observational study — association is small and not causal",
                    "original_title": "Coffee linked to longer lifespan according to observational study...",
                    "domain": "nytimes.com",
                    "credible": True
                },
                {
                    "refined_title": "Experts warn study shows correlation, not causation",
                    "original_title": "Experts warn study shows correlation, not causation",
                    "domain": "reuters.com",
                    "credible": True
                }
            ],
            "label": "real with misinformation"
        }
    ]

    # Formatar exemplos no estilo “linha única” e sem indicar campos
    def format_example(ex):
        lines = [f"Headline: {ex['title']}"]
        for r in ex['results']:
            lines.append(
                f"- {r['refined_title']} | {r['original_title']} | {r['domain']} | {'credible' if r['credible'] else 'credibility unknown'}"
            )
        lines.append(f"Answer: {ex['label']}")
        return "\n".join(lines)

    examples_text = "\n\n".join([format_example(e) for e in examples])

    # Formatar resultados filtrados do título atual
    filtered_text = "\n".join([
        f"- {r.get('refined_title')} | {r.get('original_title')} | {r.get('domain')} | {'credible source' if r['credible'] else 'credibility unknown'}"
        for r in results_filtered
    ])

    prompt = f"""
Classify the news headline as 'fake', 'real' or 'real with misinformation'.

Examples (each line shows refined_title | original_title | domain | credibility):

{examples_text}

Now classify the following headline:
Headline: {title_to_check}

Results from web search (each line shows refined_title | original_title | domain | credibility):
{filtered_text}

Answer only one of the following: 'fake', 'true', 'real with misinformation'. Do not explain.
    """
    return prompt



def build_classification_prompt_test3(title_to_check: str, results_filtered: list) -> str:
    """
    Prompt mínimo: classifica apenas com base no headline,
    sem usar resultados de busca.
    """

    examples = [
        {
            "title": "NASA announces new water discovery on Mars",
            "label": "real"
        },
        {
            "title": "Celebrity endorses miracle cure for cancer",
            "label": "fake"
        }
    ]

    examples_text = "\n\n".join([
        f"Headline: {e['title']}\nAnswer: {e['label']}"
        for e in examples
    ])

    prompt = f"""
Classify the news headline as 'fake' or 'real'.

Examples:
{examples_text}

Now classify the following headline:
Headline: {title_to_check}

Answer only 'fake' or 'real'. Do not explain.
    """.strip()

    return prompt





PROMPT_REGISTRY = {
    "test1": build_classification_prompt_test1,
    "test2": build_classification_prompt_test2,
    "test3": build_classification_prompt_test3
}



def build_prompt(mode: str, title_to_check: str, results_filtered: list):
    if mode not in PROMPT_REGISTRY:
        raise ValueError(f"Unknown prompt mode '{mode}'")

    return PROMPT_REGISTRY[mode](title_to_check, results_filtered)
