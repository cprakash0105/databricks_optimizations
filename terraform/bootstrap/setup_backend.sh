#!/bin/bash
# Bootstrap script: Creates Azure Storage Account for Terraform remote state
# Run this ONCE from Azure Cloud Shell before running the main Terraform

set -e

RESOURCE_GROUP="rg-terraform-state"
LOCATION="uksouth"
STORAGE_ACCOUNT="stterraformstate$(openssl rand -hex 4)"
CONTAINER_NAME="tfstate"

echo "🔧 Creating Resource Group: $RESOURCE_GROUP"
az group create --name $RESOURCE_GROUP --location $LOCATION

echo "🔧 Creating Storage Account: $STORAGE_ACCOUNT"
az storage account create \
  --resource-group $RESOURCE_GROUP \
  --name $STORAGE_ACCOUNT \
  --sku Standard_LRS \
  --encryption-services blob

echo "🔧 Creating Blob Container: $CONTAINER_NAME"
az storage container create \
  --name $CONTAINER_NAME \
  --account-name $STORAGE_ACCOUNT

echo ""
echo "✅ Bootstrap complete!"
echo ""
echo "Update your terraform/main.tf backend config with:"
echo "  storage_account_name = \"$STORAGE_ACCOUNT\""
echo ""
echo "Then run:"
echo "  cd terraform/"
echo "  terraform init"
echo "  terraform plan -var-file=terraform.tfvars"
echo "  terraform apply -var-file=terraform.tfvars"
