variable "resource_group_name" {
  type = string
}

variable "location" {
  type = string
}

variable "server_name" {
  type = string
}

variable "suffix" {
  type = string
}

variable "database_name" {
  type    = string
  default = "rag"
}

variable "administrator_login" {
  type    = string
  default = "ragadmin"
}

variable "administrator_password" {
  type      = string
  sensitive = true
}

variable "sku_name" {
  type    = string
  default = "B_Standard_B1ms"
}

variable "storage_mb" {
  type    = number
  default = 32768
}
