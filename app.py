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


# <-- bs4크롤링 -->
headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
data = requests.get('https://www.subway.co.kr/utilizationSubway',headers=headers)

soup = BeautifulSoup(data.text, 'html.parser')

trs = soup.select('#content > div > div.pd_list_wrapper > ul')

#li:nth-child(4) > div.img > img

for tr in trs:

    menuimg = tr.select_one({"img":'<img onerror="this.src='/images/common/noneImage.jpg'" src="/upload/menu/터키베이컨아보카도_20220426035102168.png" alt="터키 베이컨 아보카도">',"menu":터키 베이컨 아보카도})
    breadimg = tr.select_one('li:nth-child(2) > div > img')['src']
    vegeimg = tr.select_one('li:nth-child(4) > div > img')['src']
    souceimg = tr.select_one('li:nth-child(4) > div > img')['src']

    doc = {
        'menuimg':menuimg,
        'breadimg':breadimg,
        'vegeimg':vegeimg,
        'souceimg':souceimg
    }
    db.images.insert_one(doc)




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
