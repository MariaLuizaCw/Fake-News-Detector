
import trafilatura
from newspaper import Article
from bs4 import BeautifulSoup
import json

###############################

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/127.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,pt-BR;q=0.8",
    "Referer": "https://www.google.com/",
}

###############################

def extract_page_content(url):
    content = {}
    
    article = Article(url, browser_user_agent='Mozilla/5.0', request_timeout=2)
    article.download()
    article.parse()
    
    try:
        content['newspaper_title'] = article.title
        #print ("newspaper.Article.title:\n", article.title)
    except:
        print("Failed: newspaper.Article.title")
    
    try:
        content['newspaper_meta_description'] = article.meta_description
        #print("newspaper.Article.meta_description:\n", article.meta_description)
    except:
        print("Failed: newspaper.Article.meta_description")
    
    try:
        content['newspaper_text'] = article.text
        #print ("newspaper.Article.text:\n", article.text)
    except:
        print("Failed: newspaper.Article.text")
    
    
    
    try:
        soup = BeautifulSoup(article.html, "html.parser")
        
    except:
        print("Failed: bs4.BeautifulSoup")
        soup = None
    
    
    
    if soup:
        try:
            titulo_html = soup.title.get_text(strip=True) if soup.title else None
            #print("- titulo_html:", titulo_html)
            content['bs4_title'] = titulo_html
        except:
            print("Failed: bs4_title")
    
        '''
        try:
            titulo_og = soup.find("meta", property="og:title")
            titulo_og = titulo_og["content"] if titulo_og else None
            print("- titulo_og:", titulo_og)
            content['titulo_og'] = titulo_og
        except:
            print("Failed: titulo_og")
        '''
    
        try:
            desc = soup.find("meta", property="og:description")
            if not desc:
                desc = soup.find("meta", attrs={"name": "description"})
            descricao = desc["content"] if desc else None
            #print("- descricao:", descricao)
            content['bs4_description'] = descricao
        except:
            print("Failed: bs4_description")
    
    
        try:
            canonical = soup.find("link", rel="canonical")
            canonical_url = canonical["href"] if canonical else None
            #print("- canonical_url:", canonical_url)
            content['bs4_link'] = canonical_url
        except:
            print("Failed: bs4_link")        
    
        
        
        dados = trafilatura.extract(
            str(soup),
            output_format="json",
            include_comments=False
        )
    
        if dados:
            dados = json.loads(dados)
        else:
            dados = {}
    
        if dados['text']:
            #print("- content:", dados['text'])
            content['trafilatura_text'] = dados['text']
    
    return content