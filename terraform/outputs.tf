output "resource_group_name" {
  value = azurerm_resource_group.main.name
}

output "azure_openai_endpoint" {
  value = module.azure_openai.endpoint
}

output "azure_openai_key" {
  value     = module.azure_openai.primary_key
  sensitive = true
}

output "azure_openai_deployment_name" {
  value = module.azure_openai.chat_deployment_name
}

output "azure_openai_embedding_deployment_name" {
  value = module.azure_openai.embedding_deployment_name
}

output "azure_search_endpoint" {
  value = module.azure_search.endpoint
}

output "azure_search_key" {
  value     = module.azure_search.primary_key
  sensitive = true
}

output "storage_connection_string" {
  value     = module.storage.connection_string
  sensitive = true
}

output "storage_account_name" {
  value = module.storage.account_name
}

output "document_intelligence_endpoint" {
  value = module.document_intelligence.endpoint
}

output "document_intelligence_key" {
  value     = module.document_intelligence.primary_key
  sensitive = true
}
