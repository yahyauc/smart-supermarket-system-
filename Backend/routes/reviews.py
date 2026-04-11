from flask import Blueprint, request, jsonify
from models import db
from models.review import Review
from models.product import Product

reviews_bp = Blueprint("reviews", __name__)


@reviews_bp.route("/products/<int:pid>/reviews", methods=["GET"])
def get_reviews(pid):
    reviews = Review.query.filter_by(product_id=pid)\
                          .order_by(Review.created_at.desc()).all()
    avg = round(sum(r.rating for r in reviews) / len(reviews), 1) if reviews else 0
    return jsonify({
        "reviews": [r.to_dict() for r in reviews],
        "count":   len(reviews),
        "average": avg
    }), 200


@reviews_bp.route("/products/<int:pid>/reviews", methods=["POST"])
def add_review(pid):
    product = Product.query.get_or_404(pid)
    data    = request.get_json()

    user_id  = data.get("user_id")
    username = data.get("username", "").strip()
    rating   = data.get("rating")
    comment  = data.get("comment", "").strip()

    if not user_id or not username or not rating or not comment:
        return jsonify({"error": "All fields are required"}), 400

    if not (1 <= int(rating) <= 5):
        return jsonify({"error": "Rating must be between 1 and 5"}), 400

    # One review per user per product
    existing = Review.query.filter_by(product_id=pid, user_id=user_id).first()
    if existing:
        existing.rating  = int(rating)
        existing.comment = comment
        db.session.commit()
        return jsonify({"message": "Review updated", "review": existing.to_dict()}), 200

    review = Review(
        product_id = pid,
        user_id    = user_id,
        username   = username,
        rating     = int(rating),
        comment    = comment
    )
    db.session.add(review)
    db.session.commit()
    return jsonify({"message": "Review added", "review": review.to_dict()}), 201


@reviews_bp.route("/products/<int:pid>/reviews/<int:rid>", methods=["DELETE"])
def delete_review(pid, rid):
    review = Review.query.filter_by(id=rid, product_id=pid).first_or_404()
    db.session.delete(review)
    db.session.commit()
    return jsonify({"message": "Review deleted"}), 200