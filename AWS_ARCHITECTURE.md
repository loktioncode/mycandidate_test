# AWS Architecture Design for MyCandidate

## Overview

This document describes the AWS architecture for deploying the MyCandidate Flask application using ECS (Elastic Container Service) in the **af-south-1 (Africa - Cape Town, South Africa)** region to ensure data residency compliance for South African election data.

## Note: Verify instance type availability in af-south-1; some newer instance types may have limited availability in this region


## Architecture Components

### 1. Container Orchestration: ECS Fargate

**Service**: Amazon ECS (Elastic Container Service) with Fargate launch type

**Location**: af-south-1 region, deployed in private subnets across 2+ Availability Zones

**Configuration**:
- Launch Type: Fargate (serverless, no EC2 management)
- Task Definition: Flask application container
- Service: ECS Service with auto-scaling
- Cluster: Dedicated ECS cluster for MyCandidate

**Benefits**:
- No server management required
- Automatic scaling based on demand
- Pay only for running tasks
- Integrated with other AWS services

### 2. Load Balancing: Application Load Balancer (ALB)

**Service**: Application Load Balancer

**Location**: af-south-1 region, deployed in public subnets

**Configuration**:
- Type: Application Load Balancer (Layer 7)
- SSL/TLS: HTTPS termination with ACM certificate
- Health Checks: Configured to check `/api/v1/health` endpoint
- Target Groups: ECS Fargate tasks in private subnets
- Listener: Port 443 (HTTPS), redirect HTTP to HTTPS

**Security**:
- WAF integration for DDoS protection
- Security groups restrict access to ECS tasks only

### 3. Compute: ECS Fargate Tasks

**Service**: ECS Fargate Tasks

**Location**: af-south-1 region, private subnets

**Initial Configuration**:
- CPU: 0.5 vCPU per task
- Memory: 1GB RAM per task
- Tasks: 2 minimum, 10 maximum (auto-scaling)

**Scaling Configuration**:
- Target Tracking: CPU utilization at 70%
- Step Scaling: Based on request count
- Cooldown: 300 seconds

### 4. Database: Amazon RDS PostgreSQL

**Service**: Amazon RDS for PostgreSQL

**Location**: af-south-1 region, Multi-AZ deployment

**Configuration**:
- Engine: PostgreSQL 12.6+
- Instance: db.t3.medium (2 vCPU, 4GB RAM)
- Multi-AZ: Enabled for high availability
- Storage: 100GB GP3 SSD with auto-scaling
- Backup: Automated daily backups, 7-day retention
- Read Replicas: 1 read replica in different AZ for read scaling

**Data Residency**: All data stored in af-south-1, backups in af-south-1

### 5. Caching: Amazon ElastiCache Redis

**Service**: Amazon ElastiCache for Redis

**Location**: af-south-1 region, private subnets

**Configuration**:
- Engine: Redis 7.x
- Mode: Cluster mode enabled
- Node Type: cache.t3.small (0.5 vCPU, 1.37GB RAM)
- Replication: Multi-AZ with automatic failover
- Backup: Daily snapshots, 7-day retention

**Use Cases**:
- Session storage
- Candidate data caching
- API response caching

### 6. Networking: VPC Configuration

**VPC**: Custom VPC in af-south-1

**Subnet Configuration**:
- **Public Subnets** (2 AZs): ALB, NAT Gateway
  - Subnet 1: 10.0.1.0/24 (af-south-1a)
  - Subnet 2: 10.0.2.0/24 (af-south-1b)
  
- **Private Subnets** (2 AZs): ECS, RDS, ElastiCache
  - Subnet 1: 10.0.10.0/24 (af-south-1a)
  - Subnet 2: 10.0.20.0/24 (af-south-1b)

**Internet Gateway**: Attached to VPC for public subnet access

**NAT Gateway**: For outbound internet access from private subnets (1 per AZ for HA)

