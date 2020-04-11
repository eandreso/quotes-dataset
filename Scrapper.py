
#Importación de las librerías necesarias

import requests as rq
from bs4 import BeautifulSoup as bsoup
import numpy as np
import pandas as pd
import plotly.graph_objects as go

#Se abre una nueva petición a la página con los datos mediante la librería requests y se guarda en la variable page

page = rq.get('https://finance.yahoo.com/quote/TEF.MC/history?period1=1428537600&period2=1586390400&interval=1d')

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

#Se exportan los datos en un archivo .CSV

datos.to_csv('TEF-MC.csv')

#Se crea un gráfico con los datos para mostrar como imagen descriptiva.

fig = go.Figure(data=go.Ohlc(x=datos.index,
                open=datos['Open'],
                high=datos['High'],
                low=datos['Low'],
                close=datos['Close*']))
fig.update(layout_xaxis_rangeslider_visible=False)

# Adding customized text
fig.update_layout(
    title='TEF.MC',
    yaxis_title='Cotización')

# Show OHLC Chart
fig.show()