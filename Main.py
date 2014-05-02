from flask import *

from Models import *

import hashlib

app = Flask(__name__)


#ROUTING

@app.route('/')
def index():
    return render_template('basic.html')

@app.route('/notes')
def notes():
    if is_logged_in():
        return render_template('notes.html')
    else:
        return  redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if is_logged_in():
        return redirect(url_for('notes'))

    if request.method == 'POST':
            if is_logged_in():
                return redirect(url_for('notes'))
            elif request.form.get('email', None) and request.form.get('password', None):
                user = user_exists(request.form.get('email'), request.form.get('password'))
                if user:
                    session_login(user)
                    return redirect(url_for('notes'))
                else:
                    return render_template('login.html', error='Wrong email or password')
            else:
                render_template('login.html', error='Email or password missing')
    else:
        return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
            if is_logged_in():
                return redirect(url_for('notes'))
            elif request.form.get('email', None) and request.form.get('password', None):
                if email_used(request.form.get('email')):
                    return render_template('register.html', error='Email already in use')
                else:
                    user = User(email=request.form.get('email'), password=hashlib.sha512(request.form.get('password').encode()).hexdigest())
                    user.save()
                    session_login(user)
                    return redirect(url_for('notes'))
            else:
                render_template('register.html', error='Email or password missing')
    else:
        return render_template('register.html')

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'),404


#FUNCTIONS

def session_login(user):
    session['id'] = user.id
    session['email'] = user.email


def is_logged_in():
    return True if 'email' in session and 'id' in session else False
        
def email_used(email):
    try:
        user = User.get(User.email == email)
        return user
    except User.DoesNotExist, e:
        return None

def user_exists(email,password):
    try:
        user = User.get(User.email == email, User.password == hashlib.sha512(password.encode()).hexdigest())
        return user
    except User.DoesNotExist, e:
        return None

if __name__ == '__main__':
    app.debug = True
    app.secret_key = "SECRET"
    app.run()