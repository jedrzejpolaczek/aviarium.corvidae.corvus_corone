# Deployment Guide

> **Deployment guide for HPO Benchmarking Platform system**

---

## Deployment Options Overview

Corvus Corone was designed with **PC-first, Cloud-ready** philosophy, offering flexible deployment options:

### PC/Lab Deployment
- **Docker Compose** - Single-node deployment
- **Ideal for:** Development, small research teams, proof-of-concept
- **Capacity:** Up to 10 concurrent users, 1-4 workers

### Cloud Deployment  
- **Kubernetes** - Scalable, production-ready
- **Ideal for:** Production, large teams, enterprise
- **Capacity:** Elastic scaling, auto-scaling

### Hybrid Deployment
- **Core services** in cloud, **Workers** locally
- **Ideal for:** Compliance, data locality, custom hardware

---

## PC/Lab Deployment (Docker Compose)

### System Requirements

#### Minimum requirements
```yaml
CPU: 4 cores (8 threads)
RAM: 16GB  
Disk: 100GB SSD
OS: Ubuntu 20.04+, Windows 10+ with WSL2, macOS 11+
Docker: 20.10+
Docker Compose: 2.0+
```

#### Recommended requirements
```yaml
CPU: 8 cores (16 threads)
RAM: 32GB
Disk: 500GB SSD + 1TB HDD for data
Network: 1Gbps
GPU: Optional (for algorithms requiring GPU)
```

### Quick Start

#### 1. Clone repository
```bash
git clone https://github.com/AviariumSoftware/corvus-corone.git
cd corvus-corone
```

#### 2. Configure environment
```bash
# Copy example environment
cp .env.example .env

# Edit configuration
vim .env
```

#### 3. Start services
```bash
# Pull images and start all services
docker-compose up -d

# Check service health
docker-compose ps
docker-compose logs -f
```

#### 4. Initialize system
```bash
# Run database migrations
docker-compose exec api python manage.py migrate

# Create admin user
docker-compose exec api python manage.py createsuperuser

# Load sample data
docker-compose exec api python manage.py loaddata sample_benchmarks.json
```

#### 5. Access system
```
Web UI: http://localhost:3000
API: http://localhost:8000/api/v1/
Admin: http://localhost:8000/admin/
Monitoring: http://localhost:3001 (Grafana)
```

### Directory structure
```
corvus-corone/
├── docker-compose.yml          # Main orchestration
├── docker-compose.override.yml # Local customizations  
├── .env.example               # Environment template
├── data/                      # Persistent data
│   ├── postgres/             # Database files
│   ├── minio/                # Object storage
│   └── logs/                 # Application logs
├── config/                   # Service configurations
│   ├── nginx/               # Reverse proxy config
│   ├── grafana/             # Monitoring dashboards  
│   └── prometheus/          # Metrics collection
└── scripts/                 # Utility scripts
    ├── backup.sh           # Backup procedures
    ├── restore.sh          # Restore procedures
    └── scale-workers.sh    # Worker scaling
```

### Service configuration

#### Core services
```yaml
# docker-compose.yml excerpt
services:
  # Web UI
  web-ui:
    image: corvus-corone/web-ui:latest
    ports:
      - \"3000:3000\"
    environment:
      - REACT_APP_API_URL=http://localhost:8000
      
  # API Gateway
  api-gateway:
    image: corvus-corone/api-gateway:latest
    ports:
      - \"8000:8000\"
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/corvus
      - REDIS_URL=redis://redis:6379/0
      
  # Workers (scalable)
  worker:
    image: corvus-corone/worker:latest
    scale: 2  # Start with 2 workers
    environment:
      - WORKER_CONCURRENCY=4
      - WORKER_TIMEOUT=3600
```

#### Database services
```yaml
  # PostgreSQL
  postgres:
    image: postgres:14
    environment:
      - POSTGRES_DB=corvus
      - POSTGRES_USER=corvus_user
      - POSTGRES_PASSWORD=secure_password
    volumes:
      - ./data/postgres:/var/lib/postgresql/data
      
  # Redis (Message Broker)
  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - ./data/redis:/data
      
  # MinIO (Object Storage)
  minio:
    image: minio/minio:latest
    command: server /data --console-address \":9001\"
    environment:
      - MINIO_ROOT_USER=minio_admin
      - MINIO_ROOT_PASSWORD=secure_minio_password
    volumes:
      - ./data/minio:/data
    ports:
      - \"9000:9000\"
      - \"9001:9001\"
```

### Customization

#### Worker scaling
```bash
# Scale workers up
docker-compose up -d --scale worker=4

# Scale workers down  
docker-compose up -d --scale worker=1

# Check worker status
docker-compose ps worker
```

