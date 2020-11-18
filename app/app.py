from flask import Flask, Response, render_template, url_for, request, session, redirect, flash, abort
from flask_pymongo import PyMongo
import json
import os
import bcrypt
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, NoneOf
from dotenv import load_dotenv
from flask_mail import Mail, Message
import requests


app = Flask(__name__)

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = os.getenv('GMAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('GMAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True

mail = Mail(app)

road_map_dir = os.path.expanduser('/Users/diye/PycharmProjects/MachineLearning/RoadMap')
load_dotenv(os.path.join(road_map_dir, '.env'))

map_api_key = os.getenv('ADDIS_SQUID_GOOGLE_MAPS_API_KEY')

# app.config["MONGO_URI"] = "mongodb://localhost:27017/testdb"
mongo_users = PyMongo(app, uri = 'mongodb://localhost:27017/testdb')
mongo_road_data = PyMongo(app, uri = 'mongodb://localhost:27017/addissquid_db')

class AddUserForm(FlaskForm):
    first_name = StringField('First Name',validators = [DataRequired(), Length(min=2, max=20)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=20)])
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=64)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Add')

class LoginForm(FlaskForm):
    username = StringField('Username', validators = [DataRequired(), Length(min=2, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField('Password', validators = [DataRequired(), Length(min=8, max=64)], render_kw={"placeholder": "Password"})
    submit = SubmitField('Login')

class InviteUserForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Invite')


hashpass = bcrypt.hashpw('adminpass101'.encode('utf-8'), bcrypt.gensalt())

# users = mongo_users.db.users
    # users.insert({
    #     'FName': 'Admin',
    #     'LName': 'Admin',
    #     'UName': 'admin',
    #     'Password': hashpass,
    #     'IsAdmin': 1
    # })
    # for x in users.find():
    #     print(x)
    # users.delete_one({"UName": "admin"})
    # users.delete_one({"UName": "admin"})
    # users.delete_one({"UName": "new_admin"})
    # for x in users.find():
    #     print(x)

@app.route("/")
def index():
    if 'username' in session:
        return render_template("index.html", username = session['username'],isAdmin = session['IsAdmin'])
    return redirect(url_for('login'))

@app.route("/login", methods=['POST', 'GET'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            users = mongo_users.db.users
            login_user = users.find_one({'UName': request.form['username']})

            if login_user:
                if bcrypt.hashpw(request.form['password'].encode('utf-8'), login_user['Password']) == login_user['Password']:
                    session['username'] = request.form['username']
                    session['IsAdmin'] = login_user['IsAdmin']
                    flash(f'Welcome {form.username.data}!', 'success')
                    return redirect(url_for('index'))
    else:
        if 'username' in session:
            return redirect(url_for('index'))
        # return render_template("login.html")
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    # if 'username' in session:
    #     session.pop('username')
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/delete_user/<username>')
def delete_user(username):
    if 'username' in session:
        if session['IsAdmin'] == 1:
            users = mongo_users.db.users
            if username == 'admin':
                flash(f'Unable to Delete User {username}', 'danger')
            else:
                users.delete_one({'UName': username})
                flash(f'Account {username} Deleted!', 'success')
            return redirect(url_for('users'))
        else:
            abort(404)
    return redirect(url_for('login'))

@app.route('/active_map')
def active_map():
    if 'username' in session:
        road_data = mongo_road_data.db.addissquid_data
        documents = road_data.find()
        response = []
        for document in documents:
            document['_id'] = str(document['_id'])
            response.append(document['lat_lng'])

        print(response)
        return render_template("active_map.html", isAdmin = session['IsAdmin'], len = len(response), map_api_key = map_api_key, road_data = response)
    return redirect(url_for('login'))
    # return render_template('active_map.html')

@app.route('/archived_map')
def archived_map():
    if 'username' in session:
        road_data = mongo_road_data.db.addissquid_data
        documents = road_data.find()
        response = []
        for document in documents:
            document['_id'] = str(document['_id'])
            response.append(document['lat_lng'])

        print(response)
        return render_template("archived_map.html", isAdmin = session['IsAdmin'], len = len(response), map_api_key = map_api_key, road_data = response)
    return redirect(url_for('login'))
    # return render_template('archived_map.html')

@app.route('/add_user', methods=['POST', 'GET'])
def add_user():
    form = AddUserForm()
    if 'username' in session:
        if session['IsAdmin'] == 1:
            if request.method == 'POST':
                if form.validate_on_submit():
                    users = mongo_users.db.users
                    existing_user = users.find_one({'UName': request.form['username']})
                    if existing_user is None:
                        hashpass = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())
                        users.insert({
                            'FName': request.form['first_name'],
                            'LName': request.form['last_name'],
                            'Email': request.form['email'],
                            'UName': request.form['username'],
                            'Password': hashpass,
                            'IsAdmin': 0
                        })
                        flash(f'Account created for {form.username.data}!', 'success')
                        return redirect(url_for('add_user'))

                    flash(f'User {form.username.data} Already Exists!', 'danger')
                    return redirect(url_for('add_user'))

            return render_template('add_user.html', form=form, isAdmin = session['IsAdmin'])
        else:
            abort(404)
    return redirect(url_for('login'))

@app.route('/invite_user', methods=['POST', 'GET'])
def invite_user():
    invite_form = InviteUserForm()
    signup_form = AddUserForm()
    if 'username' in session:
        if session['IsAdmin'] == 1:
            if request.method == 'POST':
                if invite_form.validate_on_submit():
                    msg = Message('Test Message',
                                  sender="diyye101@gmail.com",
                                  recipients=["diyedev@gmail.com"])
                    msg.body = "http://127.0.0.1:5000/signup"
                    # msg.html = render_template('signup.html', form=signup_form)
                    mail.send(msg)

                    flash(f'User {invite_form.email.data} invited!', 'success')
                    return redirect(url_for('invite_user'))

            return render_template('invite_user.html', form=invite_form, isAdmin = session['IsAdmin'])
        else:
            abort(404)
    return redirect(url_for('login'))

@app.route('/signup', methods=['POST', 'GET'])
def sign_up():
    form = AddUserForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            users = mongo_users.db.users
            existing_user = users.find_one({'UName': request.form['username']})
            if existing_user is None:
                hashpass = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())
                users.insert({
                    'FName': request.form['first_name'],
                    'LName': request.form['last_name'],
                    'Email': request.form['email'],
                    'UName': request.form['username'],
                    'Password': hashpass,
                    'IsAdmin': 0
                })
                flash(f'Account created for {form.username.data}!', 'success')
                return redirect(url_for('login'))

            flash(f'User {form.username.data} Already Exists!', 'danger')
            return redirect(url_for('login'))

    return render_template('signup.html', form=form)

@app.route('/users')
def users():
    if 'username' in session:
        if session['IsAdmin'] == 1:
            users = mongo_users.db.users
            documents = users.find()
            response = []
            for document in documents:
                document['_id'] = str(document['_id'])
                response.append(document)
            print(response)
            return render_template("users.html", isAdmin=session['IsAdmin'], len = len(response), users = response)
    #     return render_template("users.html", isAdmin = session['IsAdmin'])
    # return redirect(url_for('login'))
        else:
            abort(404)
    return redirect(url_for('login'))

@app.route('/device')
def device():
    if 'username' in session:
        if session['IsAdmin'] == 1:
            # pie_address = "http://192.168.43.90:5000/location"
            # response = requests.get(pie_address)
            # lat_lng = response.json()
            # users = mongo_users.db.users
            # documents = users.find()
            # response = []
            # for document in documents:
            #     document['_id'] = str(document['_id'])
            #     response.append(document)
            # print(response)
            return render_template("device.html", isAdmin=session['IsAdmin'])
    #     return render_template("users.html", isAdmin = session['IsAdmin'])
    # return redirect(url_for('login'))
        else:
            abort(404)
    return redirect(url_for('login'))

@app.route('/start_all_services')
def start_services():
    if 'username' in session:
        if session['IsAdmin'] == 1:
            pie_address = "http://192.168.43.90:5000"
            response = requests.get(pie_address)
            print(response.json())
            response_json = response.json()
            # print(response_json['status'])
            if response_json['status']:
                flash("All Services Started Successfully", 'success')
            else:
                flash("Strating Services Failed", 'danger')
            return render_template("device.html", isAdmin=session['IsAdmin'])
    #     return render_template("users.html", isAdmin = session['IsAdmin'])
    # return redirect(url_for('login'))
        else:
            abort(404)
    return redirect(url_for('login'))

@app.route('/stop_all_services')
def stop_services():
    if 'username' in session:
        if session['IsAdmin'] == 1:
            pie_address = "http://192.168.43.90:5000/stop"
            requests.get(pie_address)

            # response = requests.get(pie_address)
            # print(response.json())
            return render_template("device.html", isAdmin=session['IsAdmin'])
    #     return render_template("users.html", isAdmin = session['IsAdmin'])
    # return redirect(url_for('login'))
        else:
            abort(404)
    return redirect(url_for('login'))




@app.errorhandler(404)
def page_not_found(error):
    if 'username' in session:
        return render_template('error.html', title = '404', isAdmin = session['IsAdmin']), 404
    return redirect(url_for('login'))



# @app.route('/data')
# def get_data():
#     documents = mongo.db.users.find()
#     response = []
#     for document in documents:
#         document['_id'] = str(document['_id'])
#         response.append(document)
#     return json.dumps(response)


# @app.errorhandler(404)
# def page_not_found_error(error):
#     return render_template('error.html', error=error)
#
# @app.errorhandler(500)
# def internal_server_error(error):
#     return render_template('error.html', error=error)


if __name__ == '__main__':
    app.secret_key = 'mysecret'
    app.run()
    # app.run(host= "192.168.0.194", port="5000")
    # app.run(host="192.168.43.205", port="5000")
