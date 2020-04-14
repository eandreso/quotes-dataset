import requests as rq
from zipfile import ZipFile
from selenium import webdriver
import os
from bs4 import BeautifulSoup as bsoup
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import datetime
import argparse
import time
import random
import platform

# Analizamos los argumentos de la linea de comandos, incluimos valores por defecto

parser = argparse.ArgumentParser()
parser.add_argument("--ticker", help="Enter corporation ticker symbol", default='TEF.MC')
parser.add_argument("--startDate", help="Enter start date of interval YY-MM-DD",
                    default=str(datetime.date.today() - datetime.timedelta(days=1825)))
parser.add_argument("--endDate", help="Enter end date of interval YY-MM-DD", default=str(datetime.date.today()))
args = parser.parse_args()

# Se asignan los valores de entrada requeridos

ticker = args.ticker
startDate = datetime.datetime.strptime(str(args.startDate), "%Y-%m-%d")
endDate = datetime.datetime.strptime(str(args.endDate), "%Y-%m-%d")

# Se transforman las variables de fechas para que se puedan utilizar en la url, ya que Yahoo aplica los filtros mediante este formato de Unix

period1 = int(startDate.timestamp())
period2 = int(endDate.timestamp())

# Configuración de la url que contiene los datos para que se filtre por empresa (ticker) y fechas deseadas (startDate y endDate)

url = "https://finance.yahoo.com/quote/%s/history?period1=%s&period2=%s&interval=1d" % (ticker, period1, period2)

# Lista de user agents posibles para ir rotando a la hora de realizar las consultas

