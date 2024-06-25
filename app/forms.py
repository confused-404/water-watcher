from flask_wtf import FlaskForm
from wtforms import FloatField, SelectField, StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
import sqlalchemy as sa
from app import db
from app.models import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')
    
class RegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_email(self, email):
        user = db.session.scalar(sa.select(User).where(
            User.email == email.data))
        if user is not None:
            raise ValidationError('Please use a different email address.')
        
class WaterUsageForm(FlaskForm):
    time_taken = FloatField('Time taken in Minutes', validators=[DataRequired()])
    usage_type = SelectField('Usage Type', validators=[DataRequired()], choices=[
        ('shower', 'Shower'),
        ('washing_dishes', 'Washing Dishes'),
        ('washing_clothes', 'Washing Clothes'),
        ('flushing_toilet', 'Flushing Toilet'),
        ('drinking', 'Drinking'),
        ('other', 'Other'),
    ])
    submit = SubmitField('Submit')
    
    def validate_time_taken(self, time_taken):
        if time_taken.data <= 0:
            raise ValidationError('Time taken must be greater than 0')
        if not isinstance(time_taken.data, float):
            raise ValidationError('Time taken must be a number')