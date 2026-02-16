variable "resource_group_name" {
  type = string
}

variable "location" {
  type = string
}

variable "project_prefix" {
  type = string
}

variable "sku" {
  description = "SKU tier for Azure AI Search"
  type        = string
  default     = "standard"
}
