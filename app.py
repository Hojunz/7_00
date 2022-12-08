# flask, flask-jwt-extended, pymysql 라이브러리 설치
from flask import Flask, render_template, request, jsonify, redirect, url_for
# local sql 연결
import pymysql
# 유효기간 및 작성 날짜 정보
from datetime import datetime, timedelta
# client 통신 할때 형식 jsonquery
import json
# 토큰 발행
import jwt

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

SECRET_KEY = 'Zoo'


# 특정데이터 테스트
# db = pymysql.connect(host='localhost', user='root', db='flask_test', password='12345678', charset='utf8')
# curs = db.cursor()
#
# email_receive = 'aaaa'
#
# sql = """
# 	SELECT *
# 		FROM users u
# 		WHERE u.email = %s
# 	"""
#
# curs.execute(sql, email_receive)
#
# users_result = curs.fetchall()
# print(users_result[0])
#
# json_str = json.dumps(users_result, indent=4, sort_keys=True, default=str)
# db.commit()
# db.close()

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/', methods=['POST'])
def move_to_mypage():
    token_receive = request.cookies.get('mytoken')

    try:
        jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        return jsonify({'result': 'success'})
    except(jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return jsonify({'result': 'fail', 'msg': '로그인을 먼저 진행해주세요!!'})


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def log_in():
    email_receive = request.form["email_give"]
    password_receive = request.form["password_give"]
    # print(email_receive)
    # print(password_receive)

    db = pymysql.connect(host='localhost', user='root', db='test', password='!', charset='utf8')
    # curs = db.cursor()
    curs = db.cursor(pymysql.cursors.DictCursor)

    sql = """
		SELECT u.user_id, u.email, u.password
		FROM user u
		where u.email = %s
		"""

    curs.execute(sql, email_receive)

    users_result = curs.fetchall()[0]
    print(users_result['user_id'])

    json_str = json.dumps(users_result, indent=4, sort_keys=True, default=str)
    # 딕션너리 형태로 바꿔주기. spartagram 코드 app.py 4번째 줄 쯤..
    db.commit()
    db.close()

    if users_result['password'] != password_receive:
        msg = "비밀번호가 일치하지 않습니다. 다시 로그인해주세요."
        return jsonify({'result': 'fail', 'msg': msg})
    else:
        # 토큰 발행, id, payload, 시크릿키가 필요
        payload = {
            'id': users_result['user_id'],  # user_id 값이 들어가야함
            'email': email_receive,
            'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        # print(token)
        return jsonify({'result': 'success', 'token': token})


@app.route('/signup')
def signup():
    return render_template('signup.html')


@app.route('/users/sign_up', methods=['POST'])
def save_users_info():
    email_receive = request.form['email2_give']
    password_receive = request.form['password_give']
    # password2_receive = request.form['password2_give']
    name_receive = request.form['name_give']

    file = request.files["file_give"]
    print(file)
    extension = file.filename.split('.')[-1]
    today = datetime.now()
    mytime = today.strftime("%Y-%m-%d-%H-%M-%S")
    filename = f'file-{mytime}'
    save_to = f'{filename}.{extension}'
    file.save(f'static/images/{save_to}')
    print(save_to)

    db = pymysql.connect(host='localhost', user='root', db='test', password='!', charset='utf8')
    curs = db.cursor()

    sql = """
		insert into user (email, password, name, regdate, filename)
         values (%s,%s,%s,%s,%s)
		"""

    curs.execute(sql, (email_receive, password_receive, name_receive, mytime, save_to))

    users_result = curs.fetchall()
    # print(users_result[0][1] != password_receive)

    json_str = json.dumps(users_result, indent=4, sort_keys=True, default=str)
    db.commit()
    db.close()

    return jsonify({"result": "success", 'msg': '회원가입 완료!'})


@app.route('/mypage')
def mypage():
    return render_template('mypage.html')


@app.route("/user_info", methods=["GET"])
def user_info_get():
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    target_id = payload['id']

    db = pymysql.connect(host='localhost', user='root', db='test', password='!', charset='utf8')
    curs = db.cursor(pymysql.cursors.DictCursor)

    sql = """
		SELECT *
			FROM user u
			WHERE u.user_id = %s
		"""

    curs.execute(sql, target_id)

    users_result = curs.fetchall()[0]
    print(users_result)

    json_str = json.dumps(users_result, indent=4, sort_keys=True, default=str)
    db.commit()
    db.close()

    return jsonify({'msg': 'GET 연결 완료!', 'user_info': users_result})


@app.route('/user_only', methods=['POST'])
def user_only():
    token_receive = request.cookies.get('mytoken')

    try:
        jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        return jsonify({'result': 'success'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return jsonify({'result': 'fail', 'msg': '로그인을 먼저 진행해주세요!!'})


# ! 게시글 수정 페이지

@app.route('/write_page')
def write_page():
    return render_template('write_page.html')


@app.route('/write_page_update')
def write_page_update():
    return render_template('write_page_update.html')


# ! 게시글 불러오기

@app.route('/posts/list', methods=["GET"])
def get_post():
    db = pymysql.connect(host='localhost', user='root',
                         db='test', password='!', charset='utf8')
    curs = db.cursor()

    sql = """
		SELECT title,content,topic,filename
		FROM post p
		"""

    curs.execute(sql)

    post_list = curs.fetchall()

    db.commit()
    db.close()

    return jsonify({'post_list': post_list})


# ! 게시글 작성

@app.route("/posts/save", methods=["POST"])
def save_post():
    title = request.form['title']
    topic = request.form['topic']
    content = request.form['content']
    file = request.files['file']

    print(request.form)
    extension = file.filename.split('.')[-1]
    today = datetime.now()
    mytime = today.strftime("%Y-%m-%d-%H-%M-%S")
    filename = f'file-{mytime}'
    save_to = f'{filename}.{extension}'
    file.save(f'static/images/{save_to}')

    db = pymysql.connect(host='localhost', user='root',
                         db='test', password='!', charset='utf8')
    curs = db.cursor()

    sql = """
		INSERT INTO post (title,topic,content, filename) VALUES (%s,%s,%s,%s)
		"""

    curs.execute(sql, (title, topic, content, save_to))

    db.commit()
    db.close()

    return jsonify({'msg': '게시글 작성 완료!'})


# ! 게시글 업데이트

@app.route('/updatepost', methods=["PUT"])
def update():
    post_id = request.form['post_id']
    title = request.form['title']
    topic = request.form['topic']
    content = request.form['content']

    db = pymysql.connect(host='localhost', user='root',
                         db='test', password='!', charset='utf8')
    curs = db.cursor()

    sql = """
		UPDATE post SET title = %s, topic = %s, content = %s WHERE post_id = %s
		"""

    curs.execute(sql, (title, topic, content, post_id))

    db.commit()
    db.close()

    return jsonify({'msg': '게시글 수정 완료'})


if __name__ == '__main__':
    app.run('127.0.0.1', port=5000, debug=True)
