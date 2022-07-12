from pymongo import MongoClient
import certifi
from flask import Flask, render_template, request, jsonify, redirect, url_for
from bson.objectid import ObjectId
import datetime
from datetime import datetime, timedelta
import hashlib
import jwt

app = Flask(__name__)

ca = certifi.where()
client = MongoClient('mongodb+srv://test:sparta@cluster0.a32x0.mongodb.net/cluster0?retryWrites=true&w=majority',
                     tlsCAFile=ca)
db = client.dbsparta

# 토큰을 위한 시크릿키
SECRET_KEY = 'SUBLab'

# 인덱스 삭제
# db.ingredients.drop_indexes()

# 검색을 위한 text 인덱스 생성
# db.ingredients.create_index([('menu', 'text')]) #메뉴
db.ingredients.create_index([('$**', 'text')]) #전체

def menu_rank():
    # 유저가 만든 레시피 중 평점의 평균이 높은 순으로 5위까지만 보여주는 함수
    menu_ranks = list(db.recepies.aggregate([{'$group': {'_id': '$menu_id', 'avg_star': {'$avg': '$star'}}}, {'$sort': {'avg_star': -1}}, {'$limit': 5}]))
    return menu_ranks


# 코드에 참고하세요!
# @app.route('/')
# def home():
#     token_receive = request.cookies.get('mytoken')
#     try:
#         payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
#
#         return render_template('index.html')
#     except jwt.ExpiredSignatureError:
#         return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
#     except jwt.exceptions.DecodeError:
#         return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


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

@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/sign-up/check-id', methods=['POST'])
# check_id() :: id가 동일한 다른 사용자가 DB에 존재하지 않으면 참, 아니면 거짓을 반환.
def check_id():
    id_receive = request.form['id_give']
    exists = bool(db.users.find_one({"id": id_receive}))
    return jsonify({'ok': not exists})


@app.route('/sign-up', methods=['POST'])
def sign_up():
    id_receive = request.form['id_give']
    password_receive = request.form['password_give']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    user = {
        "id": id_receive,
        "password": password_hash,
    }
    db.users.insert_one(user)
    return jsonify({'message': '회원가입 되었습니다.'})


@app.route('/sign-in', methods=['POST'])
def sign_in():
    id_receive = request.form['id_give']
    password_receive = request.form['password_give']
    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    user = db.users.find_one({'id': id_receive, 'password': pw_hash})
    if user is not None:
        payload = {
            'id': id_receive,
            'exp': datetime.utcnow() + timedelta(days=1)  # 로그인 24시간 유지
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')
        return jsonify({'ok': True, 'token': token})
    else:
        return jsonify({'ok': False, 'message': '아이디 혹은 비밀번호가 일치하지 않습니다.'})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
