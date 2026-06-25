import traceframe as tf

tf.start("finance_revenue_analysis")
revenue = tf.read_csv("revenue.csv", name="revenue")
tf.chart(revenue, x="month", y="revenue", kind="bar", title="Revenue", name="revenue_chart")
tf.export_report("finance_audit_report.html")

