import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_order_confirmation_data(user_email, username, order_id, order_total, order_note, order_date, order_items):
    """Send order confirmation email using smtplib directly — no Flask-Mail needed."""

    MAIL_SERVER  = "smtp.gmail.com"
    MAIL_PORT    = 587
    MAIL_USER    = os.getenv("MAIL_USERNAME", "")
    MAIL_PASS    = os.getenv("MAIL_PASSWORD", "")

    date_str = order_date.strftime("%B %d, %Y at %H:%M")

    # Build items rows
    items_rows = ""
    for item in order_items:
        items_rows += f"""
        <tr>
            <td style="padding:10px 14px;border-bottom:1px solid #e8ecf0;font-size:14px;color:#1a1f36">{item['product_name']}</td>
            <td style="padding:10px 14px;border-bottom:1px solid #e8ecf0;font-size:14px;color:#6b7280;text-align:center">{item['quantity']}</td>
            <td style="padding:10px 14px;border-bottom:1px solid #e8ecf0;font-size:14px;color:#1a1f36;text-align:right">{item['price']:.2f} MAD</td>
            <td style="padding:10px 14px;border-bottom:1px solid #e8ecf0;font-size:14px;font-weight:600;color:#1a1f36;text-align:right">{item['subtotal']:.2f} MAD</td>
        </tr>"""

    note_html = f'<div style="margin-top:16px;padding:12px 16px;background:#f5f6fa;border-radius:8px;font-size:13px;color:#6b7280">Note: {order_note}</div>' if order_note else ""

    html_body = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#f5f6fa;font-family:'Segoe UI',Arial,sans-serif">
<div style="max-width:600px;margin:40px auto;background:#ffffff;border-radius:16px;overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,0.08)">

    <div style="background:#2563eb;padding:32px 40px;text-align:center">
        <div style="font-size:36px;margin-bottom:10px">&#128722;</div>
        <h1 style="color:#ffffff;margin:0;font-size:24px;font-weight:700">Smart Supermarket</h1>
        <p style="color:rgba(255,255,255,0.85);margin:8px 0 0;font-size:15px">Order Confirmation</p>
    </div>

    <div style="padding:36px 40px">
        <h2 style="color:#1a1f36;font-size:20px;margin:0 0 8px">Thank you, {username}!</h2>
        <p style="color:#6b7280;font-size:14px;margin:0 0 28px;line-height:1.6">
            Your order has been placed successfully and is now being processed.
        </p>

        <div style="background:#f0f4ff;border:1px solid #bfcffe;border-radius:12px;padding:20px;margin-bottom:28px">
            <table style="width:100%;border-collapse:collapse"><tr>
                <td style="padding:4px 8px">
                    <div style="font-size:11px;font-weight:700;color:#6b7280;text-transform:uppercase">Order ID</div>
                    <div style="font-size:20px;font-weight:800;color:#2563eb">#{order_id}</div>
                </td>
                <td style="padding:4px 8px">
                    <div style="font-size:11px;font-weight:700;color:#6b7280;text-transform:uppercase">Date</div>
                    <div style="font-size:13px;font-weight:600;color:#1a1f36">{date_str}</div>
                </td>
                <td style="padding:4px 8px;text-align:right">
                    <div style="font-size:11px;font-weight:700;color:#6b7280;text-transform:uppercase">Status</div>
                    <div style="font-size:14px;font-weight:700;color:#ca8a04">Pending</div>
                </td>
            </tr></table>
        </div>

        <h3 style="color:#1a1f36;font-size:15px;font-weight:700;margin:0 0 12px">Order Items</h3>
        <table style="width:100%;border-collapse:collapse;border:1px solid #e8ecf0">
            <thead><tr style="background:#f5f6fa">
                <th style="padding:10px 14px;text-align:left;font-size:11px;font-weight:700;color:#6b7280;text-transform:uppercase">Product</th>
                <th style="padding:10px 14px;text-align:center;font-size:11px;font-weight:700;color:#6b7280;text-transform:uppercase">Qty</th>
                <th style="padding:10px 14px;text-align:right;font-size:11px;font-weight:700;color:#6b7280;text-transform:uppercase">Price</th>
                <th style="padding:10px 14px;text-align:right;font-size:11px;font-weight:700;color:#6b7280;text-transform:uppercase">Subtotal</th>
            </tr></thead>
            <tbody>{items_rows}</tbody>
        </table>

        <div style="text-align:right;margin-top:16px;padding:16px 20px;background:#f0fdf4;border:1px solid #bbf7d0;border-radius:10px">
            <span style="font-size:14px;color:#6b7280">Total: </span>
            <span style="font-size:22px;font-weight:800;color:#16a34a">{order_total:.2f} MAD</span>
        </div>

        {note_html}

        <div style="margin-top:28px;padding:20px;background:#fff7ed;border:1px solid #fed7aa;border-radius:10px">
            <h4 style="color:#ea580c;margin:0 0 8px;font-size:14px;font-weight:700">What happens next?</h4>
            <p style="color:#9a3412;font-size:13px;margin:0;line-height:1.7">
                Track your order anytime in <strong>My Orders</strong>. We will update the
                status as your order progresses through confirmation, shipping, and delivery.
            </p>
        </div>
    </div>

    <div style="background:#f5f6fa;padding:24px 40px;text-align:center;border-top:1px solid #e8ecf0">
        <p style="color:#9ca3af;font-size:12px;margin:0;line-height:1.8">
            <strong style="color:#6b7280">Smart Supermarket</strong><br>
            Final Year Project (PFE) — IDIA Students<br>
            This is an automated email, please do not reply.
        </p>
    </div>
</div>
</body></html>"""

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"Order Confirmation #{order_id} - Smart Supermarket"
        msg["From"]    = f"Smart Supermarket <{MAIL_USER}>"
        msg["To"]      = user_email
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP(MAIL_SERVER, MAIL_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(MAIL_USER, MAIL_PASS)
            server.sendmail(MAIL_USER, user_email, msg.as_string())

        print(f"[EMAIL OK] Sent to {user_email} for order #{order_id}")
        return True

    except Exception as e:
        import traceback
        print(f"[EMAIL ERROR] {e}")
        traceback.print_exc()
        return False


# Alias for backward compatibility
def send_order_confirmation(user_email, username, order):
    return send_order_confirmation_data(
        user_email, username,
        order.id,
        round(sum(float(i.price or 0) * int(i.quantity or 1) for i in order.items), 2),
        order.note or "",
        order.created_at,
        [{"product_name": i.product_name or "Product",
          "quantity": int(i.quantity or 1),
          "price": float(i.price or 0),
          "subtotal": float(i.price or 0) * int(i.quantity or 1)
         } for i in order.items]
    )