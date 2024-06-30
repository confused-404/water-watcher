from urllib.parse import urlsplit
from flask import flash, redirect, render_template, request, url_for
import pandas as pd
from app import app, db
from app.chart_generation.stacked_bar import bucket_data, save_chart
from app.forms import LoginForm, RegistrationForm, WaterUsageForm
from flask_login import current_user, login_required, login_user, logout_user
import sqlalchemy as sa
from app.models import User, WaterUsage
import json

from app.tips_generation.generate_tips import generate_tips

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
    water_usages.reverse()
    return render_template('user.html', title='User', user=user, water_usages=water_usages)

@app.route('/dashboard')
@login_required
def dashboard():
    print(current_user.id)
    all_water_usages = db.session.query(WaterUsage).all()
    all_water_usages.reverse()
    return render_template('dashboard.html', title='Dashboard', water_usages=all_water_usages)

@app.route('/leaderboards')
@login_required
def leaderboards():
    def get_leaderboard_data():
        return enumerate((db.session.query(User.id, User.first_name, User.last_name, sa.func.sum(WaterUsage.amount))
            .join(WaterUsage, User.id == WaterUsage.user_id)
            .group_by(User.id)
            .having(sa.func.sum(WaterUsage.amount) > 0)
            .order_by(sa.func.sum(WaterUsage.amount))
            .all()
        ), start=1)
    
    global_leaderboard = get_leaderboard_data()
    return render_template('leaderboards.html', title='Leaderboards', enumerated_leaderboard=global_leaderboard)

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
    user = db.session.get(User, current_user.id)
    query = user.water_usages.select()
    water_usages = db.session.scalars(query)
    
    input_dict = []
    for water_usage in water_usages:
        input_dict.append(
            {
                "usage_type": water_usage.usage_type,
                "amount": water_usage.amount,
                "timestamp": water_usage.timestamp,
            }
        )
        
    raw_data = pd.DataFrame(input_dict)
    # raw_data = pd.read_json("app/test_data.json")
    
    paths = {}
    week_data, bucket_labels = bucket_data(raw_data, 7)
    if len(bucket_labels) != 0:
        paths['week'] = save_chart(week_data, bucket_labels, "week", current_user.id).replace("app/", "")
    
    month_data, bucket_labels = bucket_data(raw_data, 30)
    if len(bucket_labels) != 0:
        paths['month'] = save_chart(month_data, bucket_labels, "month", current_user.id).replace("app/", "")
    
    year_data, bucket_labels = bucket_data(raw_data, 365)
    if len(bucket_labels) != 0:
        paths['year'] = save_chart(year_data, bucket_labels, "year", current_user.id).replace("app/", "")
    
    return render_template('charts.html', title='Charts', chart_paths=paths)

@app.route('/tips')
@login_required
def tips():
    tips = generate_tips()
    return render_template('tips.html', title='Tips', tips=tips)