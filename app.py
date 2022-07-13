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

client = MongoClient('mongodb+srv://test:sparta@cluster0.a32x0.mongodb.net/?retryWrites=true&w=majority', tlsCAFile=ca)
db = client.dbsparta


@app.route('/post_recipe', methods=['POST'])
def post_recipe():
    bread_receive =  request.form.get('bread')
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

# 토큰을 위한 시크릿키
SECRET_KEY = 'SUBLab'

# 인덱스 삭제
# db.ingredients.drop_indexes()

# 검색을 위한 text 인덱스 생성
# db.ingredients.create_index([('menu', 'text')]) #메뉴
db.ingredients.create_index([('$**', 'text')]) #전체

def menu_rank():
    # 유저가 만든 레시피 중 평점의 평균이 높은 순으로 4위까지만 보여주는 함수
    menu_ranks = list(db.comments.aggregate([{'$group': {'_id': '$menu_id', 'avg_star': {'$avg': '$star'}}}, {'$sort': {'avg_star': -1}}, {'$limit': 4}]))
    return menu_ranks


SECRET_KEY = 'SUBLab'


@app.route('/')
def home():
    menu_ranks = menu_rank()
    menu_name = []
    menu_id = []
    for menu in menu_ranks:
        # 메뉴 아이디에 해당되는 메뉴 정보 가져오기
        m = db.ingredients.find_one({'_id': ObjectId(menu['_id'])})
        menu_name.append(m['menu'])
        menu_id.append(m['_id'])
    token_receive = request.cookies.get('mytoken')
    if token_receive is not None:
        try:
            payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
            login_status = 1
            return render_template('home.html', menu_ranks=menu_ranks, menu_name=menu_name, menu_id=menu_id, login_status=login_status)
        except jwt.ExpiredSignatureError:
            return redirect(url_for("login", msg="로그인 시간이 만료되었습니다.", login_status=login_status))
        except jwt.exceptions.DecodeError:
            return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다.", login_status=login_status))
    else:
        login_status = 0
        return render_template('home.html', menu_ranks=menu_ranks, menu_name=menu_name, menu_id=menu_id, login_status=login_status)

@app.route('/search')
def search():
    menu_receive = request.args.get('menu_give')
    # 전체 속성에서 검색어를 포함하는 메뉴 리스트 반환
    menu_list = list(db.ingredients.find({'$text': {'$search': menu_receive}}))
    menu_star_avg = []
    result = []
    for i in range(len(menu_list)):
        print(menu_list[i]['_id'])
        result = list(db.comments.aggregate([{'$group': {'_id': ObjectId(menu_list[i]['_id']), 'avg_star': {'$avg': '$star'}}}]))
        print(result)
        menu_star_avg.append(result[0]['avg_star'])
        print(menu_star_avg)

    token_receive = request.cookies.get('mytoken')
    msg = ''
    if len(menu_list) != 0:
        menu_list = menu_list
        msg = "검색에 성공했습니다"
    else:
        msg = "검색 결과가 없습니다."
        menu_list = 0

    if token_receive is not None:
        try:
            payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
            login_status = 1
            return render_template('result.html', msg=msg, menu_list=menu_list, login_status=login_status,
                                   menu_ranks=menu_star_avg)
        except jwt.ExpiredSignatureError:
            return redirect(url_for("login", msg="로그인 시간이 만료되었습니다.", menu_list=menu_list, login_status=login_status,
                                   menu_ranks=menu_star_avg))
        except jwt.exceptions.DecodeError:
            return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다.", menu_list=menu_list, login_status=login_status,
                                   menu_ranks=menu_star_avg))
    else:
        login_status = 0
        return render_template('result.html', msg=msg, menu_list=menu_list, login_status=login_status, menu_ranks=menu_star_avg)

@app.route('/detail')
def detail():
    menu_id = request.args.get('menu_id')
    star = request.args.get('avg_star')
    receipe_info = db.ingredients.find_one({"_id": ObjectId(menu_id)})
    print("detail페이지 접속했을 때 레시피 아이디 : "+str(receipe_info['_id']))
    token_receive = request.cookies.get('mytoken')
    id_receive = request.cookies.get('userID')
    if token_receive is not None:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        return render_template('detail.html' ,receipe_info=receipe_info, user_id=id_receive, star=star)
    else:
        return render_template('detail.html', receipe_info=receipe_info, user_id=id_receive, star=star)

@app.route('/comment/create', methods=["POST"])
def add():
    name_receive = request.form['name_give']
    address_receive = request.form['comment_give']
    star_receive = request.form['star_give']
    menuId_receive = request.form['menuId_give']

    doc = {
        'name': name_receive,
        'comment': address_receive,
        'star': star_receive,
        'menu_id' : ObjectId(menuId_receive)
    }
    db.comments.insert_one(doc)

    return jsonify({'msg': '댓글 작성 완료!'})

@app.route("/comment", methods=["GET"])
def comments_get():
    menu_id = request.args.get('menu_id')
    print(menu_id)
    comment_list = list(db.comments.find({'menu_id':ObjectId(menu_id)}, {'_id': False, 'menu_id': False}))
    print(comment_list)
    return jsonify({'comments': comment_list})


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
        return jsonify({'ok': True, 'token': token, 'userID': id_receive})
    else:
        return jsonify({'ok': False, 'message': '아이디 혹은 비밀번호가 일치하지 않습니다.'})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
