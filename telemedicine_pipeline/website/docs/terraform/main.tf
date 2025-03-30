provider "aws" {
  region = var.aws_region
}

# VPC and Network Configuration
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"
  version = "~> 3.0"

  name = "${var.project_name}-vpc"
  cidr = var.vpc_cidr

  azs             = var.availability_zones
  private_subnets = var.private_subnet_cidrs
  public_subnets  = var.public_subnet_cidrs

  enable_nat_gateway = true
  single_nat_gateway = var.environment != "production"
  
  enable_vpn_gateway = false

  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-vpc"
    }
  )
}

# S3 Buckets for Data Storage
resource "aws_s3_bucket" "raw_data" {
  bucket = "${var.project_name}-raw-data-${var.environment}"
  
  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-raw-data"
      DataClassification = "Sensitive"
    }
  )
}

resource "aws_s3_bucket_versioning" "raw_data_versioning" {
  bucket = aws_s3_bucket.raw_data.id
  
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "raw_data_encryption" {
  bucket = aws_s3_bucket.raw_data.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket" "processed_data" {
  bucket = "${var.project_name}-processed-data-${var.environment}"
  
  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-processed-data"
      DataClassification = "Sensitive"
    }
  )
}

resource "aws_s3_bucket_versioning" "processed_data_versioning" {
  bucket = aws_s3_bucket.processed_data.id
  
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "processed_data_encryption" {
  bucket = aws_s3_bucket.processed_data.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# RDS PostgreSQL for Provider Data
resource "aws_db_subnet_group" "rds_subnet_group" {
  name       = "${var.project_name}-rds-subnet-group"
  subnet_ids = module.vpc.private_subnets

  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-rds-subnet-group"
    }
  )
}

resource "aws_security_group" "rds_sg" {
  name        = "${var.project_name}-rds-sg"
  description = "Security group for RDS PostgreSQL"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = module.vpc.private_subnets_cidr_blocks
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-rds-sg"
    }
  )
}

resource "aws_db_instance" "postgres" {
  identifier             = "${var.project_name}-postgres-${var.environment}"
  engine                 = "postgres"
  engine_version         = "13.7"
  instance_class         = var.rds_instance_class
  allocated_storage      = var.rds_allocated_storage
  max_allocated_storage  = var.rds_max_allocated_storage
  storage_type           = "gp2"
  storage_encrypted      = true
  
  name                   = var.rds_database_name
  username               = var.rds_username
  password               = var.rds_password
  
  multi_az               = var.environment == "production"
  db_subnet_group_name   = aws_db_subnet_group.rds_subnet_group.name
  vpc_security_group_ids = [aws_security_group.rds_sg.id]
  
  backup_retention_period = var.environment == "production" ? 7 : 1
  backup_window           = "03:00-04:00"
  maintenance_window      = "sun:04:30-sun:05:30"
  
  skip_final_snapshot     = var.environment != "production"
  final_snapshot_identifier = var.environment == "production" ? "${var.project_name}-postgres-final-snapshot" : null
  
  deletion_protection     = var.environment == "production"
  
  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-postgres"
    }
  )
}

# Amazon MSK (Managed Streaming for Kafka)
resource "aws_security_group" "msk_sg" {
  name        = "${var.project_name}-msk-sg"
  description = "Security group for Amazon MSK"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port   = 9092
    to_port     = 9092
    protocol    = "tcp"
    cidr_blocks = module.vpc.private_subnets_cidr_blocks
  }

  ingress {
    from_port   = 9094
    to_port     = 9094
    protocol    = "tcp"
    cidr_blocks = module.vpc.private_subnets_cidr_blocks
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-msk-sg"
    }
  )
}

resource "aws_msk_cluster" "kafka" {
  cluster_name           = "${var.project_name}-msk-${var.environment}"
  kafka_version          = "2.8.1"
  number_of_broker_nodes = var.environment == "production" ? 3 : 2

  broker_node_group_info {
    instance_type   = var.msk_instance_type
    client_subnets  = module.vpc.private_subnets
    security_groups = [aws_security_group.msk_sg.id]
    
    storage_info {
      ebs_storage_info {
        volume_size = var.msk_volume_size
      }
    }
  }

  encryption_info {
    encryption_in_transit {
      client_broker = "TLS"
      in_cluster    = true
    }
  }

  configuration_info {
    arn      = aws_msk_configuration.kafka_config.arn
    revision = aws_msk_configuration.kafka_config.latest_revision
  }

  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-msk"
    }
  )
}

resource "aws_msk_configuration" "kafka_config" {
  name = "${var.project_name}-msk-config"
  
  server_properties = <<PROPERTIES
auto.create.topics.enable=true
delete.topic.enable=true
log.retention.hours=24
PROPERTIES
}

# Amazon MWAA (Managed Workflows for Apache Airflow)
resource "aws_s3_bucket" "airflow" {
  bucket = "${var.project_name}-airflow-${var.environment}"
  
  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-airflow"
    }
  )
}

