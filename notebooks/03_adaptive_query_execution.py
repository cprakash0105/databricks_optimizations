# Databricks notebook source
# MAGIC %md
# MAGIC # ⚡ Optimization 3: Adaptive Query Execution (AQE)
# MAGIC
# MAGIC **Problem:** Joining `orders` with `order_items` is slow because some products
# MAGIC (e.g., best-sellers) have 1000x more records than others, causing **data skew**.
# MAGIC The query planner picks a suboptimal join strategy at compile time.
# MAGIC
# MAGIC **Solution:** AQE dynamically re-optimizes the query plan at runtime based on actual
# MAGIC data statistics — handling skew, coalescing partitions, and switching join strategies.

# COMMAND ----------

CATALOG = "ecommerce_lakehouse_az"
SCHEMA = "optimizations"
ORDERS = f"{CATALOG}.{SCHEMA}.orders"
ORDER_ITEMS = f"{CATALOG}.{SCHEMA}.order_items"

# COMMAND ----------

# MAGIC %md
# MAGIC ## ❌ Before: AQE Disabled

# COMMAND ----------

# Disable AQE to show baseline performance
spark.conf.set("spark.sql.adaptive.enabled", "false")
spark.conf.set("spark.sql.adaptive.skewJoin.enabled", "false")

# Skewed join — some products have disproportionately more items
skewed_query = f"""
SELECT
    oi.category,
    o.status,
    COUNT(*) as total_items,
    SUM(oi.unit_price * oi.quantity) as gross_revenue,
    AVG(oi.discount_pct) as avg_discount
FROM {ORDER_ITEMS} oi
JOIN {ORDERS} o ON oi.order_id = o.order_id
WHERE o.order_date >= '2023-01-01'
GROUP BY oi.category, o.status
ORDER BY gross_revenue DESC
"""

df_before = spark.sql(skewed_query)
df_before.collect()

# COMMAND ----------

# MAGIC %md
# MAGIC ## ✅ Enable AQE

# COMMAND ----------

# Enable all AQE features
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.sql.adaptive.skewJoin.enabled", "true")
spark.conf.set("spark.sql.adaptive.coalescePartitions.enabled", "true")
spark.conf.set("spark.sql.adaptive.localShuffleReader.enabled", "true")

print("✅ AQE enabled with all sub-features:")
print("   - Skew join optimization")
print("   - Partition coalescing")
print("   - Local shuffle reader")

# COMMAND ----------

# MAGIC %md
# MAGIC ## ✅ After: AQE Enabled

# COMMAND ----------

# Same query — AQE dynamically optimizes at runtime
df_after = spark.sql(skewed_query)
df_after.show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 🔍 What AQE Did Behind the Scenes
# MAGIC
# MAGIC Check the Spark UI's SQL tab to see:
# MAGIC 1. **Skew Join Handling** — Split skewed partitions into smaller sub-partitions
# MAGIC 2. **Partition Coalescing** — Merged small shuffle partitions to reduce overhead
# MAGIC 3. **Join Strategy Switch** — Converted sort-merge join to broadcast join for small tables

# COMMAND ----------

# Demonstrate partition coalescing
spark.conf.set("spark.sql.adaptive.coalescePartitions.initialPartitionNum", "200")
spark.conf.set("spark.sql.adaptive.coalescePartitions.minPartitionSize", "64MB")

coalesce_query = f"""
SELECT customer_id, COUNT(*) as order_count, SUM(total_amount) as lifetime_value
FROM {ORDERS}
WHERE status = 'completed'
GROUP BY customer_id
HAVING COUNT(*) > 5
ORDER BY lifetime_value DESC
LIMIT 100
"""

df = spark.sql(coalesce_query)
df.show(10)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 📊 Key Takeaways
# MAGIC
# MAGIC | AQE Feature | What It Does | Our Use Case |
# MAGIC |-------------|-------------|--------------|
# MAGIC | Skew Join | Splits hot partitions | Best-seller products with 1000x more items |
# MAGIC | Coalesce Partitions | Merges small partitions | Reduces task overhead after filters |
# MAGIC | Switch Join Strategy | Changes join type at runtime | Small filtered table → broadcast join |
# MAGIC
# MAGIC **AQE is enabled by default in DBR 12.0+**, but understanding its features helps you:
# MAGIC - Diagnose performance issues in the Spark UI
# MAGIC - Tune thresholds for your specific workload
# MAGIC - Know when manual intervention is still needed
