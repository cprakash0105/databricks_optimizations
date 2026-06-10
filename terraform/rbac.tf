# Unity Catalog - Create catalog and schema
resource "databricks_catalog" "ecommerce" {
  name    = "ecommerce_demo"
  comment = "E-commerce demo catalog for optimization benchmarks"
}

resource "databricks_schema" "optimizations" {
  catalog_name = databricks_catalog.ecommerce.name
  name         = "optimizations"
  comment      = "Schema for Databricks optimization demo tables"
}

# Groups
resource "databricks_group" "data_engineers" {
  display_name = "${var.project_name}-data-engineers"
}

resource "databricks_group" "data_analysts" {
  display_name = "${var.project_name}-data-analysts"
}

# Group memberships
resource "databricks_group_member" "engineers" {
  for_each  = toset(var.data_engineers)
  group_id  = databricks_group.data_engineers.id
  member_id = databricks_user.engineers[each.key].id
}

resource "databricks_group_member" "analysts" {
  for_each  = toset(var.data_analysts)
  group_id  = databricks_group.data_analysts.id
  member_id = databricks_user.analysts[each.key].id
}

# Users
resource "databricks_user" "engineers" {
  for_each  = toset(var.data_engineers)
  user_name = each.value
}

resource "databricks_user" "analysts" {
  for_each  = toset(var.data_analysts)
  user_name = each.value
}

# Catalog-level grants
resource "databricks_grants" "catalog" {
  catalog = databricks_catalog.ecommerce.name

  grant {
    principal  = databricks_group.data_engineers.display_name
    privileges = ["USE_CATALOG", "USE_SCHEMA", "CREATE_SCHEMA", "CREATE_TABLE"]
  }

  grant {
    principal  = databricks_group.data_analysts.display_name
    privileges = ["USE_CATALOG", "USE_SCHEMA"]
  }
}

# Schema-level grants
resource "databricks_grants" "schema" {
  schema = "${databricks_catalog.ecommerce.name}.${databricks_schema.optimizations.name}"

  grant {
    principal  = databricks_group.data_engineers.display_name
    privileges = ["ALL_PRIVILEGES"]
  }

  grant {
    principal  = databricks_group.data_analysts.display_name
    privileges = ["SELECT"]
  }
}

# Cluster policy permissions
resource "databricks_permissions" "engineering_policy" {
  cluster_policy_id = databricks_cluster_policy.data_engineering.id

  access_control {
    group_name       = databricks_group.data_engineers.display_name
    permission_level = "CAN_USE"
  }
}

resource "databricks_permissions" "analyst_policy" {
  cluster_policy_id = databricks_cluster_policy.data_analyst.id

  access_control {
    group_name       = databricks_group.data_analysts.display_name
    permission_level = "CAN_USE"
  }
}

# Cluster permissions
resource "databricks_permissions" "cluster_optimizations" {
  cluster_id = databricks_cluster.optimizations.id

  access_control {
    group_name       = databricks_group.data_engineers.display_name
    permission_level = "CAN_RESTART"
  }

  access_control {
    group_name       = databricks_group.data_analysts.display_name
    permission_level = "CAN_ATTACH_TO"
  }
}
