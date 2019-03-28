import functools
import os
from flask import(
    Blueprint,flash,g,redirect,render_template,request,session,url_for
    )

from werkzeug.security import check_password_hash,generate_password_hash

from flaskr.db import get_db

bp = Blueprint('auth' , __name__,url_prefix='/auth')

@bp.route('/register',methods=('GET','POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email_id = request.form['email']
        APP_ROOT = os.path.dirname(os.path.abspath(__file__))
        target = os.path.join(APP_ROOT,'static')
        print(target)
        if not os.path.isdir(target):
            os.mkdir(target)

        file = request.files.getlist("file")[0]
        print(file)

        filename = file.filename
        destination = "\\".join([target,filename])
        print(destination)
        file.save(destination)
        db=get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif not email_id:
            error = 'Email id is required.'
        elif db.execute(
            'SELECT username FROM user WHERE username = ?' , (username,)
        ).fetchone() is not None:
            error ='User {} is already registered.'.format(username)

        if error is None:
            db.execute(
                'INSERT INTO user  (username,password,emailid,img) VALUES(?,?,?,?)',
                (username,generate_password_hash(password),email_id,filename)
                )
            db.commit()
            return redirect(url_for('auth.login'))

        flash(error)

    return render_template('auth/register_new.html')


@bp.route('/upload',methods=('GET','POST'))
def upload():
    if request.method == 'POST':
        APP_ROOT = os.path.dirname(os.path.abspath(__file__))
        target = os.path.join(APP_ROOT,'static')
        file = request.files.getlist("file")[0]
        filename = file.filename
        destination = "\\".join([target,filename])
        print(destination)
        file.save(destination)
        db=get_db()
        error = None
        if error is None:
            db.execute(
                'UPDATE user  SET img = ? where id = ? ',
                (filename,g.user['id'])
                )
            db.commit()
            return redirect(url_for('forum.dashboard'))

        flash(error)

    return render_template('auth/register_new.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':

            username = request.form['username']
            password = request.form['password']
            db = get_db()
            error = None
            user = db.execute(
                'SELECT * FROM user WHERE username = ?', (username,)
            ).fetchone()

            if user is None:
                error = 'Incorrect username.'
                print("hi")
            elif not check_password_hash(user['password'], password):
                error = 'Incorrect password.'
            if error is None:
                session.clear()
                session['user_id'] = username
                return redirect(url_for('forum.dashboard'))

            flash(error)



    return render_template('auth/login.html')


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE Username = ?', (user_id,)
        ).fetchone()


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
