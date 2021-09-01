from flask import Flask, render_template,request
from flask_pymongo import PyMongo
import pymongo

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://localhost:27017/bercomat'
mongo = PyMongo(app)

url_base = "https://www.familiabercomat.com"

@app.route('/')
def home():
    try:
        ofertas = mongo.db.productos_oferta.find({}).sort("diff", -1)
        data = {
            'title': 'Home',
            'url_base': url_base,
            'ofertas': ofertas
        }
        return render_template('home.html', data=data)
    except pymongo.errors.ServerSelectionTimeoutError as e:
        return "Error en Base de Datos %s" % e

@app.route('/product/<id>')
def product(id):
    try:
        producto = mongo.db.productos.find_one({"id": id})
        historial = mongo.db.productos.find({"id":id},{"price":1, "created":1}).sort("created", -1).limit(10)

        data_chart = []
        labels = []
        for h in historial:        
            data_chart.append(h['price'])
            labels.append(h['created'].strftime('%Y-%m-%d'))
        
        data_chart.reverse()
        labels.reverse()

        data = {
            'title': 'Product',
            'producto': producto,
            'labels': labels,
            'data_chart': data_chart
        }
        return render_template('product.html',data=data)
    except pymongo.errors.ServerSelectionTimeoutError as e:
        return "Error en Base de Datos %s" % e

@app.route('/about')
def about():
    return render_template('about.html')

def query_string():
    print(request)
    print(request.args)
    print(request.args.get('p1'))
    return 'Ok'

def pagina_no_encontrada(error):    
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.add_url_rule('/query_string',view_func=query_string)

    app.register_error_handler(404,pagina_no_encontrada)

    app.run(debug=True, port=5000)