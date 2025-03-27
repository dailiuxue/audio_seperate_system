from flask import Flask, render_template, redirect, url_for, flash, session, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf import FlaskForm
from wtforms import BooleanField
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 请替换为你的实际密钥
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False)
    has_permission = db.Column(db.Boolean, default=True)  # 新增字段

# 创建数据库
with app.app_context():
    db.create_all()

# 注册表单
class RegistrationForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired()])
    password = PasswordField('密码', validators=[DataRequired()])
    confirm_password = PasswordField('确认密码', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('注册')

# 登录表单
class LoginForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired()])
    password = PasswordField('密码', validators=[DataRequired()])
    submit = SubmitField('登录')

# 管理员登录表单
class AdminLoginForm(FlaskForm):
    username = StringField('管理员用户名', validators=[DataRequired()])
    password = PasswordField('密码', validators=[DataRequired()])
    submit = SubmitField('登录')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        if username == 'admin':
            flash('不能设置管理员账号!', 'danger')
            return render_template('register.html', form=form)
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('用户名已存在!', 'danger')
        else:
            new_user = User(username=username,
                            password=password)
                            #registered_at=datetime_to_seconds(datetime.utcnow()))
            db.session.add(new_user)
            db.session.commit()
            flash('注册成功! 请登录.', 'success')
            return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/add_user', methods=['POST'])
def add_user():
    if not session.get('admin_logged_in'):
        flash('请先登录管理员账户!', 'danger')
        return redirect(url_for('admin_login'))

    username = request.form['username']
    password = request.form['password']
    has_permission = request.form.get('has_permission') == 'on'

    existing_user = User.query.filter_by(username=username).first()

    if existing_user:
        flash('用户名已存在!', 'danger')
    else:
        new_user = User(username=username,
                        password=password,
                        has_permission=has_permission)
        db.session.add(new_user)
        db.session.commit()
        flash('新用户添加成功!', 'success')

    return redirect(url_for('user_management'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            if user.has_permission:
                flash('登录成功!', 'success')
                return redirect('http://127.0.0.1:7860')
            else:
                flash('没有服务的使用权限', 'danger')
        else:
            flash('用户名或密码错误', 'danger')
    return render_template('login.html', form=form)

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    form = AdminLoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        admin = User.query.filter_by(username=username, password=password, is_admin=True).first()
        if admin:
            session['admin_logged_in'] = True
            session['admin_username'] = username
            flash('管理员登录成功!', 'success')
            return redirect(url_for('user_management'))
        else:
            flash('管理员用户名或密码错误', 'danger')
    return render_template('admin_login.html', form=form)

@app.route('/update_permission/<int:user_id>', methods=['POST'])
def update_permission(user_id):
    if not session.get('admin_logged_in'):
        flash('请先登录管理员账户!', 'danger')
        return redirect(url_for('admin_login'))
    user = User.query.get(user_id)
    if user.username == 'admin':
        flash('禁止修改管理员权限!', 'danger')
        return redirect(url_for('user_management'))

    if user:
        has_permission = request.form.get('has_permission') == 'on'
        user.has_permission = has_permission
        db.session.commit()
        flash('用户权限修改成功!', 'success')
    else:
        flash('用户不存在!', 'danger')
    return redirect(url_for('user_management'))

@app.route('/user_management')
def user_management():
    if not session.get('admin_logged_in'):
        flash('请先登录管理员账户!', 'danger')
        return redirect(url_for('admin_login'))
    users = User.query.all()
    return render_template('user_management.html', users=users, admin_username=session.get('admin_username'))

@app.route('/')
def home():
    return redirect(url_for('register'))

@app.route('/logout')
def logout():
    session.clear()
    flash('已退出管理员登录。', 'success')
    return redirect(url_for('admin_login'))

@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    # 这里需要添加你删除用户的逻辑
    # 例如，使用 SQLAlchemy 来删除用户，你可以这么写:
    try:
        user_to_delete = User.query.get(user_id)
        if user_to_delete.username == 'admin':
            flash('禁止删除管理员!', 'danger')
            return redirect(url_for('user_management')) 

        if user_to_delete:
            db.session.delete(user_to_delete)
            db.session.commit()
            flash('用户已成功删除。', 'success')
        else:
            flash('找不到用户。', 'error')
    except Exception as e:
        db.session.rollback()
        flash(str(e), 'error')
    
    # 最后，重定向回用户管理页面
    return redirect(url_for('user_management'))

if __name__ == '__main__':
    app.run(debug=True)

