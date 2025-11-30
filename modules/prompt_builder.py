
def build_classification_prompt_test1(title_to_check: str, results_filtered: list) -> str:
    """
    Cria prompt compacto no formato "toon" para classificar fake/true,
    sem JSON, apenas cada resultado em linha | refined_title | snippet | domain | credibility
    """

    examples = [
        {
            "title": "Fossil fuel companies accused of “greenwashing” environmental commitment",
            "results": [
                {
                    "refined_title": "Oil firms' climate claims are greenwashing, study concludes",
                    "snippet": "Accusations of greenwashing against major oil companies that claim to be in transition to clean energy are well-founded, according to the most comprehensive ...",
                    "domain": "theguardian.com",
                    "credible": True
                },
                {
                    "refined_title": "Revealed: 9 examples of fossil fuel company greenwashing",
                    "snippet": "We've launched the Greenwashing Files to highlight how advertising and other public claims from companies don't always match up to reality.",
                    "domain": "clientearth.org",
                    "credible": False
                }
            ],
            "label": "real"
        },
        {
            "title": "Pope Francis endorses Donald Trump for president",
            "results": [
                {
                    "refined_title": "Fake News",
                    "snippet": "His comments come amid warnings of a 'fake news' crisis in online media following last month's US elections. Pope Francis Shocks World, Endorses. Donald Trump ...",
                    "domain": "theguardian.com",
                    "credible": False
                },
                {
                    "refined_title": "Read all about it: The biggest fake news stories of 2016",
                    "snippet": "But while the Brexit vote and the U.S. election were making headlines, so too were apparently genuine stories that Pope Francis had endorsed ...",
                    "domain": "cnbc.com",
                    "credible": True
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
                f"- {r['refined_title']} | {r['snippet']} | {r['domain']} | {'credible' if r['credible'] else 'credibility unknown'}"
            )
        lines.append(f"Answer: {ex['label']}")
        return "\n".join(lines)

    examples_text = "\n\n".join([format_example(e) for e in examples])



    filtered_text = "\n".join([
        f"- {r['refined_title']} | {r['snippet']} | {r['domain']} | "
        f"{'credible source' if r.get('credible') else 'credibility unknown'}"
        for r in results_filtered
        if r.get('refined_title') and r.get('snippet') and r.get('domain')
    ])

    prompt = f"""
Classify the news headline as 'fake' or 'real'.

Examples (each line shows refined_title | snippet | domain | credibility):

{examples_text}

Now classify the following headline:
Headline: {title_to_check}

Results from web search (each line shows refined_title | snippet | domain | credibility):
{filtered_text}

Answer only 'fake' or 'real'. Do not explain.
    """
    return prompt



def build_classification_prompt_test2(title_to_check: str, results_filtered: list) -> str:
    """
    Cria prompt compacto no formato "toon" para classificar fake/true,
    sem JSON, apenas cada resultado em linha | refined_title | snippet | domain | credibility
    """

    # 1-shot examples compactos
    examples = [
        {
            "title": "Fossil fuel companies accused of “greenwashing” environmental commitment",
            "results": [
                {
                    "refined_title": "Oil firms' climate claims are greenwashing, study concludes",
                    "snippet": "Accusations of greenwashing against major oil companies that claim to be in transition to clean energy are well-founded, according to the most comprehensive ...",
                    "domain": "theguardian.com",
                    "credible": True
                },
                {
                    "refined_title": "Revealed: 9 examples of fossil fuel company greenwashing",
                    "snippet": "We've launched the Greenwashing Files to highlight how advertising and other public claims from companies don't always match up to reality.",
                    "domain": "clientearth.org",
                    "credible": False
                }
            ],
            "label": "real"
        },
        {
            "title": "Pope Francis endorses Donald Trump for president",
            "results": [
                {
                    "refined_title": "Fake News",
                    "snippet": "His comments come amid warnings of a 'fake news' crisis in online media following last month's US elections. Pope Francis Shocks World, Endorses. Donald Trump ...",
                    "domain": "theguardian.com",
                    "credible": False
                },
                {
                    "refined_title": "Read all about it: The biggest fake news stories of 2016",
                    "snippet": "But while the Brexit vote and the U.S. election were making headlines, so too were apparently genuine stories that Pope Francis had endorsed ...",
                    "domain": "cnbc.com",
                    "credible": True
                }
            ],
            "label": "fake"
        },
        {
            "title": "Eating chocolate can help you lose weight",
            "results": [
                {
                    "refined_title": "Chocolate Helps Burn Body Fat",
                    "snippet": "The morning chocolate women saw smaller waist sizes, lower stress hormones and greater fat burning. Both groups had a change in their gut ...",
                    "domain": "utmb.edu",
                    "credible": False
                },
                {
                    "refined_title": "Chocolate 'may help keep people slim",
                    "snippet": "Even though chocolate is loaded with calories, it contains ingredients that may favour weight loss rather than fat synthesis, scientists ...",
                    "domain": "bbc.com",
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
                f"- {r['refined_title']} | {r['snippet']} | {r['domain']} | {'credible' if r['credible'] else 'credibility unknown'}"
            )
        lines.append(f"Answer: {ex['label']}")
        return "\n".join(lines)

    examples_text = "\n\n".join([format_example(e) for e in examples])

    # Formatar resultados filtrados do título atual
    filtered_text = "\n".join([
        f"- {r.get('refined_title')} | {r.get('snippet')} | {r.get('domain')} | {'credible source' if r['credible'] else 'credibility unknown'}"
        for r in results_filtered
    ])

    prompt = f"""
Classify the news headline as 'fake', 'real' or 'real with misinformation'.

Examples (each line shows refined_title | snippet | domain | credibility):

{examples_text}

Now classify the following headline:
Headline: {title_to_check}

Results from web search (each line shows refined_title | snippet | domain | credibility):
{filtered_text}

Answer only one of the following: 'fake', 'real', 'real with misinformation'. Do not explain.
    """
    return prompt



def build_classification_prompt_test3(title_to_check: str, results_filtered: list) -> str:
    """
    Prompt mínimo: classifica apenas com base no headline,
    sem usar resultados de busca.
    """

    examples = [
        {
            "title": "Fossil fuel companies accused of “greenwashing” environmental commitment",
            "label": "real"
        },
        {
            "title": "Pope Francis endorses Donald Trump for president",
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


def build_classification_prompt_test5(title_to_check: str, results_filtered: list) -> str:
    prompt = f"""
You are a tone-based news classifier.
Classify the following news text as “fake” or “real” based only on tone, style, emotional charge, and linguistic cues.

Important rules:

Do NOT check factual accuracy.

Do NOT use external knowledge.

Do NOT verify if the information is true in reality.

Judge ONLY the tone and writing style.

Your entire output must be only one word: “fake” or “real”, with no explanation.

Text:
{title_to_check}
"""
    return prompt


PROMPT_REGISTRY = {
    "test1": build_classification_prompt_test1,
    "test2": build_classification_prompt_test2,
    "test3": build_classification_prompt_test3,
    'test4': build_classification_prompt_test1,
    'test5': build_classification_prompt_test5
}



def build_prompt(mode: str, title_to_check: str, results_filtered: list):
    if mode not in PROMPT_REGISTRY:
        raise ValueError(f"Unknown prompt mode '{mode}'")

    return PROMPT_REGISTRY[mode](title_to_check, results_filtered)
