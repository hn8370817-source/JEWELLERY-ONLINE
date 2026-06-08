from flask import Flask, render_template, redirect, url_for, request, flash, session, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
from models import db, User, Category, Product, ProductImage, Subscriber, WishlistItem
from forms import LoginForm, RegisterForm, SubscribeForm
from datetime import datetime
import json

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ---------- Context Processors ----------
@app.context_processor
def inject_globals():
    return dict(
        categories=Category.query.all(),
        subscribe_form=SubscribeForm(),
        cart_count=len(session.get('cart', []))
    )

# ---------- Cart Helper Functions ----------
def get_cart():
    return session.get('cart', [])

def save_cart(cart):
    session['cart'] = cart

def cart_total():
    cart = get_cart()
    total = 0
    for item in cart:
        product = Product.query.get(item['product_id'])
        if product:
            total += product.price * item['quantity']
    return total

# ---------- Routes ----------
@app.route('/')
def index():
    featured = Product.query.order_by(Product.id.desc()).limit(8).all()
    return render_template('index.html', featured=featured)

@app.route('/category/<int:cat_id>')
def category(cat_id):
    cat = Category.query.get_or_404(cat_id)
    products = Product.query.filter_by(category_id=cat_id).all()
    return render_template('category.html', category=cat, products=products)

@app.route('/product/<int:prod_id>')
def product(prod_id):
    prod = Product.query.get_or_404(prod_id)
    return render_template('product.html', product=prod)

# Auth routes same as before...
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegisterForm()
    if form.validate_on_submit():
        existing = User.query.filter((User.email==form.email.data) | (User.username==form.username.data)).first()
        if existing:
            flash('Email or username already exists.')
            return render_template('register.html', form=form)
        user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=generate_password_hash(form.password.data)
        )
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        flash('Invalid email or password')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/subscribe', methods=['POST'])
def subscribe():
    form = SubscribeForm()
    if form.validate_on_submit():
        existing = Subscriber.query.filter_by(email=form.email.data).first()
        if not existing:
            sub = Subscriber(email=form.email.data)
            db.session.add(sub)
            db.session.commit()
            flash('Thank you for subscribing!')
        else:
            flash('You are already subscribed.')
    return redirect(request.referrer or url_for('index'))

# ---------- Cart Routes ----------
@app.route('/add_to_cart/<int:prod_id>', methods=['POST'])
def add_to_cart(prod_id):
    product = Product.query.get_or_404(prod_id)
    if product.stock < 1:
        flash('Sorry, this product is out of stock.')
        return redirect(request.referrer)
    cart = get_cart()
    # check if already in cart
    for item in cart:
        if item['product_id'] == prod_id:
            item['quantity'] += 1
            save_cart(cart)
            flash(f'Added another {product.name} to cart.')
            return redirect(request.referrer)
    cart.append({'product_id': prod_id, 'quantity': 1})
    save_cart(cart)
    flash(f'{product.name} added to cart.')
    return redirect(request.referrer)

@app.route('/cart')
def view_cart():
    cart = get_cart()
    items = []
    for c in cart:
        product = Product.query.get(c['product_id'])
        if product:
            items.append({'product': product, 'quantity': c['quantity']})
    return render_template('cart.html', items=items, total=cart_total())

@app.route('/remove_from_cart/<int:prod_id>', methods=['POST'])
def remove_from_cart(prod_id):
    cart = get_cart()
    cart = [item for item in cart if item['product_id'] != prod_id]
    save_cart(cart)
    flash('Item removed from cart.')
    return redirect(url_for('view_cart'))

@app.route('/buy_now', methods=['POST'])
def buy_now():
    cart = get_cart()
    if not cart:
        flash('Your cart is empty.')
        return redirect(url_for('view_cart'))
    # Simulate purchase: clear cart, show success
    save_cart([])
    flash('Thank you for your order! Your items will be delivered soon. (Demo)')
    return redirect(url_for('index'))

# ---------- Wishlist Routes ----------
@app.route('/wishlist')
@login_required
def wishlist():
    items = WishlistItem.query.filter_by(user_id=current_user.id).all()
    return render_template('wishlist.html', items=items)

@app.route('/add_to_wishlist/<int:prod_id>', methods=['POST'])
@login_required
def add_to_wishlist(prod_id):
    product = Product.query.get_or_404(prod_id)
    existing = WishlistItem.query.filter_by(user_id=current_user.id, product_id=prod_id).first()
    if existing:
        flash('Already in your wishlist.')
    else:
        item = WishlistItem(user_id=current_user.id, product_id=prod_id)
        db.session.add(item)
        db.session.commit()
        flash(f'{product.name} added to wishlist.')
    return redirect(request.referrer)

@app.route('/remove_from_wishlist/<int:item_id>', methods=['POST'])
@login_required
def remove_from_wishlist(item_id):
    item = WishlistItem.query.get_or_404(item_id)
    if item.user_id != current_user.id:
        flash('Unauthorized.')
        return redirect(url_for('wishlist'))
    db.session.delete(item)
    db.session.commit()
    flash('Removed from wishlist.')
    return redirect(url_for('wishlist'))

# ---------- Quick View Data (API) ----------
@app.route('/quick_view/<int:prod_id>')
def quick_view(prod_id):
    product = Product.query.get_or_404(prod_id)
    images = [{'url': img.url, 'alt': img.alt_text or product.name} for img in product.images]
    data = {
        'name': product.name,
        'description': product.description,
        'price': product.price,
        'stock': product.stock,
        'category': product.category.name,
        'images': images
    }
    return jsonify(data)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
