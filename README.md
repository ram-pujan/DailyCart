# Daily Cart — Prototype

A working slice of the "Daily Cart" sports e-commerce plan: storefront,
cart, checkout with Cash on Delivery, order tracking, and an admin
dashboard — backed by a real SQLite database.

## Stack (and why)

- **Python stdlib `http.server` + `sqlite3`** for the backend. Zero
  external dependencies — no `pip install`, no Node, no build step.
  You run one file and it works, which matters most for a prototype
  you want to actually open and click through today.
- **Plain HTML/CSS/vanilla JS** for the frontend, served as static
  files. No React/Next.js build pipeline to fight with yet.
- **SQLite** as the database, in a single `daily_cart.db` file.

This is a deliberate simplification of the PRD's target stack
(Next.js + FastAPI + PostgreSQL). The API routes and JSON shapes are
written so that swapping the backend for FastAPI, or the DB for
Postgres, is a mechanical port rather than a rewrite — see "What to
extend first" below.

## What's built

- **Storefront:** homepage, category browsing, search, sort/filter,
  product detail pages.
- **Cart:** add/remove/adjust quantity (stored in `localStorage`).
- **Checkout:** delivery details form, Cash on Delivery, creates a
  real order in the database and decrements stock.
- **Order tracking:** `/order?order=DC-...` shows a live status
  ladder (Pending → Confirmed → Processing → Shipped → Out for
  Delivery → Delivered).
- **Admin dashboard** (`/admin`, password `daily123`): today's sales,
  order list with status updates, product list with add/disable and
  low-stock flags.
- Seeded with 14 real sports products across Cricket, Football,
  Badminton, and Fitness, matching the PRD's initial catalog.

## What's deliberately left out (per the PRD's own MVP scope)

Accounts/login for customers, wishlist, reviews, coupons, online
payment gateways (eSewa/Khalti), and delivery-partner integration —
all flagged in the PRD as Phase 2 or later.

## How to run it

Requires only Python 3.8+ (no other installs).

```bash
cd daily-cart
python3 app.py
```

Then open:

- **Storefront:** http://localhost:8000
- **Admin:** http://localhost:8000/admin (password: `daily123`)

The database (`daily_cart.db`) is created and seeded automatically on
first run. To reset it back to the original seed data at any point:

```bash
rm daily_cart.db
python3 db.py
```

Stop the server with `Ctrl+C`.

## Try this flow

1. Go to the homepage → click into **Cricket** → add a bat and a ball
   to your cart.
2. Go to `/cart`, adjust quantities, proceed to checkout.
3. Fill in delivery details, place the order (COD) — you land on the
   order confirmation page with a live tracking scoreboard.
4. Open `/admin` in another tab, log in, go to **Orders**, and move
   that order's status forward — refresh the tracking page and watch
   it update.
5. In **Products**, add a new product or disable one and see it
   disappear from the shop instantly.

## What I'd extend first

1. **Real auth.** Admin auth here is a single hardcoded password
   compared on every request — fine for a prototype, not for
   production. Add password hashing + sessions for admin, and
   email/password (or phone OTP, common in Nepal) for customer
   accounts with guest checkout preserved.
2. **Payment gateways.** The checkout form already has a disabled
   "eSewa / Khalti" option placeholder — wiring up eSewa first (most
   widely used) is the highest-leverage next integration, since COD
   alone caps order value and adds delivery risk.
3. **Move to FastAPI + PostgreSQL.** The current SQLite/stdlib setup
   won't hold up under concurrent writes or multiple admin users.
   The route shapes here map almost 1:1 onto FastAPI path operations,
   so this is a rewrite of the transport layer, not the logic.
4. **Analytics on top of the order data.** You already asked for this
   in the PRD (section 30) — once real orders start flowing through
   `orders`/`order_items`, a simple `/admin` reports tab (top
   products, revenue by category, average order value) is a small
   addition with outsized business value.
5. **Image uploads.** Products currently use an emoji as a stand-in
   thumbnail so the prototype needs no file storage. Swapping that
   for real product photos (S3-compatible storage + an upload field
   in the admin product form) is the most visible thing standing
   between this and a live storefront.
