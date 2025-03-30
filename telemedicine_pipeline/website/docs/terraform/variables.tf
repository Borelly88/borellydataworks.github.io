variable "aws_region" {
  description = "The AWS region to deploy resources"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "The name of the project"
  type        = string
  default     = "telemedicine-pipeline"
}

variable "environment" {
  description = "The deployment environment (dev, staging, production)"
  type        = string
  default     = "dev"
  validation {
    condition     = contains(["dev", "staging", "production"], var.environment)
    error_message = "Environment must be one of: dev, staging, production."
  }
}

variable "vpc_cidr" {
  description = "The CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "The availability zones to use"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b", "us-east-1c"]
}

variable "private_subnet_cidrs" {
  description = "The CIDR blocks for the private subnets"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
}

variable "public_subnet_cidrs" {
  description = "The CIDR blocks for the public subnets"
  type        = list(string)
  default     = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]
}

variable "common_tags" {
  description = "Common tags to apply to all resources"
  type        = map(string)
  default     = {
    Project     = "TelemedicinePipeline"
    ManagedBy   = "Terraform"
    Environment = "dev"
    Owner       = "DataEngineering"
  }
}

# RDS Variables
variable "rds_instance_class" {
  description = "The instance class for the RDS instance"
  type        = string
  default     = "db.t3.medium"
}

variable "rds_allocated_storage" {
  description = "The allocated storage for the RDS instance in GB"
  type        = number
  default     = 20
}

variable "rds_max_allocated_storage" {
  description = "The maximum allocated storage for the RDS instance in GB"
  type        = number
  default     = 100
}

variable "rds_database_name" {
  description = "The name of the database to create"
  type        = string
  default     = "telemedicine"
}

variable "rds_username" {
  description = "The username for the RDS instance"
  type        = string
  default     = "admin"
  sensitive   = true
}

variable "rds_password" {
  description = "The password for the RDS instance"
  type        = string
  default     = "ChangeMe123!"  # This should be changed and stored securely
  sensitive   = true
}

# MSK Variables
variable "msk_instance_type" {
  description = "The instance type for the MSK brokers"
  type        = string
  default     = "kafka.t3.small"
}

variable "msk_volume_size" {
  description = "The volume size for the MSK brokers in GB"
  type        = number
  default     = 100
}

# MWAA Variables
variable "mwaa_environment_class" {
  description = "The environment class for the MWAA environment"
  type        = string
  default     = "mw1.small"
}

variable "mwaa_max_workers" {
  description = "The maximum number of workers for the MWAA environment"
  type        = number
  default     = 5
}

variable "mwaa_min_workers" {
  description = "The minimum number of workers for the MWAA environment"
  type        = number
  default     = 1
}

# Redshift Variables
variable "redshift_node_type" {
  description = "The node type for the Redshift cluster"
  type        = string
  default     = "dc2.large"
}

variable "redshift_cluster_type" {
  description = "The cluster type for the Redshift cluster (single-node or multi-node)"
  type        = string
  default     = "single-node"
  validation {
    condition     = contains(["single-node", "multi-node"], var.redshift_cluster_type)
    error_message = "Cluster type must be one of: single-node, multi-node."
  }
}

variable "redshift_node_count" {
  description = "The number of nodes for the Redshift cluster (only used if cluster_type is multi-node)"
  type        = number
  default     = 2
}

variable "redshift_database_name" {
  description = "The name of the Redshift database"
  type        = string
  default     = "telemedicine_dw"
}

variable "redshift_username" {
  description = "The username for the Redshift cluster"
  type        = string
  default     = "admin"
  sensitive   = true
}

variable "redshift_password" {
  description = "The password for the Redshift cluster"
  type        = string
  default     = "ChangeMe123!"  # This should be changed and stored securely
  sensitive   = true
}

# Alert Variables
variable "alert_email" {
  description = "The email address to send alerts to"
  type        = string
  default     = ""  # This should be set to a valid email address
}
