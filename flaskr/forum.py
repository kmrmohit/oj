from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db
import datetime
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time

bp = Blueprint('forum', __name__,url_prefix='/dashboard')

@bp.route('/')
@login_required
def dashboard():
    db=get_db()
    obj=datetime.datetime.now()
    if obj.hour==0 and obj.minute==0 and obj.second==0:
        array=[]
        ind=0
        driver = webdriver.Firefox(executable_path="D:\geckodriver.exe")
        driver.get("https://www.codechef.com")
        print(driver.title)
        print(driver.current_url)
        driver.find_element_by_xpath("/html/body/header/div/div/nav/div/div/ul/li[2]/a").click()
        #time.sleep(100)
        a=driver.find_elements_by_class_name("content-wrapper")
        for i in a:
            b=i.find_elements_by_class_name("dataTable")
            #time.sleep(100
            for j in b:
                c=j.find_element_by_tag_name("tbody")
                #time.sleep(100)
                c=c.find_elements_by_tag_name("tr")
                #time.sleep(100)
                for k in c:
                    d=k.find_elements_by_tag_name("td")
                    #time.sleep(100)
                    temp=[]
                    temp.insert(0,"codechef")
                    jj=1
                    for items in d:
                        kk=items.text.splitlines()
                        for it in kk:
                            temp.insert(jj,it)
                            jj+=1
                    array.insert(ind,temp)
                    ind+=1
                    if ind>20:
                        break
                if ind>20:
                    break
            if(ind>20):
                break

        for i in range(0,len(array)):
            db.execute(
                'INSERT INTO contests (site,schedule,contestlink,other_det)'
                ' VALUES (?, ?,?,?)',
                (array[i][0],array[i][1],array[i][2],array[i][4])
            )

        """array=[]
        ind=0
        driver.get("https://www.codeforces.com")
        driver.find_element_by_xpath("/html/body/div[5]/div[3]/div[5]/ul/li[3]/a").click()
        c=driver.find_elements_by_tag_name("tbody")
        #time.sleep(100)
        for j in c:
            c=j.find_elements_by_tag_name("tr")
            #time.sleep(100)
            for k in c:
                d=k.find_elements_by_tag_name("td")
                #time.sleep(100)
                temp=[]
                temp.insert(0,"codeforces")
                jj=0
                for items in d:
                    jj+=1
                    temp.insert(jj,items.text)
                array.insert(ind,temp)
                ind+=1
        for i in range(0,len(array)):
            print(len(array[i]))
            '{} {} {} {}'.format(array[i][0],array[i][1],array[i][2],array[i][3])
            print("\n")
            db.execute(
                'INSERT INTO contests (site,schedule,contestlink,other_det)'
                ' VALUES (?, ?,?,?)',
                (array[i][0],array[i][1],"helo","helo")
            )
            """
        db.commit()
        driver.close()#close one window
        driver.quit()#closes all open windows

    details=get_db().execute(
            ' SELECT * '
            ' FROM contests '
    ).fetchall()
    return render_template('forum/dashboard.html',posts=details)


@bp.route('/solve', methods=('GET', 'POST'))
@login_required
def solve():
    db=get_db()
    details=db.execute(
            ' SELECT * '
            ' FROM problems '
    ).fetchall()
    return render_template('forum/solve.html',posts=details)


@bp.route('/<string:id>/profile', methods=('GET', 'POST'))
@login_required
def view_profile(id):
    return render_template('auth/profile.html')


@bp.route('/answer', methods=('GET', 'POST'))
@login_required
def view_ques():
    db = get_db()
    ques = db.execute(
            'SELECT DISTINCT q.id as qid, body as qbody,created'
            ' FROM questions q '
            ' WHERE q.author_id != ?'
            ' ORDER BY qid DESC',
            ( g.user['id'] ,)
        ).fetchall()
    try:
        return render_template('forum/other_ques.html',posts=ques)
    except:
        print("no questions yet")

def get_ques(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id,p.body,author_id'
        ' FROM questions p'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))



    return post

@bp.route('/<int:id>/your_ques', methods=('GET', 'POST'))
@login_required
def your_ques(id):
    db = get_db()
    ques = db.execute(
            ' SELECT DISTINCT q.id as qid, body as qbody ,created'
            ' FROM questions q , user u '
            ' WHERE q.author_id = ? '
            ' ORDER BY qid DESC ',
            ( id ,)
        ).fetchall()
        #print("hi")
    return render_template('forum/your_ques.html', posts=ques)



@bp.route('/<int:id>/answer', methods=('GET', 'POST'))
@login_required
def answer(id):
    ques = get_ques(id)
    if request.method == 'POST':
        body = request.form['body']
        error = None

        if not body:
            error = 'Body is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO user_sol (userid,problemid,answerid)'
                ' VALUES (?, ?,?)',
                (g.user['username'],id,body)
            )
            db.execute(
                'INSERT INTO solution (questionid,body)'
                ' VALUES (?, ?)',
                (id,body)
            )
            db.commit()
            det=db.execute(
              'SELECT *'
              'FROM answers'
            ).fetchall()
            for items in det:
                print(items['body'])
            return redirect(url_for('forum.dashboard'))

    return render_template('forum/answer.html', posts=ques)


@bp.route('/<int:id>/view_answers', methods=('GET', 'POST'))
@login_required
def view_answers(id):
    db = get_db()
    error = None
    res = db.execute(
            ' SELECT question_id , body ,created'
            ' FROM solution a '
            ' WHERE a.question_id = ? ',
            (id,)
    ).fetchall()
    if(len(res)==0):
        error="No answers for this question yet."
    if error is not None:
        flash(error)
#    print(len(res))
#    for items in res:
#        print(str(items["question_id"]) + " " +str(items["id"]) + " " + items["body"])

    return render_template('forum/view_answers.html', posts=res)


@bp.route('/add', methods=('GET', 'POST'))
@login_required
def add_problem():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        error = None

        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO problems ( author_id, title, body )'
                ' VALUES (?, ?, ?)',
                (g.user['username'],title, body)
            )
            db.commit()
            return redirect(url_for('forum.solve'))

    return render_template('forum/add.html')


@bp.route('/<int:id>/submit/', methods=('GET', 'POST'))
@login_required
def submit(id):
    if request.method == 'POST':
        body = request.form['body']
        error = None

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO solution ( question_id, body )'
                ' VALUES (?, ?)',
                (id, body)
            )
            db.execute(
                'INSERT INTO user_sol ( userid, problemid )'
                ' VALUES (?, ?)',
                (g.user['username'], id)
            )
            db.commit()
            return redirect(url_for('forum.solve'))

    return render_template('forum/submit.html')
