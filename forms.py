from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, SubmitField, FloatField,
    IntegerField, TextAreaField, FileField, SelectField
)
from wtforms.validators import DataRequired, Length, Email, NumberRange, EqualTo

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Register as', choices=[('buyer', 'Buyer'), ('seller', 'Seller')], validators=[DataRequired()])
    submit = SubmitField('Register')

class ProductForm(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired()])
    description = TextAreaField('Description')
    price = FloatField('Price', validators=[DataRequired(), NumberRange(min=0)])
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=0)])
    image = FileField('Product Image')
    submit = SubmitField('Save')

class OrderForm(FlaskForm):
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Buy')

class ProfileForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    background = StringField('Background Info')
    profile_pic = FileField('Profile Picture')
    submit = SubmitField('Save Profile')
