from flask import Flask, render_template, flash, request

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length
from werkzeug.security import generate_password_hash, check_password_hash

# DataBase imports
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime

# Create a Flask Instance
app = Flask(__name__)

# Add Database
"""Old SQLite DB"""
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
"""New MySQL db"""
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://username:password@localhost/db_name'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqldb://root:Legend1240s26#@localhost/flask_blog_db'
# Enable Tracking Modifications
app.config['SQLACHEMY_TRCAK_MODIFICATIONS'] = True
# Secret Key!
app.config['SECRET_KEY'] = "Master of Mystic Arts"

# Initialize THe Database
db = SQLAlchemy(app)
migrate = Migrate(app, db)
app.app_context().push()


# Create Model
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100))
    fav_color = db.Column(db.String(40))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    passwd = db.Column(db.String(126), nullable=False)

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


# Create a Form Class
class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    fav_color = StringField("Favourite Color")
    passwd = PasswordField("Password", validators=[
                           DataRequired(), EqualTo("passwd2", message="Password Must Match")])
    passwd2 = PasswordField("Confirm Password", validators=[DataRequired()])
    submit = SubmitField("Submit")


# Create a Form Class
class NamerForm(FlaskForm):
    name = StringField("What's Your Name?", validators=[DataRequired()])
    submit = SubmitField("Submit")


# Create a Password Form Class
class PasswordForm(FlaskForm):
    email = StringField("What's your email", validators=[DataRequired()])
    passwd = PasswordField("What's your password", validators=[DataRequired()])
    submit = SubmitField("Submit")


# Create a route decorator
@app.route('/')
def index():
    first_name = "Sem"
    flash("Welcome to our Website!")
    return render_template('index.html', first_name=first_name)


@app.route('/user/<name>')
def user(name):
    return render_template('user.html', user_name=name)


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
            
            user = Users(name=form.name.data, email=form.email.data,
                         fav_color=form.fav_color.data, passwd=hashed_passwd)
            db.session.add(user)
            db.session.commit()

        name = form.name.data
        form.name.data = ''
        form.email.data = ''
        form.fav_color.data = ''
        form.passwd.data = ''

        flash("User Added Successfully!")

    our_users = Users.query.order_by(Users.date_added)

    return render_template("add_user.html", form=form, name=name, our_users=our_users)


# Create Password Test Page
@app.route('/test_pw', methods=['GET', 'POST'])
def test_pw():
    email= None
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
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == 'POST':
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.fav_color = request.form['fav_color']

        try:
            db.session.commit()
            flash("User Updated Successfully")

            return render_template('update.html', form=form, name_to_update=name_to_update)

        except:
            flash("Error! Encountered a problem...Try Again")

            return render_template('update.html', form=form, name_to_update=name_to_update)

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


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True, port=50100, host='localhost')

