resource "azurerm_resource_group" "main" {
  name     = var.resource_group_name
  location = var.location
}

module "azure_openai" {
  source = "./modules/azure-openai"

  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  project_prefix      = var.project_prefix
  model_name          = var.openai_model_name
  embedding_model_name = var.openai_embedding_model_name
}

module "azure_search" {
  source = "./modules/azure-search"

  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  project_prefix      = var.project_prefix
  sku                 = var.search_service_sku
}

module "storage" {
  source = "./modules/storage"

  resource_group_name  = azurerm_resource_group.main.name
  location             = azurerm_resource_group.main.location
  storage_account_name = var.storage_account_name
}

module "document_intelligence" {
  source = "./modules/document-intelligence"

  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  project_prefix      = var.project_prefix
}