userAgents = [
    # Chrome
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (Windows NT 5.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
    # Firefox
    'Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1)',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (Windows NT 6.2; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)',
    'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)',
    'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729)'
]

# Seleccionamos user agent aleatoriamente

userAgent = random.choice(userAgents)

# Se descarga el driver necesario para trabajar con Selenium y Google Chrome. El if-statement sirve para discriminar el driver que se debe descargar en función del sistema operativo

print(platform.system())
print(platform.release())

if platform.system() == "Windows":
    driver = rq.get('http://chromedriver.storage.googleapis.com/80.0.3987.106/chromedriver_win32.zip')

    with open('chrome_driver.zip', 'wb') as d:
        d.write(driver.content)

    with ZipFile('chrome_driver.zip', 'r') as zip:
        zip.extractall()

elif platform.system() == "Linux":
    os.system('sudo apt-get install chromium-browser')
    driver = rq.get('http://chromedriver.storage.googleapis.com/80.0.3987.106/chromedriver_linux64.zip')

    with open('chromedriver_linux64.zip', 'wb') as d:
        d.write(driver.content)

    with ZipFile('chromedriver_linux64.zip', 'r') as zip:
        zip.extractall()
    print("descomprimido")
    os.system('chmod +x chromedriver')
    os.system('sudo mv -f chromedriver /usr/local/share/chromedriver')
    os.system('sudo ln -s /usr/local/share/chromedriver /usr/local/bin/chromedriver')
    os.system('sudo ln -s /usr/local/share/chromedriver /usr/bin/chromedriver')

# Se eligen las opciones que se requieren para el driver de Selenium. Headless sirve para ocultar el driver y que no se vea mientras navega por la web. 
# Los 2 siguientes sirven para evitar mensajes extra en la ejecución y el último es para establecer el user-agent

options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')
options.add_argument('user-agent=%s' % (userAgent))

# Creamos objeto webdriver (selenium), que es el que realiza la petición con las opciones anteriormente establecidas

driver = webdriver.Chrome(options=options)

# Se aplica el retardo en la petición de 1 segundo. Se puede configurar para mayor o menor tiempo
seconds = 1
driver.implicitly_wait(seconds)

# Se abre una nueva petición a la página deseada

driver.get(url)

# Ahora el driver de selenium se configura para hacer click en el botón de aceptar de un mensaje de información que aparece

agent = driver.execute_script("return navigator.userAgent")
print(agent)

driver.find_element_by_xpath('//button[text()="Acepto"]').click()

# Se establecen 2 variables para comparar los archivos HTMLs de la página que se usarán en el bucle

html1 = driver.page_source
html2 = 0

# Se configura el final de la página al que se quiere llegar

end = driver.find_element_by_xpath('//span[contains(text(), "*Close price adjusted for splits.")]')

# Leemos la página hasta llegar al final de la tabla (ScrollDown) indefinidamente mientras los archivos HTMLs no coincidan.
# Esto se ha hecho así porque siempre que se pueda hacer ScrollDown, el HTML de la página cambiará con respecto al antrior.
# Así, el bucle termina cuando los documentos HTML anterior al ScrollDown y posterior coincidan, de forman que se habría llegado al final de la página

while html1 != html2:
    html1 = driver.page_source
    time.sleep(2)
    driver.execute_script('arguments[0].scrollIntoView(true);', end)
    html2 = driver.page_source

# Se asigna el documento HTML traducido por Beautifulsoup a la variable que se requiere y se cierra el driver de Selenium.
# Se aplica un retardo entre acciones para que no haya problemas para guardar los datos, ya que si el driver se cierra antes de que se termine de extraer los datos,
# probablemente dará problemas

soup = bsoup(html2, features='lxml')

driver.implicitly_wait(seconds)

driver.close()

# Una vez que el driver se ha cerrado, se procede a eliminar los archivos del driver según el sistema operativo en el que se esté ejecutando

if platform.system() == "Windows":
    os.system('TASKKILL /F /IM chromedriver.exe')

if platform.system() == "Windows":
    time.sleep(2)
    os.remove('chromedriver.exe')
    os.remove('chrome_driver.zip')

# Se crea una lista vacía y mediante un bucle for, se guardan los títulos de la tabla que se quiere almacenar

tablehead = []

for header in soup.body.thead.tr.children:
    tablehead.append(header.text)

# En este apartado se limpian algunos datos erróneos como el dato nulo encontrado en 'Volume' del día 25/12/2019, que se cambia de '-' a 0.
# También se modifica el registro que contiene la fecha 17/12/2019 duplicada con un valor "Dividend".

if len(soup.body.tbody.find_all(text='-')) > 0:
    for dato in soup.body.tbody.find_all(text='-'):
        codigo = dato.find_parent('td')['data-reactid']
        soup.body.tbody.find('td', attrs={'data-reactid': codigo}).string = '0'

if len(soup.body.tbody.find_all(text='Dividend')) > 0:
    for registro in soup.body.tbody.find_all(text='Dividend'):
        registro.find_parent('tr').extract()

# Se crea una lista vacía y se vuelcan los datos extraídos en ella. Cada dato está unido a la etiqueta td (table data) y pueden contener tanto fechas como cotizaciones

datos = []
for dato in soup.body.tbody.find_all('td'):
    datos.append(dato.string)

# Se cambia la forma de la lista para que coincida con las columnas volcadas anteriormente en 'tablehead'.
# Posteriormente se crea un pandas DataFrame con tablehead como columnas y se establece la columna Date como nombre de los índices.

datos = np.reshape(datos, (int(len(datos) / len(tablehead)), len(tablehead)))
datos = pd.DataFrame(datos, columns=tablehead)

# Se cambia formato de fechas ejemplo Apr 09, 2020 a 2020-4-09

for i in range(len(datos['Date'])):
    datos['Date'][i] = datetime.datetime.strptime(str(datos['Date'][i]), '%b %d, %Y').strftime('%Y-%m-%d')

datos = datos.set_index('Date', verify_integrity=True)

# En esta parte se deben cambiar las comas en la variable 'Volume', por puntos para poder transofrmar el formato numérico con el método pd.to_numeric de pandas.

datos = datos.replace(to_replace=r',', value='', regex=True)

datos = datos.apply(pd.to_numeric)

# Se exportan los datos en un archivo .CSV

datos.to_csv(ticker + '.csv')

# Se coloca la fecha en una columna del dataframe para poder realizar el gráfico

datos.reset_index(inplace=True, drop=False)

# Se ordena por fecha

datos = datos.sort_values('Date')

# Se crea un gráfico con los datos para mostrar como imagen descriptiva.

fig = go.Figure(data=go.Ohlc(x=datos['Date'],
                             open=datos['Open'],
                             high=datos['High'],
                             low=datos['Low'],
                             close=datos['Close*']))
fig.update(layout_xaxis_rangeslider_visible=False)

# Se añaden los títulos del gráfico

fig.update_layout(title=ticker, yaxis_title='Cotización')

# Se graba el gráfico html

fig.write_html(ticker + '.html')
