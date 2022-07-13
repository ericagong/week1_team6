from pymongo import MongoClient
import certifi
from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup

ca = certifi.where()

client = MongoClient('mongodb+srv://test:sparta@cluster0.a32x0.mongodb.net/?retryWrites=true&w=majority', tlsCAFile=ca)
db = client.dbsparta

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb+srv://test:sparta@cluster0.a32x0.mongodb.net/?retryWrites=true&w=majority"


#
# headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
# data = requests.get('https://www.subway.co.kr/menuList/sandwich',headers=headers)
# soup = BeautifulSoup(data.text, 'html.parser')
#content > div > div.pd_list_wrapper > ul > li:nth-child(1) > div.img > img

def get_urls():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get('https://www.subway.co.kr/menuList/sandwich', headers=headers)
    soup = BeautifulSoup(data.text, 'html.parser')
    trs = soup.select('#content > div > div.pd_list_wrapper > ul')
    urls = []
    for tr in trs:
        a = tr.select_one('li:nth-child(1) > div.img > img')
        if a is not None:
            base_url = 'https://www.subway.co.kr/'
            url = base_url + a['src']
            urls.append(url)

    return urls

def insert_img(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get(url, headers=headers)

    soup = BeautifulSoup(data.text, 'html.parser')

    name = soup.select_one('#content > div > div.pd_list_wrapper > ul > li:nth-child(1) > strong')
    img_url = soup.select_one('#content > div > div.pd_list_wrapper > ul > li:nth-child(1) > div.img > img')['src']
    cal = soup.select_one(
        '#content > div > div.pd_list_wrapper > ul > li:nth-child(1) > span.cal').text

    doc = {
        'name': name,
        'img_url': img_url,
        'cal': cal,
        'url': url
    }

    db.ingeredients.insert_one(doc)
    print('완료!', name)

# @app.route('/api/list', methods=['GET'])
# def show_stars():
#     movie_star = list(db.mystar.find({},{'_id':False}).sort('like',-1))
#     return jsonify({'movie_stars': movie_star})

@app.route("/recipe/ingredients", methods=["get"])
def ingredients_get():
    all_ingredients = list(db.ingredients.find({}, {'_id' : False}))
    # print(all_ingredients)
    # if len(all_ingredients) == 0:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    url = 'https://www.subway.co.kr/menuList/sandwich'
    data = requests.get(url, headers=headers)
    soup = BeautifulSoup(data.text, 'html.parser')
    images = soup.select('#content > div > div.pd_list_wrapper > ul > li > div.img > img')
    print(len(images))
    for i in images:
        print('https://www.subway.co.kr' + str(i['src']))
    return jsonify({'ok': True})


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
    # recipes = mongo.db.recipes
    post = {
        'bread': bread_receive,
        'cheese': cheese_receive,
        'topping': topping_receive,
        'vege': vege_receive,
        'souce': souce_receive,
        'menu': menu_receive,
        'name': name_receive
    }
    db.recipe.insert_one(post)
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
