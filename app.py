from flask import Flask, render_template, redirect, url_for, request
from models import db, StockItem

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stock.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

@app.before_request
def create_tables():
    db.create_all()  # Ensure tables are created

@app.route('/')
def home():
    top_items = StockItem.query.order_by(StockItem.quantity.desc()).limit(5).all()  # Get top 5 items
    return render_template('home.html', top_items=top_items)

@app.route('/stock')
def index():
    page = request.args.get('page', 1, type=int)
    items_per_page = 10
    items = StockItem.query.paginate(page=page, per_page=items_per_page, error_out=False)
    return render_template('stock.html', items=items)

@app.route('/add', methods=['GET', 'POST'])
def add_item():
    if request.method == 'POST':
        name = request.form['name']
        quantity = request.form['quantity']
        new_item = StockItem(name=name, quantity=quantity)
        db.session.add(new_item)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_item.html')

@app.route('/delete/<int:item_id>', methods=['POST'])
def delete_item(item_id):
    item_to_delete = StockItem.query.get_or_404(item_id)
    db.session.delete(item_to_delete)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure tables are created
    app.run(debug=True)