import psycopg2
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options

drive_path = r'D:\\geckodriver.exe'

options = Options()
options.binary_location = r'C:\Program Files\Mozilla Firefox\firefox.exe'


uri = "https://clasificados.lostiempos.com/inmuebles"


def config():
    service = Service(executable_path=drive_path)
    driver = webdriver.Firefox(service=service, options=options)
    driver.get(uri)
    driver.implicitly_wait(0.5)
    return driver


def get_data():
    driver = config()
    titles = driver.find_elements(By.CLASS_NAME, "title")
    field_contents = driver.find_elements(By.CLASS_NAME, "field-content")
    
    data = []
    for title, field_content in zip(titles, field_contents):
        data.append((title.text, field_content.text))
    
    driver.quit()
    return data

def store_data_in_postgres(data):
    conn = psycopg2.connect(
        dbname="testbig data",
        user="postgres",
        password="34353435",
        host="localhost"
    )
    cur = conn.cursor()
    
    for title, field_content in data:
        cur.execute("INSERT INTO periodico (titulo, descripcion) VALUES (%s, %s)", (title, field_content))
    
    conn.commit()
    cur.close()
    conn.close()

# Ejecutar la función para obtener los datos
data = get_data()

# Almacenar los datos en PostgreSQL
store_data_in_postgres(data)