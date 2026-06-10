# Databricks notebook source
# MAGIC %md
# MAGIC # 📋 Optimization 5: Checkpointing
# MAGIC
# MAGIC **Problem:** The `orders` table receives frequent MERGE/UPDATE operations (order status
# MAGIC updates, cancellations, refunds). After 500+ transactions, every query must replay
# MAGIC all JSON log files in `_delta_log/` to reconstruct the current table state — adding
# MAGIC 10-15 seconds of overhead before any data is even read.
# MAGIC
# MAGIC **Solution:** Delta Lake checkpointing creates periodic Parquet snapshots of the
# MAGIC transaction log. Instead of replaying 500 JSON files, the engine reads 1 checkpoint file.

# COMMAND ----------

CATALOG = "ecommerce_demo"
SCHEMA = "optimizations"

# COMMAND ----------

# MAGIC %md
# MAGIC ## 🔍 Understanding Delta Transaction Log

# COMMAND ----------

# Create a demo table to simulate heavy write operations
spark.sql(f"""
CREATE OR REPLACE TABLE {CATALOG}.{SCHEMA}.orders_checkpoint_demo
AS SELECT * FROM {CATALOG}.{SCHEMA}.orders LIMIT 1000000
""")

TABLE = f"{CATALOG}.{SCHEMA}.orders_checkpoint_demo"

# COMMAND ----------

# MAGIC %md
# MAGIC ## 🔄 Simulate Heavy Transaction Activity

# COMMAND ----------

# Simulate 50 small updates (like real-time order status changes)
for i in range(50):
    spark.sql(f"""
    UPDATE {TABLE}
    SET status = 'shipped'
    WHERE order_id BETWEEN {i * 1000 + 1} AND {(i + 1) * 1000}
      AND status = 'processing'
    """)

print("✅ Simulated 50 UPDATE transactions (order status changes)")

# COMMAND ----------

# Check how many log files exist now
history = spark.sql(f"DESCRIBE HISTORY {TABLE}")
print(f"Total versions: {history.count()}")
history.select("version", "operation", "timestamp").show(20, truncate=False)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 📂 Inspect the Delta Log Structure

# COMMAND ----------

# Delta creates checkpoints every 10 commits by default
# Let's look at the log directory structure
log_path = spark.sql(f"DESCRIBE DETAIL {TABLE}").select("location").first()[0] + "/_delta_log/"

log_files = dbutils.fs.ls(log_path)
json_files = [f for f in log_files if f.name.endswith(".json")]
checkpoint_files = [f for f in log_files if "checkpoint" in f.name]

print(f"JSON log files: {len(json_files)}")
print(f"Checkpoint files: {len(checkpoint_files)}")
print(f"\nLatest checkpoints:")
for f in sorted(checkpoint_files, key=lambda x: x.name)[-5:]:
    print(f"  {f.name} ({f.size / 1024:.1f} KB)")

# COMMAND ----------

# MAGIC %md
# MAGIC ## ⚙️ How Checkpointing Works
# MAGIC
# MAGIC ```
# MAGIC _delta_log/
# MAGIC ├── 00000000000000000000.json    ← initial commit
# MAGIC ├── 00000000000000000001.json
# MAGIC ├── ...
# MAGIC ├── 00000000000000000009.json
# MAGIC ├── 00000000000000000010.checkpoint.parquet  ← CHECKPOINT (snapshot at v10)
# MAGIC ├── 00000000000000000011.json
# MAGIC ├── ...
# MAGIC ├── 00000000000000000019.json
# MAGIC ├── 00000000000000000020.checkpoint.parquet  ← CHECKPOINT (snapshot at v20)
# MAGIC └── ...
# MAGIC ```
# MAGIC
# MAGIC To read at version 25, engine reads:
# MAGIC - `v20.checkpoint.parquet` + `v21.json` + `v22.json` + `v23.json` + `v24.json` + `v25.json`
# MAGIC - Instead of replaying all 25 JSON files!

# COMMAND ----------

# MAGIC %md
# MAGIC ## ✅ Tune Checkpoint Interval

# COMMAND ----------

# Default checkpoint interval is every 10 commits
# For high-frequency tables, you can tune this:

spark.sql(f"""
ALTER TABLE {TABLE}
SET TBLPROPERTIES ('delta.checkpointInterval' = '5')
""")

print("✅ Checkpoint interval set to every 5 commits (from default 10)")
print("   → Reduces log replay overhead for frequently updated tables")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 🧹 VACUUM: Clean Up Old Log Files

# COMMAND ----------

# After checkpointing, old JSON files before the checkpoint can be cleaned
# VACUUM removes data files; log cleanup is automatic after checkpoint

spark.conf.set("spark.databricks.delta.retentionDurationCheck.enabled", "false")

spark.sql(f"VACUUM {TABLE} RETAIN 168 HOURS")  # 7 days retention
print("✅ VACUUM complete — old data files cleaned up")

# COMMAND ----------

# MAGIC %md
# MAGIC ## ⏱️ Performance Comparison

# COMMAND ----------

import time

# Cold read — measures log replay time
spark.catalog.clearCache()

start = time.time()
spark.sql(f"SELECT COUNT(*) FROM {TABLE}").collect()
elapsed = time.time() - start

print(f"Query time (includes log resolution): {elapsed:.2f}s")
print("With checkpoint: engine reads 1 Parquet checkpoint + few JSON files")
print("Without checkpoint: engine would replay ALL JSON files sequentially")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 📊 Key Takeaways
# MAGIC
# MAGIC | Aspect | Details |
# MAGIC |--------|---------|
# MAGIC | Default interval | Every 10 commits |
# MAGIC | Checkpoint format | Parquet (fast to read) |
# MAGIC | Configurable | `delta.checkpointInterval` table property |
# MAGIC | Automatic | ✅ No manual action needed |
# MAGIC | Best for | Tables with frequent small writes/updates |
# MAGIC
# MAGIC **When to tune checkpointing:**
# MAGIC - Streaming tables with micro-batches (set interval to 5)
# MAGIC - Tables with 100s of daily MERGE operations
# MAGIC - When you notice slow "planning" time in Spark UI before actual data scan
