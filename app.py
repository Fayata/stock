from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import db, User, Stock, StockCategory
from forms import LoginForm, RegistrationForm, StockForm
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stock.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create tables
def init_db():
    with app.app_context():
        db.create_all()
        # Create default category if it doesn't exist
        if not StockCategory.query.first():
            default_category = StockCategory(name='General', description='Default category')
            db.session.add(default_category)
            db.session.commit()

# Routes
@app.route('/')
def home():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    # Get the category with highest stock quantity
    highest_category = db.session.query(
        StockCategory,
        db.func.sum(Stock.quantity).label('total_quantity')
    ).join(Stock).group_by(StockCategory).order_by(
        db.desc('total_quantity')
    ).first()
    return render_template('home.html', highest_category=highest_category)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Login successful!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        flash('Invalid username or password', 'danger')
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already exists', 'danger')
            return render_template('register.html', form=form)
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/stock', methods=['GET', 'POST'])
@login_required
def stock():
    form = StockForm()
    # Populate category choices
    form.category.choices = [(c.id, c.name) for c in StockCategory.query.all()]
    
    if form.validate_on_submit():
        stock = Stock(
            item_name=form.item_name.data,
            quantity=form.quantity.data,
            price=form.price.data,
            category_id=form.category.data
        )
        db.session.add(stock)
        db.session.commit()
        flash('Stock item added successfully!', 'success')
        return redirect(url_for('stock'))

    page = request.args.get('page', 1, type=int)
    stocks = Stock.query.paginate(page=page, per_page=8)
    return render_template('stock.html', form=form, stocks=stocks)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)