"""
Load the CSV files into a SQLite database with proper schema and foreign keys.

Run this after data/generate_data.py.
"""

import csv
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
DB_PATH = ROOT / "database" / "ecommerce.db"

SCHEMA = """
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS customers;

CREATE TABLE customers (
    customer_id    INTEGER PRIMARY KEY,
    customer_name  TEXT    NOT NULL,
    country        TEXT    NOT NULL,
    segment        TEXT    NOT NULL,
    signup_date    DATE    NOT NULL
);

CREATE TABLE products (
    product_id    INTEGER PRIMARY KEY,
    product_name  TEXT    NOT NULL,
    category      TEXT    NOT NULL,
    price         REAL    NOT NULL,
    cost          REAL    NOT NULL
);

CREATE TABLE orders (
    order_id     INTEGER PRIMARY KEY,
    customer_id  INTEGER NOT NULL,
    order_date   DATE    NOT NULL,
    status       TEXT    NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE order_items (
    order_item_id  INTEGER PRIMARY KEY,
    order_id       INTEGER NOT NULL,
    product_id     INTEGER NOT NULL,
    quantity       INTEGER NOT NULL,
    unit_price     REAL    NOT NULL,
    FOREIGN KEY (order_id)   REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_orders_date     ON orders(order_date);
CREATE INDEX idx_items_order     ON order_items(order_id);
CREATE INDEX idx_items_product   ON order_items(product_id);
"""


def load_csv(cursor, table, path):
    with open(path) as f:
        reader = csv.DictReader(f)
        rows = [tuple(row.values()) for row in reader]
        n_cols = len(reader.fieldnames)
    placeholders = ",".join(["?"] * n_cols)
    cursor.executemany(f"INSERT INTO {table} VALUES ({placeholders})", rows)
    return len(rows)


def main():
    DB_PATH.parent.mkdir(exist_ok=True)
    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()

    print(f"Creating schema in {DB_PATH.name}...")
    cur.executescript(SCHEMA)

    print("Loading data...")
    for table, filename in [
        ("customers",   "customers.csv"),
        ("products",    "products.csv"),
        ("orders",      "orders.csv"),
        ("order_items", "order_items.csv"),
    ]:
        n = load_csv(cur, table, DATA_DIR / filename)
        print(f"  {table:<12} {n:>6,} rows")

    conn.commit()
    conn.close()
    print(f"Database ready: {DB_PATH}")


if __name__ == "__main__":
    main()
