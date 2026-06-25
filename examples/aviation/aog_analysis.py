import traceframe as tf

tf.start("aviation_maintenance_analysis")
maintenance = tf.read_csv("maintenance.csv", name="maintenance")
tf.metric("downtime_hours", "SUM(downtime_hours)", source="maintenance")
tf.chart(
    maintenance,
    x="event_date",
    y="downtime_hours",
    kind="bar",
    title="Downtime",
    name="downtime_chart",
)
tf.export_report("aviation_audit_report.html")
