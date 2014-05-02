from flask import *

from Models import *


app = Flask(__name__)


@app.route('/')
def index():
    return render_template('basic.html')

@app.route('/notes')
def notes():
    if is_logged_in():
        return render_template('notes.html')
    else
        return  redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            if is_logged_in():
                return redirect(url_for('notes'))
            else:
                user = User.get(User.email == request.form.get('email', None), User.password == request.form.get('password', None))
                session['id'] = user.id
                session['email'] = user.email
                return redirect(url_for('notes'))
        except User.DoesNotExist, e:
            return render_template('login.html', error='Wrong email or password')
    else:
        return render_template('login.html')

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'),404


def is_logged_in():
    return if 'username' in session and 'id' in session

if __name__ == '__main__':
    app.debug = True
    app.run()