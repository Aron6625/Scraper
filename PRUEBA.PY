import time
import psycopg2
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options

# Ruta al geckodriver
drive_path = r'D:\\geckodriver.exe'

# Opciones del navegador Firefox
options = Options()
options.binary_location = r'C:\Program Files\Mozilla Firefox\firefox.exe'

# URL del sitio web
uri = "https://clasificados.lostiempos.com/inmuebles"

# Conexión a la base de datos PostgreSQL
conn = psycopg2.connect(
    dbname="testbig data",
    user="postgres",
    password="34353435",
    host="localhost"
)
table = 'datos'

# Función para configurar y obtener el navegador
def config():
    service = Service(executable_path=drive_path)
    driver = webdriver.Firefox(service=service, options=options)
    driver.get(uri)
    return driver

urls = 3;

# Función para capturar y guardar los datos en PostgreSQL
def capture_and_save_data():
    driver = config()
    
    for i in range(0, 3):
        driver.get(f"https://clasificados.lostiempos.com/inmuebles?page={i}");

        time.sleep(2)
        
        carts = driver.find_elements(By.CSS_SELECTOR, ".pane-views-panes .view-content > .views-row:not([id])")
        
        cursor = conn.cursor()
        for cart in carts:
            title = cart.find_element(By.CLASS_NAME, "title")
            body = cart.find_element(By.CLASS_NAME, "body")

            try:
                price = cart.find_element(By.CLASS_NAME, "price").text
            except:
                price = '$us 0';

            publish_date = cart.find_element(By.CLASS_NAME, "publish-date")

            # Verificar si el registro ya existe en la base de datos
            cursor.execute(
                f'SELECT * FROM clasificados WHERE title = %s AND body = %s AND price = %s AND publish_date = %s',
                (title.text, body.text, price, publish_date.text)
            )
            existing_record = cursor.fetchone()
            
            if not existing_record:
                # Insertar el nuevo registro solo si no existe en la base de datos
                cursor.execute(
                    f'INSERT INTO clasificados (title, body, price, publish_date) VALUES (%s, %s, %s, %s)',
                    (title.text, body.text, price, publish_date.text)
                )
    
        conn.commit()
        cursor.close()
        
    driver.quit()

# Ejecutar la función para capturar y guardar datos
capture_and_save_data()