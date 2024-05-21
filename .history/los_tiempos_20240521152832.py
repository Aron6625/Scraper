import requests
from bs4 import BeautifulSoup
import csv

url_website = "https://www.lostiempos.com/ultimas-noticias"

def get_page_content(url):
    response = requests.get(url)
    if response.status_code == 200:
        return BeautifulSoup(response.content, "html5lib")
    else:
        return None

def extract_news(uri):
    news = []
    soup = get_page_content(uri)

    if soup:
        try:
            main = soup.select_one('.content-column')
            if not main:
                raise AttributeError("No se encontró el elemento principal con la clase .content-column")

            region = main.find('div', class_='region')
            block_main = region.find('div', class_='block-main')
            content_article = block_main.find('div', class_='clearfix')
            article = content_article.find('article')

            title = article.find('h1', class_='node-title').get_text(strip=True)
            subsection = article.find('div', class_='subsection').get_text(strip=True)
            link = article.find('img', class_='image-style-noticia-detalle')['src']
            date_publish = article.find('div', class_='date-publish').get_text(strip=True)
            author_element = article.find('div', class_='autor').select_one('.field-item a')
            author = author_element.text if author_element else None

            body = article.find('div', class_='body')
            content = body.find('div', class_='field-items')
            description = ''
            for p in content.find_all('p', class_='rtejustify'):
                description += '\n' + ''.join(p.get_text(strip=True))
            
            print("Página escrapeada correctamente!")
            news.append({
                'title': title,
                'description': description,
                'image_url': link,
                'article_url': uri,
                'author_name': author,
                'content_time': date_publish,
                'section': subsection
            })
        except AttributeError as e:
            print(f"Error al procesar el contenido de la página: {e}")
            # Devolver las noticias ya escrapeadas hasta este punto
            return news
    else:
        print("No se pudo obtener el contenido de la página.")
    
    return news

def find_uri_page(soup, classname):
    uri = soup.select_one(f'{classname} a') 
    if uri and 'href' in uri.attrs:
        return uri['href']
    else:
        return None

def scrape_news(start_url,  csv_filename):
    current_url = start_url
    all_news = []

    while current_url:
        print(f"Scraping {current_url}")
        soup = get_page_content(current_url)
        if not soup:
            break
        
        view_content = soup.find('div', class_='view-content')
        articles = view_content.find_all('div', class_='views-row')
        for article in articles:
            uri_news = find_uri_page(article,'.field-content')
            news = extract_news(f'https://www.lostiempos.com{uri_news}')
            all_news.extend(news)
            
        next_page_url = find_uri_page(soup, ".pager-next")
        if next_page_url:
            if next_page_url.startswith('/'):
                current_url = f"https://www.lostiempos.com{next_page_url}"
            else:
                current_url = next_page_url
        else:
            break

    write_to_csv(all_news, csv_filename)


def write_to_csv(news_data, csv_filename):
    fieldnames = ['title', 'section', 'image_url','article_url', 'content_time', 'author_name', 'description']

    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for news in news_data:
            writer.writerow(news)

#inicio de scraping
scrape_news(url_website, 'los_tiempos_news_1.csv')
