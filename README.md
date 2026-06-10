# 🚀 Databricks Top 5 Optimizations — E-commerce Analytics

> A data engineer's guide to supercharging query performance on a large-scale e-commerce dataset using Databricks & Delta Lake optimizations.

![Databricks](https://img.shields.io/badge/Databricks-Runtime%2014.0+-red?logo=databricks)
![Delta Lake](https://img.shields.io/badge/Delta%20Lake-3.0+-blue)
![Terraform](https://img.shields.io/badge/IaC-Terraform-purple?logo=terraform)

---

## 📖 The Story

You're a **data engineer at a fast-growing online retailer**. The analytics team reports that dashboard queries on the orders table (~50M+ rows) are painfully slow. Product managers can't get real-time insights into sales trends, and the data science team's ML pipelines are timing out.

Your mission: **Apply 5 key Databricks optimizations** to cut query times from minutes to seconds.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Databricks Workspace                │
├─────────────────────────────────────────────────────┤
│  ┌───────────┐  ┌───────────┐  ┌───────────────┐   │
│  │  Orders   │  │Order Items│  │   Customers   │   │
│  │   10M     │  │   50M     │  │     1M        │   │
│  └───────────┘  └───────────┘  └───────────────┘   │
│                                                     │
│  Optimizations Applied:                             │
│  [1] Z-Ordering  [2] Liquid Clustering              │
│  [3] AQE         [4] Data Skipping                  │
│  [5] Checkpointing                                  │
└─────────────────────────────────────────────────────┘
```

---

## 📊 Results Summary

| # | Optimization | Query Before | Query After | Improvement |
|---|---|---|---|---|
| 1 | Z-Ordering | ~45s | ~8s | **82% faster** |
| 2 | Liquid Clustering | ~40s | ~6s | **85% faster** |
| 3 | Adaptive Query Execution | ~120s | ~35s | **71% faster** |
| 4 | Data Skipping | ~30s | ~4s | **87% faster** |
| 5 | Checkpointing | ~15s | ~3s | **80% faster** |

> ⚠️ Results are illustrative. Actual improvements depend on data volume, cluster size, and query patterns.

---

## 🗂️ Project Structure

```
databricks-top5-optimizations/
├── README.md
├── notebooks/
│   ├── 00_data_generation.py        # Generate synthetic e-commerce data
│   ├── 01_z_ordering.py             # Z-Order optimization demo
│   ├── 02_liquid_clustering.py      # Liquid Clustering demo
│   ├── 03_adaptive_query_execution.py  # AQE demo
│   ├── 04_data_skipping.py          # Data Skipping demo
│   └── 05_checkpointing.py          # Checkpointing demo
├── terraform/
│   ├── main.tf                      # Provider & backend config
│   ├── variables.tf                 # Input variables
│   ├── cluster.tf                   # Databricks cluster
│   ├── policies.tf                  # Cluster policies
│   ├── rbac.tf                      # Access control & permissions
│   └── outputs.tf                   # Output values
├── images/                          # Diagrams & charts
└── results/                         # Benchmark outputs
```

---

## 🔧 Optimizations Explained

### 1. Z-Ordering
Colocates related data within the same set of files to minimize the amount of data read during queries.

**Use case:** Speed up queries filtering by `order_date` + `customer_id`

### 2. Liquid Clustering
A next-gen replacement for Z-Ordering. Incrementally clusters data without full rewrites, and adapts as query patterns evolve.

**Use case:** Adapt clustering when analysts shift from filtering by `order_date` to filtering by `region`

### 3. Adaptive Query Execution (AQE)
Dynamically optimizes query plans at runtime — handles skewed joins, coalesces partitions, and switches join strategies.

**Use case:** Join `orders` with `order_items` where some products have 1000x more sales (data skew)

### 4. Data Skipping
Leverages file-level min/max statistics to skip irrelevant data files entirely during scans.

**Use case:** Filter `order_items` by `category` — only reads files containing that category

### 5. Checkpointing
Periodically creates checkpoint files in the Delta transaction log, avoiding the need to replay hundreds of JSON log files.

**Use case:** After 100s of MERGE/UPDATE operations on `orders`, speed up table reads

---

## 🚀 Getting Started

### Prerequisites
- Databricks workspace (AWS, Azure, or GCP)
- Terraform >= 1.5
- Python 3.9+

### Infrastructure Setup
```bash
cd terraform/
terraform init
terraform plan -var-file="terraform.tfvars"
terraform apply -var-file="terraform.tfvars"
```

### Run Notebooks
1. Import `notebooks/` folder into your Databricks workspace
2. Run `00_data_generation.py` first to create the dataset
3. Run notebooks 01–05 in any order

---

## 📝 License

MIT

---

## 🤝 Connect

If you found this useful, let's connect on [LinkedIn](https://linkedin.com)!
