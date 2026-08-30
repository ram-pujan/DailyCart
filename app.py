"""
Daily Cart — prototype server.

Deliberately built on Python's stdlib http.server only (no FastAPI/Flask/
Django) so the whole thing runs with nothing but `python3 app.py` — no
pip install, no virtualenv, no network access required. Swap this for
FastAPI + PostgreSQL later; the routes/JSON shapes below are written so
that move is mostly mechanical.

Run:
    python3 app.py
Then open:
    http://localhost:8000
Admin:
    http://localhost:8000/admin   (password: daily123)
"""
import json
import mimetypes
import os
import re
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import db

BASE_DIR = os.path.dirname(__file__)
STATIC_DIR = os.path.join(BASE_DIR, "static")
PAGES_DIR = os.path.join(STATIC_DIR, "pages")

ADMIN_PASSWORD = "daily123"  # prototype only — replace with real auth before shipping
DELIVERY_FEE = 100

PAGE_ROUTES = {
    "/": "index.html",
    "/shop": "shop.html",
    "/product": "product.html",
    "/cart": "cart.html",
    "/checkout": "checkout.html",
    "/order": "order.html",
    "/admin": "admin.html",
}


def json_default(o):
    return dict(o)


class DailyCartHandler(BaseHTTPRequestHandler):
    server_version = "DailyCart/0.1"

    # ---------- helpers ----------
    def send_json(self, data, status=200):
        body = json.dumps(data, default=json_default).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def send_error_json(self, status, message):
        self.send_json({"error": message}, status=status)

    def read_json_body(self):
        length = int(self.headers.get("Content-Length", 0) or 0)
        if length == 0:
            return {}
        raw = self.rfile.read(length)
        try:
            return json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            return {}

    def is_admin(self):
        token = self.headers.get("X-Admin-Token", "")
        return token == ADMIN_PASSWORD

    def serve_file(self, path, content_type=None):
        if not os.path.isfile(path):
            self.send_error_json(404, "Not found")
            return
        ctype = content_type or mimetypes.guess_type(path)[0] or "application/octet-stream"
        with open(path, "rb") as f:
            body = f.read()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    # ---------- routing ----------
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        if path in PAGE_ROUTES:
            self.serve_file(os.path.join(PAGES_DIR, PAGE_ROUTES[path]), "text/html")
            return

        if path.startswith("/static/"):
            rel = path[len("/static/"):]
            self.serve_file(os.path.join(STATIC_DIR, rel))
            return

        if path == "/api/categories":
            return self.api_list_categories()

        if path == "/api/products":
            return self.api_list_products(query)

        m = re.match(r"^/api/products/([\w-]+)$", path)
        if m:
            return self.api_get_product(m.group(1))

        m = re.match(r"^/api/orders/([\w-]+)$", path)
        if m:
            return self.api_get_order(m.group(1))

        if path == "/api/admin/orders":
            return self.api_admin_list_orders()

        if path == "/api/admin/products":
            return self.api_admin_list_products()

        self.send_error_json(404, "Not found")

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        body = self.read_json_body()

        if path == "/api/orders":
            return self.api_create_order(body)

        if path == "/api/admin/login":
            return self.api_admin_login(body)

        if path == "/api/admin/products":
            return self.api_admin_create_product(body)

        self.send_error_json(404, "Not found")

    def do_PATCH(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        body = self.read_json_body()

        m = re.match(r"^/api/admin/orders/(\d+)$", path)
        if m:
            return self.api_admin_update_order_status(int(m.group(1)), body)

        m = re.match(r"^/api/admin/products/(\d+)$", path)
        if m:
            return self.api_admin_update_product(int(m.group(1)), body)

        self.send_error_json(404, "Not found")

    def do_DELETE(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        m = re.match(r"^/api/admin/products/(\d+)$", path)
        if m:
            return self.api_admin_delete_product(int(m.group(1)))

        self.send_error_json(404, "Not found")

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PATCH, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-Admin-Token")
        self.end_headers()

    def log_message(self, fmt, *args):
        pass  # quiet console; comment out to debug

    # ---------- public API ----------
    def api_list_categories(self):
        conn = db.get_conn()
        rows = conn.execute("SELECT * FROM categories ORDER BY name").fetchall()
        conn.close()
        self.send_json([dict(r) for r in rows])

    def api_list_products(self, query):
        conn = db.get_conn()
        sql = """SELECT p.*, c.slug AS category_slug, c.name AS category_name
                  FROM products p JOIN categories c ON c.id = p.category_id
                  WHERE p.status = 'active'"""
        params = []

        category = query.get("category", [None])[0]
        if category:
            sql += " AND c.slug = ?"
            params.append(category)

        q = query.get("q", [None])[0]
        if q:
            sql += " AND (p.name LIKE ? OR p.brand LIKE ?)"
            like = f"%{q}%"
            params.extend([like, like])

        sort = query.get("sort", ["popular"])[0]
        order_map = {
            "price_asc": "COALESCE(p.sale_price, p.price) ASC",
            "price_desc": "COALESCE(p.sale_price, p.price) DESC",
            "newest": "p.id DESC",
            "popular": "p.rating DESC",
        }
        sql += f" ORDER BY {order_map.get(sort, order_map['popular'])}"

        rows = conn.execute(sql, params).fetchall()
        conn.close()
        self.send_json([dict(r) for r in rows])

    def api_get_product(self, slug):
        conn = db.get_conn()
        row = conn.execute(
            """SELECT p.*, c.slug AS category_slug, c.name AS category_name
               FROM products p JOIN categories c ON c.id = p.category_id
               WHERE p.slug = ?""",
            (slug,),
        ).fetchone()
        conn.close()
        if not row:
            return self.send_error_json(404, "Product not found")
        self.send_json(dict(row))

    def api_create_order(self, body):
        required = ["customer_name", "phone", "address", "items"]
        for field in required:
            if not body.get(field):
                return self.send_error_json(400, f"Missing field: {field}")
        items = body["items"]
        if not isinstance(items, list) or len(items) == 0:
            return self.send_error_json(400, "Cart is empty")

        conn = db.get_conn()
        subtotal = 0
        resolved_items = []
        for item in items:
            prod = conn.execute(
                "SELECT * FROM products WHERE id = ? AND status = 'active'",
                (item.get("product_id"),),
            ).fetchone()
            if not prod:
                conn.close()
                return self.send_error_json(400, f"Product {item.get('product_id')} not available")
            qty = max(1, int(item.get("qty", 1)))
            if prod["stock"] < qty:
                conn.close()
                return self.send_error_json(400, f"Not enough stock for {prod['name']}")
            unit_price = prod["sale_price"] or prod["price"]
            subtotal += unit_price * qty
            resolved_items.append((prod, qty, unit_price))

        delivery_fee = DELIVERY_FEE
        total = subtotal + delivery_fee
        order_number = db.generate_order_number(conn)

        cur = conn.execute(
            """INSERT INTO orders
               (order_number, customer_name, phone, email, province, district, city,
                address, notes, payment_method, subtotal, delivery_fee, total, status, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Pending', datetime('now'))""",
            (
                order_number,
                body["customer_name"],
                body["phone"],
                body.get("email"),
                body.get("province"),
                body.get("district"),
                body.get("city"),
                body["address"],
                body.get("notes"),
                body.get("payment_method", "COD"),
                subtotal,
                delivery_fee,
                total,
            ),
        )
        order_id = cur.lastrowid

        for prod, qty, unit_price in resolved_items:
            conn.execute(
                """INSERT INTO order_items (order_id, product_id, product_name, unit_price, qty)
                   VALUES (?, ?, ?, ?, ?)""",
                (order_id, prod["id"], prod["name"], unit_price, qty),
            )
            conn.execute(
                "UPDATE products SET stock = stock - ? WHERE id = ?", (qty, prod["id"])
            )

        conn.commit()
        conn.close()
        self.send_json({"order_number": order_number, "total": total}, status=201)

    def api_get_order(self, order_number):
        conn = db.get_conn()
        order = conn.execute(
            "SELECT * FROM orders WHERE order_number = ?", (order_number,)
        ).fetchone()
        if not order:
            conn.close()
            return self.send_error_json(404, "Order not found")
        items = conn.execute(
            "SELECT * FROM order_items WHERE order_id = ?", (order["id"],)
        ).fetchall()
        conn.close()
        result = dict(order)
        result["items"] = [dict(i) for i in items]
        self.send_json(result)

    # ---------- admin API ----------
    def api_admin_login(self, body):
        if body.get("password") == ADMIN_PASSWORD:
            self.send_json({"token": ADMIN_PASSWORD})
        else:
            self.send_error_json(401, "Incorrect password")

    def api_admin_list_orders(self):
        if not self.is_admin():
            return self.send_error_json(401, "Unauthorized")
        conn = db.get_conn()
        rows = conn.execute("SELECT * FROM orders ORDER BY id DESC").fetchall()
        conn.close()
        self.send_json([dict(r) for r in rows])

    def api_admin_update_order_status(self, order_id, body):
        if not self.is_admin():
            return self.send_error_json(401, "Unauthorized")
        status = body.get("status")
        valid = {"Pending", "Confirmed", "Processing", "Shipped", "Out for Delivery",
                 "Delivered", "Cancelled", "Returned"}
        if status not in valid:
            return self.send_error_json(400, "Invalid status")
        conn = db.get_conn()
        conn.execute("UPDATE orders SET status = ? WHERE id = ?", (status, order_id))
        conn.commit()
        conn.close()
        self.send_json({"ok": True})

    def api_admin_list_products(self):
        if not self.is_admin():
            return self.send_error_json(401, "Unauthorized")
        conn = db.get_conn()
        rows = conn.execute(
            """SELECT p.*, c.name AS category_name FROM products p
               JOIN categories c ON c.id = p.category_id ORDER BY p.id DESC"""
        ).fetchall()
        conn.close()
        self.send_json([dict(r) for r in rows])

    def api_admin_create_product(self, body):
        if not self.is_admin():
            return self.send_error_json(401, "Unauthorized")
        required = ["slug", "name", "category_id", "price", "stock"]
        for field in required:
            if body.get(field) in (None, ""):
                return self.send_error_json(400, f"Missing field: {field}")
        conn = db.get_conn()
        try:
            conn.execute(
                """INSERT INTO products
                   (slug, name, category_id, brand, price, sale_price, stock, rating, icon, description)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    body["slug"], body["name"], body["category_id"], body.get("brand", ""),
                    int(body["price"]), body.get("sale_price") or None, int(body["stock"]),
                    float(body.get("rating", 4.5)), body.get("icon", "\U0001F3F7\uFE0F"),
                    body.get("description", ""),
                ),
            )
            conn.commit()
        except Exception as e:
            conn.close()
            return self.send_error_json(400, str(e))
        conn.close()
        self.send_json({"ok": True}, status=201)

    def api_admin_update_product(self, product_id, body):
        if not self.is_admin():
            return self.send_error_json(401, "Unauthorized")
        allowed = ["name", "brand", "price", "sale_price", "stock", "description", "status", "category_id"]
        sets, params = [], []
        for field in allowed:
            if field in body:
                sets.append(f"{field} = ?")
                params.append(body[field])
        if not sets:
            return self.send_error_json(400, "No fields to update")
        params.append(product_id)
        conn = db.get_conn()
        conn.execute(f"UPDATE products SET {', '.join(sets)} WHERE id = ?", params)
        conn.commit()
        conn.close()
        self.send_json({"ok": True})

    def api_admin_delete_product(self, product_id):
        if not self.is_admin():
            return self.send_error_json(401, "Unauthorized")
        conn = db.get_conn()
        conn.execute("UPDATE products SET status = 'disabled' WHERE id = ?", (product_id,))
        conn.commit()
        conn.close()
        self.send_json({"ok": True})


def main():
    # Auto-initialize database with sample data if it doesn't exist
    db.init_db(reset=False)
    db.seed_sample_orders()  # Add sample orders for demo
    
    port = int(os.environ.get("PORT", 8000))
    server = ThreadingHTTPServer(("0.0.0.0", port), DailyCartHandler)
    print(f"✓ Daily Cart running at http://localhost:{port}")
    print(f"✓ Admin panel at   http://localhost:{port}/admin  (password: {ADMIN_PASSWORD})")
    print(f"✓ Shop at         http://localhost:{port}/shop")
    print(f"\nDatabase: {db.DB_PATH}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")


if __name__ == "__main__":
    main()
