import pandas as pd

data = {
    "order_id":  [1, 1, 1, 2, 2, 3, 3, 4],
    "customer":  ["Renato", "Renato", "Renato", "Ana", "Ana", "Carlos", "Carlos", "Renato"],
    "product":   ["Keyboard", "Mouse", "Monitor", "Mouse", "Headset", "Keyboard", "Chair", "Chair"],
    "category":  ["Peripherals", "Peripherals", "Monitor", "Peripherals", "Audio", "Peripherals", "Furniture", "Furniture"],
    "quantity":  [1, 4, 3, 2, 5, 3, 4, 7],
    "unit_price":[50.0, 25.0, 200.0, 25.0, 80.0, 45.0, 300.0, 300.0]
}

df = pd.DataFrame(data)
df["total"] = df["quantity"] * df["unit_price"]

print("\n=== RAW DATAFRAME ===")
print(df)

# ===========================================================
print("\n=== BASIC AGGREGATIONS ===")

total_revenue = df["total"].sum()
print(f"Total revenue:\t\t{total_revenue}")

avg_ticket = df["total"].mean()
print(f"Average line total:\t{avg_ticket}")

min_line = df["total"].min()
max_line = df["total"].max()
print(f"Min line total:\t\t{min_line}")
print(f"Max line total:\t\t{max_line}")

std_total = df["total"].std()
print(f"Std deviation:\t\t{std_total}")

# ===========================================================
print("\n=== DISTINCT / UNIQUE VALUES ===")

print("Unique products:\t", df["product"].unique())
print("Number of products:\t", df["product"].nunique())

# ===========================================================
print("\n=== GROUP BY CUSTOMER ===")

customer_stats = df.groupby("customer")["total"].agg(
    sum="sum", mean="mean", min="min", max="max", count="count", std="std"
)

print(customer_stats)

# ===========================================================
print("\n=== GROUP BY CUSTOMER + CATEGORY ===")

customer_category_stats = df.groupby(["customer", "category"])["total"].agg(
    sum="sum", mean="mean", min="min", max="max", count="count"
)

print(customer_category_stats)

# ===========================================================
print("\n=== PRODUCT LEVEL STATS ===")

product_stats = df.groupby("product").agg(
    total_revenue=("total", "sum"),
    avg_unit_price=("unit_price", "mean"),
    times_sold=("order_id", "count"),
    distinct_customers=("customer", "nunique")
)

print(product_stats)

# ===========================================================
print("\n=== SUMMARY OF AGGREGATION FUNCTIONS ===")

summary = df["total"].agg(
    sum="sum", mean="mean", min="min", max="max", count="count", std="std"
)

print(summary)

print("\nDistinct products:\t", df["product"].nunique())
print("Product list:\t\t", list(df["product"].unique()))
