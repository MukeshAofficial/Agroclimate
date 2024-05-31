from flask import Flask, render_template, request, jsonify
import openai
import requests
from datetime import datetime
from flask import Flask, render_template, request,send_file,jsonify,flash,url_for
import openai
import os
from datetime import datetime
from bs4 import BeautifulSoup
import requests
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from sqlalchemy.exc import IntegrityError
from IPython.display import display, Markdown

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)





class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        try:
            db.session.add(user)
            db.session.commit()
            flash('Your account has been created! You are now able to log in', 'success')
            return redirect(url_for('login'))
        except IntegrityError:
            db.session.rollback()
            flash('An account with this email address already exists. Please use a different email address.', 'danger')
    return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            flash('You have been logged in!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)



# OpenAI API key
openai.api_key = ""

# OpenWeatherMap API key and URL
API_KEY = '73b48ecfece17f28d57b8f06a4dd9306'
URL = 'https://api.openweathermap.org/data/2.5/weather'

# Function to get recommendation from GPT
def get_recommendation(crop, weather):
    prompt = f"Provide agricultural advice for the crop '{crop}' given the weather condition '{weather}'."
    response = openai.Completion.create(
        engine="gpt-3.5-turbo-instruct",
        prompt=prompt,
        max_tokens=150
    )
    return response.choices[0].text.strip()



@app.route('/chatbot')
def chatbot():
    return render_template('chatbot.html')

@app.route('/get_response', methods=['POST'])
def get_response():
    data = request.json
    user_message = data['message']
    response = openai.Completion.create(
        engine="gpt-3.5-turbo-instruct",
        prompt=user_message,
        max_tokens=150
    )
    gpt_response = response.choices[0].text.strip()
    return jsonify({'response': gpt_response})

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/')
def web():
    return render_template('web.html')

@app.route('/wheather')
def index():
    return render_template('index.html')


@app.route('/Agri')
def Agri():
    # Format date in day-month-year format
    for item in news_data:
        # Parse the ISO 8601 formatted date and convert it to day-month-year
        item['date'] = datetime.fromisoformat(item['date'].replace('Z', '+00:00')).strftime('%d-%m-%Y')

    return render_template('news.html', news=news_data)

# API endpoint for news data
url = 'https://oevortex-webscout.hf.space/api/news'
params = {
        'q': 'Agriculture and climate',  # Query parameter
        'max_results': 10,               # Maximum number of results
        'safesearch': 'moderate',        # Safe search option
        'region': 'wt-wt'    # Region parameter
}


headers = {
    'accept': 'application/json'
}

# Get news data from API
response = requests.get(url, params=params, headers=headers)

if response.status_code == 200:
    news_data = response.json()['results']  # Access 'results' key
    # or do something with the data
else:
    print("Error:", response.status_code)

@app.route('/get_recommendation', methods=['POST'])
def recommendation():
    crop = request.form['crop']
    weather = request.form['weather']
    recommendation = get_recommendation(crop, weather)
    return render_template('result.html', crop=crop, weather=weather, recommendation=recommendation)

@app.route('/weather', methods=['GET'])
def weather():
    city = request.args.get('city')
    req_url = f"{URL}?q={city}&appid={API_KEY}"

    response = requests.get(req_url)

    if response.status_code == 200:
        data = response.json()
        return jsonify(data)
    else:
        return jsonify({'message': 'An error occurred'}), response.status_code

if __name__ == '__main__':
    app.run(debug=True)

