from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'asdga654asdfga65aefb61'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'index', 'blog', 'singleUser']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if not user:
            flash("Username not found.")
            return redirect('/signup')
        elif user.password != password:
            flash("Wrong Password")
            return redirect('/login')
        else:
            session['username'] = username
            flash("Logged In!")
            return redirect('/newpost')

    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            flash("Username is taken.")
            return redirect('/signup')

        elif not (username and password and verify):
            flash("You must fill out all fields", "error")
            return redirect('/signup')

        elif len(username) < 3 or len(username) > 20:
            flash("Username must be between 3-20 characters.")
            return redirect('/signup')

        elif len(password) < 3 or len(password) > 20:
            flash("Password must be between 3-20 characters.")
            return redirect('/signup')

        elif password != verify:
            flash("Passwords do not match.")
            return redirect('/signup')

        else:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')

    return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['username']
    flash("Logged Out.")
    return redirect('/blog.html')

@app.route('/')
def index():
    users = User.query.all()
    return render_template("index.html", users=users)


@app.route('/blog')
@app.route('/blog/<bid>', methods=['GET'])
def blog():

    blogs = Blog.query.all()
    blog_id = request.args.get('bid')
    if blog_id:
        new_post = Blog.query.get(blog_id)
        return render_template('postblog.html', blogs=blogs, post=new_post)
    else:
        return render_template('blog.html', blogs=blogs)

@app.route('/newpost', methods=['POST', 'GET'])
def new_post():

    owner = User.query.filter_by(username=session['username']).first()
    error_text = ''
    
    if request.method == 'POST':
        blog_title = request.form['title']
        blog_body = request.form['body']

        if blog_title == '' :
            flash('Title can not be blank.')
            return redirect('/newpost')
        else:
            title_error = ''

        if blog_body == '':
            flash('Please enter a post.')
            return redirect('/newpost')
        else:
            body_error = ''

        if title_error == '' and body_error == '' :
            onwer = User.query.filter_by(username=session['username']).first()
            new_post = Blog(blog_title, blog_body, owner)
            db.session.add(new_post)
            db.session.commit()
            return redirect("/blog?id="+str(new_post.id))
        else:
            return render_template('newpost.html', title="Create New Blog Post", blog_title=blog_title, blog_body=blog_body)

    else:
        return render_template('newpost.html')

        blogs = Blog.query.all()

        return render_template('blog.html', blogs=blogs)

    return render_template('newpost.html')

@app.route('/singleUser')
@app.route('/singleUser/<user>')
def singleUser():
    user_name_fetch = request.args.get('user')
    user = User.query.filter_by(username=user_name_fetch).first()
    return render_template('singleUser.html', user=user)


if __name__ == '__main__':
    app.run()