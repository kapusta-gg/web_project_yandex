import os

from flask import Flask, render_template, redirect, request
from flask_login import LoginManager, login_required, logout_user, login_user
import flask_user
from werkzeug.utils import secure_filename

from data import db_session

from data.users import User
from data.comments import Comments
from data.content import Content

from data.register import RegisterForm
from data.login import LoginForm
from data.content_maker import MakerForm
from data.comments_form import CommentsForm

app = Flask(__name__)
UPLOAD_FOLDER_INT = '/web/static/intermediate'
UPLOAD_FOLDER_USERS = '/web/static/users_content'

app.config['SECRET_KEY'] = 'my_project'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER_INT
login_manager = LoginManager()
login_manager.init_app(app)


def allowed_file_img(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ['.png', '.jpg']


def allowed_file_song(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ['.mp3']


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


@app.route('/')
def index():
    session = db_session.create_session()
    return render_template('main_page.html', content=session.query(Content).all())


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        text_search = request.form['search']
    else:
        text_search = ''
    session = db_session.create_session()
    session.query(Content).filter().all()
    searching_objects = \
        session.query(Content).filter(
            Content.music_author.like('%' + text_search + '%') | Content.music_name.like('%' + text_search + '%')).all()
    return render_template('search.html', content=searching_objects)


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
    if request.method == 'POST':
        author = request.form['author']
        song_name = request.form['song_name']
        song_file = request.files['song']
        img_file = request.files['img']
        if song_file and img_file:
            if ('.png' in img_file.filename) and ('.mp3' in song_file.filename):
                for i in [song_file, img_file]:
                    filename = secure_filename(i.filename)
                    i.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    old_load_file = os.path.join(UPLOAD_FOLDER_INT, i.filename)
                    new_load_file = os.path.join(UPLOAD_FOLDER_USERS,
                                                 author + '_' + song_name + '.' + i.filename.rsplit('.', 1)[1])
                    os.rename(old_load_file, new_load_file)
                session = db_session.create_session()
                content = Content(
                    music_name=song_name,
                    music_author=author,
                    url_music='static/users_content/' + author + '_' + song_name + '.mp3',
                    url_img='static/users_content/' + author + '_' + song_name + '.png',
                    user_id=flask_user.current_user.name
                )
                session.add(content)
                session.commit()
            return redirect('/')
    return render_template('maker.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/music/<name_music>/<name_author>/<id>/<user_id>', methods=['GET', 'POST'])
def music_page(name_music, name_author, id, user_id):
    session = db_session.create_session()
    data_music = session.query(Content).filter(Content.user_id == user_id,
                                               Content.id == id).first()
    user_post_name = session.query(User).filter(User.id == id).first()

    form = CommentsForm()
    if form.validate_on_submit():
        text = Comments(text=form.comment.data,
                        content_id=id,
                        user_name=flask_user.current_user.name)
        session.add(text)
        session.commit()
        return redirect('/' + '/'.join(['crutch', name_music, name_author, id, user_id]))
    comments = session.query(Comments).filter(Comments.content_id == id).all()
    return render_template('music_page.html', title_music=name_music,
                           title_author=name_author, data=data_music,
                           user=user_post_name, form=form,
                           comments=comments)


@app.route('/crutch/<name_music>/<name_author>/<id>/<user_id>')
def crutch(name_music, name_author, id, user_id):
    return redirect('/' + '/'.join(['music', name_music, name_author, id, user_id]))


if __name__ == '__main__':
    db_session.global_init("db/blogs.sqlite")
    app.run(port=8080, host='127.0.0.1', debug=True)
