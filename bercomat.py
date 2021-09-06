from bs4 import BeautifulSoup
from pymongo import MongoClient
import requests
import json
import time
import random
from datetime import datetime,timedelta

MONGO_URI = 'mongodb+srv://usrBercomat:EYcDusQq8pKLhBKX@cluster0.2ea9d.mongodb.net/bercomat?retryWrites=true&w=majority'

client = MongoClient(MONGO_URI)
db = client['bercomat']
col_productos = db['productos']

# Abro archivo de urls
f = open("data.txt", "rt")
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
            
            time.sleep(random.uniform(1.0,2.0))
    except Exception:
        print("Error en pagina {0}! Continua con la siguiente.".format(url))
        pass

    # Si la lista no esta vacia, inserto en base
    if lista:
        col_productos.insert_many(lista)

# Ofertas

fechas = db.productos.distinct("created")
fechas.sort(reverse=True)
ult_proceso = fechas[0]


today = datetime.today().replace(hour=0,minute=0,second=0)
yesterday = today - timedelta(days=1)

fechas =  db.productos.distinct("created", {"created": {"$lt": yesterday}})
fechas.sort(reverse=True)
pen_proceso = fechas[0]

print(ult_proceso,pen_proceso)

### Genero nueva collections con los ultimos productos procesados ###

result = db.productos.aggregate([{"$match": { "created": { "$eq": ult_proceso },"stock": {"$ne" : "Agotado"}}},
    {"$out": "productos_hoy"}])
    
### Genero nueva collections con los productos anteriormente procesados  ###

result = db.productos.aggregate([{"$match": { "created": { "$eq": pen_proceso },"stock": {"$ne" : "Agotado"}}},
    {"$out": "productos_antes"}])

query = [
{"$project":{"_id":0}},    
{    "$lookup": {
        "from": "productos_antes",
        "let": {"idHoy": "$id", "precioHoy": "$price" },        
        "pipeline": [
            { "$match": 
                { "$expr":
                    { "$and":
                        [{"$eq":["$id","$$idHoy"] },{"$gt":["$price", "$$precioHoy"]}]                    
                    }
                }
            },
            { "$project": { "_id":0,"category":0,"thunbnail":0,"link": 0,"list":0,"name":0}}
        ],        
        "as": "antes"
    }    
},
{"$unwind": "$antes"},
{"$addFields":{ "diff": {"$subtract": ["$antes.price","$price"]}}},
{"$out": "productos_oferta"}
]

result = db.productos_hoy.aggregate(query)

# Genera Historial
lista = []
for oferta in db.productos_oferta.find({},{"_id": 0}):
    lista.append(oferta)

if lista:
        db.producto_oferta_hist.insert_many(lista)
