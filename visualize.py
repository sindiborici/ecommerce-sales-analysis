"""
Generate the chart images shown in the README.

Reads from the SQLite database, writes PNGs to ../figures/.
"""

import sqlite3
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "database" / "ecommerce.db"
FIG_DIR = ROOT / "figures"
FIG_DIR.mkdir(exist_ok=True)

plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.grid": True,
    "grid.alpha": 0.3,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "font.size": 10,
})

conn = sqlite3.connect(DB_PATH)


# ---- 1. Monthly revenue trend ----
df = pd.read_sql_query("""
    SELECT strftime('%Y-%m', o.order_date) AS month,
           SUM(oi.quantity * oi.unit_price) AS revenue
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.status = 'Delivered'
    GROUP BY month
    ORDER BY month
""", conn)

fig, ax = plt.subplots(figsize=(11, 5))
ax.plot(df["month"], df["revenue"], marker="o", color="#2E86AB", linewidth=2)
ax.fill_between(df["month"], df["revenue"], alpha=0.15, color="#2E86AB")
ax.set_title("Monthly Revenue Trend", fontsize=13, fontweight="bold")
ax.set_xlabel("Month")
ax.set_ylabel("Revenue ($)")
ax.tick_params(axis="x", rotation=45)
plt.tight_layout()
plt.savefig(FIG_DIR / "monthly_revenue.png", dpi=130)
plt.close()


# ---- 2. Revenue by category ----
df = pd.read_sql_query("""
    SELECT p.category,
           SUM(oi.quantity * oi.unit_price) AS revenue
    FROM order_items oi
    JOIN products p ON oi.product_id = p.product_id
    JOIN orders   o ON oi.order_id   = o.order_id
    WHERE o.status = 'Delivered'
    GROUP BY p.category
    ORDER BY revenue DESC
""", conn)

fig, ax = plt.subplots(figsize=(9, 5))
bars = ax.bar(df["category"], df["revenue"], color="#2E86AB")
ax.set_title("Revenue by Product Category", fontsize=13, fontweight="bold")
ax.set_ylabel("Revenue ($)")
ax.tick_params(axis="x", rotation=20)
for bar, value in zip(bars, df["revenue"]):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
            f"${value/1000:.0f}k", ha="center", va="bottom", fontsize=9)
plt.tight_layout()
plt.savefig(FIG_DIR / "revenue_by_category.png", dpi=130)
plt.close()


# ---- 3. Revenue by country ----
df = pd.read_sql_query("""
    SELECT c.country,
           SUM(oi.quantity * oi.unit_price) AS revenue
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.status = 'Delivered'
    GROUP BY c.country
    ORDER BY revenue DESC
""", conn)

fig, ax = plt.subplots(figsize=(9, 5))
ax.barh(df["country"], df["revenue"], color="#A23B72")
ax.set_title("Revenue by Country", fontsize=13, fontweight="bold")
ax.set_xlabel("Revenue ($)")
ax.invert_yaxis()
plt.tight_layout()
plt.savefig(FIG_DIR / "revenue_by_country.png", dpi=130)
plt.close()


# ---- 4. Customer loyalty distribution ----
df = pd.read_sql_query("""
    SELECT
        CASE
            WHEN order_count = 1             THEN 'One-time'
            WHEN order_count BETWEEN 2 AND 4 THEN 'Occasional (2-4)'
            WHEN order_count BETWEEN 5 AND 9 THEN 'Regular (5-9)'
            ELSE                                  'Loyal (10+)'
        END AS customer_type,
        COUNT(*) AS num_customers,
        AVG(total_spent) AS avg_value
    FROM (
        SELECT c.customer_id,
               COUNT(DISTINCT o.order_id) AS order_count,
               SUM(oi.quantity * oi.unit_price) AS total_spent
        FROM customers c
        JOIN orders o ON c.customer_id = o.customer_id
        JOIN order_items oi ON o.order_id = oi.order_id
        WHERE o.status = 'Delivered'
        GROUP BY c.customer_id
    )
    GROUP BY customer_type
    ORDER BY MIN(order_count)
""", conn)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

colors = ["#F18F01", "#2E86AB", "#A23B72", "#3DA35D"]
ax1.bar(df["customer_type"], df["num_customers"], color=colors)
ax1.set_title("Customers by Loyalty Segment", fontsize=12, fontweight="bold")
ax1.set_ylabel("Number of customers")
ax1.tick_params(axis="x", rotation=20)

ax2.bar(df["customer_type"], df["avg_value"], color=colors)
ax2.set_title("Avg Lifetime Value by Segment", fontsize=12, fontweight="bold")
ax2.set_ylabel("Avg lifetime value ($)")
ax2.tick_params(axis="x", rotation=20)

plt.tight_layout()
plt.savefig(FIG_DIR / "customer_loyalty.png", dpi=130)
plt.close()


conn.close()
print(f"Saved 4 charts to {FIG_DIR}")