### Monitoring Stack

#### PC Deployment - Basic Monitoring
```yaml
# docker-compose.monitoring.yml
services:
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./config/prometheus:/etc/prometheus
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin123
    volumes:
      - grafana_data:/var/lib/grafana
      - ./config/grafana/dashboards:/var/lib/grafana/dashboards
      
  node-exporter:
    image: prom/node-exporter:latest
    ports:
      - "9100:9100"
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
```

#### Cloud Deployment - Full Observability Stack
```yaml
# k8s-monitoring-stack.yml
apiVersion: v1
kind: Namespace
metadata:
  name: monitoring
---
# Prometheus Operator
apiVersion: monitoring.coreos.com/v1
kind: Prometheus
metadata:
  name: prometheus
  namespace: monitoring
spec:
  replicas: 2
  retention: 30d
  storage:
    volumeClaimTemplate:
      spec:
        resources:
          requests:
            storage: 100Gi
---
# ELK Stack
apiVersion: elasticsearch.k8s.elastic.co/v1
kind: Elasticsearch
metadata:
  name: elasticsearch
  namespace: monitoring
spec:
  version: 8.5.0
  nodeSets:
  - name: default
    count: 3
    config:
      node.store.allow_mmap: false
```

### Resource limits
```yaml
# docker-compose.override.yml
services:
  worker:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '0.5'
          memory: 1G
          
  # Plugin security configuration
  plugin-runtime:
    security_opt:
      - no-new-privileges:true
      - seccomp:./config/seccomp-profile.json
    user: "1000:1000"  # non-root user
    read_only: true
    tmpfs:
      - /tmp:noexec,nosuid,size=100m
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 2G
          pids: 100
```

#### Custom algorithms
```bash
# Mount local algorithm directory
volumes:
  - ./custom-algorithms:/app/algorithms:ro
```

### Monitoring

#### Built-in monitoring stack
```yaml
  # Prometheus (metrics collection)
  prometheus:
    image: prom/prometheus:latest
    ports:
      - \"9090:9090\"
    volumes:
      - ./config/prometheus:/etc/prometheus
      
  # Grafana (dashboards)
  grafana:
    image: grafana/grafana:latest
    ports:
      - \"3001:3000\"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin_password
    volumes:
      - ./config/grafana/dashboards:/var/lib/grafana/dashboards
      - ./data/grafana:/var/lib/grafana
```

#### Key metrics to monitor
- Worker queue length
- Database connection pool usage
- Memory and CPU utilization
- Experiment success/failure rates
- API response times

---

## Cloud Deployment (Kubernetes)

### Architecture overview

```yaml
# Kubernetes namespace structure
Namespaces:
  - corvus-system     # Core platform services
  - corvus-workers    # Execution workers (scalable)
  - corvus-data       # Databases and storage
  - corvus-monitoring # Observability stack
```

### Prerequisites

#### Infrastructure requirements
```yaml
Kubernetes: v1.24+
Ingress Controller: NGINX/Traefik/AWS ALB
Service Mesh: Istio (optional, recommended for production)
Storage Classes: 
  - Fast SSD for databases
  - Standard storage for logs
  - Object storage (S3/GCS/Azure Blob)
```

#### Managed services (recommended)
```yaml
Database: 
  - AWS RDS PostgreSQL / Google Cloud SQL / Azure Database
Object Storage:
  - AWS S3 / Google Cloud Storage / Azure Blob Storage  
Message Broker:
  - AWS SQS+SNS / Google Pub/Sub / Azure Service Bus
Load Balancer:
  - AWS ALB / Google Cloud Load Balancer / Azure Application Gateway
```

### Deployment process

#### 1. Prepare cluster
```bash
# Create namespace
kubectl create namespace corvus-system

# Install cert-manager (for TLS)
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.12.0/cert-manager.yaml

# Install ingress controller
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm install ingress-nginx ingress-nginx/ingress-nginx
```

#### 2. Configure secrets
```bash
# Database credentials
kubectl create secret generic postgres-credentials \\
  --from-literal=username=corvus_user \\
  --from-literal=password=secure_db_password \\
  --namespace=corvus-system

# Object storage credentials  
kubectl create secret generic object-storage-credentials \\
  --from-literal=access-key=AKIAIOSFODNN7EXAMPLE \\
  --from-literal=secret-key=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY \\
  --namespace=corvus-system

# TLS certificates
kubectl create secret tls corvus-tls \\
  --cert=tls.crt \\
  --key=tls.key \\
  --namespace=corvus-system
```

