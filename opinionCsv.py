import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import StaleElementReferenceException

# Ruta al geckodriver
drive_path = r'D:\\geckodriver.exe'

# Opciones del navegador Firefox
options = Options()
options.binary_location = r'C:\Program Files\Mozilla Firefox\firefox.exe'

# Función para configurar y obtener el navegador
def config(uri):
    service = Service(executable_path=drive_path)
    driver = webdriver.Firefox(service=service, options=options)
    driver.get(uri)
    return driver

# Función para capturar y guardar los datos en un archivo CSV
def capture_and_save_data(driver, section, csv_writer):
    wait = WebDriverWait(driver, 10)
    
    for page_num in range(1, 11):  # Paginación hasta la página 10
        # Esperar a que los artículos estén presentes
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".onm-new.content.image-top-left")))
        
        articles = driver.find_elements(By.CSS_SELECTOR, ".onm-new.content.image-top-left")
        
        for i in range(len(articles)):
            # Re-localizar los artículos en el DOM
            articles = driver.find_elements(By.CSS_SELECTOR, ".onm-new.content.image-top-left")
            article = articles[i]

            try:
                title_element = article.find_element(By.CSS_SELECTOR, ".title.title-article a")
                title = title_element.text
                article_url = title_element.get_attribute("href")
                
                description_element = article.find_element(By.CSS_SELECTOR, ".summary")
                description = description_element.text
                
                image_element = article.find_element(By.CSS_SELECTOR, ".article-media img")
                image_url = image_element.get_attribute("data-src")
                
                # Hacer clic en el título para navegar a la página del artículo
                driver.execute_script("arguments[0].click();", title_element)
                
                # Esperar a que se cargue la página del artículo
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "article.content-cochabamba, article.content-pais, article.content-mundo")))
                
                # Capturar detalles adicionales del artículo
                try:
                    author_name = driver.find_element(By.CSS_SELECTOR, ".author-name").text
                except:
                    author_name = ""
                
                try:
                    content_time = driver.find_element(By.CSS_SELECTOR, ".content-time").text
                except:
                    content_time = ""
                
                print("Title:", title)
                print("Article URL:", article_url)
                print("Description:", description)
                print("Image URL:", image_url)
                print("Author Name:", author_name)
                print("Content Time:", content_time)
                print("Section:", section)
                print("-----------")
                
                # Escribir los datos en el archivo CSV
                csv_writer.writerow([title, description, image_url, article_url, author_name, content_time, section])
                
                # Volver a la página de la sección original
                driver.back()
                
                # Esperar a que los artículos estén nuevamente presentes
                wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".onm-new.content.image-top-left")))
            except StaleElementReferenceException:
                continue  # Si se produce la excepción, intenta nuevamente buscar los elementos
        
        # Navegar a la siguiente página
        try:
            next_button = driver.find_element(By.CSS_SELECTOR, f".pagination li a[href*='page={page_num + 1}']")
            driver.execute_script("arguments[0].click();", next_button)
            time.sleep(2)  # Esperar un momento para que la página se cargue
        except:
            break  # Salir del bucle si no hay más páginas

# Lista de secciones para extraer datos
sections = [
    ("Cochabamba", "https://www.opinion.com.bo/blog/section/cochabamba/"),
    ("País", "https://www.opinion.com.bo/blog/section/pais/"),
    ("Mundo", "https://www.opinion.com.bo/blog/section/mundo/")
]

# Crear el archivo CSV y escribir los encabezados
with open('noticias.csv', mode='w', newline='', encoding='utf-8') as file:
    csv_writer = csv.writer(file)
    csv_writer.writerow(['Title', 'Description', 'Image URL', 'Article URL', 'Author Name', 'Content Time', 'Section'])
    
    # Ejecutar la función para capturar y guardar datos para cada sección
    for section_name, uri in sections:
        print(f"Extracting data for section: {section_name}")
        driver = config(uri)
        capture_and_save_data(driver, section_name, csv_writer)
        driver.quit()
