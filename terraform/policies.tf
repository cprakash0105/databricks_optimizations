# Cluster policy for data engineers — allows larger clusters
resource "databricks_cluster_policy" "data_engineering" {
  name = "${var.project_name}-data-engineering-policy"

  definition = jsonencode({
    "spark_version" : {
      "type" : "regex",
      "pattern" : "1[3-9]\\.[0-9]+\\.x-scala.*",
      "defaultValue" : "14.3.x-scala2.12"
    },
    "node_type_id" : {
      "type" : "allowlist",
      "values" : ["i3.xlarge", "i3.2xlarge", "i3.4xlarge"],
      "defaultValue" : "i3.xlarge"
    },
    "num_workers" : {
      "type" : "range",
      "minValue" : 1,
      "maxValue" : 8,
      "defaultValue" : 2
    },
    "autotermination_minutes" : {
      "type" : "range",
      "minValue" : 10,
      "maxValue" : 60,
      "defaultValue" : 30
    },
    "custom_tags.Project" : {
      "type" : "fixed",
      "value" : var.project_name
    },
    "custom_tags.ManagedBy" : {
      "type" : "fixed",
      "value" : "terraform"
    }
  })
}

# Restricted policy for analysts — smaller clusters, cost control
resource "databricks_cluster_policy" "data_analyst" {
  name = "${var.project_name}-data-analyst-policy"

  definition = jsonencode({
    "spark_version" : {
      "type" : "fixed",
      "value" : "14.3.x-scala2.12"
    },
    "node_type_id" : {
      "type" : "fixed",
      "value" : "i3.xlarge"
    },
    "num_workers" : {
      "type" : "range",
      "minValue" : 0,
      "maxValue" : 2,
      "defaultValue" : 1
    },
    "autotermination_minutes" : {
      "type" : "fixed",
      "value" : 15
    },
    "spark_conf.spark.sql.adaptive.enabled" : {
      "type" : "fixed",
      "value" : "true"
    },
    "custom_tags.Project" : {
      "type" : "fixed",
      "value" : var.project_name
    },
    "custom_tags.CostCenter" : {
      "type" : "fixed",
      "value" : "analytics"
    }
  })
}