**Route Tables**:
- Public: Routes to Internet Gateway
- Private: Routes to NAT Gateway

**VPC Endpoints** (Optional but recommended):
- S3 endpoint (for ECR image pulls)
- ECR endpoint (for container image pulls)
- Secrets Manager endpoint (for secret retrieval)

### 7. Secrets Management: AWS Secrets Manager

**Service**: AWS Secrets Manager

**Location**: af-south-1 region

**Secrets Stored**:
- RDS database credentials
- Redis connection strings
- Application secret keys
- API keys (if any)

**Access**: ECS tasks use IAM roles to retrieve secrets at runtime


### 8. Monitoring: Amazon CloudWatch

**Service**: Amazon CloudWatch

**Location**: af-south-1 region

**Metrics Collected**:
- ECS: CPU utilization, memory usage, task count
- RDS: CPU, memory, connections, read/write IOPS
- ElastiCache: CPU, memory, cache hits/misses
- ALB: Request count, response time, error rates

**Logs**:
- ECS task logs (application logs)
- ALB access logs
- VPC Flow Logs

**Alarms**:
- High CPU utilization (>80%)
- Low memory available (<20%)
- Database connection errors
- Application errors (5xx responses)

### 9. Security Services

**AWS WAF**:
- DDoS protection
- SQL injection prevention
- XSS protection
- Rate limiting rules

**CloudTrail**:
- API call logging
- Audit trail for compliance
- Logs stored in af-south-1

**Security Groups**:
- ALB: Allow HTTPS (443) from internet, HTTP (80) from internet
- ECS Tasks: Allow HTTP (5000) from ALB security group only
- RDS: Allow PostgreSQL (5432) from ECS security group only
- ElastiCache: Allow Redis (6379) from ECS security group only

**IAM Roles**:
- ECS Task Role: Permissions for Secrets Manager, CloudWatch, S3
- ECS Execution Role: Permissions for ECR, CloudWatch Logs

## Scaling Strategy

### Horizontal Scaling (ECS Tasks)

**Auto-Scaling Policy**:
- **Min Capacity**: 2 tasks (for high availability)
- **Max Capacity**: 10 tasks
- **Target Metric**: CPU utilization at 70%
- **Scale Out**: Add 1 task when CPU > 70% for 2 minutes
- **Scale In**: Remove 1 task when CPU < 30% for 15 minutes
- **Cooldown**: 300 seconds between scaling actions

**Scaling Triggers**:
1. **CPU Utilization**: Primary metric
2. **Memory Utilization**: Secondary metric (alarm only)
3. **Request Count**: Tertiary metric (for traffic spikes)

### Vertical Scaling (Task Resources)

**Initial**: 0.5 vCPU, 1GB RAM
**Under Load**: Scale to 1 vCPU, 2GB RAM per task
**High Load**: Scale to 2 vCPU, 4GB RAM per task

### Database Scaling

**Read Scaling**:
- Read replicas: 1-3 replicas in af-south-1
- Application uses read replicas for SELECT queries
- Primary instance for writes only

**Storage Scaling**:
- Auto-scaling enabled (up to 1TB)
- Storage type: GP3 SSD (better performance than GP2)

### Cache Scaling

**ElastiCache Cluster Mode**:
- Start with 1 shard, 2 nodes (primary + replica)
- Scale to 3 shards, 6 nodes under high load
- Automatic failover within AZ

View the interactive architecture diagram:

