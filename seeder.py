import pandas as pd
import random
from datetime import datetime, timedelta

start_date = datetime(2024, 9, 26)
end_date = datetime(2025, 9, 26)

df = pd.read_csv("data.csv")

df['product_id'] = df.index + 1

df['price'] = df['price'].astype(str).str.replace('$', '', regex=False).astype(float)

total_sales_target = 1000000
days = (end_date - start_date).days + 1
average_price = df['price'].mean()
total_orders = int(total_sales_target / average_price)
orders_per_day = total_orders // days

order_id = 1
order_line_id = 1

with open("seed.sql", "w") as f:
    for day_offset in range(days):
        current_date = start_date + timedelta(days=day_offset)

        for _ in range(orders_per_day):
            hour = random.randint(7, 20)
            minute = random.randint(0, 59)
            order_datetime = current_date.replace(hour=hour, minute=minute, second=0)

            num_items = random.randint(1, 4)
            order_items = []
            order_total = 0

            for _ in range(num_items):
                product = df.sample(n=1).iloc[0]
                quantity = random.randint(1, 5)
                price = product['price'] if 'price' in product else 0
                line_total = price * quantity
                order_items.append((order_line_id, order_id, product['name'], quantity, price))
                order_line_id += 1
                order_total += line_total

            if order_total > 0:
                f.write(f"INSERT INTO orders (order_id, order_date, total) VALUES ({order_id}, '{order_datetime.strftime('%Y-%m-%d %H:%M:%S')}', {order_total:.2f});\n")
                for ol in order_items:
                    f.write(f"INSERT INTO order_line (order_line_id, order_id, product_name, quantity, price) VALUES ({ol[0]}, {ol[1]}, '{ol[2]}', {ol[3]}, {ol[4]:.2f});\n")
                order_id += 1
            else:
                break
