output "resource_group_name" {
  value = azurerm_resource_group.main.name
}

output "azure_ai_endpoint" {
  value = module.ai_foundry.endpoint
}

output "azure_ai_resource_name" {
  value = module.ai_foundry.resource_name
}

output "azure_ai_key" {
  value     = module.ai_foundry.primary_key
  sensitive = true
}

output "azure_ai_chat_deployment" {
  value = module.ai_foundry.chat_deployment_name
}

output "azure_ai_embedding_deployment" {
  value = module.ai_foundry.embedding_deployment_name
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

output "databricks_workspace_url" {
  value = module.databricks.workspace_url
}

output "databricks_workspace_id" {
  value = module.databricks.workspace_id
}

output "postgresql_host" {
  value = module.postgresql.host
}

output "postgresql_database" {
  value = module.postgresql.database_name
}

output "postgresql_user" {
  value = module.postgresql.administrator_login
}

output "postgresql_password" {
  value     = module.postgresql.administrator_password
  sensitive = true
}

output "postgresql_connection_string" {
  value     = module.postgresql.connection_string
  sensitive = true
}
