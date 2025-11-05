import os
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import (
    LoginManager, login_user, logout_user, login_required, current_user
)
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Product, Order, CartItem
from forms import RegisterForm, LoginForm, ProfileForm, ProductForm
from flask_mail import Mail
from datetime import datetime

import forms
from importlib import reload
reload(forms)
print("🔁 Reloaded ProductForm definition:", hasattr(forms.ProductForm, "quantity"))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}


def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_secret_key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'DATABASE_URL', 'sqlite:///agrimarket.db'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = 'static/uploads'
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = (
        'AgriMarket PH', os.environ.get('MAIL_USERNAME')
    )

    db.init_app(app)
    mail = Mail(app)

    login_manager = LoginManager(app)
    login_manager.login_view = 'login'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    with app.app_context():
        db.create_all()

    @app.route('/')
    def home():
        products = Product.query.all()
        return render_template('index.html', products=products)

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        form = RegisterForm()
        if form.validate_on_submit():
            existing_user = User.query.filter_by(email=form.email.data).first()
            if existing_user:
                flash('Email already exists', 'danger')
                return redirect(url_for('register'))

            hashed_pw = generate_password_hash(form.password.data)
            new_user = User(
                username=form.username.data,
                email=form.email.data,
                password=hashed_pw,
                role=form.role.data
            )

            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully! You can now log in.', 'success')
            return redirect(url_for('login'))

        return render_template('register.html', form=form)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user and check_password_hash(user.password, form.password.data):
                login_user(user)
                flash('Login successful!', 'success')
                return redirect(url_for('home'))
            else:
                flash('Invalid email or password', 'danger')
        return render_template('login.html', form=form)

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('Logged out successfully!', 'info')
        return redirect(url_for('login'))

    @app.route('/profile', methods=['GET', 'POST'])
    @login_required
    def profile():
        form = ProfileForm()
        if form.validate_on_submit():
            if form.display_name.data:
                current_user.username = form.display_name.data
            current_user.location = form.location.data

            if 'profile_image' in request.files:
                f = request.files['profile_image']
                if f and allowed_file(f.filename):
                    filename = secure_filename(f.filename)
                    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    f.save(path)
                    current_user.profile_image = f'/static/uploads/{filename}'

            if 'background_image' in request.files:
                f = request.files['background_image']
                if f and allowed_file(f.filename):
                    filename = secure_filename(f.filename)
                    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    f.save(path)
                    current_user.background_image = f'/static/uploads/{filename}'

            db.session.commit()
            flash('Profile updated!', 'success')
            return redirect(url_for('profile'))

        form.display_name.data = current_user.username
        form.location.data = current_user.location
        return render_template('profile.html', form=form, user=current_user)

    @app.route('/cart')
    @login_required
    def view_cart():
        if current_user.role != 'buyer':
            flash('Only buyers can access the cart.', 'danger')
            return redirect(url_for('home'))

        items = CartItem.query.filter_by(user_id=current_user.id).all()
        total = sum((item.product.price or 0) * item.quantity for item in items)
        return render_template('cart.html', items=items, total=total)

    @app.route('/cart/add/<int:product_id>', methods=['POST'])
    @login_required
    def add_to_cart(product_id):
        if current_user.role != 'buyer':
            flash('Only buyers can add items to cart.', 'danger')
            return redirect(url_for('home'))

        product = Product.query.get_or_404(product_id)
        if product.seller_id == current_user.id:
            flash("You can't buy your own product.", 'warning')
            return redirect(url_for('home'))

        existing = CartItem.query.filter_by(
            user_id=current_user.id, product_id=product.id
        ).first()
        if existing:
            existing.quantity += 1
        else:
            db.session.add(
                CartItem(user_id=current_user.id, product_id=product.id, quantity=1)
            )
        db.session.commit()
        flash(f'{product.name} added to cart!', 'success')
        return redirect(request.referrer or url_for('home'))

    @app.route('/cart/remove/<int:item_id>', methods=['POST'])
    @login_required
    def remove_from_cart(item_id):
        if current_user.role != 'buyer':
            flash('Only buyers can remove items from cart.', 'danger')
            return redirect(url_for('home'))

        item = CartItem.query.get_or_404(item_id)
        if item.user_id != current_user.id:
            flash('Unauthorized action.', 'danger')
            return redirect(url_for('view_cart'))
        db.session.delete(item)
        db.session.commit()
        flash('Item removed from cart.', 'info')
        return redirect(url_for('view_cart'))

    @app.route('/cart/checkout', methods=['POST'])
    @login_required
    def checkout():
        if current_user.role != 'buyer':
            flash('Only buyers can checkout.', 'danger')
            return redirect(url_for('home'))

        items = CartItem.query.filter_by(user_id=current_user.id).all()
        if not items:
            flash('Your cart is empty.', 'warning')
            return redirect(url_for('view_cart'))

        for item in items:
            if item.product.quantity < item.quantity:
                flash(f'Not enough stock for {item.product.name}', 'danger')
                return redirect(url_for('view_cart'))

        for item in items:
            total_price = item.product.price * item.quantity
            order = Order(
                buyer_id=current_user.id,
                product_id=item.product.id,
                quantity=item.quantity,
                total_price=total_price,
                status='Pending'
            )
            item.product.quantity -= item.quantity
            db.session.add(order)
            db.session.delete(item)

        db.session.commit()
        flash('Checkout complete! Thank you for your order.', 'success')
        return render_template('checkout_success.html')


    @app.route('/seller/add-product', methods=['GET', 'POST'])
    @login_required
    def add_product():
        if current_user.role != 'seller':
            flash('Access denied. Only sellers can add products.', 'danger')
            return redirect(url_for('home'))

        form = ProductForm()
        if form.validate_on_submit():
            filename = None
            if form.image.data and allowed_file(form.image.data.filename):
                filename = secure_filename(form.image.data.filename)
                form.image.data.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            new_product = Product(
                name=form.name.data,
                description=form.description.data,
                price=form.price.data,
                quantity=form.quantity.data,
                image=f'static/uploads/{filename}' if filename else None,
                seller_id=current_user.id
            )
            db.session.add(new_product)
            db.session.commit()
            flash('Product added successfully!', 'success')
            return redirect(url_for('my_products'))

        return render_template('add_product.html', form=form)

    @app.route('/seller/my-products')
    @login_required
    def my_products():
        if current_user.role != 'seller':
            flash('Access denied.', 'danger')
            return redirect(url_for('home'))

        products = Product.query.filter_by(seller_id=current_user.id).all()
        return render_template('my_products.html', products=products)

    @app.route('/orders')
    @login_required
    def order_history():
        if current_user.role != 'buyer':
            flash('Access denied: only buyers can view order history.', 'danger')
            return redirect(url_for('home'))

        orders = Order.query.filter_by(buyer_id=current_user.id).all()
        return render_template('buyer_orders.html', orders=orders)

    @app.route('/seller/orders')
    @login_required
    def seller_orders():
        if current_user.role != 'seller':
            flash('Access denied: only sellers can view customer orders.', 'danger')
            return redirect(url_for('home'))

        orders = (
            Order.query.join(Product)
            .filter(Product.seller_id == current_user.id)
            .all()
        )
        return render_template('seller_orders.html', orders=orders)

    @app.route('/healthz')
    def health_check():
        return "OK", 200

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
