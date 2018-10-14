from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:password@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route('/blog', methods=['POST', 'GET'])
def blog():

    blogs = Blog.query.all()
    id = request.query_string
    if request.method == 'GET':
        if not id:
            return render_template('blog.html', blogs=blogs)
        else:
            b = int(request.args.get('b'))
            blog = Blog.query.get(b)
            return render_template('singlepost.html', blog=blog)

@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
    
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']

        if not title:
            flash('Title can not be blank.')
            return redirect('/newpost')

        if not body:
            flash('Please enter a post.')
            return redirect('/newpost')
        
        else:
            new_post = Blog(title, body)
            db.session.add(new_post)
            db.session.commit()

            b = new_post.id
            blog = Blog.query.get(b)
            return render_template('singlepost.html', blog=blog)

        return redirect('/blog')

    return render_template('newpost.html')

app.run()