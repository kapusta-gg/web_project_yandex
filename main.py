from flask import Flask, render_template, redirect
from flask_login import LoginManager, login_required, logout_user, login_user
from werkzeug.utils import secure_filename
from math import ceil

from data import db_session
from data.users import User
from data.content import Content
from data.register import RegisterForm
from data.login import LoginForm
from data.content_maker import MakerForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'my_project'
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


@app.route('/')
def index():
    session = db_session.create_session()
    return render_template('main_window.html', content=session.query(Content).all())


@app.route('/register', methods=['GET', 'POST'])
def registration():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html',
                                   form=form,
                                   message="Пароли не совпадают")
        session = db_session.create_session()
        if session.query(User).filter(User.name == form.name.data).first():
            return render_template('register.html',
                                   form=form,
                                   message="Такой пользователь уже есть")
        if session.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html',
                                   form=form,
                                   message="Такой почта уже зарегестрирована")
        user = User(
            name=form.name.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        return redirect('/login')
    return render_template('register.html', form=form)


@app.route('/author_rights')
def author_rights():
    return render_template('rights.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', form=form)

@app.route('/maker', methods=['GET', 'POST'])
def maker():
    form = MakerForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        if '.png' in form.image.name:
            return render_template('register.html',
                                   form=form,
                                   message="Такой почта уже зарегестрирована")
    return render_template('maker.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")

@app.route('/music/<name_music>/<name_author>/<user_id>')
def music_page(name_music, name_author, user_id):
    return redirect('/music_page')


if __name__ == '__main__':
    db_session.global_init("db/blogs.sqlite")
    app.run(port=8080, host='127.0.0.1', debug=True)