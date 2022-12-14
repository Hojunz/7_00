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
# 비밀번호 암호화.
import hashlib

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

SECRET_KEY = 'Zoo'


@app.route('/')
def home():
    return render_template('index.html')

# 마이페이지 갈 때 유효성 검사


@app.route('/', methods=['POST'])
def move_to_mypage():
    token_receive = request.cookies.get('mytoken')

    try:
        jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        return jsonify({'result': 'success'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return jsonify({'result': 'fail', 'msg': '로그인을 먼저 진행해주세요!!'})


@app.route('/login')
def login():
    return render_template('login.html')

# 로그인


@app.route('/login', methods=['POST'])
def log_in():
    email_receive = request.form["email_give"]
    password_receive = request.form["password_give"]
    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    print(pw_hash)

    db = pymysql.connect(host='localhost', user='root',
                         db='test', password='0000', charset='utf8')
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
    db.commit()
    db.close()

    if users_result['password'] != pw_hash:
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
        return jsonify({'result': 'success', 'token': token})


@app.route('/signup')
def signup():
    return render_template('signup.html')

# 회원가입


@app.route('/users/sign_up', methods=['POST'])
def save_users_info():
    email_receive = request.form['email2_give']
    password_receive = request.form['password_give']
    password_hash = hashlib.sha256(
        password_receive.encode('utf-8')).hexdigest()
    name_receive = request.form['name_give']

    file = request.files["file_give"]
    extension = file.filename.split('.')[-1]
    today = datetime.now()
    mytime = today.strftime("%Y-%m-%d-%H-%M-%S")
    filename = f'file-{mytime}'
    save_to = f'{filename}.{extension}'
    file.save(f'static/images/{save_to}')

    db = pymysql.connect(host='localhost', user='root',
                         db='test', password='0000', charset='utf8')

    curs = db.cursor()

    sql = """
		insert into user (email, password, name, regdate, filename)
         values (%s,%s,%s,%s,%s)
		"""

    curs.execute(sql, (email_receive, password_hash,
                 name_receive, mytime, save_to))

    users_result = curs.fetchall()

    json_str = json.dumps(users_result, indent=4, sort_keys=True, default=str)
    db.commit()
    db.close()

    return jsonify({"result": "success", 'msg': '회원가입 완료!'})


@app.route('/mypage')
def mypage():
    return render_template('mypage.html')


# 마이페이지
@app.route("/users/info", methods=["GET"])
def user_info_get():
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    target_id = payload['id']

    db = pymysql.connect(host='localhost', user='root',
                         db='test', password='0000', charset='utf8')
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

# 마이페이지 수정


@app.route('/users/info/edit', methods=['PUT'])
def edit_done():
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    target_id = payload['id']

    email_receive = request.form['email_edit_give']
    password_receive = request.form['password_edit_give']
    name_receive = request.form['name_edit_give']

    file = request.files["file_edit_give"]
    extension = file.filename.split('.')[-1]
    today = datetime.now()
    mytime = today.strftime("%Y-%m-%d-%H-%M-%S")
    filename = f'file-{mytime}'
    save_to = f'{filename}.{extension}'
    file.save(f'static/images/{save_to}')

    db = pymysql.connect(host='localhost', user='root',
                         db='test', password='0000', charset='utf8')
    curs = db.cursor()

    sql = """
         UPDATE
                user
            SET
                email = %s,
                password = %s,
                name = %s,
                filename = %s
            WHERE
                user_id = %s;
		"""

    curs.execute(sql, (email_receive, password_receive,
                 name_receive, save_to, target_id))

    users_result = curs.fetchall()

    db.commit()
    db.close()

    return jsonify({"result": "success", 'msg': '마이페이지 정보 수정 완료!'})

# 유효성 검사


@app.route('/user_only', methods=['POST'])
def user_only():
    token_receive = request.cookies.get('mytoken')

    try:
        jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        return jsonify({'result': 'success'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return jsonify({'result': 'fail', 'msg': '권한이 없습니다'})


# 게시글 수정 페이지

@app.route('/posts')
def write_page():
    return render_template('write_page.html')


@app.route('/posts/update/<id>')
def write_page_update(id):
    print(id)
    return render_template('write_page_update.html', id=id)


# 게시글 불러오기

@app.route('/posts/list', methods=["GET"])
def get_post():
    db = pymysql.connect(host='localhost', user='root',
                         db='test', password='0000', charset='utf8')
    curs = db.cursor()

    sql = """
		SELECT title,content,topic,p.filename,post_id,name,reg_date FROM post p 
        LEFT JOIN USER u ON u.user_id = p.user_id;
		"""

    curs.execute(sql)

    post_list = curs.fetchall()

    db.commit()
    db.close()

    return jsonify({'post_list': post_list})


# 게시글 작성

@app.route("/posts/save", methods=["POST"])
def save_post():
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    target_id = payload['id']

    title = request.form['title']
    topic = request.form['topic']
    content = request.form['content']
    file = request.files['file']
    extension = file.filename.split('.')[-1]
    today = datetime.now()
    mytime = today.strftime("%Y-%m-%d-%H-%M-%S")
    filename = f'file-{mytime}'
    save_to = f'{filename}.{extension}'
    file.save(f'static/images/{save_to}')

    db = pymysql.connect(host='localhost', user='root',
                         db='test', password='0000', charset='utf8')

    curs = db.cursor()

    sql = """
		INSERT INTO post (title,topic,content, filename, user_id) VALUES (%s,%s,%s,%s,%s)
		"""

    curs.execute(sql, (title, topic, content, save_to, target_id))

    db.commit()
    db.close()

    return jsonify({'msg': '게시글 작성 완료!'})


# 게시글 업데이트

@app.route('/posts/update', methods=["PUT"])
def update_post():
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    target_id = payload['id']

    title_receive = request.form['title_give']
    topic_receive = request.form['topic_give']
    content_receive = request.form['content_give']
    post_id_receive = request.form['post_id_give']
    file = request.files['file_give']
    extension = file.filename.split('.')[-1]
    today = datetime.now()
    mytime = today.strftime("%Y-%m-%d-%H-%M-%S")
    filename = f'file-{mytime}'
    save_to = f'{filename}.{extension}'
    file.save(f'static/images/{save_to}')

    db = pymysql.connect(host='localhost', user='root',
                         db='test', password='0000', charset='utf8')
    curs = db.cursor()

    sql = """
		UPDATE post SET title = %s, topic = %s, content = %s, filename = %s WHERE post_id = %s AND user_id = %s
		"""

    curs.execute(sql, (title_receive, topic_receive,
                 content_receive, save_to, post_id_receive, target_id))

    db.commit()
    db.close()

    return jsonify({"result": "success", 'msg': '게시글 수정 완료!'})


# 게시글 삭제

@app.route('/posts/delete', methods=["DELETE"])
def delete():
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    target_id = payload['id']

    post_id = request.form['post_id']
    print(request.form['post_id'])
    db = pymysql.connect(host='localhost', user='root',
                         db='test', password='0000', charset='utf8')
    curs = db.cursor()

    sql = """
		DELETE FROM post WHERE post_id = %s and user_id = %s
		"""

    curs.execute(sql, (post_id, target_id))

    db.commit()
    db.close()

    return jsonify({'msg': '게시글 삭제 완료!'})


if __name__ == '__main__':
    app.run('127.0.0.1', port=5000, debug=True)
