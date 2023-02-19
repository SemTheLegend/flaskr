from flask import Flask, render_template, flash, request, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash

# DataBase imports
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime, date
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_ckeditor import CKEditor

# import forms from webforms
from webforms import LoginForm, PasswordForm, UserForm, PostForm, SearchForm


# Create a Flask Instance
app = Flask(__name__)
# Add CKEditor
ckeditor = CKEditor(app)
# Add Database
"""Old SQLite DB"""
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
"""New MySQL db"""
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://username:password@localhost/db_name'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqldb://root:Legend1240s26#@localhost/flask_blog_db'
# Enable Tracking Modifications
app.config['SQLACHEMY_TRCAK_MODIFICATIONS'] = True
# Secret Key!
app.config['SECRET_KEY'] = "Master of Mystic Arts"

# Initialize THe Database
db = SQLAlchemy(app)
migrate = Migrate(app, db)
app.app_context().push()

# Flask Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


# Create User Model
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100))
    fav_color = db.Column(db.String(40))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    passwd = db.Column(db.String(126), nullable=False)

    # User Can Have Many Posts
    posts = db.relationship('Posts', backref='poster')

    @property
    def password(self):
        raise AttributeError("password is not readable")

    @password.setter
    def password(self, password):
        self.passwd = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.passwd, password)

    # Create A String
    def __repr__(self):
        return '<Name %r>' % self.name


# Create a BLog Post Model
class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text)
    # author = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(255))

    # ForeignKey To Link Users (refer to primary of the user)
    post_id = db.Column(db.Integer, db.ForeignKey('users.id'))


# ADMIN Page
@app.route('/admin')
@login_required
def admin():
    id = current_user.id
    
    if id == 1:
        return render_template('admin.html')
    else:
        flash("Sorry you must be the Admin to access this page")
        return redirect(url_for('dashboard'))
        
        
# Create a route decorator
@app.route('/')
@login_required
def index():
    first_name = "Sem"
    flash("Welcome to our Website!")
    return render_template('index.html', first_name=first_name)


@app.route('/user/<name>')
@login_required
def user(name):
    return render_template('user.html', user_name=name)


# Returning Json Strings
@app.route('/date')
def get_current_date():
    return {"Date": date.today()}


# Create custom Error Pages:

# Invalid URL
# Infrastructure Error
@app.errorhandler(401)
def page_not_found(e):
    return render_template('404.html'), 401


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# Internal Server Error


@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 500


# Pass Stuff To Navbar
@app.context_processor
def base():
    form = SearchForm()
    return dict(form=form)


# Create Search Function
@app.route('/search', methods=["POST"])
def search():
    form = SearchForm()
    posts = Posts.query

    if form.validate_on_submit():
        # Get data from submitted form
        post.searched = form.searched.data
        
        # Query the Database
        posts = posts.filter(Posts.content.like('%' + post.searched + '%'))
        posts = posts.order_by(Posts.title).all()

        return render_template("search.html", form=form, searched=post.searched, posts=posts)


# Create Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user:
            # Check the password hash if it matches the typed password
            if check_password_hash(user.passwd, form.passwd.data):
                login_user(user)
                flash("Logged In Successfully")
                return redirect(url_for('dashboard'))
            else:
                flash("Incorrect password! - Try Again")
        else:
            flash("Incorrect Username. Try Again")

    return render_template('login.html', form=form)


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    form = UserForm()
    id = current_user.id
    name_to_update = Users.query.get_or_404(id)

    if request.method == 'POST':
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.fav_color = request.form['fav_color']
        name_to_update.username = request.form['username']

        try:
            db.session.commit()
            flash("User Updated Successfully")

            return render_template('dashboard.html', form=form, name_to_update=name_to_update)

        except:
            flash("Error! Encountered a problem...Try Again")

            return render_template('dashboar.html', form=form, name_to_update=name_to_update)

    else:
        return render_template('dashboard.html', form=form, name_to_update=name_to_update, id=id)


# Create Logout Function/Page
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash("You Have Been Logged Out!")
    return redirect(url_for('login'))

# Users Functions


@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
    name = None
    form = UserForm()

    # Validate Form
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()

        if user is None:
            # Hash the password
            hashed_passwd = generate_password_hash(form.passwd.data, "sha256")

            user = Users(username=form.username.data, name=form.name.data, email=form.email.data,
                         fav_color=form.fav_color.data, passwd=hashed_passwd)
            db.session.add(user)
            db.session.commit()

        name = form.name.data
        form.name.data = ''
        form.username.data = ''
        form.email.data = ''
        form.fav_color.data = ''
        form.passwd.data = ''

        flash("User Added Successfully!")

    our_users = Users.query.order_by(Users.date_added)

    return render_template('add_user.html', form=form, name=name, our_users=our_users)


