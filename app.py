from pymongo import MongoClient
import certifi
from flask import Flask, render_template, request, jsonify, redirect, url_for
from bson.objectid import ObjectId

app = Flask(__name__)

ca = certifi.where()
client = MongoClient('mongodb+srv://test:sparta@cluster0.a32x0.mongodb.net/cluster0?retryWrites=true&w=majority',
                     tlsCAFile=ca)
db = client.dbsparta

# 인덱스 삭제
# db.ingredients.drop_indexes()

# 검색을 위한 text 인덱스 생성
# db.ingredients.create_index([('menu', 'text')]) #메뉴
db.ingredients.create_index([('$**', 'text')]) #전체

def menu_rank():
    # 유저가 만든 레시피 중 평점의 평균이 높은 순으로 5위까지만 보여주는 함수
    menu_ranks = list(db.recepies.aggregate([{'$group': {'_id': '$menu_id', 'avg_star': {'$avg': '$star'}}}, {'$sort': {'avg_star': -1}}, {'$limit': 5}]))
    return menu_ranks

@app.route('/')
def home():
    menu_ranks = menu_rank()
    menu_name = []
    for menu in menu_ranks:
        m = db.ingredients.find_one({'_id': ObjectId(menu['_id'])})
        print(m['menu'])
        menu_name.append(m['menu'])
    return render_template('home.html', menu_ranks=menu_ranks, menu_name=menu_name)
    # return render_template('home.html', menu_ranks=menu_ranks)

@app.route('/search')
def search():
    menu_receive = request.args.get('menu_give')
    # 전체 속성에서 검색어를 포함하는 메뉴 리스트 반환
    menu_list = list(db.ingredients.find({'$text': {'$search': menu_receive}}, {'_id': False}))
    print(menu_list)
    return render_template('result.html', menu_list=menu_list)

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/login')
def login():
    return render_template('login.html')

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
