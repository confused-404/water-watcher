from urllib.parse import urlsplit
from flask import flash, redirect, render_template, request, url_for
from app import app, db
from app.forms import LoginForm, RegistrationForm, WaterUsageForm
from flask_login import current_user, login_required, login_user, logout_user
import sqlalchemy as sa
from app.models import User, WaterUsage
import json

with open('app/usage_rates.json', 'r') as f:
    usage_rates = json.load(f)

@app.route('/')
@app.route('/index')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html', title='Home')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(first_name=form.first_name.data, last_name=form.last_name.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('You are now registered! Thanks for your commitment to save the Earth!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.email == form.email.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid email or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('dashboard')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/user/<id>')
@login_required
def user(id):
    user = db.first_or_404(sa.select(User).where(User.id == id))
    water_usages = db.session.query(WaterUsage).filter(WaterUsage.user == user).all()
    return render_template('user.html', title='User', user=user, water_usages=water_usages)

@app.route('/dashboard')
@login_required
def dashboard():
    print(current_user.id)
    all_water_usages = db.session.query(WaterUsage).all()
    return render_template('dashboard.html', title='Dashboard', water_usages=all_water_usages)

@app.route('/leaderboards')
@login_required
def leaderboards():
    return render_template('leaderboards.html', title='Leaderboards')

@app.route('/log', methods=['GET', 'POST'])
@login_required
def log():
    form = WaterUsageForm()
    if form.validate_on_submit():
        amount = form.time_taken.data * usage_rates[form.usage_type.data]
        water_usage = WaterUsage(time_taken=form.time_taken.data, usage_type=form.usage_type.data, amount=amount, user=current_user)
        db.session.add(water_usage)
        db.session.commit()
        flash("Water usage logged!")
        return redirect(url_for('dashboard'))
    return render_template('log.html', title='Log', form=form)

@app.route('/charts')
@login_required
def charts():
    return render_template('charts.html', title='Charts')