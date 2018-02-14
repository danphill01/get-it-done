from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import re

app = Flask(__name__)
app.config['DEBUG'] = True
# Note: the connection string after :// contains the following info:
# user:password@server:portNumber/databaseName
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://get-it-done:beproductive@localhost:8889/get-it-done'
# Good for debug by causing SQL commands to echo to terminal
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'mysecretkey'


class Task(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    completed = db.Column(db.Boolean)   

    def __init__(self, name):
        self.name = name
        self.completed = False


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))

    def __init__(self, email, password):
        self.email = email
        self.password = password


def invalid_string_length(string):
    return (len(string) < 3 or len(string) > 20)


@app.before_request
def require_login():
    allowed_routes = ['login', 'register']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            session['email'] = email
            flash("Logged in",'info')
            return redirect('/')
        else:
            flash('User password incorrect, or user does not exist', 'error')

    return render_template('login.html')


@app.route('/logout')
def logout():
    del session['email']
    return redirect('/login')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']

        # TODO - validate user's data
        if not username:
            flash("username is required", 'error')
        elif re.search('\s', username):
            flash("username must not contain space characters so I removed them", 'error')
            username = re.sub('\s', '', username)
        elif invalid_string_length(username):
            flash("username must be between 3 and 20 characters", 'error')
        if not password:
            flash("password is required", 'error')
        elif re.search('\s', password):
            flash("password must not contain space characters so I removed them", 'error')
        elif invalid_string_length(password):
            flash("password must be between 3 and 20 characters", 'error')
        elif not verify:
            flash("verify password is required", 'error')
        elif re.search('\s', verify):
            flash("verify password must not contain space characters so I removed them", 'error')
        elif invalid_string_length(verify):
            flash("verify password must be between 3 and 20 characters", 'error')
        elif password != verify:
            flash("verify password does not match password", 'error')
        if email:
            if len(email.split('@')) != 2:
                flash("email must contain exactly one @ symbol", 'error')
            elif len(email.split('.')) != 2:
                flash("email must contain exactly one period", 'error')
            elif re.search('\s', email):
                flash("email must not contain space characters so I removed them", 'error')
            elif invalid_string_length(email):
                flash("email must be between 3 and 20 characters", 'error')
                
 

        existing_user = User.query.filter_by(email=email).first()
        if not existing_user and 'flash' not in session:
            new_user = User(email, password)
            db.session.add(new_user)
            db.session.commit()

            return render_template('welcome.html', username = username)
        else:
            # TODO - user better response messaging
            flash("The email address  {}  has already been registered".format(email), 'error')

    return render_template('register.html')



@app.route('/', methods=['POST', 'GET'])
def index():

    if request.method == 'POST':
        task_name = request.form['task']
        new_task = Task(task_name)
        db.session.add(new_task)
        db.session.commit()

    tasks = Task.query.filter_by(completed=False).all()
    completed_tasks = Task.query.filter_by(completed=True).all()
    return render_template('todos.html',title="Get It Done!", tasks=tasks, completed_tasks=completed_tasks)


@app.route('/delete-task', methods=["POST"])
def delete_task():

    task_id = int(request.form['task-id'])
    task = Task.query.get(task_id)
    task.completed = True
    db.session.add(task)
    db.session.commit()

    return redirect("/")

if __name__ == '__main__':
    app.run()