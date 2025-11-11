from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, SubmitField, IntegerField,
    TextAreaField, DecimalField, FileField, SelectField
)
from wtforms.validators import DataRequired, Length, Email, NumberRange, EqualTo
from flask_wtf.file import FileAllowed

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
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
    description = TextAreaField('Description', validators=[DataRequired()])
    price = DecimalField('Price', validators=[DataRequired(), NumberRange(min=0)])
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=0)])
    image = FileField('Product Image', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Images only!')])
    submit = SubmitField('Add Product')

class OrderForm(FlaskForm):
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Buy')

class ProfileForm(FlaskForm):
    display_name = StringField('Display Name', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    background = StringField('Background Info')
    profile_pic = FileField('Profile Picture', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Images only!')])
    submit = SubmitField('Save Profile')
