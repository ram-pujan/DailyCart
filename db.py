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
from datetime import datetime

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
    # slug, name, category, brand, price, sale_price, stock, rating, icon, description
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
    ("football-classic", "Match Football Size 5", "football", "Nivia", 1500, 1299, 25, 4.5, "\u26BD",
     "Hand-stitched size 5 football, FIFA-inspection-ready panel design."),
    ("football-boots", "Football Boots", "football", "Nivia", 2800, 2399, 12, 4.3, "\U0001F45F",
     "Firm-ground studs with a synthetic leather upper for control on the ball."),
    ("football-gloves", "Goalkeeper Gloves", "football", "Nivia", 1400, None, 9, 4.1, "\U0001F9E4",
     "Latex palm gloves with wrist strap for extra grip on saves."),
    ("badminton-racket", "Carbon Fibre Racket", "badminton", "Yonex", 3200, 2799, 14, 4.6, "\U0001F3F8",
     "Full carbon-fibre frame, medium flex, strung and ready to play."),
    ("shuttlecocks", "Feather Shuttlecocks (Tube of 10)", "badminton", "Yonex", 1800, None, 20, 4.4, "\U0001FAB6",
     "Goose-feather shuttles for consistent flight in club play."),
    ("badminton-net", "Badminton Net + Poles Set", "badminton", "Generic", 2200, 1899, 3, 4.0, "\U0001F578\uFE0F",
     "Portable net and pole set for backyard or community-court games."),
    ("resistance-bands", "Resistance Band Set (5-piece)", "fitness", "PowerMax", 1100, 899, 30, 4.3, "\U0001F4AA",
     "Five resistance levels for strength training, mobility and rehab work."),
    ("skipping-rope", "Speed Skipping Rope", "fitness", "PowerMax", 500, None, 50, 4.2, "\U0001FA79",
     "Ball-bearing handles for fast, smooth rotations during cardio sessions."),
    ("yoga-mat", "Yoga & Exercise Mat", "fitness", "Generic", 1300, 1099, 22, 4.5, "\U0001F9D8",
     "6mm non-slip mat, lightweight and easy to roll for home workouts."),
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


if __name__ == "__main__":
    init_db(reset=True)
    print(f"Database created and seeded at {DB_PATH}")
