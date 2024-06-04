import time
import psycopg2
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException, NoSuchElementException
from datetime import datetime, timedelta

# Ruta al geckodriver
drive_path = r'D:\\geckodriver.exe'

# Opciones del navegador Firefox
options = Options()
options.binary_location = r'C:\Program Files\Mozilla Firefox\firefox.exe'
options.headless = True  # Para ejecutar en modo headless

# Conexión a la base de datos PostgreSQL
conn = psycopg2.connect(
    dbname="noticias",
    user="postgres",
    password="34353435",
    host="localhost"
)

# Crear un cursor
cursor = conn.cursor()

# Crear la tabla deber si no existe
create_table_query = '''
CREATE TABLE IF NOT EXISTS deber (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    image_url TEXT NOT NULL,
    article_url TEXT NOT NULL,
    author_name TEXT,
    content_date DATE,
    section TEXT NOT NULL,
    revista TEXT NOT NULL
);
'''
cursor.execute(create_table_query)
conn.commit()

# Función para configurar y obtener el navegador
def config(uri):
    service = Service(executable_path=drive_path)
    driver = webdriver.Firefox(service=service, options=options)
    driver.get(uri)
    return driver

# Función para capturar y guardar los datos en PostgreSQL
def capture_and_save_data(driver, section):
    wait = WebDriverWait(driver, 10)
    try:
        news_blocks = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'jsx-742874305.nota.linkedjsx-742874305.component.component--small.lastNews')))
        print(news_blocks)
        for block in news_blocks:
            try:
                title = block.find_element(By.TAG_NAME, 'h2').text.strip()
                # description = block.find_element(By.CSS_SELECTOR, 'p').text.strip()
                description = block.find_element(By.CSS_SELECTOR, 'div.jsx-742874305.text > p.jsx-742874305').text.strip()
                # description = block.find_element(By.XPATH, '//div[@class="jsx-742874305 text"]').find_element(By.TAG_NAME, 'p')
                image_url = block.find_element(By.TAG_NAME, 'img').get_attribute('src')
                article_url = block.find_element(By.CLASS_NAME, 'jsx-742874305.nota-link').get_attribute('href')
                author_name = block.find_element(By.CLASS_NAME, 'author').text.strip() if block.find_elements(By.CLASS_NAME, 'author') else None
                content_date = datetime.now().date()
                cursor.execute('''
                INSERT INTO deber (title, description, image_url, article_url, author_name, content_date, section, revista)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ''', (title, description, image_url, article_url, author_name, content_date, section, 'EL DEBER'))
                
                # cursor.execute('''
                # INSERT INTO deber (title, description, image_url, article_url, author_name, content_date, section, revista)
                # VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                # ''', (title, description, image_url, article_url, author_name, content_date, section, 'EL DEBER'))
                
                conn.commit()
            except NoSuchElementException:
                print("No se encontró un elemento esperado en el bloque de noticias.")
                continue
    except TimeoutException:
        print("Timeout while waiting for news blocks")

# Generar URLs para todas las fechas de mayo y abril
base_url = 'https://eldeber.com.bo/ultimas-noticias/'
dates = [datetime(2024, 5, d) for d in range(1, 32)] + [datetime(2024, 4, d) for d in range(1, 31)]

for date in dates:
    url = base_url + date.strftime('%d-%m-%Y')
    driver = config(url)
    capture_and_save_data(driver, 'Ultimas Noticias')
    driver.quit()

# Cerrar la conexión a la base de datos
cursor.close()
conn.close()
