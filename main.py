import os

from PIL import Image
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
from data.comments_form import CommentsForm

# Создаем flask
app = Flask(__name__)
UPLOAD_FOLDER_INT = '/web/static/intermediate'
UPLOAD_FOLDER_USERS = '/web/static/users_content'

app.config['SECRET_KEY'] = 'my_project'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER_INT
login_manager = LoginManager()
login_manager.init_app(app)

# Загружаем пользователя
@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


# Основная страница нашего сайта
@app.route('/')
def index():
    session = db_session.create_session()
    return render_template('main_page.html', content=session.query(Content).all())

# Страница поиска
@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        # Забирем из input текст пользователя
        text_search = request.form['search']
    else:
        # Чтоб не выскакивала ошибка
        text_search = ''
    session = db_session.create_session()
    # Делаем запрос в бд с фильтром на текст пользователя
    searching_objects = \
        session.query(Content).filter(
            Content.music_author.like('%' + text_search + '%') | Content.music_name.like('%' + text_search + '%')).all()
    return render_template('search.html', content=searching_objects)


# Форма регестрации
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
        # создаем таблицу с данными пользователя и добавляем его в бд
        user = User(
            name=form.name.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        return redirect('/login')
    return render_template('register.html', form=form)


# Страница Авторского права
@app.route('/author_rights')
def author_rights():
    return render_template('rights.html')


# Страница логина
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


# Страница добавления музыки
@app.route('/maker', methods=['GET', 'POST'])
def maker():
    if request.method == 'POST':
        # Забираем из input'ов данные
        author = request.form['author']
        song_name = request.form['song_name']
        song_file = request.files['song']
        img_file = request.files['img']
        # проверяем файлы
        if song_file and img_file:
            if ('.png' in img_file.filename or '.jpg' in img_file.filename) and ('.mp3' in song_file.filename):
                for i in [song_file, img_file]:
                    filename = secure_filename(i.filename)
                    # Переименовываем файлы для того чтобы они не накладывались друг на друга

                    save_file = author + '_' + song_name + '.' + i.filename.rsplit('.', 1)[1]

                    i.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    old_load_file = os.path.join(UPLOAD_FOLDER_INT, i.filename)
                    new_load_file = os.path.join(UPLOAD_FOLDER_USERS, save_file)
                    # Добавляем файлы в общую папку для пользовательского контента
                    try:
                        os.rename(old_load_file, new_load_file)
                    except FileExistsError:
                        pass

                session = db_session.create_session()
                # Пересохраняем файлы из .jpg в .png
                # Вообще это не обязательно
                # Но для однородноси файлов сойдет
                if '.jpg' in img_file.filename:
                    im = Image.open(UPLOAD_FOLDER_USERS + '/' + save_file)
                    im.save(UPLOAD_FOLDER_USERS + '/' + author + '_' + song_name + '.png')
                # Добавляем в бд
                content = Content(
                    music_name=song_name,
                    music_author=author,
                    url_music='static/users_content/' + author + '_' + song_name + '.mp3',
                    url_img='static/users_content/' + author + '_' + song_name + '.png',
                    user_id=flask_user.current_user.name
                )
                session.add(content)
                session.commit()
            else:
                return render_template('maker.html', message='Неправильный тип файла')
            return redirect('/')
    return render_template('maker.html')


# Для выхода пользователя
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


# Страница контента пользователей
@app.route('/music/<name_music>/<name_author>/<id>/<user_id>', methods=['GET', 'POST'])
def music_page(name_music, name_author, id, user_id):
    session = db_session.create_session()
    # Забираем все нужные данные
    data_music = session.query(Content).filter(Content.user_id == user_id,
                                               Content.id == id).first()
    user_post_name = session.query(User).filter(User.id == id).first()

    # Добавляем комментарий пользователя в бд
    form = CommentsForm()
    if form.validate_on_submit():
        text = Comments(text=form.comment.data,
                        content_id=id,
                        user_name=flask_user.current_user.name)
        session.add(text)
        session.commit()
        # Специальный костыль
        return redirect('/' + '/'.join(['crutch', name_music, name_author, id, user_id]))
    comments = session.query(Comments).filter(Comments.content_id == id).all()
    return render_template('music_page.html', title_music=name_music,
                           title_author=name_author, data=data_music,
                           user=user_post_name, form=form,
                           comments=comments)


# Данная страница нужна для того чтобы комментарий пользователя сразу
# отображался на странице контента
# Без этого костыля комментарий добавляеться в бд,
# но не отображаеться на странице
@app.route('/crutch/<name_music>/<name_author>/<id>/<user_id>')
def crutch(name_music, name_author, id, user_id):
    return redirect('/' + '/'.join(['music', name_music, name_author, id, user_id]))


# Запуск сайта
if __name__ == '__main__':
    db_session.global_init("db/blogs.sqlite")
    app.run(port=8080, host='127.0.0.1', debug=True)