#### 3. Deploy with Helm
```bash
# Add Corvus Corone Helm repository
helm repo add corvus-corone https://charts.corvus-corone.io
helm repo update

# Install with custom values
helm install corvus-corone corvus-corone/corvus-corone \\
  --namespace=corvus-system \\
  --values=production-values.yaml \\
  --create-namespace
```

### Production values.yaml

```yaml
# production-values.yaml
global:
  imageRegistry: \"your-registry.com\"
  storageClass: \"fast-ssd\"
  
ingress:
  enabled: true
  className: \"nginx\"
  hosts:
    - host: corvus.your-domain.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: corvus-tls
      hosts:
        - corvus.your-domain.com

database:
  type: \"external\"  # Use managed database
  external:
    host: \"your-rds-instance.amazonaws.com\"
    port: 5432
    database: \"corvus\"
    existingSecret: \"postgres-credentials\"

objectStorage:
  type: \"s3\"
  s3:
    region: \"us-west-2\"
    bucket: \"corvus-artifacts\"
    existingSecret: \"object-storage-credentials\"

workers:
  replicaCount: 5
  autoscaling:
    enabled: true
    minReplicas: 2
    maxReplicas: 20
    targetCPUUtilizationPercentage: 70
    targetMemoryUtilizationPercentage: 80
  resources:
    limits:
      cpu: \"2\"
      memory: \"4Gi\"
    requests:
      cpu: \"1\"
      memory: \"2Gi\"

monitoring:
  prometheus:
    enabled: true
    storageClass: \"standard\"
    retention: \"30d\"
  grafana:
    enabled: true
    adminPassword: \"secure_grafana_password\"
    persistence:
      enabled: true
      storageClass: \"standard\"
      size: \"10Gi\"

security:
  networkPolicies:
    enabled: true
  podSecurityStandards:
    enabled: true
    standard: \"restricted\"
```

### Auto-scaling configuration

#### Horizontal Pod Autoscaler (HPA)
```yaml
# worker-hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: corvus-worker-hpa
  namespace: corvus-system
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: corvus-worker
  minReplicas: 2
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  - type: Pods
    pods:
      metric:
        name: queue_length
      target:
        type: AverageValue
        averageValue: \"10\"
```

#### Vertical Pod Autoscaler (VPA)
```yaml
# api-vpa.yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: corvus-api-vpa
  namespace: corvus-system
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: corvus-api-gateway
  updatePolicy:
    updateMode: \"Auto\"
  resourcePolicy:
    containerPolicies:
    - containerName: api-gateway
      maxAllowed:
        cpu: \"4\"
        memory: \"8Gi\"
      minAllowed:
        cpu: \"100m\"
        memory: \"256Mi\"
```

### Security hardening

#### Network policies
```yaml
# network-policy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: corvus-network-policy
  namespace: corvus-system
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: corvus-system
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: corvus-data
    ports:
    - protocol: TCP
      port: 5432  # PostgreSQL
  - to: []  # Allow external object storage access
    ports:
    - protocol: TCP
      port: 443
```

#### Pod Security Standards
```yaml
# pod-security.yaml  
apiVersion: v1
kind: Namespace
metadata:
  name: corvus-system
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
```

---

## Hybrid Deployment

### Architecture pattern

```mermaid
---
config:
  theme: redux-dark
---
flowchart TB
    subgraph Cloud [\"Cloud (K8s)\"]
        API[\"API Gateway\"]
        WEB[\"Web UI\"]
        TRACK[\"Tracking Service\"]
        DB[(\"Database\")]
        S3[(\"Object Storage\")]
    end
    
    subgraph OnPrem [\"On-Premises\"]
        WORKER1[\"Worker 1\"]
        WORKER2[\"Worker 2\"]  
        WORKER3[\"Worker N\"]
        DATA[\"Sensitive Data\"]
    end
    
    API --> WORKER1
    API --> WORKER2
    API --> WORKER3
    WORKER1 --> S3
    WORKER2 --> S3
    WORKER3 --> S3
    WORKER1 -.-> DATA
    WORKER2 -.-> DATA
    WORKER3 -.-> DATA
```

### Use cases for hybrid deployment

#### Compliance and data locality
- Data cannot leave the organization
- Regulatory requirements (GDPR, HIPAA)
- Custom hardware requirements (specjalne GPU, TPU)

#### Cost optimization  
- Utilization of existing on-premises resources
- Burst to cloud during peak load
- Data transfer cost optimization

### Configuration

#### Cloud-side configuration
```yaml
# Enable hybrid mode
hybrid:
  enabled: true
  allowExternalWorkers: true
  workerAuthToken: \"secure-worker-token\"
  
# Message broker accessible from external
messageBroker:
  external:
    enabled: true  
    host: \"broker.corvus.your-domain.com\"
    port: 5672
    tls: true
```

