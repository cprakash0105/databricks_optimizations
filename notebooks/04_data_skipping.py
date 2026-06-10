# Databricks notebook source
# MAGIC %md
# MAGIC # 📂 Optimization 4: Data Skipping
# MAGIC
# MAGIC **Problem:** Queries filtering `order_items` by `category` (e.g., "Electronics") still read
# MAGIC all data files, even though only 1/8th of the data matches.
# MAGIC
# MAGIC **Solution:** Delta Lake automatically collects min/max/null statistics per column per file.
# MAGIC When a query filters on a column, files where the filter value is outside the min/max range
# MAGIC are skipped entirely — zero I/O for irrelevant files.

# COMMAND ----------

CATALOG = "ecommerce_lakehouse_az"
SCHEMA = "optimizations"
ORDER_ITEMS = f"{CATALOG}.{SCHEMA}.order_items"

# COMMAND ----------

# MAGIC %md
# MAGIC ## 🔍 Understanding File-Level Statistics

# COMMAND ----------

# Check current table stats
detail = spark.sql(f"DESCRIBE DETAIL {ORDER_ITEMS}")
detail.select("numFiles", "sizeInBytes").show()

# View the Delta log to see per-file stats
history = spark.sql(f"DESCRIBE HISTORY {ORDER_ITEMS} LIMIT 5")
history.select("version", "operation", "operationMetrics").show(truncate=False)

# COMMAND ----------

# MAGIC %md
# MAGIC ## ❌ Before: Without Optimized File Layout

# COMMAND ----------

spark.conf.set("spark.databricks.io.cache.enabled", "false")

# Query for a single category — should only need ~12.5% of data
category_query = f"""
SELECT
    product_id,
    SUM(quantity) as total_sold,
    SUM(unit_price * quantity) as revenue,
    AVG(discount_pct) as avg_discount
FROM {ORDER_ITEMS}
WHERE category = 'Electronics'
GROUP BY product_id
ORDER BY revenue DESC
LIMIT 20
"""

df_before = spark.sql(category_query)
df_before.explain(True)  # Check physical plan for files scanned
df_before.show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## ✅ Optimize for Data Skipping

# COMMAND ----------

# OPTIMIZE compacts small files and sorts data within files
# This improves min/max statistics effectiveness
spark.sql(f"""
OPTIMIZE {ORDER_ITEMS}
ZORDER BY (category)
""")

print("✅ Table optimized — files now have tight min/max bounds on 'category'")

# COMMAND ----------

# MAGIC %md
# MAGIC ## ✅ After: Data Skipping in Action

# COMMAND ----------

# Same query — now Delta skips files where category != 'Electronics'
df_after = spark.sql(category_query)
df_after.explain(True)  # Compare physical plan — fewer files scanned
df_after.show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 📈 Verify Skipping with Metrics

# COMMAND ----------

# Enable verbose metrics to see how many files were skipped
spark.conf.set("spark.databricks.delta.stats.collect", "true")

# Run with SQL metrics
spark.sql(f"""
SELECT COUNT(*) FROM {ORDER_ITEMS} WHERE category = 'Electronics'
""").show()

# Check the Spark UI SQL tab for:
# - "number of files read" vs "total number of files"
# - "size of files read" vs "total size of files"

# COMMAND ----------

# MAGIC %md
# MAGIC ## 🧪 Multi-Column Skipping

# COMMAND ----------

# Data skipping works on multiple columns simultaneously
multi_filter_query = f"""
SELECT category, COUNT(*) as items, SUM(unit_price * quantity) as revenue
FROM {ORDER_ITEMS}
WHERE category IN ('Electronics', 'Books')
  AND unit_price > 100
  AND quantity >= 3
GROUP BY category
"""

spark.sql(multi_filter_query).show()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 📊 Key Takeaways
# MAGIC
# MAGIC | Aspect | Details |
# MAGIC |--------|---------|
# MAGIC | How it works | Min/max stats per column per file → skip files outside range |
# MAGIC | Stats collected on | First 32 columns by default |
# MAGIC | Best for | Low-cardinality or range-based filters |
# MAGIC | Cost | Free — happens automatically on Delta tables |
# MAGIC | Improved by | OPTIMIZE + ZORDER (tighter min/max bounds) |
# MAGIC
# MAGIC **Pro Tips:**
# MAGIC - Reorder columns so frequently-filtered ones are in the first 32
# MAGIC - Use `delta.dataSkippingNumIndexedCols` to increase indexed columns
# MAGIC - Combine with Z-Ordering for maximum skipping efficiency
