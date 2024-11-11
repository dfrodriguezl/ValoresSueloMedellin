import json
from concurrent.futures import ThreadPoolExecutor
from requests_html import HTMLSession
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
import pandas as pd
import numpy as np
import csv
import chompjs
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager

# Configuración del WebDriver
# service = Service(executable_path='C:/Users/DIEGO/Documents/Python_MetroCuadrado/chrome-win64/chrome-win64/chrome.exe')
# driver = webdriver.Chrome(service=service)
driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))

# URL base de la página
url_base = 'https://www.metrocuadrado.com/apartaestudio-apartamento-casa/venta/medellin/'
driver.get(url_base)

# Extracción de enlaces
links = []
condition = True
while condition:
    try:
        block = driver.find_elements(By.CSS_SELECTOR, 'div.card-header a.sc-bdVaJa.ebNrSm')  # Selector CSS correcto
        for e in block:
            i = e.get_attribute('href')
            links.append(i)
            print('Número de link extraído:', len(links))
        # Intentamos ir a la siguiente página
        next_button = driver.find_element(By.CSS_SELECTOR, '.item-icon-next > a')
        next_button.click()
        time.sleep(3)
    except Exception as e:
        print(f"Error durante la extracción de enlaces: {e}")
        condition = False  # No hay más páginas, salir del bucle

# Guardar los links extraídos en un archivo CSV
if links:  # Asegurarse de que haya datos antes de guardarlos
    urls_df = pd.DataFrame(links, columns=['link'])
    urls_df.to_csv('links_metrocuadrado.csv', index=False)
    print("Archivo de enlaces 'links_metrocuadrado.csv' generado correctamente.")
else:
    print("No se encontraron enlaces para guardar.")

# # Si tienes ya un archivo de links, lo puedes agregar
# with open('links_metrocuadrado.csv', 'r') as f:
#     csv_reader = csv.reader(f, delimiter=';')
#     for row in csv_reader:
#         if row: 
#             links.append(row[0])

# Eliminar duplicados
links = pd.unique(links)

# Definir la función de parseo de datos
datos = []

def parse(url):
    s = HTMLSession()
    try:
        r = s.get(url, timeout=20)
        info = 'script[type="application/json"]'
        # info = "//script[@type='application/ld+json'"
        script_element = r.html.find(info, first=True)

        if script_element:
            script_txt = script_element.text.strip()
            json_data = chompjs.parse_js_object(script_txt)
            data = json.dumps(json_data)
            dt = json.loads(data)
            
            # Extraer la información necesaria con manejo de errores
            def get_data(key, default=np.nan):
                try:
                    print(dt['props']['initialState']['realestate']['basic'])
                    return dt['props']['initialState']['realestate']['basic'].get(key, default)
                except KeyError:
                    return default
            
            # Datos a extraer de la propiedad
            details = {
                'businessType': get_data('businessType'),
                'salePrice': get_data('salePrice'),
                'area': get_data('area'),
                'areaPrivada': get_data('areaPrivada'),
                'rooms': get_data('rooms'),
                'bathrooms': get_data('bathrooms'),
                'garages': get_data('garages'),
                'city': get_data('city')["nombre"],
                'longitude': get_data('coordinates')["lon"],
                'latitude': get_data('coordinates')["lat"]
            }
            
            datos.append(details)
            print(f'Datos extraídos de {url}:', details)
        else:
            print(f"No se encontró el script necesario en {url}")

            # Intentar otro método de extracción desde los elementos HTML (como los selectores CSS)
            # Ejemplo: podrías intentar extraer el precio o el área desde elementos específicos:
            try:
                price = r.html.find('span.price', first=True).text
                area = r.html.find('span.area', first=True).text
                print(f"Extraído manualmente: Precio {price}, Área {area}")
            except Exception as e:
                print(f"No se pudo extraer información alternativa en {url}")

    except Exception as e:
        print(f"Error procesando la URL {url}: {e}")
    
    return

# Empezar el scraping con hilos para mayor eficiencia
start = time.perf_counter()

with ThreadPoolExecutor(max_workers=4) as executor:  # Aumentamos a 4 hilos
    executor.map(parse, links)

fin = time.perf_counter() - start
print('Tiempo total:', fin)

# Crear el DataFrame con los datos
if datos:  # Solo guardar si hay datos extraídos
    df = pd.DataFrame(datos)

    # Guardar los datos en un archivo CSV
    df.to_csv('metro_cuadrado_data_20241110.csv', index=False, sep=";")
    print("Archivo de datos 'metro_cuadrado_data_20241031.csv' generado correctamente.")
else:
    print("No se encontraron datos para guardar.")
