from flask import Flask, render_template, request, redirect, session
import pickle
import numpy as np
import mysql.connector
import os
import datetime

app = Flask(__name__)
model = pickle.load(open('model.pkl', 'rb'))

app.secret_key = os.urandom(24)

# conn = mysql.connector.connect(host="localhost", user="root",
#                                password="", database="sales_prediction")


conn = mysql.connector.connect(user="sales_prediction", password="Saurabh@028",
                               host="sales-prediction.mysql.database.azure.com",
                               port=3306, database="sales_prediction")
if conn.is_connected():
    print('connected to database')

cursor = conn.cursor()


@app.route('/')
def login():
    return render_template("login.html")


@app.route('/index')
def index():
    if 'user_id' in session:
        return render_template("index.html")
    else:
        return redirect('/')


@app.route('/register')
def register():
    return render_template('registration.html')


@app.route('/login_validation', methods=['POST'])
def login_validation():
    email = request.form.get('email')
    password = request.form.get('password')

    cursor.execute("""SELECT * FROM signup WHERE email LIKE '{}' AND password LIKE '{}'"""
                   .format(email, password))
    users = cursor.fetchall()
    if len(users) > 0:
        session['user_id'] = users[0][0]
        return redirect('/index')
    else:
        return redirect("/")


@app.route('/add_user', methods=['POST'])
def add_user():
    name = request.form.get('uname')
    email = request.form.get('uemail')
    password = request.form.get('upassword')

    cursor.execute("""INSERT INTO `signup`(`name`, `email`, `password`) VALUES ('{}','{}','{}')"""
                   .format(name, email, password))
    conn.commit()

    cursor.execute("""SELECT * from signup WHERE email LIKE '{}'""".format(email))
    my_user = cursor.fetchall()
    session['user_id'] = my_user[0][0]
    print(session['user_id'])
    return redirect('/index')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    name = request.form.get('name')
    email = request.form.get('email')
    subject = request.form.get('subject')
    message = request.form.get('message')

    cursor.execute("""INSERT INTO contact(name, email, subject, message) VALUES ('{}','{}','{}', '{}')"""
                   .format(name, email, subject, message))
    conn.commit()
    return 'Successful'


@app.route('/analysis')
def analysys():
    return render_template('analysis.html')


@app.route('/logout')
def logout():
    session.pop('user_id')
    return redirect('/')


@app.route('/predict', methods=['GET', 'POST'])
def predict():
    date = request.form['date']
    date = datetime.datetime.strptime(date, '%Y-%m-%d')
    day_of_week = date.weekday()
    day = date.day
    month = date.month
    year = date.year

    open = request.form['open']
    if open == "Yes":
        open = 1
    else:
        open = 0

    state_holiday = request.form['state_holiday']
    if state_holiday == 'Yes':
        state_holiday = 1
    else:
        state_holiday = 0

    school_holiday = request.form['school_holiday']
    if school_holiday == 'Yes':
        school_holiday = 1
    else:
        school_holiday = 0

    promo = request.form['promo']
    if promo == 'Yes':
        promo = 1
    else:
        promo = 0

    store = int(request.form.get('id'))
    store += 8

    x = np.zeros(1123)
    x[0] = day_of_week
    x[1] = open
    x[2] = promo
    x[3] = state_holiday
    x[4] = school_holiday
    x[5] = year
    x[6] = month
    x[7] = day

    x[store] = 1

    prediction = model.predict([x])[0]
    if open == 0:
        prediction = 0

    prediction_text = 'Your Prediction for day '+ str(date.date())+'is '+ str(prediction)
    return render_template('index.html', prediction_text= prediction_text)

if __name__ == "__main__":
    app.run(debug=True)
