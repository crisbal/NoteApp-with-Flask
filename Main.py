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
        notes = Note.select().join(User).where(User.id == session['id']).order_by(Note.last_edit.desc())
        return render_template('notes.html', notes = notes)
    else:
        return  redirect(url_for('login'))


@app.route('/notes/add',methods=['GET', 'POST'])
def add_note():
    if request.method == 'GET':
        return  redirect(url_for('notes'))

    if is_logged_in():
        if request.form.get('title', None) and request.form.get('body', None):
            title = request.form.get('title', None)
            body = request.form.get('body', None)
            user = User.get(User.id == session['id'])
            note = Note.create(user = user,title = title, body = body)
            return jsonify(status="OK", renderedNote = render_template('note.html', note = note))
        else:
            return jsonify(status="Wrong or missing parameters"), 400 
    else:
       return jsonify(status="Not logged in"), 403

@app.route('/login', methods=['GET', 'POST'])
def login():
    if is_logged_in():
        return redirect(url_for('notes'))

    if request.method == 'POST':
        if request.form.get('email', None) and request.form.get('password', None):
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
    if is_logged_in():
        return redirect(url_for('notes'))
    if request.method == 'POST':
        if request.form.get('email', None) and request.form.get('password', None):
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
    session['logged_in']=True
    session['id'] = user.id
    


def is_logged_in():
    return True if 'logged_in' in session and 'id' in session else False
        
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