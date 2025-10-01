import os, csv, random
from datetime import datetime, timedelta
import pandas as pd

TOTAL_SALES_TARGET = 1_000_000.00
START_DATE = datetime(2024, 9, 26)
END_DATE = datetime(2025, 9, 26)
CSV_PATH = "data.csv"
OUTPUT_SQL = "seed.sql"
random.seed(42)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PRODUCTS_STAGE_CSV = os.path.join(BASE_DIR, "products_stage.csv")
ORDERS_STAGE_CSV = os.path.join(BASE_DIR, "orders_stage.csv")
ORDER_ITEMS_STAGE_CSV = os.path.join(BASE_DIR, "order_items_stage.csv")
PRODUCT_RECIPE_STAGE_CSV = os.path.join(BASE_DIR, "product_recipe_stage.csv")

df = pd.read_csv(CSV_PATH)
if "name" in df.columns:
    df.rename(columns={"name": "product_name"}, inplace=True)
if "unit_price" not in df.columns and "price" in df.columns:
    df.rename(columns={"price": "unit_price"}, inplace=True)
df["product_name"] = df["product_name"].astype(str).str.strip()
df["unit_price"] = df["unit_price"].astype(str).str.replace("$", "", regex=False).str.strip().astype(float)
if "fruit" in df.columns:
    df["fruit"] = df["fruit"].astype(str).str.strip().str.lower()
if "tea" in df.columns:
    df["tea"] = df["tea"].astype(str).str.strip().str.lower().replace({
        "milk": "milk tea", "milk tea": "milk tea",
        "green": "green tea", "green tea": "green tea",
    })
df = df.reset_index(drop=True)
df["product_id"] = df.index + 1

with open(PRODUCTS_STAGE_CSV, "w", newline="", encoding="utf-8") as c:
    w = csv.writer(c); w.writerow(["product_id", "product_name", "unit_price"])
    for _, r in df.iterrows():
        w.writerow([int(r["product_id"]), r["product_name"], f"{float(r['unit_price']):.2f}"])

prs_rows = []
for _, r in df.iterrows():
    pid = int(r["product_id"])
    fruit = str(r.get("fruit", "")).strip().lower()
    tea = str(r.get("tea", "")).strip().lower()
    if fruit:
        prs_rows.append([pid, fruit, "1.0"])
    if tea:
        prs_rows.append([pid, tea, "1.0"])
with open(PRODUCT_RECIPE_STAGE_CSV, "w", newline="", encoding="utf-8") as c:
    w = csv.writer(c); w.writerow(["product_id", "ingredient_name", "quantity_per_unit"])
    w.writerows(prs_rows)

days = (END_DATE - START_DATE).days + 1
avg_price = float(df["unit_price"].mean())
expected_items_per_order = (1 + 4) / 2.0
expected_qty_per_line = (1 + 5) / 2.0
expected_order_value = avg_price * expected_items_per_order * expected_qty_per_line
total_orders = max(1, int(TOTAL_SALES_TARGET / expected_order_value))
orders_per_day = total_orders // days
remainder_days = total_orders % days

orders_rows, order_items_rows = [], []
order_id, order_item_id = 1, 1
for d in range(days):
    day = START_DATE + timedelta(days=d)
    if (day.month == 11 and day.day == 30) or (day.month == 12 and day.day == 25):
        daily_total = 0.0
        while daily_total < 5000:
            hour = random.randint(7, 20)
            minute = random.randint(0, 59)
            ts = day.replace(hour=hour, minute=minute, second=0)
            num_lines = random.randint(1, 4)
            order_total = 0.0
            lines = []
            for _ in range(num_lines):
                prod = df.sample(n=1).iloc[0]
                pid = int(prod["product_id"])
                base_price = float(prod["unit_price"])
                qty = random.randint(1, 5)
                unit_price_at_sale = round(base_price, 2)
                order_total += unit_price_at_sale * qty
                lines.append((order_item_id, order_id, pid, qty, f"{unit_price_at_sale:.2f}"))
                order_item_id += 1
            orders_rows.append([order_id, ts.strftime("%Y-%m-%d %H:%M:%S"), f"{order_total:.2f}"])
            for row in lines:
                order_items_rows.append(list(row))
            order_id += 1
            daily_total += order_total
    else:
        todays_orders = orders_per_day + (1 if d < remainder_days else 0)
        for _ in range(todays_orders):
            hour = random.randint(7, 20)
            minute = random.randint(0, 59)
            ts = day.replace(hour=hour, minute=minute, second=0)
            num_lines = random.randint(1, 4)
            order_total = 0.0
            lines = []
            for _ in range(num_lines):
                prod = df.sample(n=1).iloc[0]
                pid = int(prod["product_id"])
                base_price = float(prod["unit_price"])
                qty = random.randint(1, 5)
                unit_price_at_sale = round(base_price, 2)
                order_total += unit_price_at_sale * qty
                lines.append((order_item_id, order_id, pid, qty, f"{unit_price_at_sale:.2f}"))
                order_item_id += 1
            orders_rows.append([order_id, ts.strftime("%Y-%m-%d %H:%M:%S"), f"{order_total:.2f}"])
            for row in lines:
                order_items_rows.append(list(row))
            order_id += 1

