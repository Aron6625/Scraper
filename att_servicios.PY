import time
import psycopg2
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options

# Ruta al geckodriver
drive_path = r'D:\\geckodriver.exe'

# Opciones del navegador Firefox
options = Options()
options.binary_location = r'C:\Program Files\Mozilla Firefox\firefox.exe'

# Conexión a la base de datos PostgreSQL
conn = psycopg2.connect(
    dbname="testinBig",
    user="postgres",
    password="8776959",
    host="localhost"
)

# Crear un cursor
cursor = conn.cursor()

# Crear la tabla attservicioc si no existe
create_table_query = '''
CREATE TABLE IF NOT EXISTS attservicioc (
    id SERIAL PRIMARY KEY,
    operador TEXT NOT NULL,
    departamento TEXT NOT NULL,
    tarifa TEXT NOT NULL,
    velocidad INT NOT NULL,
    precio INT NOT NULL,
    tipo_conexion TEXT NOT NULL
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
def capture_and_save_data(driver):
    wait = WebDriverWait(driver, 10)
    
    src_input = driver.find_element(By.CSS_SELECTOR, "input[type=search]")
    src_input.send_keys("Cochabamba")  # Realizar la búsqueda para "Cochabamba"
    time.sleep(2)
    
    select_element = driver.find_element(By.CSS_SELECTOR, "select[name=kt_table_length]")
    select_element.click()
    option = select_element.find_element(By.CSS_SELECTOR, "option[value='-1']")
    option.click()
    time.sleep(2)
    
    # Paginación hasta la página 10
    for page_num in range(1, 11):
        rows = driver.find_elements(By.CSS_SELECTOR, "table.dataTable tbody tr[role=row]")
        for row in rows:
            data = row.find_elements(By.CSS_SELECTOR, "td")
            operador = data[0].text
            departamento = data[1].text
            tarifa = data[2].text
            velocidad = int(data[3].text)
            precio = int(data[4].text)
            tipo_conexion = data[5].text
            
            cursor.execute("""
                INSERT INTO attservicioc (operador, departamento, tarifa, velocidad, precio, tipo_conexion)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (operador, departamento, tarifa, velocidad, precio, tipo_conexion))
            conn.commit()
        
        # Verificar si hay una siguiente página y navegar a ella
        try:
            next_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".paginate_button.next:not(.disabled)")))
            next_button.click()
            time.sleep(2)
        except:
            break  # Salir del bucle si no hay más páginas

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
    capture_and_save_data(driver)
    driver.quit()

# Cerrar la conexión a la base de datos
cursor.close()
conn.close()
