terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "=5.0.0"
    }
  }
}

# Configure the Microsoft Azure Provider
provider "azurerm" {
  features {}
  subscription_id = file("credentials.txt")
}

resource "azurerm_resource_group" "urban_city_rgg" {
  name     = "urban-city-rgg"
  location = "UK South"
}

resource "azurerm_storage_account" "urban_city_storageee" {
  name                     = "urbancitystorageee"
  resource_group_name      = azurerm_resource_group.urban_city_rgg.name
  location                 = azurerm_resource_group.urban_city_rgg.location
  account_tier             = "Standard"
  account_replication_type = "GRS"

  tags = {
    environment = "staging"
  }
}

resource "azurerm_storage_container" "bronze" {
  name                  = "bronze"
  storage_account_id    = azurerm_storage_account.urban_city_storageee.id
  container_access_type = "private"
  depends_on = [azurerm_storage_account.urban_city_storageee]
}

resource "azurerm_storage_container" "silver" {
  name                  = "silver"
  storage_account_id    = azurerm_storage_account.urban_city_storageee.id
  container_access_type = "private"
  depends_on = [azurerm_storage_account.urban_city_storageee]
}

resource "azurerm_postgresql_flexible_server" "db_serverr" {
  name                          = "urbancitypgserverr"
  resource_group_name           = azurerm_resource_group.urban_city_rgg.name
  location                      = azurerm_resource_group.urban_city_rgg.location
  version                       = "16"
  public_network_access_enabled = true
  administrator_login           = var.username
  administrator_password        = var.pg_password
  zone                          = "1"

  storage_mb   = 32768
  storage_tier = "P30"

  sku_name   = "GP_Standard_D4s_v3"
  create_mode = "Default"

authentication {
  password_auth_enabled = true
}

  depends_on = [azurerm_resource_group.urban_city_rgg]

}

resource "azurerm_postgresql_flexible_server_database" "db_databasee" {
  name      = "urban_city_dbb"
  server_id = azurerm_postgresql_flexible_server.db_serverr.id
  collation = "en_US.utf8"
  charset   = "UTF8"

  # prevent the possibility of accidental data loss
  lifecycle {
    prevent_destroy = false
  }
}




# Data Factory

data "azurerm_storage_account" "storage_account_dataa" {
  name                = "urbancitystorageee"
  resource_group_name = azurerm_resource_group.urban_city_rgg.name
}

resource "azurerm_data_factory" "data_factory_serverr" {
  name                = "urbancityfactoryy"
  location            = azurerm_resource_group.urban_city_rgg.location
  resource_group_name = azurerm_resource_group.urban_city_rgg.name
}

resource "azurerm_data_factory_linked_service_azure_blob_storage" "blobstoragels" {
  name              = "blob_storage_ls"
  data_factory_id   = azurerm_data_factory.data_factory_serverr.id
  connection_string = data.azurerm_storage_account.storage_account_dataa.primary_connection_string
}


resource "azurerm_data_factory_dataset_parquet" "urbancitydss" {
  name                = "urban_city_parquet_dss"
  data_factory_id     = azurerm_data_factory.data_factory_serverr.id
  linked_service_name = azurerm_data_factory_linked_service_azure_blob_storage.blobstoragels.name

  compression_codec = "snappy"

  azure_blob_storage_location {
    container = "silver"
    filename = "urban_service_requests.parquet"
  }
}