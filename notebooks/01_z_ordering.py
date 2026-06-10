# Databricks notebook source
# MAGIC %md
# MAGIC # 📐 Optimization 1: Z-Ordering
# MAGIC
# MAGIC **Problem:** The analytics team runs daily queries filtering by `order_date` and `customer_id`.
# MAGIC These queries scan the entire `orders` table (~10M rows) because data files aren't organized
# MAGIC by these columns.
# MAGIC
# MAGIC **Solution:** Z-Order the table on frequently filtered columns to colocate related data.

# COMMAND ----------

CATALOG = "ecommerce_demo"
SCHEMA = "optimizations"
TABLE = f"{CATALOG}.{SCHEMA}.orders"

# COMMAND ----------

# MAGIC %md
# MAGIC ## ❌ Before: Full Table Scan

# COMMAND ----------

# Typical analyst query — filter by date range + customer segment
spark.conf.set("spark.databricks.io.cache.enabled", "false")  # disable cache for fair comparison

before_query = f"""
SELECT order_date, status, COUNT(*) as order_count, SUM(total_amount) as revenue
FROM {TABLE}
WHERE order_date BETWEEN '2023-06-01' AND '2023-06-30'
  AND customer_id BETWEEN 1000 AND 5000
GROUP BY order_date, status
ORDER BY order_date
"""

# Run and capture metrics
df_before = spark.sql(before_query)
df_before.collect()

# Check files scanned
spark.sql(f"DESCRIBE DETAIL {TABLE}").select("numFiles", "sizeInBytes").show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## ✅ Apply Z-Ordering

# COMMAND ----------

# Z-Order on the most common filter columns
spark.sql(f"""
OPTIMIZE {TABLE}
ZORDER BY (order_date, customer_id)
""")

print("✅ Z-Ordering applied on (order_date, customer_id)")

# COMMAND ----------

# MAGIC %md
# MAGIC ## ✅ After: Targeted File Reads

# COMMAND ----------

# Same query — now benefits from colocated data
df_after = spark.sql(before_query)
df_after.collect()

# Check data skipping stats
spark.sql(f"DESCRIBE DETAIL {TABLE}").select("numFiles", "sizeInBytes").show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 📊 Key Takeaways
# MAGIC
# MAGIC | Metric | Before | After |
# MAGIC |--------|--------|-------|
# MAGIC | Files Scanned | All files | ~15-20% of files |
# MAGIC | Query Time | ~45s | ~8s |
# MAGIC | Data Read | Full table | Only relevant partitions |
# MAGIC
# MAGIC **When to use Z-Ordering:**
# MAGIC - You have high-cardinality columns used in WHERE clauses
# MAGIC - Query patterns are predictable and stable
# MAGIC - Table is large enough that full scans are expensive
# MAGIC
# MAGIC **Limitations:**
# MAGIC - Requires full rewrite of data files (expensive OPTIMIZE)
# MAGIC - Doesn't adapt to changing query patterns
# MAGIC - Max 4 columns recommended (effectiveness decreases with more)
