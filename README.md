# E-Commerce Sales Analysis (SQL + Python)

End-to-end analysis of an e-commerce dataset using **SQL** and **Python**. The project generates a realistic synthetic dataset, loads it into a SQLite database with a proper relational schema, runs eight analytical SQL queries, and produces visualisations to answer concrete business questions about sales, customers, and product performance.

Everything in this repo is reproducible from a single `pip install` — no external data downloads required.

---

## Tech Stack

- **SQL** — SQLite, with JOINs, GROUP BY, CASE, subqueries, CTEs, and window functions (`RANK() OVER`)
- **Python** — `pandas`, `matplotlib`, `sqlite3`
- **Data** — Synthetic e-commerce dataset across 4 related tables (~5,400 rows)

---

## Project Structure

```
ecommerce-sales-analysis/
├── data/
│   ├── generate_data.py        # Generates the synthetic dataset
│   ├── customers.csv
│   ├── products.csv
│   ├── orders.csv
│   └── order_items.csv
├── database/
│   ├── load_to_sqlite.py       # Creates schema + loads CSVs into SQLite
│   └── ecommerce.db            # Generated database
├── sql/
│   └── queries.sql             # 8 analytical queries (read this!)
├── analysis/
│   ├── run_analysis.py         # Runs every query and prints results
│   └── results.txt             # Saved output from the last run
├── figures/
│   ├── monthly_revenue.png
│   ├── revenue_by_category.png
│   ├── revenue_by_country.png
│   └── customer_loyalty.png
├── visualize.py                # Generates the four charts above
├── requirements.txt
└── README.md
```

---

## Database Schema

```
customers     (customer_id PK, customer_name, country, segment, signup_date)
products      (product_id  PK, product_name,  category, price, cost)
orders        (order_id    PK, customer_id FK → customers, order_date, status)
order_items   (order_item_id PK, order_id FK → orders, product_id FK → products,
               quantity, unit_price)
```

Foreign keys are declared in the schema and indexes are created on the join columns for query performance.

---

## How to Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Generate the synthetic dataset (CSVs)
python data/generate_data.py

# 3. Create the SQLite database and load the data
python database/load_to_sqlite.py

# 4. Run the eight analytical queries
python analysis/run_analysis.py

# 5. Generate the charts
python visualize.py
```

The whole pipeline runs in well under a minute on any machine.

---

## Business Questions Answered

1. **Which products drive the most revenue?** → Q1
2. **How are sales trending month over month?** → Q2 + `monthly_revenue.png`
3. **Where are our highest-value markets?** → Q3 + `revenue_by_country.png`
4. **Who are our top customers?** → Q4
5. **Which categories are most *profitable* (not just highest revenue)?** → Q5
6. **Where are we losing orders to returns and cancellations?** → Q6
7. **Who are the top 3 customers in each country?** → Q7 (window function)
8. **What does our customer loyalty distribution look like?** → Q8 + `customer_loyalty.png`

---

## Key Findings

Numbers below come from the generated dataset (`random.seed(42)`), so they are reproducible.

- **Revenue:** ~$1.09M across 1,307 delivered orders over a 35-month window.
- **Category mix:** *Electronics* leads on revenue (~$586k, more than half of total sales) — but *Sports* has the highest **profit margin** at ~47%, so revenue ≠ profit.
- **Geography:** *Germany* is the top market (~$190k), followed by Netherlands and Italy. Premium-segment customers are concentrated in just a few countries.
- **Quality issues:** *Beauty* has the highest return rate (~8.7%) — worth investigating in any real business.
- **Customer behaviour:** Only 2 one-time buyers vs. 118 "regular" customers (5–9 orders) and 32 "loyal" (10+). The loyal segment has an average lifetime value ~3× the occasional segment.

---

## Sample Query — Window Function

Top 3 customers in each country, ranked by spend:

```sql
WITH customer_spend AS (
    SELECT c.customer_id, c.customer_name, c.country,
           SUM(oi.quantity * oi.unit_price) AS total_spent
    FROM customers c
    JOIN orders o       ON c.customer_id = o.customer_id
    JOIN order_items oi ON o.order_id    = oi.order_id
    WHERE o.status = 'Delivered'
    GROUP BY c.customer_id
),
ranked AS (
    SELECT country, customer_name, total_spent,
           RANK() OVER (PARTITION BY country ORDER BY total_spent DESC) AS rank_in_country
    FROM customer_spend
)
SELECT * FROM ranked WHERE rank_in_country <= 3 ORDER BY country, rank_in_country;
```

---

## Skills Demonstrated

- Designing a relational schema with foreign keys and indexes
- Writing multi-table SQL JOINs (up to 4 tables in one query)
- Aggregation, conditional aggregation (`CASE`), subqueries, CTEs
- Window functions (`RANK() OVER (PARTITION BY …)`)
- Python ↔ SQL integration via `sqlite3` and `pandas.read_sql_query`
- Data visualisation with `matplotlib`
- Clean project structure, reproducibility, documentation

---

## Author

**Sindi Borici** — early-career software engineer, MSc Software Engineering (in progress).
Durrës, Albania · (www.linkedin.com/in/sindi-borici-5a884b2b7) · sindiborici12@gmail.com
