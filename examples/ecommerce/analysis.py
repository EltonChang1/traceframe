import traceframe as tf

tf.start("ecommerce_revenue_analysis")

orders = tf.read_csv("orders.csv", name="orders")

clean_orders = tf.track(
    orders.drop_duplicates("order_id"),
    name="clean_orders",
    source="orders",
    operation="drop_duplicates(order_id)",
)

large_orders = tf.filter_rows(
    clean_orders,
    "total_price >= 100",
    name="large_orders",
)

tf.metric(
    name="revenue",
    formula="SUM(total_price)",
    source="large_orders",
    description="Total order revenue after duplicate order IDs are removed.",
)

monthly = tf.sql(
    """
    SELECT
        strftime('%Y-%m', CAST(order_date AS DATE)) AS month,
        SUM(total_price) AS revenue,
        COUNT(*) AS order_count
    FROM large_orders
    GROUP BY 1
    ORDER BY 1
""",
    name="monthly_revenue",
)

tf.chart(
    monthly,
    x="month",
    y="revenue",
    kind="line",
    title="Monthly Revenue",
    name="monthly_revenue_chart",
)

tf.claim(
    "Monthly revenue trend was calculated after removing duplicate order IDs.",
    supports=["monthly_revenue", "monthly_revenue_chart"],
    confidence="high",
)

tf.export_report("ecommerce_audit_report.html")
