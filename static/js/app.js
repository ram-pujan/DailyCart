// Daily Cart — shared front-end helpers (no framework, no build step).

const DC = {
  CART_KEY: "dc_cart",       // [{product_id, name, icon, price, qty}]
  ADMIN_KEY: "dc_admin_token",

  // ---- API ----
  async api(path, { method = "GET", body, admin = false } = {}) {
    const headers = { "Content-Type": "application/json" };
    if (admin) headers["X-Admin-Token"] = localStorage.getItem(DC.ADMIN_KEY) || "";
    const res = await fetch(path, {
      method,
      headers,
      body: body ? JSON.stringify(body) : undefined,
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.error || `Request failed (${res.status})`);
    return data;
  },

  // ---- cart (localStorage) ----
  getCart() {
    try {
      return JSON.parse(localStorage.getItem(DC.CART_KEY)) || [];
    } catch {
      return [];
    }
  },
  saveCart(cart) {
    localStorage.setItem(DC.CART_KEY, JSON.stringify(cart));
    DC.updateCartBadge();
  },
  addToCart(product, qty = 1) {
    const cart = DC.getCart();
    const existing = cart.find((i) => i.product_id === product.id);
    if (existing) {
      existing.qty += qty;
    } else {
      cart.push({
        product_id: product.id,
        name: product.name,
        icon: product.icon,
        price: product.sale_price || product.price,
        qty,
      });
    }
    DC.saveCart(cart);
  },
  setQty(productId, qty) {
    let cart = DC.getCart();
    if (qty <= 0) {
      cart = cart.filter((i) => i.product_id !== productId);
    } else {
      const item = cart.find((i) => i.product_id === productId);
      if (item) item.qty = qty;
    }
    DC.saveCart(cart);
  },
  removeFromCart(productId) {
    DC.saveCart(DC.getCart().filter((i) => i.product_id !== productId));
  },
  cartCount() {
    return DC.getCart().reduce((sum, i) => sum + i.qty, 0);
  },
  cartSubtotal() {
    return DC.getCart().reduce((sum, i) => sum + i.qty * i.price, 0);
  },
  clearCart() {
    localStorage.removeItem(DC.CART_KEY);
    DC.updateCartBadge();
  },
  updateCartBadge() {
    const el = document.getElementById("cart-count");
    if (el) el.textContent = DC.cartCount();
  },

  // ---- utils ----
  money(n) {
    return "Rs. " + Number(n).toLocaleString("en-IN");
  },
  toast(msg) {
    let el = document.getElementById("dc-toast");
    if (!el) {
      el = document.createElement("div");
      el.id = "dc-toast";
      el.className = "toast";
      document.body.appendChild(el);
    }
    el.textContent = msg;
    el.classList.add("show");
    clearTimeout(DC._toastTimer);
    DC._toastTimer = setTimeout(() => el.classList.remove("show"), 1800);
  },
  qs(name) {
    return new URLSearchParams(window.location.search).get(name);
  },
  escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = str ?? "";
    return div.innerHTML;
  },

  // ---- validation ----
  validateEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  },
  validatePhone(phone) {
    return /^\d{10}$/.test(phone.replace(/\D/g, ""));
  },

  // ---- formatting ----
  formatDate(dateStr) {
    return new Date(dateStr).toLocaleDateString("en-IN", {
      year: "numeric", month: "short", day: "numeric"
    });
  },
  formatTime(dateStr) {
    return new Date(dateStr).toLocaleTimeString("en-IN", {
      hour: "2-digit", minute: "2-digit"
    });
  },

  // ---- modal helpers ----
  showModal(id) {
    const el = document.getElementById(id);
    if (el) el.classList.add("show");
  },
  hideModal(id) {
    const el = document.getElementById(id);
    if (el) el.classList.remove("show");
  },

  // ---- order status ----
  isOrderComplete(status) {
    return ["Delivered", "Returned", "Cancelled"].includes(status);
  },
  getStatusStep(status) {
    const steps = {
      "Pending": 0,
      "Confirmed": 1,
      "Processing": 2,
      "Shipped": 3,
      "Out for Delivery": 4,
      "Delivered": 5
    };
    return steps[status] || 0;
  }
};

document.addEventListener("DOMContentLoaded", DC.updateCartBadge);
