resource "azurerm_search_service" "search" {
  name                = "${var.project_prefix}-search"
  resource_group_name = var.resource_group_name
  location            = var.location
  sku                 = var.sku
  semantic_search_sku = "free"
}
