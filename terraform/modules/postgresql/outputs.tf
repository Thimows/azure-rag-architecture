output "host" {
  value = azurerm_postgresql_flexible_server.main.fqdn
}

output "port" {
  value = 5432
}

output "database_name" {
  value = azurerm_postgresql_flexible_server_database.app.name
}

output "administrator_login" {
  value = azurerm_postgresql_flexible_server.main.administrator_login
}

output "administrator_password" {
  value     = azurerm_postgresql_flexible_server.main.administrator_password
  sensitive = true
}

output "connection_string" {
  value     = "postgresql://${azurerm_postgresql_flexible_server.main.administrator_login}:${var.administrator_password}@${azurerm_postgresql_flexible_server.main.fqdn}:5432/${azurerm_postgresql_flexible_server_database.app.name}?sslmode=require"
  sensitive = true
}

output "dev_ip" {
  value = data.http.my_ip.response_body
}
