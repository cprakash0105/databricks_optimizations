# Databricks cluster for running optimization notebooks
resource "databricks_cluster" "optimizations" {
  cluster_name            = "${var.project_name}-${var.environment}"
  spark_version           = "14.3.x-scala2.12"
  node_type_id            = "Standard_DS3_v2"
  autotermination_minutes = var.cluster_autotermination_minutes
  num_workers             = var.cluster_num_workers

  spark_conf = {
    "spark.sql.adaptive.enabled"                       = "true"
    "spark.sql.adaptive.skewJoin.enabled"              = "true"
    "spark.sql.adaptive.coalescePartitions.enabled"    = "true"
    "spark.databricks.delta.optimizeWrite.enabled"     = "true"
    "spark.databricks.delta.autoCompact.enabled"       = "true"
    "spark.databricks.delta.properties.defaults.enableChangeDataFeed" = "true"
  }

  custom_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "terraform"
  }

  library {
    pypi {
      package = "faker"
    }
  }
}

# Smaller cluster for development/testing
resource "databricks_cluster" "dev" {
  cluster_name            = "${var.project_name}-dev-single-node"
  spark_version           = "14.3.x-scala2.12"
  node_type_id            = "Standard_DS3_v2"
  autotermination_minutes = 15
  num_workers             = 0

  spark_conf = {
    "spark.master"                     = "local[*]"
    "spark.databricks.cluster.profile" = "singleNode"
  }

  custom_tags = {
    Project       = var.project_name
    Environment   = "dev"
    ResourceClass = "SingleNode"
    ManagedBy     = "terraform"
  }
}
