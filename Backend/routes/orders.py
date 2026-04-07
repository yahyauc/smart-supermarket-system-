from flask import Blueprint, request, jsonify
from models import db
from models.order import Order
from models.order_item import OrderItem
from models.product import Product

orders_bp = Blueprint("orders", __name__)

VALID_STATUSES = ["pending", "confirmed", "shipped", "delivered", "cancelled"]


@orders_bp.route("/orders", methods=["GET"])
def get_all_orders():
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return jsonify([o.to_dict() for o in orders]), 200


@orders_bp.route("/orders/user/<int:user_id>", methods=["GET"])
def get_user_orders(user_id):
    orders = Order.query.filter_by(user_id=user_id)\
                        .order_by(Order.created_at.desc()).all()
    return jsonify([o.to_dict() for o in orders]), 200


@orders_bp.route("/orders/<int:oid>", methods=["GET"])
def get_order(oid):
    order = Order.query.get_or_404(oid)
    return jsonify(order.to_dict()), 200


@orders_bp.route("/orders", methods=["POST"])
def create_order():
    data    = request.get_json()
    user_id = data.get("user_id")
    items   = data.get("items", [])
    note    = data.get("note", "")

    if not items:
        return jsonify({"error": "Order must contain at least one item"}), 400

    order = Order(user_id=user_id, status="pending", note=note)
    db.session.add(order)
    db.session.flush()

    for item in items:
        product  = Product.query.get(item.get("product_id"))
        quantity = int(item.get("quantity", 1))

        if not product:
            db.session.rollback()
            return jsonify({"error": f"Product ID {item.get('product_id')} not found"}), 404

        if product.stock < quantity:
            db.session.rollback()
            return jsonify({"error": f"Not enough stock for '{product.name}' (available: {product.stock})"}), 400

        product.stock -= quantity

        db.session.add(OrderItem(
            order_id     = order.id,
            product_id   = product.id,
            product_name = product.name,
            price        = product.price,
            quantity     = quantity
        ))

    db.session.commit()
    return jsonify({"message": "Order placed successfully", "order": order.to_dict()}), 201


@orders_bp.route("/orders/<int:oid>/status", methods=["PUT"])
def update_status(oid):
    order  = Order.query.get_or_404(oid)
    data   = request.get_json()
    status = data.get("status")

    if status not in VALID_STATUSES:
        return jsonify({"error": f"Invalid status. Use one of: {VALID_STATUSES}"}), 400

    order.status = status
    db.session.commit()
    return jsonify({"message": "Status updated", "order": order.to_dict()}), 200