- [Architecture Diagram](https://mermaid.live/view#pako:eNqNVW1v2jAQ_isnf5g2CSjJVsqiaVIIbVcNMgZ0lUr2wSResJo4yHa6sbb_fRcnvBRSOiGSu3uee7F95zyQMIsYcUgs6XIB014gAqHyealeCc2kYHoWkLUYkJ8F5VoxqWbmaXQmomee7s0EnfAJYxbzTDhAfzVVlutF06pCbLg_Rh5y8emA1W6Z34nV2WeN8nnCw0k-xyIU8ksdKsOnuTz5_NYG91a9qzzdQW_mLpdIohorgEFGI-jRhIqQScP_Mp2OJifTwQSmTKZcGJ7x9d3pDP9wSTX7TVe1SxxJfo_wTkWl4UhJG99zb-IlucItRT9UoNIqHlouqIwxmDUr0EqBKVV3YJnA7dYp3Huj6wZYlz0Yu8M9R_vQ0f4vR__Q0TeObq6zpgppwkXsgN202qARrT__PtV0ThXD5a1FGNDVZoXj_gS3K6VyNUMRRpnSsWST7wOTqoIciOYt_b6VsojnqUGGeaJ5071dBxkzc8AmyJjhAVcGQ971rq3So-GiKNG8n9V3nlCleYnvyBg-4uXJVicGQ5wfYwgLQpFQpTRJdvPtp52wMJdcrzDzWkSbvOchU1V-tEvsoSEVNMYmKQapMkFlMzn7PfAki5jQnCaqAe7oCr6yVXkmN-6FccR3Se5nuNMy0yzcNLqXZHl0Q3W4mG1Fwx5ksYI3MGRa8lBtyVNJeTLbilVvRFzjhMUxNkfN0s-9MbbVGLxMaMoFbltxLSgtV2VlWXiHtqsUF_asn8wFA83m50czq4-AQ13N9sb6CDvjcgy0j4H-Dljs2N4YGvO2afdm7SjqH0U3kavGfSFyLeofRcvIO81bF_pF2D8Ol8Gfd2ld_GMM_1VGmWXbmHUZXkL9GrS40gvr5mO2n62FnfEt1_MsF9EjIP0g4ysM_0XGuERGeZJUjX7QuK-R7P8h-aSBH3MeEUfLnDVIip82WqjkIRAAAdELlrKAOChGVN4FJBBP6LOk4jbL0rWbzPJ4QZxfeK2gli8jDN3nFC-wLQWHlEkP16mJc2oiEOeB_CFOp93qdM9O29aZbXe69sdug6yIY3fs1oeuZXfft-2zs0739MNTg_w1OdstpD_9Az796qw)


## Security Best Practices

### Network Security

1. **VPC Isolation**: All resources in private subnets except ALB
2. **Security Groups**: Least privilege access (only necessary ports)
3. **NACLs**: Network ACLs for additional layer of security
4. **VPC Endpoints**: Use VPC endpoints for AWS services to avoid internet egress
5. **No Public IPs**: ECS tasks have no public IP addresses

### Data Security

1. **Encryption at Rest**:
   - RDS: AES-256 encryption enabled
   - ElastiCache: Encryption at rest enabled
   - EBS volumes: Encrypted

2. **Encryption in Transit**:
   - ALB: TLS 1.2+ only
   - RDS: SSL/TLS required
   - ElastiCache: TLS encryption enabled

3. **Secrets Management**:
   - No hardcoded credentials
   - AWS Secrets Manager for all secrets
   - IAM roles for service access
   - Secrets rotation enabled (where applicable)

### Application Security

1. **WAF Rules**:
   - SQL injection protection
   - XSS protection
   - Rate limiting (1000 requests/minute per IP)
   - Geographic restrictions (if needed)

2. **Container Security**:
   - Non-root user in containers
   - Minimal base images
   - Regular security scanning (ECR image scanning)
   - No secrets in container images

3. **IAM Best Practices**:
   - Least privilege principle
   - Separate IAM roles for ECS tasks and execution
   - No long-lived access keys
   - MFA for console access

### Compliance

1. **Data Residency**: All data stored in af-south-1 (South Africa)
2. **POPI Act Compliance**: Personal information processed within South Africa
3. **Audit Logging**: CloudTrail logs all API calls
4. **Backup Retention**: 7-day retention for RDS and ElastiCache backups

## Data Residency and Compliance

### Region: af-south-1 (Africa - Cape Town, South Africa)

**Rationale**:
- Ensures data residency compliance for South African election data
- Reduces latency for local users
- Meets data sovereignty requirements (POPI Act compliance)
- All data must remain within South African borders

### Data Residency Guarantees

1. **All Data Storage in af-south-1**:
   - RDS database and backups
   - ElastiCache data and snapshots
   - ECR container images
   - CloudWatch logs and metrics
   - Secrets Manager secrets

2. **No Cross-Region Replication**:
   - RDS read replicas only within af-south-1
   - No cross-region backup copies
   - No data transfer outside South Africa

3. **Network Traffic**:
   - VPC endpoints keep AWS service traffic within AWS network in af-south-1
   - No data egress outside South Africa

### Compliance Considerations

- **POPI Act (Protection of Personal Information Act)**: Data localization ensures compliance
- **Election Data Security**: Sensitive election candidate data remains in-country
- **Audit Requirements**: All logs and audit trails stored in af-south-1

## Cost Optimization

1. **ECS Fargate**: Pay only for running tasks (no idle EC2 costs)
2. **Auto-Scaling**: Scale down during low-traffic periods
3. **Reserved Instances**: Consider RDS Reserved Instances for 1-3 year commitments
4. **Storage**: Use GP3 SSD for better price/performance than GP2
5. **ElastiCache**: Start small, scale as needed
6. **CloudWatch**: Set log retention policies (7-30 days)
7. **NAT Gateway**: Consider NAT Instance for dev environments (lower cost)

## Disaster Recovery

1. **RDS Automated Backups**: Daily backups with 7-day retention
2. **ElastiCache Snapshots**: Daily snapshots with 7-day retention
3. **Infrastructure as Code**: Terraform/CloudFormation for quick recovery
4. **Multi-AZ Deployment**: Automatic failover for RDS and ElastiCache

## Monitoring and Alerting

### Key Metrics to Monitor

1. **Application**:
   - Request rate
   - Error rate (4xx, 5xx)
   - Response time (p50, p95, p99)
   - Active connections

2. **Infrastructure**:
   - ECS task count
   - CPU utilization
   - Memory utilization
   - Network throughput

3. **Database**:
   - Connection count
   - Query performance
   - Replication lag
   - Storage utilization

4. **Cache**:
   - Cache hit rate
   - Evictions
   - Memory usage
   - Connection count

### Alerting Thresholds

- **Critical**: CPU > 90%, Memory < 10%, Error rate > 5%
- **Warning**: CPU > 70%, Memory < 20%, Error rate > 1%
- **Info**: Task scaling events, backup completions

## Deployment Strategy

1. **Blue/Green Deployment**: ECS supports blue/green deployments for zero-downtime
2. **Rolling Updates**: Gradual task replacement
3. **Canary Deployments**: Route small percentage of traffic to new version
4. **Database Migrations**: Run Alembic migrations as part of deployment pipeline

## Next Steps
1. Create Terraform/CloudFormation templates for infrastructure
2. Set up CI/CD pipeline (Jenkins) for automated deployments
3. Configure monitoring dashboards in CloudWatch
4. Set up alerting for critical metrics
5. Perform load testing to validate scaling policies
6. Document runbooks for common operations



1. **Start all services**:
   ```bash
   podman-compose -f docker-compose.yml up -d
   ```

2. **Initialize the database** (wait a few seconds for services to start):
   ```bash
   sleep 10
   podman exec -it mycandidate-web python rebuild_db.py
   ```

3. **Test the API**:
   ```bash
   chmod +x test-api.sh
   ./test-api.sh
   ```

4. **Or test manually**:
   ```bash
   # Health check
   curl http://localhost:5000/api/v1/health
   
   # Get candidates by ward
   curl http://localhost:5000/api/v1/wards/WARD001/candidates
   ```

5. **Stop services**:
   ```bash
   podman-compose -f podman-compose.yml down

