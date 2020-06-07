from flask import Flask, g, render_template, flash, redirect, url_for
from flask_bcrypt import check_password_hash
from flask_login import LoginManager, login_user, logout_user, current_user, login_required

import models
import forms

DEBUG = True
PORT = 8000
HOST = '0.0.0.0'

app = Flask(__name__)
# noinspection SpellCheckingInspection
app.secret_key = 'qwpoeifna;sldn;oasiheop;wienglkn.glsjhoi;uj'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    try:
        return models.User.get(models.User.id == user_id)
    except models.DoesNotExist:
        return None


@app.before_request
def before_request():
    """Connect to the database before each request."""
    g.db = models.DATABASE
    g.db.connect()
    g.user = current_user


@app.after_request
def after_request(response):
    """Close the database connection after each request."""
    g.db.close()
    return response


@app.route('/register', methods=('GET', 'POST'))
def register():
    form = forms.RegisterForm()
    if form.validate_on_submit():
        flash("You're ready to make some tacos", "success")
        models.User.create_users(
            email=form.email.data,
            password=form.password.data
        )
        return redirect(url_for('index'))
    return render_template('register.html', form=form)


@app.route('/login', methods=('GET', 'POST'))
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        try:
            user = models.User.get(models.User.email == form.email.data)
        except models.DoesNotExist:
            flash("No tacos for you!", "error")
        else:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                flash("Taco time, bitches!")
                return redirect(url_for('index'))
            else:
                flash("No tacos for you!", "error")
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You've been logged out! Come make some more tacos soon", "success")
    return redirect(url_for('index'))


@app.route('/taco_create')
@login_required
def taco():
    form = forms.TacoForm()
    if form.validate_on_submit():
        models.Taco.create(user=g.user._get_current_object(),
                           protein=form.protein.data,
                           shell=form.shell.data,
                           cheese=form.cheese.data,
                           extras=form.extras.data
                           )
        flash('Sick taco bro!', "success")
        return redirect(url_for('index'))
    return render_template('taco.html', form=form)


@app.route('/')
def index():
    tacos = models.Taco.select().limit(100)
    return render_template('index.html', tacos=tacos)


if __name__ == '__main__':
    models.initialize()
    try:
        models.User.create_user(
            email="wardenj@gmail.com",
            password='tryandguess')
    except ValueError:
        pass
    app.run(debug=DEBUG, host=HOST, port=PORT)