resource "aws_s3_bucket_versioning" "airflow_versioning" {
  bucket = aws_s3_bucket.airflow.id
  
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "airflow_encryption" {
  bucket = aws_s3_bucket.airflow.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_object" "dags" {
  bucket = aws_s3_bucket.airflow.id
  key    = "dags/"
  source = "/dev/null"
}

resource "aws_s3_object" "plugins" {
  bucket = aws_s3_bucket.airflow.id
  key    = "plugins.zip"
  source = "/dev/null"
}

resource "aws_s3_object" "requirements" {
  bucket  = aws_s3_bucket.airflow.id
  key     = "requirements.txt"
  content = <<EOF
apache-airflow-providers-amazon>=2.0.0
apache-airflow-providers-postgres>=2.0.0
apache-airflow-providers-http>=2.0.0
pandas>=1.3.0
numpy>=1.20.0
EOF
}

resource "aws_security_group" "mwaa_sg" {
  name        = "${var.project_name}-mwaa-sg"
  description = "Security group for MWAA"
  vpc_id      = module.vpc.vpc_id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-mwaa-sg"
    }
  )
}

resource "aws_mwaa_environment" "airflow" {
  name = "${var.project_name}-mwaa-${var.environment}"
  
  airflow_version         = "2.2.2"
  environment_class       = var.mwaa_environment_class
  max_workers             = var.mwaa_max_workers
  min_workers             = var.mwaa_min_workers
  
  dag_s3_path             = "dags"
  plugins_s3_path         = "plugins.zip"
  requirements_s3_path    = "requirements.txt"
  
  source_bucket_arn       = aws_s3_bucket.airflow.arn
  execution_role_arn      = aws_iam_role.mwaa_execution_role.arn
  
  network_configuration {
    security_group_ids = [aws_security_group.mwaa_sg.id]
    subnet_ids         = module.vpc.private_subnets
  }
  
  logging_configuration {
    dag_processing_logs {
      enabled   = true
      log_level = "INFO"
    }
    
    scheduler_logs {
      enabled   = true
      log_level = "INFO"
    }
    
    task_logs {
      enabled   = true
      log_level = "INFO"
    }
    
    webserver_logs {
      enabled   = true
      log_level = "INFO"
    }
    
    worker_logs {
      enabled   = true
      log_level = "INFO"
    }
  }
  
  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-mwaa"
    }
  )
}

# IAM Role for MWAA
resource "aws_iam_role" "mwaa_execution_role" {
  name = "${var.project_name}-mwaa-execution-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "airflow-env.amazonaws.com"
        }
      },
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "airflow.amazonaws.com"
        }
      }
    ]
  })
  
  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-mwaa-execution-role"
    }
  )
}

resource "aws_iam_role_policy_attachment" "mwaa_service_role_attachment" {
  role       = aws_iam_role.mwaa_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonMWAAServiceRolePolicy"
}

# Amazon Redshift for Data Warehouse
resource "aws_redshift_subnet_group" "redshift_subnet_group" {
  name       = "${var.project_name}-redshift-subnet-group"
  subnet_ids = module.vpc.private_subnets

  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-redshift-subnet-group"
    }
  )
}

resource "aws_security_group" "redshift_sg" {
  name        = "${var.project_name}-redshift-sg"
  description = "Security group for Redshift"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port   = 5439
    to_port     = 5439
    protocol    = "tcp"
    cidr_blocks = module.vpc.private_subnets_cidr_blocks
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-redshift-sg"
    }
  )
}

resource "aws_redshift_cluster" "redshift" {
  cluster_identifier        = "${var.project_name}-redshift-${var.environment}"
  database_name             = var.redshift_database_name
  master_username           = var.redshift_username
  master_password           = var.redshift_password
  
  node_type                 = var.redshift_node_type
  cluster_type              = var.redshift_cluster_type
  number_of_nodes           = var.redshift_cluster_type == "single-node" ? null : var.redshift_node_count
  
  cluster_subnet_group_name = aws_redshift_subnet_group.redshift_subnet_group.name
  vpc_security_group_ids    = [aws_security_group.redshift_sg.id]
  
  encrypted                 = true
  
  automated_snapshot_retention_period = var.environment == "production" ? 7 : 1
  
  skip_final_snapshot       = var.environment != "production"
  final_snapshot_identifier = var.environment == "production" ? "${var.project_name}-redshift-final-snapshot" : null
  
  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-redshift"
    }
  )
}

# AWS Glue for ETL
resource "aws_glue_catalog_database" "glue_database" {
  name = "${var.project_name}_${var.environment}_db"
}

resource "aws_iam_role" "glue_role" {
  name = "${var.project_name}-glue-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "glue.amazonaws.com"
        }
      }
    ]
  })
  
  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-glue-role"
    }
  )
}

