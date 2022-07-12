from pymongo import MongoClient
import certifi
from flask import Flask, render_template, url_for, request, jsonify
from flask_pymongo import PyMongo
from bs4 import BeautifulSoup
import requests

ca = certifi.where()

client = MongoClient('mongodb+srv://test:sparta@cluster0.a32x0.mongodb.net/?retryWrites=true&w=majority', tlsCAFile=ca)
db = client.dbsparta

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb+srv://test:sparta@cluster0.a32x0.mongodb.net/?retryWrites=true&w=majority"
mongo = PyMongo(app)





@app.route('/post_recipe', methods=['POST'])
def post_recipe():
    bread_receive = request.form.get('bread')
    cheese_receive = request.form.get('cheese')
    topping_receive = request.form.get("topping")
    vege_receive = request.form.get('vege')
    souce_receive = request.form.get('souce')
    menu_receive = request.form.get('menu')
    name_receive = request.form.get('name')
    print(bread_receive, cheese_receive, topping_receive, vege_receive, souce_receive, menu_receive)
    # ingredients = mongo.db.ingredients
    post = {
        'bread': bread_receive,
        'cheese': cheese_receive,
        'topping': topping_receive,
        'vege': vege_receive,
        'souce': souce_receive,
        'menu': menu_receive,
        'name': name_receive
    }
    db.ingredients.insert_one(post)
    # x = ingredients.insert_one(post)
    # print(x.inserted_id)
    # return redirect(url_for("detail", idx=x.inserted_id))
    return jsonify({'name': name_receive+"을 등록하였습니다"})


@app.route('/recipe', methods=['GET'])
def recipe():
    return render_template('recipe.html')

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/login')
def login():
    return render_template('login.html')

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
