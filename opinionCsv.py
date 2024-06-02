import time
import sqlite3
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException, TimeoutException
from datetime import datetime

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

# Función para convertir la fecha al formato YYYY-MM-DD
def convertir_fecha(fecha_str):
    try:
        meses = {
            'enero': '01', 'febrero': '02', 'marzo': '03', 'abril': '04',
            'mayo': '05', 'junio': '06', 'julio': '07', 'agosto': '08',
            'septiembre': '09', 'octubre': '10', 'noviembre': '11', 'diciembre': '12'
        }
        # Extraer la fecha
        partes = fecha_str.split()
        dia = partes[0]
        mes = meses[partes[2]]
        anio = partes[4]
        fecha_formateada = f"{anio}-{mes}-{dia}"
        return fecha_formateada
    except Exception as e:
        print(f"Error al convertir la fecha: {e}")
        return ""

# Función para capturar y guardar los datos en la base de datos
def capture_and_save_data(driver, section, cursor, conn):
    wait = WebDriverWait(driver, 10)
    
    for page_num in range(1, 31):  # Paginación hasta la página 30
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
                image_url = image_element.getAttribute("data-src")
                
                # Hacer clic en el título para navegar a la página del artículo
                driver.execute_script("arguments[0].click();", title_element)
                
                # Esperar a que se cargue la página del artículo
                try:
                    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "article.content-cochabamba, article.content-pais, article.content-mundo")))
                except TimeoutException:
                    print("TimeoutException: No se pudo cargar la página del artículo.")
                    driver.back()
                    continue
                
                # Capturar detalles adicionales del artículo
                try:
                    author_name = driver.find_element(By.CSS_SELECTOR, ".author-name").text
                except NoSuchElementException:
                    author_name = ""
                
                try:
                    content_time = driver.find_element(By.CSS_SELECTOR, ".content-time").text
                    content_date = convertir_fecha(content_time)
                except NoSuchElementException:
                    content_date = ""
                
                print("Title:", title)
                print("Article URL:", article_url)
                print("Description:", description)
                print("Image URL:", image_url)
                print("Author Name:", author_name)
                print("Content Date:", content_date)
                print("Section:", section)
                print("-----------")
                
                # Insertar los datos en la base de datos
                cursor.execute("""
                    INSERT INTO articles (title, description, image_url, article_url, author_name, content_date, section, revista)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (title, description, image_url, article_url, author_name, content_date, section, "opinion"))
                conn.commit()
                
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
        except NoSuchElementException:
            break  # Salir del bucle si no hay más páginas

# Conectar a la base de datos SQLite
conn = sqlite3.connect('noticias.db')
cursor = conn.cursor()

# Crear la tabla si no existe
cursor.execute("""
    CREATE TABLE IF NOT EXISTS articles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        description TEXT,
        image_url TEXT,
        article_url TEXT,
        author_name TEXT,
        content_date TEXT,
        section TEXT,
        revista TEXT
    )
""")
conn.commit()

# Lista de secciones para extraer datos
sections = [
    ("Cochabamba", "https://www.opinion.com.bo/blog/section/cochabamba/"),
    ("País", "https://www.opinion.com.bo/blog/section/pais/"),
    ("Mundo", "https://www.opinion.com.bo/blog/section/mundo/")
]

# Ejecutar la función para capturar y guardar datos para cada sección
for section_name, uri in sections:
    print(f"Extracting data for section: {section_name}")
    driver = config(uri)
    capture_and_save_data(driver, section_name, cursor, conn)
    driver.quit()

# Cerrar la conexión a la base de datos
conn.close()
