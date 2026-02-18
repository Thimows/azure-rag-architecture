variable "resource_group_name" {
  type = string
}

variable "location" {
  type = string
}

variable "project_prefix" {
  type = string
}

variable "chat_deployment_name" {
  description = "Deployment name for the chat model"
  type        = string
  default     = "Mistral-Large-3"
}

variable "chat_model_format" {
  description = "Model provider format (e.g. 'Mistral AI', 'OpenAI', 'DeepSeek', 'MoonshotAI')"
  type        = string
  default     = "Mistral AI"
}

variable "chat_model_name" {
  description = "Chat model to deploy"
  type        = string
  default     = "Mistral-Large-3"
}

variable "chat_model_version" {
  description = "Chat model version"
  type        = string
  default     = "1"
}

variable "rewrite_deployment_name" {
  description = "Deployment name for the query rewriting model"
  type        = string
  default     = "gpt-5-nano"
}

variable "rewrite_model_name" {
  description = "Query rewriting model to deploy"
  type        = string
  default     = "gpt-5-nano"
}

variable "rewrite_model_version" {
  description = "Query rewriting model version"
  type        = string
  default     = "2025-08-07"
}

variable "embedding_model_name" {
  description = "Embedding model to deploy"
  type        = string
  default     = "text-embedding-3-large"
}

variable "embedding_model_version" {
  description = "Embedding model version"
  type        = string
  default     = "1"
}

variable "embedding_deployment_name" {
  description = "Deployment name for the embedding model"
  type        = string
  default     = "text-embedding-3-large"
}
