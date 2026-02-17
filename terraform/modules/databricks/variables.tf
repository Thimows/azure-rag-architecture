variable "resource_group_name" {
  description = "Name of the Azure resource group"
  type        = string
}

variable "location" {
  description = "Azure region for the Databricks workspace"
  type        = string
}

variable "project_prefix" {
  description = "Prefix for resource naming"
  type        = string
}

variable "sku" {
  description = "Databricks workspace SKU (standard, premium, or trial)"
  type        = string
  default     = "premium"
}
