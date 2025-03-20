from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FloatField, TextAreaField, SelectField, BooleanField, SelectMultipleField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(), 
        Length(min=3, max=80)
    ])
    email = StringField('Email', validators=[
        DataRequired(), 
        Email()
    ])
    password = PasswordField('Password', validators=[
        DataRequired(), 
        Length(min=6)
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(), 
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(), 
        Email()
    ])
    password = PasswordField('Password', validators=[
        DataRequired()
    ])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')

class WineForm(FlaskForm):
    name = StringField('Wine Name', validators=[DataRequired()])
    type = SelectField('Wine Type', choices=[
        ('Red', 'Red Wine'), 
        ('White', 'White Wine'), 
        ('Rosé', 'Rosé Wine'), 
        ('Sparkling', 'Sparkling Wine')
    ])
    region = StringField('Region', validators=[DataRequired()])
    vintage = StringField('Vintage')
    price = FloatField('Price', validators=[DataRequired()])
    description = TextAreaField('Description')
    image_url = StringField('Image URL')
    submit = SubmitField('Add Wine')

class ReviewForm(FlaskForm):
    rating = SelectField('Rating', choices=[
        (1, '1 Star'), 
        (2, '2 Stars'), 
        (3, '3 Stars'), 
        (4, '4 Stars'), 
        (5, '5 Stars')
    ], coerce=int)
    comment = TextAreaField('Review')
    submit = SubmitField('Submit Review')

class SignupForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=3, max=50)
    ])
    email = StringField('Email', validators=[
        DataRequired(),
        Email()
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=6)
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    traits = SelectMultipleField('Wine Preferences', coerce=int)

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')