from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options

# drive_path = '/home/jhomani/projects/python/geckodriver'
# drive_path = r'C:\Users\Hp\Music\geckodriver.exe'
drive_path = r'D:\\geckodriver.exe'
options = Options()
options.binary_location = r'C:\Program Files\Mozilla Firefox\firefox.exe'

uri = "https://www.bing.com/translator"

def config():
  # driver = webdriver.Firefox(service=Service(executable_path=drive_path))
  service = Service(executable_path=drive_path)
  # driver = webdriver.Firefox(executable_path=drive_path, options=options)
  driver = webdriver.Firefox(service=service, options=options)
  driver.get(uri)
  driver.implicitly_wait(0.5)

  src_options = driver.find_element(by=By.ID, value="tta_srcsl")
  src_options.click()
  option = src_options.find_element(by=By.CSS_SELECTOR, value="option[value=es]")
  option.click()

  src_options = driver.find_element(by=By.ID, value="tta_tgtsl")
  src_options.click()
  option = src_options.find_element(by=By.CSS_SELECTOR, value="option[value=en]")
  option.click()

  return driver

wait_translation = lambda d : d.find_element(
  By.CSS_SELECTOR,
  "div[class=tta_playc]"
)

def translate_phrases(phrases = []):
  translated = []

  driver = config()

  text_box = driver.find_element(by=By.ID, value="tta_input_ta")
  target_box = driver.find_element(by=By.ID, value="tta_output_ta")
  clear_btn = driver.find_element(by=By.ID, value="tta_clear")

  for item in phrases:
    text_box.send_keys(item)

    WebDriverWait(driver, timeout=5).until(wait_translation)

    translated.append(target_box.get_attribute('value'))

    clear_btn.click()

  driver.quit()

  return translated

target_list = [
  "En ese ejemplo, pasamos una función anónima.",
  "Esto no es ejemplo, pasamos una función anónima.",
  "Amo los ejemplo, pasamos una función anónima.",
]

print(translate_phrases(target_list))
