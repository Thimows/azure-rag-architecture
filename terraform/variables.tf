variable "resource_group_name" {
  description = "Name of the Azure resource group"
  type        = string
}

variable "location" {
  description = "Azure region for all resources"
  type        = string
  default     = "eastus2"
}

variable "openai_model_name" {
  description = "Name of the OpenAI chat model deployment"
  type        = string
  default     = "gpt-5.3"
}

variable "openai_embedding_model_name" {
  description = "Name of the OpenAI embedding model deployment"
  type        = string
  default     = "text-embedding-3-large"
}

variable "search_service_sku" {
  description = "SKU tier for Azure AI Search"
  type        = string
  default     = "standard"
}

variable "storage_account_name" {
  description = "Name of the Azure Storage account (must be globally unique)"
  type        = string
}

variable "project_prefix" {
  description = "Prefix for resource naming"
  type        = string
  default     = "rag"
}
