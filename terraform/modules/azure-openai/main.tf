resource "azurerm_cognitive_account" "openai" {
  name                = "${var.project_prefix}-openai"
  location            = var.location
  resource_group_name = var.resource_group_name
  kind                = "OpenAI"
  sku_name            = "S0"
}

resource "azurerm_cognitive_deployment" "chat" {
  name                 = "${var.project_prefix}-chat"
  cognitive_account_id = azurerm_cognitive_account.openai.id

  model {
    format  = "OpenAI"
    name    = var.model_name
    version = "latest"
  }

  sku {
    name     = "Standard"
    capacity = 10
  }
}

resource "azurerm_cognitive_deployment" "embedding" {
  name                 = "${var.project_prefix}-embedding"
  cognitive_account_id = azurerm_cognitive_account.openai.id

  model {
    format  = "OpenAI"
    name    = var.embedding_model_name
    version = "latest"
  }

  sku {
    name     = "Standard"
    capacity = 10
  }
}
