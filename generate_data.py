"""
Generate a synthetic e-commerce dataset.

Creates four related CSV files:
    customers.csv      - 200 customers across 8 countries and 3 segments
    products.csv       - 60 products in 6 categories
    orders.csv         - ~1,800 orders spanning ~2 years
    order_items.csv    - ~4,500 order line items

Random seed is fixed so results are reproducible.
"""

import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

random.seed(42)

OUTPUT_DIR = Path(__file__).parent

COUNTRIES = ["USA", "Germany", "UK", "France", "Italy", "Spain", "Netherlands", "Albania"]
SEGMENTS = ["Consumer", "Business", "Premium"]
SEGMENT_WEIGHTS = [60, 30, 10]

CATEGORIES = {
    "Electronics": ["Laptop", "Headphones", "Smartphone", "Tablet", "Smartwatch", "Camera"],
    "Home & Kitchen": ["Coffee Maker", "Blender", "Toaster", "Vacuum Cleaner", "Air Fryer"],
    "Clothing": ["T-Shirt", "Jeans", "Jacket", "Sneakers", "Dress", "Hoodie"],
    "Books": ["Novel", "Cookbook", "Biography", "Self-Help Book", "Textbook"],
    "Sports": ["Yoga Mat", "Dumbbells", "Running Shoes", "Bicycle", "Tennis Racket"],
    "Beauty": ["Perfume", "Lipstick", "Shampoo", "Face Cream", "Hair Dryer"],
}

PRICE_RANGES = {
    "Electronics":     (80, 1500),
    "Home & Kitchen":  (30, 400),
    "Clothing":        (20, 200),
    "Books":           (10, 60),
    "Sports":          (15, 800),
    "Beauty":          (8, 120),
}


def generate_customers():
    customers = []
    start = datetime(2023, 1, 1)
    for cid in range(1, 201):
        signup = start + timedelta(days=random.randint(0, 700))
        customers.append({
            "customer_id": cid,
            "customer_name": f"Customer_{cid:04d}",
            "country": random.choice(COUNTRIES),
            "segment": random.choices(SEGMENTS, weights=SEGMENT_WEIGHTS)[0],
            "signup_date": signup.strftime("%Y-%m-%d"),
        })
    return customers


def generate_products():
    products = []
    pid = 1
    for cat, names in CATEGORIES.items():
        lo, hi = PRICE_RANGES[cat]
        for name in names:
            for variant in ["A", "B"]:
                price = round(random.uniform(lo, hi), 2)
                cost = round(price * random.uniform(0.4, 0.7), 2)
                products.append({
                    "product_id": pid,
                    "product_name": f"{name} {variant}",
                    "category": cat,
                    "price": price,
                    "cost": cost,
                })
                pid += 1
    return products


def generate_orders_and_items(customers, products):
    orders = []
    items = []
    order_id = 1
    item_id = 1
    end_date = datetime(2025, 11, 30)

    for _ in range(2000):
        customer = random.choice(customers)
        signup = datetime.strptime(customer["signup_date"], "%Y-%m-%d")
        order_date = signup + timedelta(days=random.randint(1, 800))
        if order_date > end_date:
            continue

        status = random.choices(
            ["Delivered", "Shipped", "Cancelled", "Returned"],
            weights=[78, 9, 7, 6],
        )[0]

        orders.append({
            "order_id": order_id,
            "customer_id": customer["customer_id"],
            "order_date": order_date.strftime("%Y-%m-%d"),
            "status": status,
        })

        # 1-5 items per order, weighted toward smaller orders
        n_items = random.choices([1, 2, 3, 4, 5], weights=[40, 30, 15, 10, 5])[0]
        for _ in range(n_items):
            product = random.choice(products)
            qty = random.choices([1, 2, 3], weights=[70, 20, 10])[0]
            # Occasional discount
            discount = random.choice([1.0, 1.0, 1.0, 1.0, 0.9, 0.85])
            unit_price = round(product["price"] * discount, 2)
            items.append({
                "order_item_id": item_id,
                "order_id": order_id,
                "product_id": product["product_id"],
                "quantity": qty,
                "unit_price": unit_price,
            })
            item_id += 1

        order_id += 1

    return orders, items


def write_csv(filename, rows, fieldnames):
    path = OUTPUT_DIR / filename
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"  Wrote {len(rows):,} rows -> {filename}")


def main():
    print("Generating synthetic e-commerce dataset...")
    customers = generate_customers()
    products = generate_products()
    orders, items = generate_orders_and_items(customers, products)

    write_csv("customers.csv",   customers, ["customer_id", "customer_name", "country", "segment", "signup_date"])
    write_csv("products.csv",    products,  ["product_id", "product_name", "category", "price", "cost"])
    write_csv("orders.csv",      orders,    ["order_id", "customer_id", "order_date", "status"])
    write_csv("order_items.csv", items,     ["order_item_id", "order_id", "product_id", "quantity", "unit_price"])
    print("Done.")


if __name__ == "__main__":
    main()
