variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

variable "databricks_host" {
  description = "Databricks workspace URL"
  type        = string
}

variable "databricks_token" {
  description = "Databricks personal access token"
  type        = string
  sensitive   = true
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "project_name" {
  description = "Project name for resource tagging"
  type        = string
  default     = "ecommerce-optimizations"
}

variable "cluster_autotermination_minutes" {
  description = "Auto-termination time in minutes"
  type        = number
  default     = 30
}

variable "cluster_num_workers" {
  description = "Number of worker nodes"
  type        = number
  default     = 2
}

variable "data_engineers" {
  description = "List of data engineer user emails"
  type        = list(string)
  default     = []
}

variable "data_analysts" {
  description = "List of data analyst user emails"
  type        = list(string)
  default     = []
}
