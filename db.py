"""
Daily Cart — database layer.
Plain sqlite3 (stdlib only, no ORM) so the prototype has zero external
dependencies. Run this file directly to (re)create and seed the DB:

    python3 db.py
"""
import sqlite3
import os
import random
import string
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), "daily_cart.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    icon TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    category_id INTEGER NOT NULL REFERENCES categories(id),
    brand TEXT,
    price INTEGER NOT NULL,          -- Rs., regular price
    sale_price INTEGER,              -- Rs., nullable
    stock INTEGER NOT NULL DEFAULT 0,
    low_stock_threshold INTEGER NOT NULL DEFAULT 5,
    rating REAL NOT NULL DEFAULT 4.5,
    icon TEXT NOT NULL,
    description TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active'   -- active | disabled
);

CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_number TEXT UNIQUE NOT NULL,
    customer_name TEXT NOT NULL,
    phone TEXT NOT NULL,
    email TEXT,
    province TEXT,
    district TEXT,
    city TEXT,
    address TEXT NOT NULL,
    notes TEXT,
    payment_method TEXT NOT NULL DEFAULT 'COD',
    subtotal INTEGER NOT NULL,
    delivery_fee INTEGER NOT NULL,
    total INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'Pending',
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL REFERENCES orders(id),
    product_id INTEGER NOT NULL REFERENCES products(id),
    product_name TEXT NOT NULL,
    unit_price INTEGER NOT NULL,
    qty INTEGER NOT NULL
);
"""

CATEGORIES = [
    ("cricket", "Cricket", "\U0001F3CF"),
    ("football", "Football", "\u26BD"),
    ("badminton", "Badminton", "\U0001F3F8"),
    ("fitness", "Fitness", "\U0001F4AA"),
]

PRODUCTS = [
    # Cricket products
    ("pro-cricket-bat", "Professional Cricket Bat", "cricket", "SS", 3500, 2999, 15, 4.6, "\U0001F3CF",
     "English willow bat tuned for power hitting. Grade 1 willow, mid-swell profile."),
    ("cricket-ball-leather", "Leather Cricket Ball (Red)", "cricket", "Kookaburra", 1200, None, 40, 4.4, "\U0001F534",
     "Match-quality four-piece leather ball with a hand-stitched seam."),
    ("cricket-gloves", "Batting Gloves", "cricket", "SS", 1800, 1499, 4, 4.3, "\U0001F9E4",
     "Lightweight batting gloves with reinforced knuckle padding."),
    ("cricket-pads", "Batting Pads (Pair)", "cricket", "SG", 2600, None, 10, 4.2, "\U0001F6E1\uFE0F",
     "Full-length batting pads with cane inserts for lightweight protection."),
    ("cricket-helmet", "Cricket Helmet", "cricket", "Masuri", 4200, 3699, 6, 4.7, "\u26D1\uFE0F",
     "Steel-grille helmet meeting British safety standards, adjustable fit."),
    ("cricket-stumps", "Wooden Stumps & Bails Set", "cricket", "Generic", 800, None, 25, 4.3, "\U0001F3CF",
     "Regulation-size wooden stumps with bails for practice or casual play."),
    ("cricket-catching-gloves", "Wicket Keeper Gloves", "cricket", "SS", 3200, 2799, 8, 4.5, "\U0001F9E4",
     "Professional wicket keeper gloves with extra padding and wrist support."),
    ("cricket-bat-cover", "Bat Cover & Shoulder Strap", "cricket", "Generic", 400, None, 50, 4.2, "\U0001F454",
     "Protective bag for bat transport with shoulder strap and foam padding."),

    # Football products
    ("football-classic", "Match Football Size 5", "football", "Nivia", 1500, 1299, 25, 4.5, "\u26BD",
     "Hand-stitched size 5 football, FIFA-inspection-ready panel design."),
    ("football-boots", "Football Boots", "football", "Nivia", 2800, 2399, 12, 4.3, "\U0001F45F",
     "Firm-ground studs with a synthetic leather upper for control on the ball."),
    ("football-gloves", "Goalkeeper Gloves", "football", "Nivia", 1400, None, 9, 4.1, "\U0001F9E4",
     "Latex palm gloves with wrist strap for extra grip on saves."),
    ("football-shin-guards", "Shin Guard Set", "football", "Nivia", 1200, 999, 18, 4.4, "\U0001F9E4",
     "Lightweight EVA foam shin guards with adjustable straps."),
    ("football-training-cones", "Training Cones (Set of 10)", "football", "Generic", 600, None, 30, 4.3, "\U0001F340",
     "Bright red and yellow cones for dribbling drills and agility training."),
    ("football-ball-pump", "Ball Pump (Manual)", "football", "Generic", 300, None, 40, 4.2, "\U0001F51B",
     "Hand pump with pressure gauge for maintaining ball inflation."),
    ("football-training-vest", "Training Bibs (Pack of 6)", "football", "Generic", 900, 799, 20, 4.3, "\U0001F455",
     "Breathable mesh bibs for team drills and practice sessions."),

    # Badminton products
    ("badminton-racket", "Carbon Fibre Racket", "badminton", "Yonex", 3200, 2799, 14, 4.6, "\U0001F3F8",
     "Full carbon-fibre frame, medium flex, strung and ready to play."),
    ("shuttlecocks", "Feather Shuttlecocks (Tube of 10)", "badminton", "Yonex", 1800, None, 20, 4.4, "\U0001FAB6",
     "Goose-feather shuttles for consistent flight in club play."),
    ("badminton-net", "Badminton Net + Poles Set", "badminton", "Generic", 2200, 1899, 3, 4.0, "\U0001F578\uFE0F",
     "Portable net and pole set for backyard or community-court games."),
    ("badminton-racket-grip", "Grip Tape (Pack of 3)", "badminton", "Yonex", 600, None, 35, 4.3, "\U0001F39E\uFE0F",
     "Anti-slip grip tape for improved racket handle control and comfort."),
    ("badminton-shuttle-plastic", "Plastic Shuttlecocks (Tube of 12)", "badminton", "Generic", 700, None, 45, 4.2, "\U0001FAB6",
     "Durable nylon shuttles for beginners and training sessions."),
    ("badminton-wrist-support", "Wrist Support Brace", "badminton", "Generic", 500, 399, 22, 4.3, "\U0001F4A7",
     "Compression wrist brace to prevent injury during intensive play."),
    ("badminton-court-marker", "Court Boundary Tape", "badminton", "Generic", 400, None, 25, 4.1, "\U0001F4E6",
     "High-visibility tape for marking court boundaries in indoor spaces."),

    # Fitness products
    ("resistance-bands", "Resistance Band Set (5-piece)", "fitness", "PowerMax", 1100, 899, 30, 4.3, "\U0001F4AA",
     "Five resistance levels for strength training, mobility and rehab work."),
    ("skipping-rope", "Speed Skipping Rope", "fitness", "PowerMax", 500, None, 50, 4.2, "\U0001FA79",
     "Ball-bearing handles for fast, smooth rotations during cardio sessions."),
    ("yoga-mat", "Yoga & Exercise Mat", "fitness", "Generic", 1300, 1099, 22, 4.5, "\U0001F9D8",
     "6mm non-slip mat, lightweight and easy to roll for home workouts."),
    ("dumbbell-set", "Adjustable Dumbbell Pair (20kg)", "fitness", "PowerMax", 3500, 2999, 8, 4.6, "\U0001F4AA",
     "Compact adjustable dumbbells, perfect for home gym training."),
    ("push-up-stand", "Push-up Stand & Handle", "fitness", "Generic", 800, 649, 16, 4.4, "\U0001F4AA",
     "Ergonomic push-up bars to reduce wrist strain during exercises."),
    ("ab-roller", "Ab Wheel Roller", "fitness", "PowerMax", 1200, 999, 18, 4.5, "\U0001F4AA",
     "Professional-grade ab wheel for core and abdominal strengthening."),
    ("foam-roller", "Foam Roller (60cm)", "fitness", "Generic", 1500, 1299, 12, 4.4, "\U0001F32B\uFE0F",
     "High-density foam roller for self-massage and muscle recovery."),
    ("resistance-loop-bands", "Loop Resistance Bands (Set of 4)", "fitness", "PowerMax", 900, 749, 26, 4.3, "\U0001F4AA",
     "Heavy-duty loop bands for lower body and glute training."),
    ("exercise-ball", "Stability Ball 65cm", "fitness", "Generic", 1800, 1499, 10, 4.4, "\U0001F392",
     "Anti-burst exercise ball for balance, core and rehabilitation exercises."),
    ("jump-rope-crossfit", "Crossfit Jump Rope", "fitness", "PowerMax", 1100, 899, 15, 4.5, "\U0001FA79",
     "Weighted jump rope for intense cardio and crossfit training."),
    ("yoga-blocks", "Yoga Block Pair (Cork)", "fitness", "Generic", 1200, None, 20, 4.3, "\U0001F9D8",
     "Natural cork blocks to support alignment and deepen stretches."),
    ("resistance-tube-set", "Resistance Tube Set with Handles", "fitness", "PowerMax", 1400, 1099, 14, 4.4, "\U0001F4AA",
     "Full-body resistance tubes for strength training and rehab."),
]


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(reset=False):
    if reset and os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    conn = get_conn()
    conn.executescript(SCHEMA)

    cat_count = conn.execute("SELECT COUNT(*) c FROM categories").fetchone()["c"]
    if cat_count == 0:
        for slug, name, icon in CATEGORIES:
            conn.execute(
                "INSERT INTO categories (slug, name, icon) VALUES (?, ?, ?)",
                (slug, name, icon),
            )
        conn.commit()

    cat_ids = {row["slug"]: row["id"] for row in conn.execute("SELECT id, slug FROM categories")}

    prod_count = conn.execute("SELECT COUNT(*) c FROM products").fetchone()["c"]
    if prod_count == 0:
        for slug, name, cat, brand, price, sale, stock, rating, icon, desc in PRODUCTS:
            conn.execute(
                """INSERT INTO products
                   (slug, name, category_id, brand, price, sale_price, stock, rating, icon, description)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (slug, name, cat_ids[cat], brand, price, sale, stock, rating, icon, desc),
            )
        conn.commit()

    conn.close()


