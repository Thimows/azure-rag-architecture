variable "resource_group_name" {
  type = string
}

variable "location" {
  type = string
}

variable "project_prefix" {
  type = string
}

variable "model_name" {
  description = "Chat model to deploy"
  type        = string
}

variable "embedding_model_name" {
  description = "Embedding model to deploy"
  type        = string
}
