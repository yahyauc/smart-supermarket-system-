from models import db
from datetime import datetime

class Review(db.Model):
    __tablename__ = "reviews"

    id         = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    user_id    = db.Column(db.Integer, db.ForeignKey("users.id"),    nullable=False)
    username   = db.Column(db.String(80), nullable=False)
    rating     = db.Column(db.Integer, nullable=False)  # 1-5
    comment    = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id":         self.id,
            "product_id": self.product_id,
            "user_id":    self.user_id,
            "username":   self.username,
            "rating":     self.rating,
            "comment":    self.comment,
            "date":       self.created_at.strftime("%B %d, %Y")
        }