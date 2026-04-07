from flask import Blueprint, request, jsonify
from models.product import Product
from models.order import Order
from models.user import User
from models import db
from datetime import datetime
from collections import defaultdict
from groq import Groq
import os

chatbot_bp = Blueprint("chatbot", __name__)

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Fastest + most capable Groq model
GROQ_MODEL = "llama-3.3-70b-versatile"


def build_store_context():
    """Fetch real data from DB and build a context string for the AI."""

    products = Product.query.all()
    orders   = Order.query.all()
    users    = User.query.filter_by(role="customer").all()

    total_revenue = round(sum(o.get_total() for o in orders), 2)
    today         = datetime.utcnow().date()
    revenue_7d    = round(sum(o.get_total() for o in orders if (today - o.created_at.date()).days <= 6),  2)
    revenue_30d   = round(sum(o.get_total() for o in orders if (today - o.created_at.date()).days <= 29), 2)

    status_counts = defaultdict(int)
    for o in orders:
        status_counts[o.status] += 1

    sales = defaultdict(lambda: {"name": "", "qty": 0, "revenue": 0.0})
    for o in orders:
        for item in o.items:
            sales[item.product_id]["name"]    = item.product_name
            sales[item.product_id]["qty"]    += item.quantity
            sales[item.product_id]["revenue"] = round(
                sales[item.product_id]["revenue"] + item.price * item.quantity, 2
            )
    top5 = sorted(sales.values(), key=lambda x: x["qty"], reverse=True)[:5]

    low_stock    = [p for p in products if 0 < p.stock <= 5]
    out_of_stock = [p for p in products if p.stock == 0]

    cat_data = defaultdict(lambda: {"count": 0, "stock": 0})
    for p in products:
        cat_data[p.category]["count"] += 1
        cat_data[p.category]["stock"] += p.stock

    recent = sorted(orders, key=lambda o: o.created_at, reverse=True)[:10]
    recent_lines = "\n".join(
        f"  - Order #{o.id} | {o.status} | {o.get_total()} MAD | {o.created_at.strftime('%Y-%m-%d')}"
        for o in recent
    )

    lines = []
    lines.append("=== SMART SUPERMARKET - LIVE DATA ===")
    lines.append(f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
    lines.append("")
    lines.append("--- GLOBAL KPIs ---")
    lines.append(f"Total products   : {len(products)}")
    lines.append(f"Total customers  : {len(users)}")
    lines.append(f"Total orders     : {len(orders)}")
    lines.append(f"Total revenue    : {total_revenue} MAD")
    lines.append(f"Revenue (7 days) : {revenue_7d} MAD")
    lines.append(f"Revenue (30 days): {revenue_30d} MAD")
    lines.append("")
    lines.append("--- ORDERS BY STATUS ---")
    for k, v in status_counts.items():
        lines.append(f"  {k}: {v}")
    if not status_counts:
        lines.append("  No orders yet")
    lines.append("")
    lines.append("--- TOP 5 BEST-SELLING PRODUCTS ---")
    for i, p in enumerate(top5):
        lines.append(f"  {i+1}. {p['name']} - {p['qty']} units sold - {p['revenue']} MAD")
    if not top5:
        lines.append("  No sales yet")
    lines.append("")
    lines.append("--- STOCK ALERTS ---")
    out_names = ", ".join(p.name for p in out_of_stock) or "None"
    low_names = ", ".join(f"{p.name} ({p.stock})" for p in low_stock) or "None"
    lines.append(f"Out of stock ({len(out_of_stock)}): {out_names}")
    lines.append(f"Low stock    ({len(low_stock)}): {low_names}")
    lines.append("")
    lines.append("--- CATALOG BY CATEGORY ---")
    for cat, d in cat_data.items():
        lines.append(f"  {cat}: {d['count']} products, {d['stock']} units in stock")
    if not cat_data:
        lines.append("  No products")
    lines.append("")
    lines.append("--- RECENT 10 ORDERS ---")
    lines.append(recent_lines or "  No orders yet")
    lines.append("======================================")

    return "\n".join(lines)


SYSTEM_PROMPT = """You are an intelligent AI business assistant for Smart Supermarket admin panel.

Your behavior depends on what the admin asks:

1. GREETINGS / CASUAL MESSAGES (hello, hi, how are you, etc.)
   - Respond naturally and warmly, 1-2 sentences only
   - Do NOT show any store data unprompted

2. BUSINESS REPORTS & DATA QUESTIONS
   - Always use professional markdown formatting
   - Use ## for section headers
   - Use markdown tables for data comparison (never plain bullet lists for data)
   - Use **bold** for important numbers and labels
   - Structure reports with clear sections: Overview, Details, Alerts, Recommendations
   - Always use MAD as currency
   - Be precise with numbers — show exact figures from the data

   Example format for a report:
   ## Store Overview
   | Metric | Value |
   |--------|-------|
   | Products | 10 |
   | Revenue | 495.00 MAD |

   ## Stock Alerts
   | Product | Stock | Status |
   |---------|-------|--------|
   | Greek Yogurt | 0 | Out of stock |

   ## Recommendation
   Restock **Greek Yogurt** immediately — currently out of stock.

3. GENERAL QUESTIONS
   - Answer helpfully and briefly in plain text

Rules:
- Always respond in English
- Use tables instead of bullet lists whenever showing data
- Never dump raw data — always format it professionally
- Match response length to the question"""


@chatbot_bp.route("/chatbot/admin", methods=["POST"])
def admin_chat():
    data     = request.get_json()
    messages = data.get("messages", [])

    if not messages:
        return jsonify({"error": "No messages provided"}), 400

    store_context = build_store_context()
    full_system   = SYSTEM_PROMPT + "\n\n" + store_context

    try:
        response = client.chat.completions.create(
            model    = GROQ_MODEL,
            messages = [
                {"role": "system", "content": full_system},
                *messages
            ],
            max_tokens  = 1024,
            temperature = 0.4,
        )
        reply = response.choices[0].message.content
        return jsonify({"reply": reply}), 200

    except Exception as e:
        return jsonify({"error": f"AI service error: {str(e)}"}), 500


@chatbot_bp.route("/chatbot/suggestions", methods=["GET"])
def get_suggestions():
    low_stock_count = Product.query.filter(Product.stock <= 5).count()
    order_count     = Order.query.count()

    suggestions = [
        "Generate a full business report with markdown tables",
        "Show this week revenue in a table",
        "Show low stock products in a table",
        "Show top selling products in a table",
        "Summarize pending orders in a table",
        "Give business insights with data tables",
    ]

    if low_stock_count > 0:
        suggestions.insert(0, f"🚨 Il y a {low_stock_count} alerte(s) de stock faible — que faire ?")

    if order_count == 0:
        suggestions = [
            "📊 Génère un rapport d'initialisation du magasin",
            "💡 Quelles stratégies pour attirer les premiers clients ?",
            "🛍️ Comment organiser au mieux le catalogue produits ?",
        ]

    return jsonify({"suggestions": suggestions}), 200