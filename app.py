from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from models import db, Stock, User
from forms import StockForm, LoginForm, RegistrationForm

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stock.db'
app.config['SECRET_KEY'] = 'your_secret_key'
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    highest_sales_category = Stock.query.order_by(Stock.quantity.desc()).first()
    return render_template('home.html', category=highest_sales_category)

@app.route('/stock', methods=['GET', 'POST'])
def stock():
    form = StockForm()
    if form.validate_on_submit():
        new_stock = Stock(item_name=form.item_name.data, quantity=form.quantity.data,
                          price=form.price.data, category=form.category.data)
        db.session.add(new_stock)
        db.session.commit()
        return redirect(url_for('stock'))
@app.route('/stock', methods=['GET', 'POST'])
def stock():
    form = StockForm()
    if form.validate_on_submit():
        new_stock = Stock(item_name=form.item_name.data, quantity=form.quantity.data,
                          price=form.price.data, category_id=form.category.data)
        db .session.add(new_stock)
        db.session.commit()
        return redirect(url_for('stock'))
    
    page = request.args.get('page', 1, type=int)
    search_term = request.args.get('search')
    if search_term:
        stocks = Stock.query.filter(Stock.item_name.like(f'%{search_term}%')).paginate(page, per_page=8)
    else:
        stocks = Stock.query.paginate(page, per_page=8)
    return render_template('stock.html', stocks=stocks, form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('home'))
        flash('Invalid username or password')
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        new_user = User(username=form.username.data)
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)