#### On-premises worker configuration
```yaml
# worker-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: hybrid-worker-config
data:
  CORVUS_MODE: \"hybrid\"
  CORVUS_API_ENDPOINT: \"https://api.corvus.your-domain.com\"
  CORVUS_BROKER_HOST: \"broker.corvus.your-domain.com\"
  CORVUS_WORKER_TOKEN: \"secure-worker-token\"
  CORVUS_DATA_PATH: \"/local/sensitive-data\"
```

---

## Backup and Recovery

### Backup strategy

#### Automated backups
```bash
#!/bin/bash
# backup.sh

# Database backup
kubectl exec -n corvus-data postgres-0 -- pg_dump -U corvus_user corvus > backup_$(date +%Y%m%d_%H%M%S).sql

# Object storage sync
aws s3 sync s3://corvus-artifacts s3://corvus-backup-$(date +%Y%m%d) --storage-class GLACIER

# Configuration backup
kubectl get all,secrets,configmaps -n corvus-system -o yaml > k8s-backup_$(date +%Y%m%d).yaml
```

#### Backup schedule
```yaml
# CronJob for automated backups
apiVersion: batch/v1
kind: CronJob
metadata:
  name: corvus-backup
  namespace: corvus-system
spec:
  schedule: \"0 2 * * *\"  # Daily at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: corvus-corone/backup:latest
            command:
            - /scripts/backup.sh
            volumeMounts:
            - name: backup-storage
              mountPath: /backups
          volumes:
          - name: backup-storage
            persistentVolumeClaim:
              claimName: backup-pvc
          restartPolicy: OnFailure
```

### Disaster recovery

#### Recovery Time Objectives (RTO)
- **PC Deployment:** < 2 hours
- **Cloud Deployment:** < 4 hours  
- **Hybrid Deployment:** < 6 hours

#### Recovery Point Objectives (RPO)
- **Database:** < 1 hour (WAL archiving)
- **Object Storage:** < 15 minutes (replication)
- **Configuration:** < 24 hours (GitOps)

#### Recovery procedures
```bash
#!/bin/bash
# restore.sh

# 1. Restore database
kubectl exec -n corvus-data postgres-0 -- psql -U corvus_user -d corvus < backup_20231119_020000.sql

# 2. Restore object storage
aws s3 sync s3://corvus-backup-20231119 s3://corvus-artifacts

# 3. Restart services
kubectl rollout restart deployment -n corvus-system

# 4. Verify system health
kubectl get pods -n corvus-system
curl -f https://api.corvus.your-domain.com/health
```

---

## Troubleshooting

### Common issues

#### Worker connection problems
```bash
# Check worker logs
docker-compose logs worker
kubectl logs -n corvus-system deployment/corvus-worker

# Test message broker connectivity
docker-compose exec worker python -c \"import pika; connection = pika.BlockingConnection(pika.URLParameters('amqp://guest:guest@rabbitmq:5672/')); print('OK')\"

# Reset worker queue
docker-compose exec rabbitmq rabbitmqctl purge_queue run_jobs
```

#### Database connection issues  
```bash
# Check database status
docker-compose ps postgres
kubectl get pods -n corvus-data -l app=postgres

# Test connection
docker-compose exec api python manage.py dbshell
kubectl exec -n corvus-data postgres-0 -- psql -U corvus_user -d corvus -c \"SELECT 1;\"

# Check connection pool
docker-compose exec api python -c \"from django.db import connection; print(connection.queries)\"
```

#### Performance issues
```bash
# Check resource usage
docker stats
kubectl top nodes
kubectl top pods -n corvus-system

# Analyze slow queries
kubectl exec -n corvus-data postgres-0 -- psql -U corvus_user -d corvus -c \"SELECT query, mean_time, calls FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;\"

# Monitor queue lengths
curl -s http://localhost:15672/api/queues | jq '.[].messages'
```

### Support contacts

- **Issues:** https://github.com/AviariumSoftware/corvus-corone/issues
- **Discussions:** https://github.com/AviariumSoftware/corvus-corone/discussions
- **Enterprise Support:** support@aviarium.software

---

## Related Documents

- **Architecture**: [Containers (C4-2)](../architecture/c2-containers.md)
- **Monitoring**: [Monitoring Guide](monitoring-guide.md)
- **Requirements**: [Functional Requirements](../requirements/functional-requirements.md), [Use Cases](../requirements/use-cases.md)
- **User Guides**: [Workflows](../user-guides/workflows.md)
- **Design**: [Design Decisions](../design/design-decisions.md)
