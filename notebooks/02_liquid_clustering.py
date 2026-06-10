# Databricks notebook source
# MAGIC %md
# MAGIC # 💧 Optimization 2: Liquid Clustering
# MAGIC
# MAGIC **Problem:** The analytics team's query patterns evolve. Initially they filtered by `order_date`,
# MAGIC but now the finance team filters by `payment_method` and `status`. Z-Ordering requires a full rewrite to change
# MAGIC clustering columns — expensive and slow.
# MAGIC
# MAGIC **Solution:** Liquid Clustering dynamically and incrementally clusters data. You can change
# MAGIC clustering keys without rewriting the entire table.

# COMMAND ----------

CATALOG = "ecommerce_lakehouse_az"
SCHEMA = "optimizations"

# COMMAND ----------

# MAGIC %md
# MAGIC ## Create Table with Liquid Clustering

# COMMAND ----------

# Create a new orders table with liquid clustering enabled
spark.sql(f"""
CREATE OR REPLACE TABLE {CATALOG}.{SCHEMA}.orders_liquid_clustered
CLUSTER BY (order_date, customer_id)
AS SELECT * FROM {CATALOG}.{SCHEMA}.orders
""")

print("✅ Table created with Liquid Clustering on (order_date, customer_id)")

# COMMAND ----------

# MAGIC %md
# MAGIC ## ✅ Query with Initial Clustering Keys

# COMMAND ----------

TABLE = f"{CATALOG}.{SCHEMA}.orders_liquid_clustered"

# Query filtering by the clustering keys — fast!
query_by_date = f"""
SELECT order_date, status, SUM(total_amount) as revenue
FROM {TABLE}
WHERE order_date BETWEEN '2023-06-01' AND '2023-06-30'
GROUP BY order_date, status
"""

df = spark.sql(query_by_date)
df.show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 🔄 Evolve Clustering Keys (No Full Rewrite!)

# COMMAND ----------

# Business requirement changed — finance team now needs fast queries by payment_method + status
# With Z-Ordering, this would require a full OPTIMIZE rewrite
# With Liquid Clustering, just ALTER the table:

spark.sql(f"""
ALTER TABLE {TABLE}
CLUSTER BY (payment_method, status)
""")

print("✅ Clustering keys changed to (payment_method, status) — no full rewrite needed!")

# COMMAND ----------

# Trigger incremental clustering on new data
spark.sql(f"OPTIMIZE {TABLE}")
print("✅ Incremental OPTIMIZE applied — only unclustered data is reorganized")

# COMMAND ----------

# MAGIC %md
# MAGIC ## ✅ Query with New Clustering Keys

# COMMAND ----------

# Now payment_method + status queries are fast
query_by_payment = f"""
SELECT payment_method, status, COUNT(*) as orders, SUM(total_amount) as revenue
FROM {TABLE}
WHERE payment_method = 'credit_card'
  AND status = 'completed'
  AND order_date >= '2023-01-01'
GROUP BY payment_method, status
"""

df = spark.sql(query_by_payment)
df.show(10)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 📊 Z-Ordering vs Liquid Clustering
# MAGIC
# MAGIC | Feature | Z-Ordering | Liquid Clustering |
# MAGIC |---------|-----------|-------------------|
# MAGIC | Rewrite required to change keys | ✅ Full rewrite | ❌ Incremental |
# MAGIC | Works with OPTIMIZE | ✅ | ✅ |
# MAGIC | Adapts to new query patterns | ❌ Manual | ✅ ALTER TABLE |
# MAGIC | Supports incremental clustering | ❌ | ✅ |
# MAGIC | Requires partitioning | Optional | ❌ Replaces it |
# MAGIC | Min DBR version | 7.0+ | 13.3+ |
# MAGIC
# MAGIC **When to use Liquid Clustering:**
# MAGIC - Query patterns change over time
# MAGIC - You want to eliminate partitioning complexity
# MAGIC - Tables receive frequent appends (incremental clustering is cheaper)
# MAGIC - New tables (preferred over Z-Ordering going forward)
