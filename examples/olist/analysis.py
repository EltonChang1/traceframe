import traceframe as tf

tf.start("olist_marketplace_analysis")

orders = tf.read_csv("data/olist_orders_dataset.csv", name="orders")
items = tf.read_csv("data/olist_order_items_dataset.csv", name="order_items")
customers = tf.read_csv("data/olist_customers_dataset.csv", name="customers")

delivered_orders = tf.filter_rows(
    orders,
    "order_status == 'delivered'",
    name="delivered_orders",
)

tf.expect_not_null(delivered_orders, ["order_id", "customer_id"])
tf.expect_unique(delivered_orders, "order_id")

tf.track(
    items,
    name="order_items_tracked",
    source="order_items",
    operation="track_order_items",
)

tf.metric(
    name="gross_merchandise_value",
    formula="SUM(price)",
    source="order_items_tracked",
    description="Total item revenue for delivered orders in the sample.",
)

monthly_by_state = tf.sql(
    """
    SELECT
        strftime('%Y-%m', CAST(o.order_purchase_timestamp AS TIMESTAMP)) AS month,
        c.customer_state AS state,
        SUM(i.price) AS revenue,
        COUNT(DISTINCT o.order_id) AS order_count
    FROM delivered_orders o
    JOIN order_items_tracked i ON o.order_id = i.order_id
    JOIN customers c ON o.customer_id = c.customer_id
    GROUP BY 1, 2
    ORDER BY 1, 2
    """,
    name="monthly_revenue_by_state",
)

tf.chart(
    monthly_by_state,
    x="month",
    y="revenue",
    kind="bar",
    title="Monthly Revenue by State",
    name="monthly_revenue_by_state_chart",
)

tf.claim(
    "State-level monthly revenue uses delivered orders only and joins orders, items, and customers.",
    supports=["monthly_revenue_by_state", "monthly_revenue_by_state_chart"],
    confidence="high",
)

tf.export_report("olist_audit_report.html")