def generate_order_number(conn):
    today = datetime.now().strftime("%Y%m%d")
    prefix = f"DC-{today}-"
    while True:
        suffix = "".join(random.choices(string.digits, k=5))
        candidate = prefix + suffix
        exists = conn.execute(
            "SELECT 1 FROM orders WHERE order_number = ?", (candidate,)
        ).fetchone()
        if not exists:
            return candidate


def seed_sample_orders():
    """Add sample orders for demonstration purposes"""
    conn = get_conn()
    existing_orders = conn.execute("SELECT COUNT(*) c FROM orders").fetchone()["c"]
    if existing_orders > 0:
        conn.close()
        return  # Don't reseed if orders already exist
    
    # Get some product IDs for the orders
    products = conn.execute("SELECT id, name, sale_price, price FROM products LIMIT 20").fetchall()
    if not len(products):
        conn.close()
        return
    
    # Sample customers
    customers = [
        ("Raj Poudel", "9841234567", "raj@example.com", "Bagmati", "Kathmandu", "Kathmandu", "Thamel, Kathmandu"),
        ("Priya Sharma", "9851234567", "priya@example.com", "Bagmati", "Bhaktapur", "Bhaktapur", "Durbar Square, Bhaktapur"),
        ("Arjun Gupta", "9861234567", "arjun@example.com", "Gandaki", "Kaski", "Pokhara", "Lakeside, Pokhara"),
        ("Neha Singh", "9871234567", "neha@example.com", "Bagmati", "Lalitpur", "Lalitpur", "Patan Dhoka, Lalitpur"),
        ("Vikram Nepal", "9881234567", "vikram@example.com", "Lumbini", "Rupandehi", "Butwal", "Main Street, Butwal"),
    ]
    
    statuses = ["Pending", "Confirmed", "Processing", "Shipped", "Out for Delivery", "Delivered"]
    
    for i, (name, phone, email, province, district, city, address) in enumerate(customers):
        # Create 1-3 orders per customer
        order_count = random.randint(1, 3)
        for _ in range(order_count):
            # Select random products for this order
            num_items = random.randint(1, 4)
            order_products = random.sample(products, min(num_items, len(products)))
            
            subtotal = 0
            for prod in order_products:
                qty = random.randint(1, 3)
                unit_price = prod["sale_price"] or prod["price"]
                subtotal += unit_price * qty
            
            delivery_fee = 100
            total = subtotal + delivery_fee
            order_number = generate_order_number(conn)
            status = random.choice(statuses)
            
            # Create order with date in past 30 days
            days_ago = random.randint(0, 30)
            created_at = (datetime.now() - timedelta(days=days_ago)).isoformat()
            
            cur = conn.execute(
                """INSERT INTO orders
                   (order_number, customer_name, phone, email, province, district, city,
                    address, payment_method, subtotal, delivery_fee, total, status, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    order_number, name, phone, email, province, district, city, address,
                    random.choice(["COD", "COD", "COD"]), subtotal, delivery_fee, total, status, created_at
                ),
            )
            order_id = cur.lastrowid
            
            # Add order items
            for prod in order_products:
                qty = random.randint(1, 3)
                unit_price = prod["sale_price"] or prod["price"]
                conn.execute(
                    """INSERT INTO order_items (order_id, product_id, product_name, unit_price, qty)
                       VALUES (?, ?, ?, ?, ?)""",
                    (order_id, prod["id"], prod["name"], unit_price, qty),
                )
    
    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db(reset=True)
    print(f"Database created and seeded at {DB_PATH}")
