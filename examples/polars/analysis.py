import traceframe as tf

tf.start("polars_revenue_analysis")

orders = tf.read_csv("orders.csv", name="orders", engine="polars")
clean_orders = tf.filter_rows(orders, "status != 'cancelled'", name="clean_orders")

tf.expect_not_null(clean_orders, "total_price")
tf.expect_unique(clean_orders, "order_id")
tf.metric("revenue", "SUM(total_price)", source="clean_orders")

monthly = tf.sql(
    """
    SELECT
        strftime('%Y-%m', CAST(order_date AS DATE)) AS month,
        SUM(total_price) AS revenue
    FROM clean_orders
    GROUP BY 1
    ORDER BY 1
""",
    name="monthly_revenue",
)

tf.chart(monthly, x="month", y="revenue", kind="bar", name="monthly_revenue_chart")
tf.claim(
    "Monthly revenue was calculated from non-cancelled Polars-tracked orders.",
    supports=["monthly_revenue", "monthly_revenue_chart"],
    confidence="high",
)
tf.export_report("polars_audit_report.html")
