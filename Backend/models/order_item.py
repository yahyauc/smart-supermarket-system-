from models import db

class OrderItem(db.Model):
    __tablename__ = "order_items"

    id           = db.Column(db.Integer, primary_key=True)
    order_id     = db.Column(db.Integer, db.ForeignKey("orders.id"),   nullable=False)
    product_id   = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=True)
    product_name = db.Column(db.String(120), nullable=False)
    price        = db.Column(db.Float,   nullable=False)
    quantity     = db.Column(db.Integer, nullable=False, default=1)

    def to_dict(self):
        return {
            "id":           self.id,
            "product_id":   self.product_id,
            "product_name": self.product_name,
            "price":        self.price,
            "quantity":     self.quantity,
            "subtotal":     round(self.price * self.quantity, 2)
        }
