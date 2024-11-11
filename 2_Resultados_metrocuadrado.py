import requests
import json

def limpiar_dato(dato):
    """Elimina saltos de línea y espacios adicionales en los datos extraídos."""
    return str(dato).replace('\n', ' ').replace('\r', '').strip()

def obtener_datos(url):
    try:
        # Realiza la solicitud al sitio web
        response = requests.get(url)
        response.raise_for_status()  # Verifica que la solicitud fue exitosa
        
        # Busca el JSON dentro del HTML
        inicio = response.text.find('{"dataManager"')
        if inicio == -1:
            print(f"No se encontró JSON en {url}")
            return None

        # Extrae el JSON crudo
        fin = response.text.find('</script>', inicio)
        json_data = response.text[inicio:fin]
        
        # Convierte el JSON a un diccionario de Python
        data = json.loads(json_data)
        
        # Asegura que los campos estén presentes antes de intentar acceder a ellos
        propiedad = data.get('props', {}).get('initialState', {}).get('realestate', {}).get('basic', {})
        
        # Extrae y limpia los valores deseados o asigna 'N/A' si están ausentes
        publicationId = limpiar_dato(propiedad.get('publicationId', 'N/A')) #id de publicacion
        precio = limpiar_dato(propiedad.get('salePrice', propiedad.get('rentPrice', 'N/A')))
        propertyType = limpiar_dato(propiedad.get('propertyType', 'N/A')) #tipo de accion
        businessType = limpiar_dato(propiedad.get('businessType', 'N/A')) #tipo de propiedad
        area = limpiar_dato(propiedad.get('area', 'N/A')) #area
        areac = limpiar_dato(propiedad.get('areac', 'N/A')) #area construida
        rooms = limpiar_dato(propiedad.get('rooms', 'N/A')) #habitaciones
        bathrooms = limpiar_dato(propiedad.get('bathrooms', 'N/A')) #Baños
        garages = limpiar_dato(propiedad.get('garages', 'N/A')) #garages
        city = limpiar_dato(propiedad.get('city', 'N/A')) #ciudad
        coordinates = limpiar_dato(propiedad.get('coordinates', 'N/A')) #coordenadas    
        comment = limpiar_dato(propiedad.get('comment', 'N/A'))

        #

        # Prepara los datos en formato delimitado por pipeline
        resultado = f"{url}|{publicationId}|{precio}|{propertyType}|{businessType}|{area}|{areac}|{rooms}|{bathrooms}|{garages}|{city}|{coordinates}|{comment}\n"
        
        return resultado
    
    except requests.exceptions.RequestException as e:
        return f"{url};Error al acceder a la URL: {e}\n"
    except json.JSONDecodeError as e:
        return f"{url};Error al decodificar JSON: {e}\n"

# URLs para extraer datos, se deben colocar los links obtenidos
urls = [
    "https://www.metrocuadrado.com/proyecto/hacienda-san-jose/1614-C0033-05",
    "https://www.metrocuadrado.com/proyecto/reserva-de-la-26/1572-C0046-01"
]
# Archivo de salida
with open("Resultados_metrocuadrado.txt", "w", encoding="utf-8") as archivo:
    for url in urls:
        resultado = obtener_datos(url)
        archivo.write(resultado)  # Escribe el resultado en el archivo
        print(f"Datos de {url} guardados en 'Resultados_metrocuadrado.txt'")