with open(ORDERS_STAGE_CSV, "w", newline="", encoding="utf-8") as c:
    w = csv.writer(c); w.writerow(["order_id", "order_date", "total_amount"]); w.writerows(orders_rows)
with open(ORDER_ITEMS_STAGE_CSV, "w", newline="", encoding="utf-8") as c:
    w = csv.writer(c); w.writerow(["order_item_id", "order_id", "product_id", "quantity", "unit_price_at_sale"])
    w.writerows(order_items_rows)

with open(OUTPUT_SQL, "w", encoding="utf-8") as f:
    f.write("BEGIN;\n")
    f.write("SET synchronous_commit = off;\n\n")
    f.write("CREATE UNLOGGED TABLE IF NOT EXISTS products_stage (product_id integer, product_name text, unit_price numeric(10,2));\n")
    f.write("CREATE UNLOGGED TABLE IF NOT EXISTS orders_stage (order_id integer, order_date timestamp, total_amount numeric(10,2));\n")
    f.write("CREATE UNLOGGED TABLE IF NOT EXISTS order_items_stage (order_item_id integer, order_id integer, product_id integer, quantity integer, unit_price_at_sale numeric(10,2));\n")
    f.write("CREATE UNLOGGED TABLE IF NOT EXISTS product_recipe_stage (product_id integer, ingredient_name text, quantity_per_unit numeric(10,1));\n\n")
    f.write(f"\\copy products_stage (product_id, product_name, unit_price) FROM '{PRODUCTS_STAGE_CSV}' CSV HEADER;\n")
    f.write(f"\\copy orders_stage (order_id, order_date, total_amount) FROM '{ORDERS_STAGE_CSV}' CSV HEADER;\n")
    f.write(f"\\copy order_items_stage (order_item_id, order_id, product_id, quantity, unit_price_at_sale) FROM '{ORDER_ITEMS_STAGE_CSV}' CSV HEADER;\n")
    f.write(f"\\copy product_recipe_stage (product_id, ingredient_name, quantity_per_unit) FROM '{PRODUCT_RECIPE_STAGE_CSV}' CSV HEADER;\n\n")
    f.write("INSERT INTO products (product_id, product_name, unit_price)\n")
    f.write("SELECT product_id, product_name, unit_price FROM products_stage\n")
    f.write("ON CONFLICT (product_id) DO UPDATE SET product_name = EXCLUDED.product_name, unit_price = EXCLUDED.unit_price;\n\n")
    f.write("INSERT INTO product_recipe (product_id, ingredient_id, quantity_per_unit)\n")
    f.write("SELECT prs.product_id, i.ingredient_id, prs.quantity_per_unit\n")
    f.write("FROM product_recipe_stage prs\n")
    f.write("JOIN inventory i ON lower(i.ingredient_name) = lower(prs.ingredient_name)\n")
    f.write("ON CONFLICT (product_id, ingredient_id) DO NOTHING;\n\n")
    f.write("INSERT INTO orders (order_id, order_date, total_amount, employee_id)\n")
    f.write("WITH days AS (\n")
    f.write("    SELECT DISTINCT order_date::date AS day FROM orders_stage\n")
    f.write("),\n")
    f.write("cashiers AS (\n")
    f.write("    SELECT employee_id FROM employees WHERE role = 'Cashier'\n")
    f.write("),\n")
    f.write("day_cashier AS (\n")
    f.write("    SELECT d.day, c.employee_id,\n")
    f.write("           ROW_NUMBER() OVER (PARTITION BY d.day ORDER BY random()) AS rn\n")
    f.write("    FROM days d\n")
    f.write("    CROSS JOIN cashiers c\n")
    f.write(")\n")
    f.write("SELECT os.order_id, os.order_date, os.total_amount, dc.employee_id\n")
    f.write("FROM orders_stage os\n")
    f.write("JOIN day_cashier dc\n")
    f.write("  ON os.order_date::date = dc.day\n")
    f.write("WHERE dc.rn = 1;\n\n")
    f.write("INSERT INTO order_items (order_item_id, order_id, product_id, quantity, unit_price_at_sale)\n")
    f.write("SELECT order_item_id, order_id, product_id, quantity, unit_price_at_sale FROM order_items_stage;\n\n")
    f.write("DROP TABLE products_stage;\n")
    f.write("DROP TABLE orders_stage;\n")
    f.write("DROP TABLE order_items_stage;\n")
    f.write("DROP TABLE product_recipe_stage;\n\n")
    f.write("SELECT setval('products_product_id_seq', (SELECT COALESCE(MAX(product_id),0) FROM products));\n")
    f.write("SELECT setval('orders_order_id_seq', (SELECT COALESCE(MAX(order_id),0) FROM orders));\n")
    f.write("SELECT setval('order_items_order_item_id_seq', (SELECT COALESCE(MAX(order_item_id),0) FROM order_items));\n")
    f.write("COMMIT;\n")