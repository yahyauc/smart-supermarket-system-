from models import db
from datetime import datetime

class Order(db.Model):
    __tablename__ = "orders"

    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    status     = db.Column(db.String(50), nullable=False, default="pending")
    note       = db.Column(db.Text, nullable=True, default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    items = db.relationship("OrderItem", backref="order", lazy=True, cascade="all, delete-orphan")

    def get_total(self):
        return round(sum(item.price * item.quantity for item in self.items), 2)

    def to_dict(self):
        return {
            "id":         self.id,
            "user_id":    self.user_id,
            "status":     self.status,
            "note":       self.note,
            "total":      self.get_total(),
            "date":       self.created_at.strftime("%Y-%m-%d %H:%M"),
            "items":      [item.to_dict() for item in self.items]
        }