# Create Password Test Page
@app.route('/test_pw', methods=['GET', 'POST'])
def test_pw():
    email = None
    password = None
    pw_to_check = None
    passed = None
    form = PasswordForm()
    # Validate Form
    if form.validate_on_submit():
        email = form.email.data
        password = form.passwd.data

        # Retrieve User by email from the Database
        pw_to_check = Users.query.filter_by(email=email).first()

        # Check Hashed Password
        passed = check_password_hash(pw_to_check.passwd, password)

        # Clear the form
        form.email.data = ''
        form.passwd.data = ''

        flash("Form Submitted Successfully!")

    return render_template('test_pw.html', email=email, password=password, pw_to_check=pw_to_check, passed=passed, form=form)


# Update Databse Record
@app.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == 'POST':
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.fav_color = request.form['fav_color']
        name_to_update.username = request.form['username']

        try:
            db.session.commit()
            flash("User Updated Successfully")

            return render_template('update.html', form=form, name_to_update=name_to_update, id=id)

        except:
            flash("Error! Encountered a problem...Try Again")

            return render_template('update.html', form=form, name_to_update=name_to_update, id=id)

    else:
        return render_template('update.html', form=form, name_to_update=name_to_update, id=id)


@app.route('/delete/<int:id>')
def delete(id):
    user_to_delete = Users.query.get_or_404(id)
    name = None
    form = UserForm()

    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash("User Deleted Succesfully!")
        our_users = Users.query.order_by(Users.date_added)
        return render_template('add_user.html', form=form, name=name, our_users=our_users)

    except:
        flash("Whoops! Encountered a problem deleting the user")
        return render_template('add_user.html', form=form, name=name, our_users=our_users)


# Add Post Page
@app.route('/add_post', methods=['GET', 'POST'])
@login_required
def add_post():
    form = PostForm()

    if form.validate_on_submit():
        poster = current_user.id
        post = Posts(title=form.title.data,
                     content=form.content.data,
                     post_id=poster,
                     slug=form.slug.data)

        # Clear the Form
        form.title.data = ''
        form.content.data = ''
        form.slug.data = ''

        # Add post to Database
        db.session.add(post)
        db.session.commit()

        # Return message
        flash("Blog Post Submitted Succesfully")

    # Redirect to the webpage
    return render_template("add_post.html", form=form)


@app.route('/posts')
@login_required
def posts():
    posts = Posts.query.order_by(Posts.date_posted)
    return render_template('posts.html', posts=posts)


@app.route('/posts/<int:id>')
@login_required
def post(id):
    post = Posts.query.get_or_404(id)

    return render_template('post.html', post=post)


@app.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    post = Posts.query.get_or_404(id)
    form = PostForm()

    if form.validate_on_submit():
        post.title = form.title.data

        post.slug = form.slug.data
        post.content = form.content.data

        # Update Database
        db.session.add(post)
        db.session.commit()

        flash("Post Updated Succesfully!")

        return redirect(url_for('post', id=post.id))

    if current_user.id == post.post_id:

        form.title.data = post.title
        form.slug.data = post.slug
        form.content.data = post.content

        return render_template('edit_post.html', form=form)
    else:
        flash("You are not authorized to edit this post!!")
        posts = Posts.query.order_by(Posts.date_posted)
        return render_template('posts.html', posts=posts)


@app.route('/posts/delete/<int:id>')
@login_required
def delete_post(id):
    post_to_delete = Posts.query.get_or_404(id)
    id = current_user.id

    if id == post_to_delete.poster.id:
        try:
            db.session.delete(post_to_delete)
            db.session.commit()

            # Return a message
            flash("Post Deleted Succesfully!")

        # Grab all posts from the Database
            posts = Posts.query.order_by(Posts.date_posted)
            return render_template('posts.html', posts=posts)

        except:
            # Return Message on Error
            flash("Whoops! Encountered a problem deleting the post, Try Again...")
            # Grab all posts from the Database
            posts = Posts.query.order_by(Posts.date_posted)
            # Return template
            return render_template('edit_post.html',  posts=posts)
    else:
        # Return a message
        flash("You Aren't Authorized To Delete That Post!!! ")

        # Grab all posts from the Database
        posts = Posts.query.order_by(Posts.date_posted)
        return render_template('posts.html', posts=posts)


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True, port=50100, host='localhost')
