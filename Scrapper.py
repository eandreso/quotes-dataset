
#Importación de las librerías necesarias

import requests as rq
from bs4 import BeautifulSoup as bsoup
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import datetime
import argparse
import time
import random

# Analizamos los argumentos de la linea de comandos, incluimos valores por defecto

parser = argparse.ArgumentParser()
parser.add_argument("--ticker", help="Enter corporation ticker symbol", default = 'TEF.MC')
parser.add_argument("--startDate", help="Enter start date of interval YY-MM-DD", default =  str(datetime.date.today()-datetime.timedelta(days = 1825)))
parser.add_argument("--endDate", help="Enter end date of interval YY-MM-DD", default = str(datetime.date.today()))
args = parser.parse_args()

# Variables entrada

ticker = args.ticker
startDate = datetime.datetime.strptime(str(args.startDate), "%Y-%m-%d")
endDate = datetime.datetime.strptime(str(args.endDate),"%Y-%m-%d")

# Fechas en unix timestamp seconds

period1 = int(startDate.timestamp())
period2 = int(endDate.timestamp())

# url

url = "https://finance.yahoo.com/quote/%s/history?period1=%s&period2=%s&interval=1d"%(ticker,period1,period2)

# Lista de user agents

userAgents = [
   #Chrome
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
    #Firefox
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

#Seleccionamos user agent aleatoriamente

userAgent = random.choice(userAgents)

# Componemos cabeceras

headers = {'User-Agent': userAgent}

# Retardo en peticiones, ahora no sería necesario (milisegundos = 0)

milisegundos = 0
time.sleep(milisegundos)

#Se abre una nueva petición a la página con los datos mediante la librería requests y se guarda en la variable page

page = rq.get(url,headers=headers)

#De la petición que se ha realizado y guardado en la variable page, se selecciona solo el contenido y se guarda en la variable soup con la clase BeautifulSoup

soup = bsoup(page.content)

#Se crea una lista vacía y mediante un bucle for, guardamos los títulos de la tabla que se quiere almacenar

tablehead = []

for header in soup.body.thead.tr.children:
    tablehead.append(header.text)

#En este apartado se limpian algunos datos erróneos como el dato nulo encontrado en 'Volume' del día 25/12/2019, que se cambia de '-' a 0. También se modifica el registro que contiene la fecha 17/12/2019 duplicada con un valor "Dividend".

print(soup.body.tbody.find(text='-').find_parent('td'))
codigo = soup.body.tbody.find(text='-').find_parent('td')['data-reactid']
soup.body.tbody.find('td', attrs={'data-reactid':codigo}).string = '0'
print(soup.body.tbody.find('td', attrs={'data-reactid':codigo}))

soup.body.tbody.find(text='Dividend').find_parent('tr').extract()

#Se crea una lista vacía y se vuelcan los datos extraídos en ella.

datos = []
for dato in soup.body.tbody.find_all('td'):
    datos.append(dato.string)

#Se cambia la forma de la lista para que coincida con las columnas volcadas anteriormente en 'tablehead'. Posteriormente se crea un pandas DataFrame con tablehead como columnas y se establece la columna Date como nombre de los índices.

datos = np.reshape(datos, (int(len(datos)/len(tablehead)), len(tablehead)))
datos = pd.DataFrame(datos, columns = tablehead)
datos = datos.set_index('Date', verify_integrity = True)

#En esta parte se deben cambiar las comas en la variable 'Volume', por puntos para que se puedan cambiar a formato numérico con el método pd.to_numeric de pandas.

datos[['Volume']] = datos[['Volume']].replace(to_replace=r',', value='', regex=True)
datos = datos.apply(pd.to_numeric)

# Cambiamos formato de fechas ejemplo Apr 09, 2020 a 2020-4-09
for i in range(len(datos['Date'])):    
    datos['Date'][i]=datetime.datetime.strptime(str(datos['Date'][i]) , '%b %d, %Y').strftime('%Y-%m-%d')
    
#Se exportan los datos en un archivo .CSV

datos.to_csv('TEF-MC.csv')

# Colocamos la fecha en una columna del dataframe

datos.reset_index(inplace=True,drop=False)

# Ordenamos por fecha

datos = datos.sort_values('Date')

# Se crea un gráfico con los datos para mostrar como imagen descriptiva.

fig = go.Figure(data=go.Ohlc(x=datos['Date'], 
                             open=datos['Open'],
                             high=datos['High'],
                             low=datos['Low'],
                             close=datos['Close*']))
fig.update(layout_xaxis_rangeslider_visible=False)

# Añadimos títulos del gráfico

fig.update_layout(title=ticker, yaxis_title='Cotización')

# Mostramos gráfico OHLC (Open, high, low, close)

fig.show()
