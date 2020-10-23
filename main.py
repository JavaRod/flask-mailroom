import os
import base64

from flask import Flask, render_template, request, redirect, url_for, session
from peewee import DoesNotExist
from model import Donation, Donor, User
from passlib.hash import pbkdf2_sha256

app = Flask(__name__)
# app.secret_key = b'\x9d\xb1u\x08%\xe0\xd0p\x9bEL\xf8JC\xa3\xf4J(hAh\xa4\xcdw\x12S*,u\xec\xb8\xb8'
app.secret_key = os.environ.get('SECRET_KEY').encode()

@app.route('/')
def home():
    if 'username' not in session:
        return redirect(url_for('login'))

    return redirect(url_for('all'))

@app.route('/donations/')
def all():
    if 'username' not in session:
        return redirect(url_for('login'))

    donations = Donation.select()
    return render_template('donations.jinja2', donations=donations)

@app.route('/create', methods=['GET', 'POST'])
def create():
    if 'username' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        donor = None
        try:
            donor = Donor.select().where(Donor.name == request.form['name']).get()
        except DoesNotExist:
            donor = Donor(name=request.form['name'])
            donor.save()

        donation = Donation(value=request.form['amount'], donor=donor)
        donation.save()

        return redirect(url_for('home'))
    else:
        return render_template('create.jinja2')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.select().where(User.name == request.form['name']).get()

        if user and pbkdf2_sha256.verify(request.form['password'], user.password):
            session['username'] = request.form['name']
            return redirect(url_for('home'))

        return render_template('login.jinja2', error="Incorrect username or password.")

    else:
        return render_template('login.jinja2')

@app.route('/retrieve')
def retrieve():
    if request.method == 'POST':
        user = User.select().where(User.name == request.form['name']).get()

    name = request.args.get('name', None)

    if name is None:
        return render_template('retrieve.jinja2')
    else:
        donations = Donation.select().join(Donor).where(Donor.name == name)
        return render_template('retrieve.jinja2', donations=donations)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 6738))
    app.run(host='0.0.0.0', port=port)

