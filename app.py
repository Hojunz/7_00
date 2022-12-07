# flask, flask-jwt-extended, pymysql 라이브러리 설치
from flask import Flask, render_template, request, jsonify, redirect, url_for
import pymysql
from datetime import datetime, timedelta
import json
import jwt

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

SECRET_KEY = 'Zoo'

# 메인 페이지


@app.route('/')
def home():
    return render_template('index.html')

# 로그인 페이지


@app.route('/login')
def login():
    return render_template('login.html')

# 로그인


@app.route('/log_in', methods=['POST'])
def log_in():
    email_receive = request.form["email_give"]
    password_receive = request.form["password_give"]

    db = pymysql.connect(host='localhost', user='root',
                         db='test', password='0000', charset='utf8')
    curs = db.cursor()

    sql = """
		SELECT *
		FROM users u
		where u.email = %s
		"""

    curs.execute(sql, email_receive)

    users_result = curs.fetchall()

    # json_str = json.dumps(users_result, indent=4, sort_keys=True, default=str)
    db.commit()
    db.close()

    if users_result[0][2] != password_receive:
        msg = "비밀번호가 일치하지 않습니다. 다시 로그인해주세요."
        return jsonify({'result': 'fail', 'msg': msg})

    else:
        # 토큰 발행, id, payload, 시크릿키가 필요
        payload = {
            'id': email_receive,
            'exp': datetime.utcnow() + timedelta(seconds=60*60*24)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        return jsonify({'result': 'success', 'token': token})


# 게시판 작성 페이지


@app.route('/write_page')
def write_page():
    return render_template('write_page.html')

# 게시글 작성(로그인한 사람만 접근 가능)


@app.route('/user_only', methods=['POST'])
def user_only():
    token_receive = request.cookies.get('mytoken')
    print(token_receive)

    try:
        payload = jwt.decode(token_receive, SECRET_KEY,
                             algorithms=['HS256'])
        msg = payload['id'] + '님은 게시물을 작성하실 수 있습니다.'
        return jsonify({'msg': msg})
        # return redirect("/templates/write_page.html")
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return jsonify({'msg': 'User Only Access!!!'})

# 게시글 불러오기


@app.route('/getpost')
def get_post():
    db = pymysql.connect(host='localhost', user='root',
                         db='test', password='0000', charset='utf8')
    curs = db.cursor()

    sql = """
		SELECT title,content,topic
		FROM posts p
		"""

    curs.execute(sql)

    post_list = curs.fetchall()

    db.commit()
    db.close()

    return jsonify({'post_list': post_list})

# 게시글 작성


@app.route("/savepost", methods=["POST"])
def save_post():
    title = request.form['title']
    topic = request.form['topic']
    content = request.form['content']

    db = pymysql.connect(host='localhost', user='root',
                         db='test', password='0000', charset='utf8')
    curs = db.cursor()

    sql = """
		INSERT INTO posts (title,topic, content) VALUES (%s,%s,%s)
		"""

    curs.execute(sql, (title, topic, content))

    db.commit()
    db.close()

    return jsonify({'msg': '게시글 작성 완료'})


if __name__ == '__main__':
    app.run('127.0.0.1', port=5000, debug=True)
