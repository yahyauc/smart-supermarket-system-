from flask import Blueprint, request, jsonify
from models import db
from models.order import Order
from models.order_item import OrderItem
from models.product import Product
from models.user import User
from utils.email_service import send_order_confirmation

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

    # Send confirmation email in background with app context
    if user_id:
        user = User.query.get(user_id)
        if user and user.email:
            import threading
            from flask import current_app
            app        = current_app._get_current_object()
            user_email = user.email
            username   = user.username

            # Detach ALL data before entering thread (avoid SQLAlchemy session issues)
            order_id   = order.id
            order_note = order.note or ""
            order_date = order.created_at

            # Calculate total manually from items list already in memory
            order_items = []
            running_total = 0.0
            for i in order.items:
                price    = float(i.price or 0)
                quantity = int(i.quantity or 1)
                subtotal = price * quantity
                running_total += subtotal
                order_items.append({
                    "product_name": i.product_name or "Product",
                    "quantity":     quantity,
                    "price":        price,
                    "subtotal":     subtotal
                })
            order_total = round(running_total, 2)

            def send_in_background():
                with app.app_context():
                    from utils.email_service import send_order_confirmation_data
                    send_order_confirmation_data(
                        user_email, username,
                        order_id, order_total, order_note, order_date, order_items
                    )

            threading.Thread(target=send_in_background, daemon=True).start()

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