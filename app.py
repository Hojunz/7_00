# flask, flask-jwt-extended, pymysql 라이브러리 설치
from flask import Flask, render_template, request, jsonify, redirect, url_for
import pymysql
from datetime import datetime, timedelta
import json
import jwt

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

SECRET_KEY = 'Zoo'

@app.route('/')
def home():
	return render_template('index.html')


@app.route('/login')
def login():
	return render_template('login.html')

@app.route('/log_in', methods=['POST'])
def log_in():
	email_receive = request.form["email_give"]
	password_receive = request.form["password_give"]
	# print(email_receive)
	# print(password_receive)

	db = pymysql.connect(host='localhost', user='root', db='flask_test', password='12345678', charset='utf8')
	curs = db.cursor()

	sql = """
		SELECT *
		FROM users u
		where u.email = %s
		"""

	curs.execute(sql, email_receive)

	users_result = curs.fetchall()
	# print(users_result[0][1] != password_receive)

	json_str = json.dumps(users_result, indent=4, sort_keys=True, default=str)
	db.commit()
	db.close()

	if users_result[0][1] != password_receive:
		msg = "비밀번호가 일치하지 않습니다. 다시 로그인해주세요."
		return jsonify({'result': 'fail', 'msg': msg})
	else:
		# 토큰 발행, id, payload, 시크릿키가 필요
		payload = {
			'id': email_receive,
			'exp': datetime.utcnow() + timedelta(seconds=30)
		}
		token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
		# print(token)
		return jsonify({'result': 'success', 'token': token})

@app.route('/user_only', methods=['POST'])
def user_only():
	token_receive = request.cookies.get('mytoken')
	print(token_receive)

	try:
		payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
		msg = payload['id'] + '님은 게시물을 작성하실 수 있습니다.'
		return jsonify({'msg': msg})
	except(jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
		return jsonify({'msg': 'User Only Access!!!'})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)