"""
Scraper de la revista colombiana Pagina12
"""

# Librerías
import requests
import pandas as pd
from bs4 import BeautifulSoup


def pull_data(secciones):
    '''
    Función que obtiene los datos para cada articulo 
    '''
    #Inicializamos el diccionario
    dict_data = dict(Titulo=[],Fecha=[],Autor=[],Volanta=[])

    # Interamos por secciones
    for seccion in secciones:
        # Iteramos por artículo de cada sección
        print('\n')
        for i, page in enumerate(seccion):
            print(f'Escrapeando nota {i}/{len(secciones)}')
            try:
                # Request de un artículo
                page_item = requests.get(page)
                if page_item.status_code == 200:
                    soup_page = BeautifulSoup(page_item.text,'lxml')

                    # Extraems el titulo
                    title = soup_page.find('h1')
                    if title:
                        dict_data['Titulo'].append(title.text)
                    else:
                        dict_data['Titulo'].append(None)
                    
                    # Extraemos fecha
                    date = soup_page.find('span', attrs={'pubdate':'pubdate'})
                    if date:
                        dict_data['Fecha'].append(date.get('datetime'))
                    else:
                        dict_data['Fecha'].append(None)

                    # Extraemos autor
                    author = soup_page.find('div', attrs={'class':'author-name'})
                    if author:
                        dict_data['Autor'].append(author.get_text())
                    else:
                        dict_data['Autor'].append(None)

                    # Extraemos la volanta                
                    flyer = soup_page.find('h4')
                    if flyer:
                        dict_data['Volanta'].append(flyer.text)
                    else:
                        dict_data['Volanta'].append(None)
                    
            except Exception as e:
                print('Error en la request')
                print(e)
                print('\n')

    return dict_data


def articles_links(soup):
    '''
    Funcion que recibe un objeto de BeautifulSoup y 
    devuelve una lista de URL's a las notas de esa seccion
    '''

    links = []
    # Obtener el listado de articulos
    article_list = soup.find_all('article')
    for xlist in article_list:
        article = xlist.find('div', attrs={'class':'article-item__header'})
        if article:
            links.append(article.a.get('href'))
    return links


def article_url(list_sections):
    '''
    Función que obtiene las url's de los artículos de cada sección 
    '''

    articles = []
    for url_section in list_sections:
        try:
            # Hacemos un request de una sección
            url_section_req = requests.get(url_section)
            if url_section_req.status_code == 200:
                soup_url_section = BeautifulSoup(url_section_req.text, 'lxml')
                # Encuentre todos los articulos de la seccion url_section y guardalos en la lista
                articles.append(articles_links(soup_url_section))            

        except Exception as e:
            print('Error en la request: article url function')
            print(e)
            print('\n')

    return articles


def pagina12_sections(url):
    """
    Obtiene lista de url's de las secciones principales de Pagina12
    """
    
    links_sections = []
    try:
        # Requests del url
        url_req = requests.get(url)
        if url_req.status_code == 200:
            # Soup del archivo html
            soup_main = BeautifulSoup(url_req.text, 'lxml')
            # Encontrar las diferentes secciones
            sections = soup_main.find('ul', attrs={'class':'horizontal-list main-sections hide-on-dropdown'}).find_all('li')
            links_sections = [section.a.get('href') for section in sections]
    except  Exception as e:
        print('Error en la request: pagina12 sections function')
        print(e)
        print('\n')

    # Regresar el link de las secciones
    return links_sections


def scraper(url):
    '''
    Hace llamados a las funciones para realizar el scraping.
    '''

    # Extraer url de las secciones principales de Pagina12.
    list_sections = pagina12_sections(url)
    
    # Obtener las URL de los artículos para casa sección.
    all_articles = article_url(list_sections)
    
    # Extraer los datos para cada artículo por sección.
    data = pull_data(all_articles)

    # Almacenar los datos en un DataFrame y exportarlo.
    df  = pd.DataFrame(data)
    df.to_csv('dataPagin12.csv')
    
    
# Entrada del programa
if __name__ == '__main__':
    url = 'https://www.pagina12.com.ar/'
    print('\n')
    print('----- Scraper de la revista Pagina12 -----')    
    print('\n')

    scraper(url)

