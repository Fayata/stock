from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class StockItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<StockItem {self.name}>'