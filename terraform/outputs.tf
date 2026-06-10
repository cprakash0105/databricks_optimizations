output "cluster_id" {
  description = "Main optimization cluster ID"
  value       = databricks_cluster.optimizations.id
}

output "dev_cluster_id" {
  description = "Dev single-node cluster ID"
  value       = databricks_cluster.dev.id
}

output "catalog_name" {
  description = "Unity Catalog name"
  value       = databricks_catalog.ecommerce.name
}

output "schema_name" {
  description = "Schema name for optimization tables"
  value       = databricks_schema.optimizations.name
}

output "engineering_policy_id" {
  description = "Data engineering cluster policy ID"
  value       = databricks_cluster_policy.data_engineering.id
}

output "analyst_policy_id" {
  description = "Data analyst cluster policy ID"
  value       = databricks_cluster_policy.data_analyst.id
}
