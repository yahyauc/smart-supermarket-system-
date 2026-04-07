from flask import Blueprint, request, jsonify
from models import db
from models.product import Product

products_bp = Blueprint("products", __name__)


@products_bp.route("/products", methods=["GET"])
def get_products():
    category = request.args.get("category")
    search   = request.args.get("search", "").strip()

    query = Product.query

    if category:
        query = query.filter_by(category=category)

    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))

    products = query.order_by(Product.name).all()
    return jsonify([p.to_dict() for p in products]), 200


@products_bp.route("/products/categories", methods=["GET"])
def get_categories():
    rows = db.session.query(Product.category).distinct().all()
    return jsonify([r[0] for r in rows]), 200


@products_bp.route("/products/<int:pid>", methods=["GET"])
def get_product(pid):
    p = Product.query.get_or_404(pid)
    return jsonify(p.to_dict()), 200


@products_bp.route("/products", methods=["POST"])
def add_product():
    data = request.get_json()

    name     = data.get("name", "").strip()
    category = data.get("category", "").strip()
    price    = data.get("price")
    stock    = data.get("stock")

    if not name or not category or price is None or stock is None:
        return jsonify({"error": "name, category, price and stock are required"}), 400

    if float(price) < 0 or int(stock) < 0:
        return jsonify({"error": "Price and stock must be positive"}), 400

    product = Product(
        name        = name,
        category    = category,
        price       = float(price),
        stock       = int(stock),
        description = data.get("description", ""),
        image_url   = data.get("image_url", "")
    )
    db.session.add(product)
    db.session.commit()

    return jsonify({"message": "Product added", "product": product.to_dict()}), 201


@products_bp.route("/products/<int:pid>", methods=["PUT"])
def update_product(pid):
    product = Product.query.get_or_404(pid)
    data    = request.get_json()

    product.name        = data.get("name",        product.name)
    product.category    = data.get("category",    product.category)
    product.price       = float(data.get("price", product.price))
    product.stock       = int(data.get("stock",   product.stock))
    product.description = data.get("description", product.description)
    product.image_url   = data.get("image_url",   product.image_url)

    db.session.commit()
    return jsonify({"message": "Product updated", "product": product.to_dict()}), 200


@products_bp.route("/products/<int:pid>", methods=["DELETE"])
def delete_product(pid):
    product = Product.query.get_or_404(pid)
    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": "Product deleted"}), 200
