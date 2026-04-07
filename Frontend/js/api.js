const API = "http://127.0.0.1:5000/api";

// ── Auth ─────────────────────────────────────────────────────────
export async function register(username, email, password) {
    const r = await fetch(`${API}/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, email, password })
    });
    return r.json();
}

export async function login(identifier, password) {
    const r = await fetch(`${API}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ identifier, password })
    });
    return r.json();
}

// ── Products ──────────────────────────────────────────────────────
export async function getProducts(params = {}) {
    const qs = new URLSearchParams(params).toString();
    const r = await fetch(`${API}/products${qs ? "?" + qs : ""}`);
    return r.json();
}

export async function getCategories() {
    const r = await fetch(`${API}/products/categories`);
    return r.json();
}

export async function addProduct(data) {
    const r = await fetch(`${API}/products`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    });
    return r.json();
}

export async function updateProduct(id, data) {
    const r = await fetch(`${API}/products/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    });
    return r.json();
}

export async function deleteProduct(id) {
    const r = await fetch(`${API}/products/${id}`, { method: "DELETE" });
    return r.json();
}

// ── Orders ────────────────────────────────────────────────────────
export async function getAllOrders() {
    const r = await fetch(`${API}/orders`);
    return r.json();
}

export async function getUserOrders(userId) {
    const r = await fetch(`${API}/orders/user/${userId}`);
    return r.json();
}

export async function createOrder(userId, items, note = "") {
    const r = await fetch(`${API}/orders`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: userId, items, note })
    });
    return r.json();
}

export async function updateOrderStatus(orderId, status) {
    const r = await fetch(`${API}/orders/${orderId}/status`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status })
    });
    return r.json();
}

// ── Stats ─────────────────────────────────────────────────────────
export async function getStats() {
    const r = await fetch(`${API}/stats`);
    return r.json();
}

export async function simulateAI() {
    const r = await fetch(`${API}/alerts/simulate`);
    return r.json();
}

// ── Session helpers ───────────────────────────────────────────────
export function getUser()        { return JSON.parse(localStorage.getItem("user")); }
export function setUser(user)    { localStorage.setItem("user", JSON.stringify(user)); }
export function removeUser()     { localStorage.removeItem("user"); }
export function isAdmin()        { return getUser()?.role === "admin"; }
export function requireAuth(redirect = "../pages/login.html") {
    if (!getUser()) { window.location.href = redirect; return null; }
    return getUser();
}
export function requireAdmin(redirect = "../index.html") {
    const u = requireAuth();
    if (u && u.role !== "admin") { alert("Admin access only."); window.location.href = redirect; return null; }
    return u;
}