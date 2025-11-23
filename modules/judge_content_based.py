
from modules.llm_base import LLM, LOCAL_LLM
from modules.extract_page_content import extract_page_content


model = "gemma3:12b" # llama3.1:8b // gemma3:12b
llm = LOCAL_LLM(
    model=model,
)


base_prompt = """
Classify the sentence to be classified as 'fake', 'real', or 'unrelated' based solely on the information from the article below:

Article Title: >>> "{}". <<< End of Article Title.
Article Content to be used as source of the information: >>> "{}". <<< End of Article Content.

Answer 'fake' if the article content contradicts the sentence to be classified.
Answer 'real' if the article content supports the sentence to be classified.
Answer 'unrelated' if the article does not address the topic of the sentence to be classified.
Respond with a single word only, without justification.

Sentence to be classified: >>> "{}". <<< End of the sentence.
"""


def judge_content_based(url , sentence):
    page_content = extract_page_content(url)
    prompt = base_prompt.format(page_content['newspaper_title'],
                                page_content['trafilatura_text'],
                                sentence,
                                )
    #print(prompt)
    response = llm.generate(prompt=prompt, temperature=0.1)
    return response.strip().lower()