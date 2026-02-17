resource "azurerm_databricks_workspace" "main" {
  name                = "${var.project_prefix}-databricks"
  resource_group_name = var.resource_group_name
  location            = var.location
  sku                 = var.sku
}
