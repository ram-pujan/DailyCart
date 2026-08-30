# ⚽ Daily Cart — Sports E-Commerce Platform

A modern, feature-rich e-commerce platform for sports equipment across Nepal. Built with Python (no external dependencies), SQLite, and vanilla JavaScript.

**Repository:** [GitHub - ram-pujan/DailyCart](https://github.com/ram-pujan/DailyCart)

---

## 🎯 Key Features

### 🛍️ Customer Experience
- ✅ **Complete shopping workflow**: Browse products, search, filter by category, add to cart
- ✅ **Product showcase**: Detailed product pages with pricing, stock status, ratings, descriptions
- ✅ **Smart cart management**: Add/remove items, adjust quantities, persistent storage via localStorage
- ✅ **Smooth checkout**: Multi-step checkout with delivery form, payment method selection
- ✅ **Order tracking**: Real-time status tracking with visual progress indicators
- ✅ **Fully responsive**: Mobile-first design, works perfectly on all devices
- ✅ **Multiple categories**: Cricket, Football, Badminton, Fitness equipment
- ✅ **40+ quality products**: Pre-loaded with realistic sports equipment and pricing

### 🔧 Admin Dashboard Features
- ✅ **Order management**: View all orders, update status, track customer information
- ✅ **Product management**: Add new products, edit prices/inventory, disable/enable items
- ✅ **Dashboard analytics**: Daily sales metrics, total orders, product inventory overview
- ✅ **Stock alerts**: Low-stock warnings, inventory tracking
- ✅ **Admin authentication**: Simple password-based auth (production-ready structure)

### 💻 Technical Architecture
- ✅ **Zero external dependencies**: Uses only Python stdlib (http.server, sqlite3, json)
- ✅ **Auto-initialization**: Database auto-creates with sample data on first run
- ✅ **RESTful API**: Clean, documented API endpoints for all operations
- ✅ **Responsive CSS**: Modern design system with custom color palette
- ✅ **Client-side cart**: Persistent localStorage shopping cart
- ✅ **Order management**: Unique order IDs, status tracking, item-level details
- ✅ **Stock depletion**: Real-time inventory updates with each order

---

## 📁 Project Structure

```
DailyCart/
├── app.py                 # Main HTTP server & API routes
├── db.py                  # SQLite database schemas & operations
├── daily_cart.db          # SQLite database (auto-created with sample data)
├── README.md              # Original documentation
└── static/
    ├── css/
    │   └── style.css      # Complete responsive design system
    ├── js/
    │   └── app.js         # Shared utilities & cart logic
    └── pages/
        ├── index.html     # Home: hero, categories, testimonials, newsletter
        ├── shop.html      # Product listing with search & filters
        ├── product.html   # Product detail with reviews & specifications
        ├── cart.html      # Shopping cart with summary
        ├── checkout.html  # Delivery form & order creation
        ├── order.html     # Order tracking & status dashboard
        └── admin.html     # Admin panel (dashboard, orders, products)
```

---

## 🚀 Getting Started

### System Requirements
- **Python 3.8+** (includes sqlite3)
- ~5MB disk space for database
- Any modern browser
- **No pip install needed** — uses only Python standard library

### Installation & Running

**Step 1: Clone the repository**
```bash
git clone https://github.com/ram-pujan/DailyCart.git
cd DailyCart
```

**Step 2: Run the server**
```bash
python3 app.py
```

You should see:
```
✓ Daily Cart running at http://localhost:8000
✓ Admin panel at   http://localhost:8000/admin  (password: daily123)
✓ Shop at         http://localhost:8000/shop
```

**Step 3: Open in browser**
- 🏠 Homepage: http://localhost:8000
- 🛒 Shop: http://localhost:8000/shop
- 👤 Admin: http://localhost:8000/admin (password: `daily123`)
- 📦 Track: http://localhost:8000/order

---

## 📋 Database Schema

### Categories Table
Stores product categories with emojis for visual appeal.
```sql
id (PK) | slug | name | icon
1       | cricket | Cricket | 🏏
2       | football | Football | ⚽
3       | badminton | Badminton | 🏸
4       | fitness | Fitness | 💪
```

### Products Table
Complete product catalog with pricing and inventory.
```sql
id | slug | name | category_id | brand | price | sale_price | stock | rating | icon | description | status
```

### Orders Table
Customer orders with detailed delivery information.
```sql
id | order_number | customer_name | phone | email | province | district | city | address | payment_method | subtotal | delivery_fee | total | status | created_at
```

### Order Items Table
Individual items within each order.
```sql
id | order_id | product_id | product_name | unit_price | qty
```

---

## 🛒 Product Categories & Inventory

### Cricket Equipment (8 products)
- Professional cricket bats (Grade 1 willow)
- Leather & practice cricket balls
- Batting gloves & pads with cane inserts
- Cricket helmets (safety certified)
- Wicket keeper gloves
- Wooden stumps & bails
- Protective bat covers

**Price range:** Rs. 400 - Rs. 4,200

### Football Equipment (7 products)
- Match-quality size 5 footballs
- Football boots with firm-ground studs
- Goalkeeper gloves with grip pads
- Shin guard sets
- Training cones for drills
- Manual ball pumps with gauge
- Team training bibs (packs)

**Price range:** Rs. 300 - Rs. 2,800

### Badminton Equipment (7 products)
- Full carbon-fiber badminton rackets
- Feather & nylon shuttlecocks
- Badminton nets with portable poles
- Grip tape for racket handles
- Wrist support braces
- Court boundary markers

**Price range:** Rs. 400 - Rs. 3,200

### Fitness & Training (18 products)
- Adjustable dumbbell sets (20kg)
- Yoga mats & exercise blocks
- Resistance bands (5-level sets)
- Speed jump ropes with bearings
- Ab wheels & ab rollers
- Foam rollers for recovery
- Stability exercise balls (65cm)
- Crossfit jump ropes
- Resistance tube sets

**Price range:** Rs. 500 - Rs. 3,500

---

## 💰 Pricing & Checkout

### Pricing Model
- **Regular Price**: Standard retail price per product
- **Sale Price** (optional): Discounted price shown with strike-through
- **Delivery Fee**: Flat Rs. 100 nationwide delivery
- **Order Total**: Subtotal + Rs. 100 delivery charge

### Payment Options
- **Cash on Delivery (COD)**: Pay when order arrives (fully implemented)
- **Online Payment**: Placeholder for eSewa/Khalti (Phase 2)

### Order Workflow

```
Customer Places Order
        ↓
    Pending (awaiting admin confirmation)
        ↓
   Confirmed (order confirmed)
        ↓
   Processing (order being prepared)
        ↓
    Shipped (handed to delivery partner)
        ↓
  Out for Delivery (in transit)
        ↓
    Delivered (customer received)
```

**Terminal States:** Cancelled | Returned

---

## 🔐 Admin Dashboard

### Access
- **URL:** http://localhost:8000/admin
- **Default Password:** `daily123`
- **Authentication:** Simple token-based (X-Admin-Token header)

### Dashboard Tab
- **Today's Sales:** Rs. value of orders placed today
- **Total Orders:** Count of all orders in system
- **Total Products:** Count of active & disabled products
- **Recent Orders:** Last 6 orders with customer names & status

### Orders Tab
- **View All Orders:** Complete order list with filters
- **Order Details:** Customer info, order number, totals, payment method
- **Status Updates:** Dropdown to change order status in real-time
- **Search:** Find orders by order number or customer name

### Products Tab
- **Product List:** All products with pricing, stock, status
- **Low Stock Alerts:** ⚠️ indicator for items below threshold
- **Add Products:** Form to add new products to catalog
- **Edit Products:** Update name, price, stock, description
- **Enable/Disable:** Toggle product visibility without deleting

---

## 🎨 Responsive Design

### Desktop (1200px+)
- Full-width layout with sidebar filters
- 4-column product grid
- Split checkout layout (form + summary)
- Multi-column footer with links

### Tablet (768px - 1199px)
- Adjusted spacing and padding
- 2-column product grid
- Single-column layouts where needed
- Optimized navigation

### Mobile (<768px)
- Single-column product list
- Touch-friendly buttons
- Full-width forms
- Hamburger-friendly navigation
- Stacked checkout layout

---

## 🔌 API Endpoints

### Public Endpoints

#### Get All Categories
```bash
GET /api/categories
Response: [{ id, slug, name, icon }]
```

#### List Products with Filters
```bash
GET /api/products?category=cricket&q=bat&sort=price_asc
Parameters:
  - category: cricket|football|badminton|fitness
  - q: search query
  - sort: popular|newest|price_asc|price_desc
Response: [{ id, slug, name, price, sale_price, stock, rating, ... }]
```

#### Get Product Details
```bash
GET /api/products/{slug}
Response: { id, name, category_name, price, sale_price, stock, description, rating, ... }
```

#### Create Order
```bash
POST /api/orders
Body: {
  customer_name: string,
  phone: string,
  email: string (optional),
  province, district, city: string,
  address: string,
  notes: string (optional),
  payment_method: "COD",
  items: [{ product_id, qty }, ...]
}
Response: { order_number, total }
```

#### Track Order
```bash
GET /api/orders/{order_number}
Response: { order_number, customer_name, status, items: [], total, delivery_fee, ... }
```

### Admin Endpoints

#### Admin Login
```bash
POST /api/admin/login
Body: { password: "daily123" }
Response: { token: "daily123" }
```
*Header for subsequent requests: `X-Admin-Token: daily123`*

#### Get All Orders (Admin)
```bash
GET /api/admin/orders
Response: [{ id, order_number, customer_name, status, total, ... }]
```

#### Update Order Status
```bash
PATCH /api/admin/orders/{id}
Body: { status: "Shipped" }
```

#### Get All Products (Admin)
```bash
GET /api/admin/products
Response: [{ id, name, price, stock, status, category_name, ... }]
```

#### Create Product
```bash
POST /api/admin/products
Body: {
  slug: string,
  name: string,
  category_id: number,
  brand: string,
  price: number,
  sale_price: number (optional),
  stock: number,
  icon: emoji string,
  description: string
}
```

#### Update Product
```bash
PATCH /api/admin/products/{id}
Body: { name?, brand?, price?, stock?, status?, ... }
```

---

## 📊 Sample Data

The application automatically loads with:
- **40 products** across 4 sports categories
- **5 sample customers** with realistic names & addresses
- **15-25 sample orders** with dates from past 30 days
- **Varied order statuses** for demonstration (Pending through Delivered)
- **Stock levels** from 3 to 50 units per product
- **Realistic pricing** from Rs. 300 to Rs. 4,200
- **Sale prices** on select items showing discounts

**Note:** Sample data is created only on first run. Subsequent runs preserve existing data.

---

## 🎨 Design System

### Color Palette
```css
--ink:         #101418    /* Main text, dark elements */
--ink-soft:    #4b5563    /* Secondary text, muted colors */
--paper:       #faf9f6    /* Light background */
--paper-raised:#ffffff    /* Card backgrounds, white space */
--navy:        #0b1220    /* Header, footer, dark sections */
--whistle:     #ff4d1c    /* Primary call-to-action (orange-red) */
--pitch:       #1b8a5a    /* Secondary accent (green) for prices */
--amber:       #ffc93c    /* Highlight, scores, important details */
--danger:      #d1293d    /* Error states, deletions */
```

### Typography
- **Display:** Arial Narrow, Impact (bold, condensed headlines)
- **Body:** System font stack (macOS SF Pro, Windows Segoe UI, Android Roboto)
- **Monospace:** ui-monospace (order numbers, technical text)
- **Line height:** 1.5 for readability

### Components
- **Buttons:** Primary (orange), Outline, Dark variants with hover states
- **Cards:** Product cards, category cards, summary cards
- **Forms:** Input fields, selects, textareas with focus states
- **Tables:** Admin data tables with striped rows
- **Status Badges:** Color-coded by order status
- **Modals:** Overlay modals for forms and dialogs
- **Toasts:** Bottom-right notifications for user feedback

---

## 🚀 Deployment

### Local Development
```bash
python3 app.py
# Runs on http://0.0.0.0:8000
```

### Production with Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:main
```

### Environment Variables
```bash
PORT=8000  # Change port if needed
```

### Docker (Optional)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
EXPOSE 8000
CMD ["python3", "app.py"]
```

---

## 📝 Pre-Production Checklist

Before going live, implement:

- [ ] **Change admin password** in `app.py` (ADMIN_PASSWORD variable)
- [ ] **Implement user authentication** for customer accounts
- [ ] **Set up HTTPS/SSL** for secure checkout (required for payment)
- [ ] **Add payment gateway** integration (eSewa, Khalti, credit cards)
- [ ] **Email notifications** for order confirmations and status updates
- [ ] **Database backups** automated and tested
- [ ] **Rate limiting** on API endpoints to prevent abuse
- [ ] **Error logging** and monitoring (Sentry, DataDog)
- [ ] **CDN** for static assets (CSS, JS, images)
- [ ] **Environment-based configuration** (dev, staging, production)
- [ ] **Security headers** (CORS, CSP, X-Frame-Options)
- [ ] **Input validation** on all forms
- [ ] **Database encryption** for sensitive data
- [ ] **Search index** optimization for product searches
- [ ] **Analytics** integration (Google Analytics, Mixpanel)

---

## 🤝 Contributing & Extending

### Areas for Enhancement

1. **Phase 2 Features** (as per original PRD)
   - User accounts & registration
   - Order history per customer
   - Wishlist & favorites
   - Product reviews & ratings
   - Coupon & promotional codes

2. **Payment Integration**
   - eSewa payment gateway
   - Khalti payment integration
   - Credit/debit card support

3. **Fulfillment**
   - Delivery partner integration
   - Shipping label generation
   - Real-time tracking via GPS

4. **Advanced Features**
   - Product recommendations
   - Inventory forecasting
   - Multi-language support (Nepali, English)
   - SMS notifications
   - Mobile app (React Native)

5. **Performance**
   - Product search optimization
   - Caching strategy
   - Image optimization
   - API rate limiting

---

## 🐛 Troubleshooting

**Port 8000 already in use?**
```bash
# Use different port
PORT=3000 python3 app.py
```

**Database corrupted or needs reset?**
```bash
# Delete database and restart (will auto-recreate with sample data)
rm daily_cart.db
python3 app.py
```

**Admin password forgotten?**
```python
# Edit app.py line 27:
ADMIN_PASSWORD = "your-new-password"
# Restart server
```

**Orders not persisting?**
- Check database file exists: `ls -la daily_cart.db`
- Verify SQLite installation: `python3 -c "import sqlite3; print(sqlite3.version)"`

---

## 📚 Technology Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| **Backend** | Python stdlib http.server | Zero dependencies, perfect for MVP |
| **Database** | SQLite | File-based, no server needed, included in Python |
| **API** | REST (JSON) | Standard, easy to test, production-ready |
| **Frontend** | Vanilla JS + CSS | No build step, instant feedback, works everywhere |
| **Hosting** | Any server (local, cloud) | Python works on AWS, Heroku, DigitalOcean, etc. |

---

## 📄 License

**MIT License** - Free for personal, educational, and commercial use. See LICENSE file for details.

---

## 👨‍💻 Author

**Ram Pujan Poudel**
- 🔗 GitHub: [@ram-pujan](https://github.com/ram-pujan)
- 📦 Project: [DailyCart](https://github.com/ram-pujan/DailyCart)
- 📧 Questions? Open an issue on GitHub

---

## ❓ Frequently Asked Questions

**Q: Can I use this for my real business?**
A: Yes! It's production-ready. Just implement security checks, payment gateways, and proper authentication before launch.

**Q: How do I add more products?**
A: Use the admin dashboard at `/admin` or directly edit `db.py` and restart the server.

**Q: Is my data safe?**
A: Data is stored locally in `daily_cart.db`. For production, use proper backups and encryption.

**Q: Can I change the design?**
A: Absolutely! Edit `static/css/style.css` and `static/pages/*.html`. CSS is well-organized with clear sections.

**Q: How many products can I add?**
A: SQLite handles millions of rows efficiently. No practical limit for a small-to-medium shop.

**Q: Can I integrate eSewa/Khalti?**
A: Yes! The API is ready to accept payment integrations. Add a POST handler in `app.py` for payment processing.

**Q: How do I backup orders?**
A: The database file `daily_cart.db` contains everything. Back it up regularly: `cp daily_cart.db daily_cart.backup.db`

**Q: Can multiple admins access the dashboard?**
A: Currently, there's one password. For multiple admins, implement user table-based auth (Phase 2).

---

**Happy selling with Daily Cart! ⚽🛒**

*Built with ❤️ for the Nepali sports community.*
