from bs4 import BeautifulSoup
from pymongo import MongoClient
import requests
import json
import time
import random
from datetime import date,datetime

MONGO_URI = 'mongodb+srv://usrBercomat:EYcDusQq8pKLhBKX@cluster0.2ea9d.mongodb.net/bercomat?retryWrites=true&w=majority'

client = MongoClient(MONGO_URI)
db = client['bercomat']
col_productos = db['productos']

# Abro archivo de urls
f = open("src/data.txt", "rt")
lista_urls = f.readlines()
f.close()

# Fecha/Hora de proceso
#created = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
created = datetime.now()

for x in lista_urls:
    url = x.rstrip('\n') + '?page='
    #url = 'https://www.familiabercomat.com/banos/?page='
    print(url)

    #lista completa
    lista = []

    try:
        # Ultima pagina
        cookies_dict = {"carea": "S08OlRPNuMSA/Z9yFRkYEogl1LeV7xoGny+7caw/c13cXpVCO4O+HOIC5yUtbZ/f"}
        page = requests.get(url + "1",cookies=cookies_dict)
        soup = BeautifulSoup(page.content, 'html.parser')
        paginacion = soup.find('ul', class_ = 'pager-list reset')

        list_li = paginacion.find_all('li')
        for li in list_li:pass
        last_page = int(li.text)
        
        # Recorro las paginas
        for x in range(1, last_page+1):
            page = requests.get(url+str(x),cookies=cookies_dict)
            soup = BeautifulSoup(page.content, 'html.parser')
            productos = soup.find_all('div', class_ = 'l-products-item')

            for producto in productos:    
                # data
                info = producto.find('div', attrs={"class":"product-tile"})    
                data = json.loads((info['data-tracking-data']))

                # thumbnail
                thumbnail = producto.find('span', attrs={"class":"thumbnail"})    
                data['thunbnail'] = thumbnail.img['data-src']    

                # stock
                stock = producto.find('span', class_="stock-indication").text.strip()
                data['stock'] = stock

                # link
                link = producto.find('a', class_="hyp-thumbnail")
                data['link'] = link['href']

                # created
                data['created'] = created

                lista.append(data)           
            
            time.sleep(random.uniform(3.0,4.0))
    except Exception:
        print("Error en pagina {0}! Continua con la siguiente.".format(url))
        pass

    # Si la lista no esta vacia, inserto en base
    if lista:
        col_productos.insert_many(lista)
