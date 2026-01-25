import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go

# ---------------------------------------------------------
# 1. CREATE A FAKE SHOPPING CART DATASET
# ---------------------------------------------------------
# This dictionary simulates a list of orders with:
# - order_id: which order the line belongs to
# - customer: who bought the products
# - product: which product was bought
# - category: which type/category of product it is
# - quantity: how many units were bought
# - unit_price: price per unit of the product
data = {
    "order_id":  [1, 1, 1, 2, 2, 3, 3, 4],
    "customer":  ["Renato", "Renato", "Renato", "Ana", "Ana", "Carlos", "Carlos", "Renato"],
    "product":   ["Keyboard", "Mouse", "Monitor", "Mouse", "Headset", "Keyboard", "Chair", "Chair"],
    "category":  ["Peripherals", "Peripherals", "Monitor", "Peripherals", "Audio", "Peripherals", "Furniture", "Furniture"],
    "quantity":  [1, 4, 3, 2, 5, 3, 4, 7],
    "unit_price":[50.0, 25.0, 200.0, 25.0, 80.0, 45.0, 300.0, 300.0]
}

# Convert the dictionary into a Pandas DataFrame,
# which is like an in-memory table (rows + columns).
df = pd.DataFrame(data)

# Create a new column "total" = quantity * unit_price.
# This represents the line total value for each item in the cart.
df["total"] = df["quantity"] * df["unit_price"]

# ---------------------------------------------------------
# 2. AGGREGATIONS (GROUPING AND SUMMARIZING THE DATA)
# ---------------------------------------------------------
# Here we group the data and calculate the total revenue
# per product, per customer, and per category.
# Then we sort descending by total so the biggest values appear first.

# Total revenue per product
product_sales = (
    df.groupby("product", as_index=False)["total"]
      .sum()
      .sort_values("total", ascending=False)
)

# Total revenue per customer
customer_sales = (
    df.groupby("customer", as_index=False)["total"]
      .sum()
      .sort_values("total", ascending=False)
)

# Total revenue per category
category_sales = (
    df.groupby("category", as_index=False)["total"]
      .sum()
      .sort_values("total", ascending=False)
)

# ---------------------------------------------------------
# 3. CREATING A 2x2 DASHBOARD LAYOUT WITH PLOTLY
# ---------------------------------------------------------
# We will build 4 charts inside a single figure:
#  - Row 1, Col 1: Bar chart - revenue per product
#  - Row 1, Col 2: Bar chart - revenue per customer
#  - Row 2, Col 1: Pie chart - revenue share by category
#  - Row 2, Col 2: Scatter plot - quantity vs line total
#
# make_subplots lets us define the layout of multiple charts.

fig = make_subplots(
    rows=2,
    cols=2,
    subplot_titles=(
        "Revenue per Product",
        "Revenue per Customer",
        "Revenue Share by Category",
        "Quantity vs Total"
    ),
    # "specs" tells Plotly what type of chart each position will hold.
    # "xy" = normal 2D chart (bar, scatter, etc.)
    # "domain" = used for charts like pie, donut, etc.
    specs=[
        [{"type": "xy"},     {"type": "xy"}],
        [{"type": "domain"}, {"type": "xy"}],  # bottom-left is a pie chart
    ]
)

# ---------------------------------------------------------
# 4. ADDING TRACES (INDIVIDUAL CHARTS) TO THE SUBPLOTS
# ---------------------------------------------------------

# (1) Bar chart: revenue per product (row 1, col 1)
fig.add_trace(
    go.Bar(
        x=product_sales["product"],  # x-axis: product names
        y=product_sales["total"],    # y-axis: total revenue per product
        name="Revenue per Product"
    ),
    row=1, col=1
)

# (2) Bar chart: revenue per customer (row 1, col 2)
fig.add_trace(
    go.Bar(
        x=customer_sales["customer"],  # x-axis: customer names
        y=customer_sales["total"],     # y-axis: total revenue per customer
        name="Revenue per Customer"
    ),
    row=1, col=2
)

# (3) Pie chart: revenue share by category (row 2, col 1)
fig.add_trace(
    go.Pie(
        labels=category_sales["category"],  # categories as labels
        values=category_sales["total"],     # total revenue per category as values
        name="Revenue by Category"
    ),
    row=2, col=1
)

# (4) Scatter plot: quantity vs total (row 2, col 2)
fig.add_trace(
    go.Scatter(
        x=df["quantity"],           # x-axis: quantity purchased
        y=df["total"],              # y-axis: line total value
        mode="markers",             # markers = dots in the scatter plot
        # Show product + customer in the hover text
        text=df["product"] + " / " + df["customer"],
        name="Quantity vs Total",
        # Custom tooltip using hovertemplate:
        # %{text} will show "Product / Customer"
        # %{x} will show the quantity
        # %{y} will show the total
        hovertemplate="<b>%{text}</b><br>qty=%{x}<br>total=%{y}<extra></extra>",
    ),
    row=2, col=2
)

# ---------------------------------------------------------
# 5. LAYOUT CONFIGURATION (TITLES, AXES, SIZE, ETC.)
# ---------------------------------------------------------

# General layout options for the whole figure
fig.update_layout(
    title="Shopping Cart Overview",  # main title at the top
    height=800,                      # height of the full dashboard in pixels
    showlegend=False                 # hide the global legend (optional)
)

# Set axis titles for each subplot
fig.update_xaxes(title_text="Product",  row=1, col=1)
fig.update_yaxes(title_text="Revenue",  row=1, col=1)

fig.update_xaxes(title_text="Customer", row=1, col=2)
fig.update_yaxes(title_text="Revenue",  row=1, col=2)

fig.update_xaxes(title_text="Quantity", row=2, col=2)
fig.update_yaxes(title_text="Line Total", row=2, col=2)

# ---------------------------------------------------------
# 6. RENDER THE DASHBOARD
# ---------------------------------------------------------
# This opens the interactive chart:
# - In Jupyter: shows inline
# - In some environments: opens in browser
fig.show()
