from flask import Blueprint, jsonify
from models.product import Product
from models.order import Order
from models.user import User
from datetime import datetime, timedelta
from collections import defaultdict

stats_bp = Blueprint("stats", __name__)


@stats_bp.route("/stats", methods=["GET"])
def get_stats():
    products = Product.query.all()
    orders   = Order.query.all()
    users    = User.query.all()

    total_revenue  = sum(o.get_total() for o in orders)
    low_stock      = [p for p in products if p.stock <= 5]

    # Orders by status
    status_counts = defaultdict(int)
    for o in orders:
        status_counts[o.status] += 1

    # Revenue last 7 days
    today = datetime.utcnow().date()
    revenue_by_day = {}
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        revenue_by_day[day.strftime("%a %d")] = 0.0

    for o in orders:
        delta = (today - o.created_at.date()).days
        if 0 <= delta <= 6:
            label = o.created_at.date().strftime("%a %d")
            revenue_by_day[label] = round(revenue_by_day.get(label, 0) + o.get_total(), 2)

    # Top 5 best-selling products
    sales = defaultdict(lambda: {"name": "", "quantity": 0, "revenue": 0.0})
    for o in orders:
        for item in o.items:
            sales[item.product_id]["name"]     = item.product_name
            sales[item.product_id]["quantity"] += item.quantity
            sales[item.product_id]["revenue"]  = round(
                sales[item.product_id]["revenue"] + item.price * item.quantity, 2
            )
    top_products = sorted(sales.values(), key=lambda x: x["quantity"], reverse=True)[:5]

    # Category stock distribution
    category_stock = defaultdict(int)
    for p in products:
        category_stock[p.category] += p.stock

    return jsonify({
        "total_products":       len(products),
        "total_orders":         len(orders),
        "total_users":          len(users),
        "total_revenue":        round(total_revenue, 2),
        "low_stock_count":      len(low_stock),
        "low_stock_products":   [p.to_dict() for p in low_stock],
        "status_counts":        dict(status_counts),
        "revenue_by_day":       revenue_by_day,
        "top_products":         top_products,
        "category_stock":       dict(category_stock),
        "recent_orders":        [o.to_dict() for o in Order.query.order_by(Order.created_at.desc()).limit(5).all()]
    }), 200


@stats_bp.route("/alerts/simulate", methods=["GET"])
def simulate_ai():
    low_stock    = Product.query.filter(Product.stock <= 5).all()
    out_of_stock = [p for p in low_stock if p.stock == 0]

    alerts = []
    if out_of_stock:
        names = ", ".join(p.name for p in out_of_stock)
        alerts.append(f"🚨 OUT OF STOCK: {names}")

    low = [p for p in low_stock if p.stock > 0]
    if low:
        names = ", ".join(f"{p.name} ({p.stock})" for p in low)
        alerts.append(f"⚠️ LOW STOCK: {names} — restock recommended")

    if alerts:
        return jsonify({"status": "alert", "message": " | ".join(alerts)}), 200

    return jsonify({"status": "ok", "message": "✅ All stock levels are healthy. No action needed."}), 200