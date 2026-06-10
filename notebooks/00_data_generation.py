# Databricks notebook source
# MAGIC %md
# MAGIC # 🛒 Data Generation — Synthetic E-commerce Dataset
# MAGIC
# MAGIC Generates realistic e-commerce data:
# MAGIC - **customers**: 1M rows
# MAGIC - **orders**: 10M rows
# MAGIC - **order_items**: 50M rows

# COMMAND ----------

from pyspark.sql import functions as F
from pyspark.sql.types import *
import random

# COMMAND ----------

CATALOG = "ecommerce_demo"
SCHEMA = "optimizations"

spark.sql(f"CREATE CATALOG IF NOT EXISTS {CATALOG}")
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.{SCHEMA}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Customers (1M rows)

# COMMAND ----------

NUM_CUSTOMERS = 100_000

regions = ["North America", "Europe", "Asia Pacific", "Latin America", "Middle East"]
tiers = ["bronze", "silver", "gold", "platinum"]

customers_df = (
    spark.range(1, NUM_CUSTOMERS + 1)
    .withColumnRenamed("id", "customer_id")
    .withColumn("region", F.element_at(F.array([F.lit(r) for r in regions]), (F.rand() * len(regions)).cast("int") + 1))
    .withColumn("tier", F.element_at(F.array([F.lit(t) for t in tiers]), (F.rand() * len(tiers)).cast("int") + 1))
    .withColumn("signup_date", F.date_add(F.lit("2019-01-01"), (F.rand() * 1800).cast("int")))
    .withColumn("email", F.concat(F.lit("user_"), F.col("customer_id"), F.lit("@example.com")))
)

customers_df.write.format("delta").mode("overwrite").saveAsTable(f"{CATALOG}.{SCHEMA}.customers")
print(f"✅ Customers table created: {NUM_CUSTOMERS:,} rows")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Orders (10M rows)

# COMMAND ----------

NUM_ORDERS = 1_000_000

statuses = ["completed", "shipped", "processing", "cancelled", "returned"]

orders_df = (
    spark.range(1, NUM_ORDERS + 1)
    .withColumnRenamed("id", "order_id")
    .withColumn("customer_id", (F.rand() * NUM_CUSTOMERS).cast("int") + 1)
    .withColumn("order_date", F.date_add(F.lit("2022-01-01"), (F.rand() * 730).cast("int")))
    .withColumn("status", F.element_at(F.array([F.lit(s) for s in statuses]), (F.rand() * len(statuses)).cast("int") + 1))
    .withColumn("total_amount", F.round(F.rand() * 500 + 10, 2))
    .withColumn("shipping_cost", F.round(F.rand() * 20 + 2, 2))
    .withColumn("payment_method", F.element_at(
        F.array([F.lit("credit_card"), F.lit("debit_card"), F.lit("paypal"), F.lit("bank_transfer")]),
        (F.rand() * 4).cast("int") + 1
    ))
)

orders_df.write.format("delta").mode("overwrite").saveAsTable(f"{CATALOG}.{SCHEMA}.orders")
print(f"✅ Orders table created: {NUM_ORDERS:,} rows")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Order Items (50M rows)

# COMMAND ----------

NUM_ITEMS = 5_000_000

categories = ["Electronics", "Clothing", "Home & Garden", "Sports", "Books", "Beauty", "Toys", "Food & Beverage"]

order_items_df = (
    spark.range(1, NUM_ITEMS + 1)
    .withColumnRenamed("id", "item_id")
    .withColumn("order_id", (F.rand() * NUM_ORDERS).cast("int") + 1)
    .withColumn("product_id", (F.rand() * 100_000).cast("int") + 1)
    .withColumn("category", F.element_at(F.array([F.lit(c) for c in categories]), (F.rand() * len(categories)).cast("int") + 1))
    .withColumn("quantity", (F.rand() * 5).cast("int") + 1)
    .withColumn("unit_price", F.round(F.rand() * 200 + 5, 2))
    .withColumn("discount_pct", F.when(F.rand() > 0.7, F.round(F.rand() * 30, 0)).otherwise(0))
)

order_items_df.write.format("delta").mode("overwrite").saveAsTable(f"{CATALOG}.{SCHEMA}.order_items")
print(f"✅ Order Items table created: {NUM_ITEMS:,} rows")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Verify Data

# COMMAND ----------

for table in ["customers", "orders", "order_items"]:
    count = spark.table(f"{CATALOG}.{SCHEMA}.{table}").count()
    print(f"  {table}: {count:,} rows")
