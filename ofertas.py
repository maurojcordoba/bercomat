from pymongo import MongoClient
import os

MONGO_URI = os.getenv('MONGO_URI')

def procesar():
    client = MongoClient(MONGO_URI)
    db = client.bercomat


    fechas = []
    for fecha in db.productos.distinct("created"):
        fechas.append(fecha)    

    fechas.sort(reverse=True)

    ult_proceso = fechas[0]
    pen_proceso = fechas[1]

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
