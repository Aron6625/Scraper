import time
import psycopg2
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options

drive_path = r'D:\\geckodriver.exe'

options = Options()
options.binary_location = r'C:\Program Files\Mozilla Firefox\firefox.exe'

state_code = ['wa', 'ny']

uri = 'https://www.zillow.com/wa'

conn = psycopg2.connect(
    dbname="testbig data",
    user="postgres",
    password="34353435",
    host="localhost"
)
table = 'datos'

def config():
    service = Service(executable_path=drive_path)
    driver = webdriver.Firefox(service=service, options=options)
    driver.get(uri)
    return driver

urls = 3;

def capture_and_save_data():
    driver = config()

    time.sleep(2)  
    rows = driver.find_element(By.CSS_SELECTOR, "ul.photo-cards_extra-attribution li")

    cursor = conn.cursor()

    for row in rows:
        data = row.find_elements(by=By.CSS_SELECTOR, value="td")
        print(data);
        # operador = data[0].text
        # departamento = data[1].text
        # velocidad = int(data[3].text)
        # tarifa = data[2].text
        # precio = int(data[4].text)
        # tipo_conexion = data[5].text
        # # cursor.execute(f'INSERT INTO (operador, Departamento, tarifa, velocidad, precio, tipo_conexion)')

        # cursor.execute("""
        #             INSERT INTO attservicioc(operador, departamento, tarifa, velocidad, precio, tipo_conexion)
        #             VALUES (%s, %s, %s, %s, %s, %s)
        #         """, (operador, departamento, tarifa, velocidad, precio, tipo_conexion))
        conn.commit()
    cursor.close()
    conn.close()
    driver.quit()
capture_and_save_data()