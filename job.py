import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone
import os
from dotenv import load_dotenv

# load_dotenv()
# PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def get_links(url):
    # Enviando requisição HTTP para obter o conteúdo da página
    response = requests.get(url)
    content = response.content

    # Analisando o conteúdo da página com BeautifulSoup
    soup = BeautifulSoup(content, 'html.parser')

    # Encontrar todas as tags ul que tenham archive-list__list na classe
    archive_list = soup.find('ul', class_='archive-list__list')

    # Encontrar todas as tags <li> dentro da tag <ul>
    li_tags = archive_list.find_all('li')

    links = []
    # Iterar sobre todas as tags <li> e extrair o href
    for li in li_tags:
        a_tag = li.find('a')
        href = a_tag['href']
        links.append(href)
    return links

def extract_article_info(url):
    try:
        # Fazer a requisição HTTP
        response = requests.get(url)
        
        # Verificar se a requisição foi bem-sucedida
        if response.status_code != 200:
            return f"Erro ao acessar a página: {response.status_code}"
            
        # Definir a codificação como UTF-8
        response.encoding = 'utf-8'

        # Fazer o parsing do HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extrair informações do artigo
        if url.startswith('https://www.poder360.com.br/poder-flash'):
            title = soup.find('h1', class_='box-poder-flash__title mt-4').text.strip()
        else:
            title = soup.find('h1', class_='inner-page-section__title title-1').text.strip()
        subtitle = soup.find('h2', class_='inner-page-section__line').text.strip()
        
        # Tentar encontrar a data e o autor
        date = soup.find('time')  # Assumindo que a data está dentro de uma tag <time>
        if date:
            date = date.text.strip()
        else:
            date = "Data não encontrada"
        
        # Extrair o autor
        author_div = soup.find('div', class_='footer-post__box')
        if author_div:
            author_name = author_div.find('a', class_='author__name')
            if author_name:
                author = author_name.text.strip()
            else:
                author = "Autor não encontrado"
        else:
            author = "Autor não encontrado"
        
        # Extrair o texto do artigo
        article_body = soup.find('div', class_='inner-page-section__text')
        if article_body:
            # Encontra e remove o elemento <form> dentro de article_body se ele existir
            form = article_body.find('form')
            if form:
                form.decompose()

            # Inicializa uma lista para armazenar o texto dos elementos
            text_elements = []

            # Itera sobre todos os filhos do article_body
            for child in article_body.children:
                if child.name == 'p':
                    text_elements.append(child.get_text(strip=True))
                elif child.name == 'ul':
                    # Itera sobre todos os <li> dentro do <ul>
                    for li in child.find_all('li'):
                        text_elements.append(li.get_text(strip=True))

            # Combina todos os textos em uma única string separada por quebras de linha
            text = '\n'.join(text_elements)
        else:
            text = "Texto do artigo não encontrado"
        
        # Concatenar informações em uma string
        article_info = f"Título: {title}\nSubtítulo: {subtitle}\nData: {date}\nAutor: {author}\n\nTexto: {text}\n\n"
        
        return article_info
    except Exception as e:
        print(f"Erro ao extrair informações do artigo: {e}")
        print(f"URL do artigo: {url}")

def push_to_vdb(data):
    embeddings = OpenAIEmbeddings()

    index_name = "poder360-dev"

    pc = Pinecone(api_key=PINECONE_API_KEY)

    # Connect ao Pinecone e carrega os documentos
    docsearch = PineconeVectorStore.from_texts(data, embeddings, index_name=index_name)

def my_scheduled_task():
    # Calcular a data de ontem
    yesterday = datetime.now() - timedelta(1)
    yesterday_str = yesterday.strftime('%Y/%m/%d')

    #construir a url das notícias de ontem
    url = f'https://www.poder360.com.br/{yesterday_str}'
    print(f"Date link: {url}")

    # links = get_links(url)
    # links_filtrados = [link for link in links if not link.startswith("https://www.poder360.com.br/author/")]
    # print(f"Cron job links: {len(links_filtrados)}")

    # news = []
    # for link in links_filtrados:
    #     article_info = extract_article_info(link)
    #     news.append(article_info)
    
    # Salva as noícias em um txt
    # with open('news.txt', 'w', encoding='utf-8') as f:
    #     for item in news:
    #         f.write("%s\n" % item)

    # push_to_vdb(news)

    print("Cron job finished")
    

if __name__ == "__main__":
    my_scheduled_task()