# Main cluster for running optimization notebooks (single node due to trial quota)
resource "databricks_cluster" "optimizations" {
  cluster_name            = "${var.project_name}-${var.environment}"
  spark_version           = "14.3.x-scala2.12"
  node_type_id            = "Standard_D4ps_v6"
  data_security_mode      = "SINGLE_USER"
  single_user_name        = var.data_engineers[0]
  autotermination_minutes = var.cluster_autotermination_minutes
  num_workers             = 0

  spark_conf = {
    "spark.master"                                     = "local[*]"
    "spark.databricks.cluster.profile"                 = "singleNode"
    "spark.sql.adaptive.enabled"                       = "true"
    "spark.sql.adaptive.skewJoin.enabled"              = "true"
    "spark.sql.adaptive.coalescePartitions.enabled"    = "true"
    "spark.databricks.delta.optimizeWrite.enabled"     = "true"
    "spark.databricks.delta.autoCompact.enabled"       = "true"
    "spark.databricks.delta.properties.defaults.enableChangeDataFeed" = "true"
  }

  custom_tags = {
    Project       = var.project_name
    Environment   = var.environment
    ResourceClass = "SingleNode"
    ManagedBy     = "terraform"
  }

  library {
    pypi {
      package = "faker"
    }
  }
}