resource "aws_iam_role_policy_attachment" "glue_service_role_attachment" {
  role       = aws_iam_role.glue_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole"
}

resource "aws_iam_role_policy" "glue_s3_policy" {
  name = "${var.project_name}-glue-s3-policy"
  role = aws_iam_role.glue_role.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "s3:GetObject",
          "s3:PutObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Effect = "Allow"
        Resource = [
          aws_s3_bucket.raw_data.arn,
          "${aws_s3_bucket.raw_data.arn}/*",
          aws_s3_bucket.processed_data.arn,
          "${aws_s3_bucket.processed_data.arn}/*"
        ]
      }
    ]
  })
}

# CloudWatch for Monitoring
resource "aws_cloudwatch_dashboard" "main_dashboard" {
  dashboard_name = "${var.project_name}-${var.environment}-dashboard"
  
  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "metric"
        x      = 0
        y      = 0
        width  = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/RDS", "CPUUtilization", "DBInstanceIdentifier", aws_db_instance.postgres.id]
          ]
          period = 300
          stat   = "Average"
          region = var.aws_region
          title  = "RDS CPU Utilization"
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 0
        width  = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/Redshift", "CPUUtilization", "ClusterIdentifier", aws_redshift_cluster.redshift.id]
          ]
          period = 300
          stat   = "Average"
          region = var.aws_region
          title  = "Redshift CPU Utilization"
        }
      },
      {
        type   = "metric"
        x      = 0
        y      = 6
        width  = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/Kafka", "CpuUser", "Cluster Name", aws_msk_cluster.kafka.cluster_name]
          ]
          period = 300
          stat   = "Average"
          region = var.aws_region
          title  = "MSK CPU Utilization"
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 6
        width  = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/MWAA", "RunningTasks", "Environment", aws_mwaa_environment.airflow.name]
          ]
          period = 300
          stat   = "Average"
          region = var.aws_region
          title  = "MWAA Running Tasks"
        }
      }
    ]
  })
}

# SNS for Alerts
resource "aws_sns_topic" "alerts" {
  name = "${var.project_name}-alerts-${var.environment}"
  
  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-alerts"
    }
  )
}

resource "aws_sns_topic_subscription" "email_subscription" {
  count     = var.alert_email != "" ? 1 : 0
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "email"
  endpoint  = var.alert_email
}

# CloudWatch Alarms
resource "aws_cloudwatch_metric_alarm" "rds_cpu_alarm" {
  alarm_name          = "${var.project_name}-rds-cpu-alarm-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  threshold           = 80
  alarm_description   = "This metric monitors RDS CPU utilization"
  alarm_actions       = [aws_sns_topic.alerts.arn]
  
  dimensions = {
    DBInstanceIdentifier = aws_db_instance.postgres.id
  }
  
  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-rds-cpu-alarm"
    }
  )
}

resource "aws_cloudwatch_metric_alarm" "redshift_cpu_alarm" {
  alarm_name          = "${var.project_name}-redshift-cpu-alarm-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/Redshift"
  period              = 300
  statistic           = "Average"
  threshold           = 80
  alarm_description   = "This metric monitors Redshift CPU utilization"
  alarm_actions       = [aws_sns_topic.alerts.arn]
  
  dimensions = {
    ClusterIdentifier = aws_redshift_cluster.redshift.id
  }
  
  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-redshift-cpu-alarm"
    }
  )
}

# QuickSight setup would typically be done through the AWS Console or API
# as Terraform doesn't have comprehensive support for QuickSight resources

# Outputs
output "vpc_id" {
  description = "The ID of the VPC"
  value       = module.vpc.vpc_id
}

output "rds_endpoint" {
  description = "The connection endpoint for the RDS instance"
  value       = aws_db_instance.postgres.endpoint
}

output "msk_bootstrap_brokers" {
  description = "The bootstrap brokers for the MSK cluster"
  value       = aws_msk_cluster.kafka.bootstrap_brokers
}

output "msk_bootstrap_brokers_tls" {
  description = "The TLS bootstrap brokers for the MSK cluster"
  value       = aws_msk_cluster.kafka.bootstrap_brokers_tls
}

output "mwaa_webserver_url" {
  description = "The webserver URL for the MWAA environment"
  value       = aws_mwaa_environment.airflow.webserver_url
}

output "redshift_endpoint" {
  description = "The connection endpoint for the Redshift cluster"
  value       = aws_redshift_cluster.redshift.endpoint
}

output "raw_data_bucket" {
  description = "The name of the raw data S3 bucket"
  value       = aws_s3_bucket.raw_data.id
}

output "processed_data_bucket" {
  description = "The name of the processed data S3 bucket"
  value       = aws_s3_bucket.processed_data.id
}

output "sns_topic_arn" {
  description = "The ARN of the SNS topic for alerts"
  value       = aws_sns_topic.alerts.arn
}
