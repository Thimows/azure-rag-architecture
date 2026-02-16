output "connection_string" {
  value     = azurerm_storage_account.storage.primary_connection_string
  sensitive = true
}

output "account_name" {
  value = azurerm_storage_account.storage.name
}
