output "workspace_url" {
  description = "The workspace URL of the Databricks workspace"
  value       = "https://${azurerm_databricks_workspace.main.workspace_url}"
}

output "workspace_id" {
  description = "The ID of the Databricks workspace"
  value       = azurerm_databricks_workspace.main.id
}
