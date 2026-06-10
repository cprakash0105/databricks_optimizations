# Resource group for catalog storage
resource "azurerm_resource_group" "catalog" {
  name     = "rg-${var.project_name}-catalog"
  location = var.azure_location
}

# Access Connector for Databricks (managed identity to access ADLS)
resource "azurerm_databricks_access_connector" "unity" {
  name                = "ac-${var.project_name}-unity"
  resource_group_name = azurerm_resource_group.catalog.name
  location            = azurerm_resource_group.catalog.location

  identity {
    type = "SystemAssigned"
  }

  tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

# ADLS Gen2 Storage for Unity Catalog
resource "azurerm_storage_account" "catalog" {
  name                     = "stecomcatalog${var.environment}"
  resource_group_name      = azurerm_resource_group.catalog.name
  location                 = azurerm_resource_group.catalog.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  is_hns_enabled           = true

  tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

resource "azurerm_storage_container" "catalog" {
  name                  = "unity-catalog"
  storage_account_name  = azurerm_storage_account.catalog.name
  container_access_type = "private"
}

# Grant the Access Connector's managed identity access to storage
resource "azurerm_role_assignment" "unity_catalog_access" {
  scope                = azurerm_storage_account.catalog.id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = azurerm_databricks_access_connector.unity.identity[0].principal_id
}

# Databricks Storage Credential using the Access Connector
resource "databricks_storage_credential" "unity" {
  name = "unity-catalog-credential"

  azure_managed_identity {
    access_connector_id = azurerm_databricks_access_connector.unity.id
  }

  depends_on = [azurerm_role_assignment.unity_catalog_access]
}

# External Location for the catalog
resource "databricks_external_location" "catalog" {
  name            = "ecommerce-catalog-location"
  url             = "abfss://${azurerm_storage_container.catalog.name}@${azurerm_storage_account.catalog.name}.dfs.core.windows.net/"
  credential_name = databricks_storage_credential.unity.name
  comment         = "Managed storage for ecommerce_demo catalog"

  depends_on = [databricks_storage_credential.unity]
}
