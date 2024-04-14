import json

from flask import Flask, request, render_template, session, redirect, url_for
from database import db

# 创建一个app
app = Flask('main')
app.secret_key = '1234567890'

# 用户登录验证
@app.route('/user/verify', methods = ['POST'])
def verify():
    user = {
        'name': "guest"
    }
    if 'userid' in session:
        user['name'] = db.get_user_byID(session['userid'])['name']
    
    return json.dumps(user)

# 主页
@app.route('/', methods = ['GET'])
def index():
    return render_template("index.html")

# 用户个人信息显示页面
@app.route('/user', methods = ['GET', 'POST'])
def user_info():
    # 判断用户是否登录
    if 'userid' in session:
        if request.method == "GET":
            # 用户已经登陆展示个人信息
            # 从数据库中获取用户信息
            user = db.get_user_byID((session['userid']))
            return render_template("self-info.html", user=user)
        else: # post请求提交用户修改后的个人信息
            db.chuser_info(session['userid'], request.json["username"], request.json["plate"], request.json["phonenum"])
            return "ok"
    else:
        # 用户没有登陆，跳转到登陆页面
        return "<script> alert('请先登陆'); window.location.href='/login'; </script>"


# 用户登录页面
@app.route('/login', methods = ['GET', 'POST'])
def login():
    # 判断用户是否已经登陆过
    if 'userid' in session:
        return redirect(url_for('user_info'))

    if request.method == "POST":
        username = request.json['userid']
        password = request.json['password']
        if username == "" or password == "" :
            return "用户名或密码不能为空", 400
        if db.check_user(username, password) == 1:
            session['userid'] = username
            return "登陆成功", 200
        else:
            return "用户名或密码错误", 400

    return render_template("login.html")

# 用户注销功能
@app.route('/logout', methods = ['GET', 'POST'])
def logout():
    # 判断用户是否已经登陆过
    if 'userid' in session:
        session.pop("userid", None)
        return "<script> alert('注销成功'); window.location.href='/'; </script>"
    else:
        return '<script>alert("未登录")</script>'

# 车库显示页面
@app.route('/parking', methods = ['GET', 'POST'])
def parks():
    argv = request.args.get('zone', None)
    if argv == None:
        return render_template("parking.html")
    else:
        if argv in ['A', 'B', 'C', 'D', 'E', 'F']:
            return json.dumps(db.get_parks(argv))
        else:
            return "未知的区域", 404

# 用户钱包界面
@app.route('/wallet', methods = ['GET', 'POST'])
def wallet():
    if 'userid' in session:
        user = db.get_user_byID(session['userid'])
        return render_template("wallet.html", user=user)
    else:
        return "<script> alert('请先登陆'); window.location.href='/login'; </script>"