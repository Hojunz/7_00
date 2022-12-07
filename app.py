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
                         db='flask_test', password='11!', charset='utf8')
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

# 회원가입

@app.route('/signup')
def signup():
	return render_template('login.html')

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

	db = pymysql.connect(host='localhost', user='root', db='flask_test', password='11!', charset='utf8')
	curs = db.cursor()

	sql = """
		insert into users (email, pw, name, regrate, filename)
         values (%s,%s,%s,%s,%s)
		"""

	curs.execute(sql, (email_receive, password_receive, name_receive, mytime, save_to))

	users_result = curs.fetchall()
	# print(users_result[0][1] != password_receive)

	json_str = json.dumps(users_result, indent=4, sort_keys=True, default=str)
	db.commit()
	db.close()

	return jsonify({"result":"success", 'msg':'회원가입 완료!'})




# 게시판 작성 페이지


@app.route('/write_page')
def write_page():
   return render_template('write_page.html')

# 게시글 작성


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


# mypage

@app.route('/mypage')
def mypage():
	return render_template('mypage.html')

# mypage index에서 이동할 때
@app.route('/', methods=['POST'])
def move_to_mypage():
	token_receive = request.cookies.get('mytoken')

	try:
		jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
		return jsonify({'result': 'success'})
	except(jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
		return jsonify({'result': 'fail', 'msg': '로그인을 먼저 진행해주세요!!'})

# mypage에서 db자료 표시

@app.route("/user_info", methods=["GET"])
def user_info_get():
	token_receive = request.cookies.get('mytoken')
	payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
	target_email = payload['id']

	db = pymysql.connect(host='localhost', user='root', db='flask_test', password='11!', charset='utf8')
	curs = db.cursor()

	sql = """
		SELECT *
			FROM users u
			WHERE u.email = %s
		"""

	curs.execute(sql, target_email)

	users_result = curs.fetchall()
	print(users_result[0])

	json_str = json.dumps(users_result, indent=4, sort_keys=True, default=str)
	db.commit()
	db.close()

	return jsonify({'msg':'GET 연결 완료!', 'user_info' : users_result[0]})



if __name__ == '__main__':
    app.run('127.0.0.1', port=5000, debug=True)