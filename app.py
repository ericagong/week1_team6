from pymongo import MongoClient
import certifi
from flask import Flask, render_template, request, jsonify, redirect, url_for

app = Flask(__name__)

ca = certifi.where()
client = MongoClient('mongodb+srv://test:sparta@cluster0.a32x0.mongodb.net/cluster0?retryWrites=true&w=majority',
                     tlsCAFile=ca)
db = client.dbsparta

# 검색을 위한 text 인덱스 생성
db.ingredients.create_index([('menu', 'text')]) #메뉴
# db.ingredients.create_index([('$**', 'text')]) #전체

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/search')
def search():
    menu_receive = request.args.get('menu_give')
    menu_list = list(db.ingredients.find({'$text': {'$search': menu_receive}}, {'_id': False}))
    print(menu_list)
    return render_template('result.html', menu_list=menu_list)

@app.route('/result')
def result_page():
    return render_template('result.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/login')
def login():
    return render_template('login.html')

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
