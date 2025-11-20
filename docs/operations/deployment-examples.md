# Deployment Examples

> **Detailed configuration examples for different deployment scenarios**

---

## Deployment Scenarios Overview

| Scenario | Use Case | Scale | Complexity | SLA |
|------------|----------|-------|---------------|-----|
| **Development** | Local development, testing | 1 developer | Low | Dev-friendly |
| **Staging** | Pre-production testing | 5-10 users | Medium | Production-like |
| **Production PC** | Small research lab | 10-20 users | Medium | 99.0% uptime |
| **Production Cloud** | Enterprise deployment | 100+ users | High | 99.9% uptime |
| **High Availability** | Mission-critical research | 500+ users | Very high | 99.95% uptime |

---

## 1. Development Environment

### docker-compose.dev.yml

```yaml
version: '3.8'

services:
  # Development-specific API Gateway
  api-gateway:
    build: 
      context: ./services/api-gateway
      dockerfile: Dockerfile.dev
      args:
        - INSTALL_DEV_DEPS=true
    ports:
      - "8000:8000"
    environment:
      - DEBUG=true
      - LOG_LEVEL=debug
      - RELOAD=true  # Hot reload
      - DATABASE_URL=postgresql://dev_user:dev_pass@postgres:5432/corvus_dev
      - REDIS_URL=redis://redis:6379/0
    volumes:
      - ./services/api-gateway/src:/app/src:ro  # Live code reload
      - ./logs/api-gateway:/app/logs
    depends_on:
      - postgres
      - redis
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

  # Development Web UI
  web-ui:
    build:
      context: ./services/web-ui
      dockerfile: Dockerfile.dev
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=development
      - REACT_APP_API_URL=http://localhost:8000
      - CHOKIDAR_USEPOLLING=true  # For Windows file watching
    volumes:
      - ./services/web-ui/src:/app/src:ro
      - ./services/web-ui/public:/app/public:ro
      - /app/node_modules  # Anonymous volume for node_modules
    command: npm start

  # Single development worker
  worker:
    build:
      context: ./services/worker
      dockerfile: Dockerfile.dev
    environment:
      - WORKER_CONCURRENCY=1  # Single thread for debugging
      - ENABLE_PROFILING=true
      - DEBUG=true
      - DATABASE_URL=postgresql://dev_user:dev_pass@postgres:5432/corvus_dev
      - REDIS_URL=redis://redis:6379/0
    volumes:
      - ./algorithms:/algorithms:ro  # Local algorithm development
      - ./datasets:/datasets:ro
      - ./logs/worker:/app/logs
    depends_on:
      - postgres
      - redis

  # Development database
  postgres:
    image: postgres:14-alpine
    environment:
      - POSTGRES_DB=corvus_dev
      - POSTGRES_USER=dev_user
      - POSTGRES_PASSWORD=dev_pass
    ports:
      - "5432:5432"  # Exposed for direct access
    volumes:
      - postgres_dev_data:/var/lib/postgresql/data
      - ./scripts/init-dev-db.sql:/docker-entrypoint-initdb.d/init.sql:ro

  # Development Redis
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"  # Exposed for debugging
    volumes:
      - redis_dev_data:/data

  # Development MinIO
  minio:
    image: minio/minio:latest
    ports:
      - "9000:9000"
      - "9001:9001"
    environment:
      - MINIO_ROOT_USER=dev_minio
      - MINIO_ROOT_PASSWORD=dev_minio_pass
    volumes:
      - minio_dev_data:/data
    command: server /data --console-address ":9001"

  # Basic monitoring dla development
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./config/prometheus/prometheus-dev.yml:/etc/prometheus/prometheus.yml:ro
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'

volumes:
  postgres_dev_data:
  redis_dev_data:
  minio_dev_data:

networks:
  default:
    name: corvus-dev
```

### Development Scripts

```bash
# scripts/dev-setup.sh
#!/bin/bash
set -e

echo "🚀 Setting up Corvus Corone development environment..."

# Create necessary directories
mkdir -p logs/{api-gateway,worker,web-ui}
mkdir -p data/{postgres,redis,minio}
mkdir -p config/{prometheus,grafana}

# Copy example configurations
cp config/examples/prometheus-dev.yml config/prometheus/
cp config/examples/.env.dev .env

# Build development images
docker-compose -f docker-compose.dev.yml build

# Start services
docker-compose -f docker-compose.dev.yml up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 30

# Run database migrations
docker-compose -f docker-compose.dev.yml exec api-gateway python manage.py migrate

# Create development superuser
docker-compose -f docker-compose.dev.yml exec api-gateway python manage.py createsuperuser --noinput --username admin --email admin@dev.local

# Load sample data
docker-compose -f docker-compose.dev.yml exec api-gateway python manage.py loaddata sample_data.json

echo "✅ Development environment ready!"
echo "🌐 Web UI: http://localhost:3000"
echo "🔧 API: http://localhost:8000"
echo "📊 Prometheus: http://localhost:9090"
echo "💾 MinIO Console: http://localhost:9001"
```

---

## 2. Staging Environment

### docker-compose.staging.yml

```yaml
version: '3.8'

services:
  # Staging API Gateway (production-like but smaller)
  api-gateway:
    image: corvus/api-gateway:staging
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '1.0'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 1G
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
    environment:
      - DATABASE_URL=postgresql://staging_user:${STAGING_DB_PASS}@postgres:5432/corvus_staging
      - REDIS_URL=redis://redis:6379/0
      - LOG_LEVEL=info
      - ENVIRONMENT=staging
    secrets:
      - db_password
      - jwt_secret
    networks:
      - corvus-staging
    depends_on:
      - postgres
      - redis

  # Staging Web UI
  web-ui:
    image: corvus/web-ui:staging
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '0.5'
          memory: 1G
    environment:
      - NODE_ENV=staging
      - REACT_APP_API_URL=https://api-staging.corvus.example.com
    networks:
      - corvus-staging

  # Staging Workers (scaled)
  worker:
    image: corvus/worker:staging
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
    environment:
      - WORKER_CONCURRENCY=4
      - DATABASE_URL=postgresql://staging_user:${STAGING_DB_PASS}@postgres:5432/corvus_staging
      - REDIS_URL=redis://redis:6379/0
      - ENVIRONMENT=staging
    networks:
      - corvus-staging
    depends_on:
      - postgres
      - redis

  # Staging Database (with replication)
  postgres:
    image: postgres:14
    environment:
      - POSTGRES_DB=corvus_staging
      - POSTGRES_USER=staging_user
      - POSTGRES_PASSWORD_FILE=/run/secrets/db_password
    secrets:
      - db_password
    volumes:
      - postgres_staging_data:/var/lib/postgresql/data
      - ./config/postgres/postgresql-staging.conf:/etc/postgresql/postgresql.conf:ro
    networks:
      - corvus-staging
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G

  # Redis Cluster dla staging
  redis:
    image: redis:7
    command: redis-server --appendonly yes --replica-read-only no
    volumes:
      - redis_staging_data:/data
    networks:
      - corvus-staging

  # Load Balancer
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./config/nginx/staging.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    networks:
      - corvus-staging
    depends_on:
      - api-gateway
      - web-ui

  # Monitoring Stack
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./config/prometheus/prometheus-staging.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus_staging_data:/prometheus
    networks:
      - corvus-staging

  grafana:
    image: grafana/grafana:latest
    environment:
      - GF_SECURITY_ADMIN_PASSWORD_FILE=/run/secrets/grafana_password
    secrets:
      - grafana_password
    volumes:
      - grafana_staging_data:/var/lib/grafana
      - ./config/grafana/dashboards:/var/lib/grafana/dashboards:ro
    networks:
      - corvus-staging

secrets:
  db_password:
    file: ./secrets/staging_db_password.txt
  jwt_secret:
    file: ./secrets/staging_jwt_secret.txt
  grafana_password:
    file: ./secrets/staging_grafana_password.txt

volumes:
  postgres_staging_data:
  redis_staging_data:
  prometheus_staging_data:
  grafana_staging_data:

networks:
  corvus-staging:
    driver: overlay
    attachable: true
```

---

## 3. Production Cloud (Kubernetes)

### k8s-production.yml

```yaml
# Namespace
apiVersion: v1
kind: Namespace
metadata:
  name: corvus-production
  labels:
    environment: production
    project: corvus-corone

---
# API Gateway Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-gateway
  namespace: corvus-production
  labels:
    app: api-gateway
    version: v1.2.0
spec:
  replicas: 5
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
      maxSurge: 2
  selector:
    matchLabels:
      app: api-gateway
  template:
    metadata:
      labels:
        app: api-gateway
        version: v1.2.0
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8000"
        prometheus.io/path: "/metrics"
    spec:
      # Security Context (ADR-005)
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        runAsGroup: 1000
        fsGroup: 1000
      containers:
      - name: api-gateway
        image: corvus/api-gateway:v1.2.0
        ports:
        - containerPort: 8000
          protocol: TCP
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: database-credentials
              key: url
        - name: REDIS_URL
          valueFrom:
            configMapKeyRef:
              name: redis-config
              key: url
        - name: JWT_SECRET
          valueFrom:
            secretKeyRef:
              name: jwt-secret
              key: secret
        # Resource Limits
        resources:
          requests:
            cpu: 500m
            memory: 1Gi
          limits:
            cpu: 2000m
            memory: 4Gi
        # Health Checks
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 2
        # Security Context
        securityContext:
          runAsNonRoot: true
          runAsUser: 1000
          readOnlyRootFilesystem: true
          allowPrivilegeEscalation: false
          capabilities:
            drop:
            - ALL
        # Volume Mounts
        volumeMounts:
        - name: tmp-volume
          mountPath: /tmp
        - name: cache-volume
          mountPath: /app/cache
      volumes:
      - name: tmp-volume
        emptyDir: {}
      - name: cache-volume
        emptyDir: {}
      nodeSelector:
        kubernetes.io/arch: amd64
        node-type: compute

---
# API Gateway Service
apiVersion: v1
kind: Service
metadata:
  name: api-gateway
  namespace: corvus-production
  labels:
    app: api-gateway
spec:
  type: ClusterIP
  ports:
  - port: 8000
    targetPort: 8000
    protocol: TCP
    name: http
  selector:
    app: api-gateway

---
# API Gateway HPA
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api-gateway-hpa
  namespace: corvus-production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api-gateway
  minReplicas: 3
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
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 100
        periodSeconds: 15
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60

---
# Worker Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: worker
  namespace: corvus-production
  labels:
    app: worker
    version: v1.2.0
spec:
  replicas: 10
  selector:
    matchLabels:
      app: worker
  template:
    metadata:
      labels:
        app: worker
        version: v1.2.0
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        runAsGroup: 1000
      containers:
      - name: worker
        image: corvus/worker:v1.2.0
        env:
        - name: WORKER_CONCURRENCY
          value: "4"
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: database-credentials
              key: url
        - name: REDIS_URL
          valueFrom:
            configMapKeyRef:
              name: redis-config
              key: url
        resources:
          requests:
            cpu: 1000m
            memory: 2Gi
          limits:
            cpu: 4000m
            memory: 8Gi
        securityContext:
          runAsNonRoot: true
          runAsUser: 1000
          readOnlyRootFilesystem: true
          allowPrivilegeEscalation: false
        volumeMounts:
        - name: tmp-volume
          mountPath: /tmp
        - name: algorithms-cache
          mountPath: /app/algorithms
      volumes:
      - name: tmp-volume
        emptyDir: {}
      - name: algorithms-cache
        emptyDir: {}
      nodeSelector:
        node-type: compute-intensive

---
# Worker HPA with Custom Metrics
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: worker-hpa
  namespace: corvus-production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: worker
  minReplicas: 5
  maxReplicas: 50
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 80
  - type: External
    external:
      metric:
        name: redis_queue_length
        selector:
          matchLabels:
            queue: worker_jobs
      target:
        type: AverageValue
        averageValue: "10"

---
# PostgreSQL (Production)
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: postgres-cluster
  namespace: corvus-production
spec:
  instances: 3
  imageName: postgres:14
  
  # Resource allocation
  resources:
    requests:
      memory: "4Gi"
      cpu: "2000m"
    limits:
      memory: "8Gi"
      cpu: "4000m"
  
  # Storage
  storage:
    size: 500Gi
    storageClass: fast-ssd
  
  # Backup configuration
  backup:
    retentionPolicy: "30d"
    barmanObjectStore:
      destinationPath: "s3://corvus-backups/postgres"
      s3Credentials:
        accessKeyId:
          name: backup-credentials
          key: ACCESS_KEY_ID
        secretAccessKey:
          name: backup-credentials
          key: SECRET_ACCESS_KEY
      wal:
        retention: "7d"
      data:
        retention: "30d"
  
  # Monitoring
  monitoring:
    enabled: true
    customQueriesConfigMap:
    - name: postgresql-monitoring
      key: custom-queries.yaml

---
# Redis Cluster
apiVersion: redis.redis.opstreelabs.in/v1beta1
kind: RedisCluster
metadata:
  name: redis-cluster
  namespace: corvus-production
spec:
  clusterSize: 6
  kubernetesConfig:
    image: redis:7.0-alpine
    imagePullPolicy: IfNotPresent
    resources:
      requests:
        cpu: 500m
        memory: 1Gi
      limits:
        cpu: 1000m
        memory: 2Gi
  storage:
    volumeClaimTemplate:
      spec:
        accessModes:
        - ReadWriteOnce
        resources:
          requests:
            storage: 100Gi
        storageClassName: fast-ssd

---
# Ingress
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: corvus-ingress
  namespace: corvus-production
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/rate-limit: "1000"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  tls:
  - hosts:
    - api.corvus.example.com
    - app.corvus.example.com
    secretName: corvus-tls
  rules:
  - host: api.corvus.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: api-gateway
            port:
              number: 8000
  - host: app.corvus.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: web-ui
            port:
              number: 3000

---
# Network Policies (Security)
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: api-gateway-netpol
  namespace: corvus-production
spec:
  podSelector:
    matchLabels:
      app: api-gateway
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: postgres-cluster
    ports:
    - protocol: TCP
      port: 5432
  - to:
    - podSelector:
        matchLabels:
          app: redis-cluster
    ports:
    - protocol: TCP
      port: 6379
```

---

## 4. High Availability Multi-Region Setup

### Multi-Region Architecture

```yaml
# Primary Region (us-east-1)
apiVersion: v1
kind: ConfigMap
metadata:
  name: region-config
  namespace: corvus-production
data:
  region: "us-east-1"
  role: "primary"
  dr_region: "us-west-2"

---
# Global Load Balancer (AWS ALB/CloudFlare)
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: corvus-global-lb
  namespace: corvus-production
  annotations:
    kubernetes.io/ingress.class: alb
    alb.ingress.kubernetes.io/scheme: internet-facing
    alb.ingress.kubernetes.io/target-type: ip
    alb.ingress.kubernetes.io/healthcheck-path: /health
    alb.ingress.kubernetes.io/healthcheck-interval-seconds: '30'
    alb.ingress.kubernetes.io/healthy-threshold-count: '2'
    alb.ingress.kubernetes.io/unhealthy-threshold-count: '5'
spec:
  rules:
  - host: corvus.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: api-gateway
            port:
              number: 8000

---
# Cross-Region Database Replication
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: postgres-primary
  namespace: corvus-production
spec:
  instances: 3
  
  # Primary cluster configuration
  bootstrap:
    initdb:
      database: corvus_production
      owner: corvus_user
      secret:
        name: postgres-credentials
  
  # Backup to cross-region storage
  backup:
    barmanObjectStore:
      destinationPath: "s3://corvus-backups-global/postgres-primary"
      s3Credentials:
        accessKeyId:
          name: backup-credentials
          key: ACCESS_KEY_ID
        secretAccessKey:
          name: backup-credentials
          key: SECRET_ACCESS_KEY
      wal:
        retention: "7d"
        compression: gzip
      data:
        retention: "30d"
        compression: gzip

---
# Disaster Recovery Cluster (us-west-2)
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: postgres-replica
  namespace: corvus-production
spec:
  instances: 3
  
  # Bootstrap from primary backup
  bootstrap:
    recovery:
      source: postgres-primary
      recoveryTargetSettings:
        recoveryTargetAction: promote
  
  # External cluster reference
  externalClusters:
  - name: postgres-primary
    barmanObjectStore:
      destinationPath: "s3://corvus-backups-global/postgres-primary"
      s3Credentials:
        accessKeyId:
          name: backup-credentials
          key: ACCESS_KEY_ID
        secretAccessKey:
          name: backup-credentials
          key: SECRET_ACCESS_KEY

---
# Monitoring and Alerting
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: corvus-ha-alerts
  namespace: corvus-production
spec:
  groups:
  - name: corvus.ha
    rules:
    - alert: DatabaseReplicationLag
      expr: pg_stat_replication_lag_seconds > 300
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "PostgreSQL replication lag is high"
        description: "Replication lag is {{ $value }} seconds"
    
    - alert: CrossRegionConnectivityLoss
      expr: up{job="postgres-replica"} == 0
      for: 2m
      labels:
        severity: critical
      annotations:
        summary: "Cross-region connectivity lost"
        description: "Cannot reach disaster recovery region"
    
    - alert: HighAvailabilityCompromised
      expr: (up{job="api-gateway"} == 0) > 0.5
      for: 1m
      labels:
        severity: critical
      annotations:
        summary: "High availability compromised"
        description: "More than 50% of API Gateway instances are down"
```

---

## 5. Deployment Scripts and Automation

### Deployment Automation

```bash
#!/bin/bash
# scripts/deploy-production.sh

set -euo pipefail

ENVIRONMENT=${1:-production}
VERSION=${2:-latest}
REGION=${3:-us-east-1}

echo "🚀 Deploying Corvus Corone to $ENVIRONMENT"
echo "📦 Version: $VERSION"
echo "🌍 Region: $REGION"

# Pre-deployment checks
echo "🔍 Running pre-deployment checks..."
./scripts/check-prerequisites.sh $ENVIRONMENT
./scripts/validate-configs.sh $ENVIRONMENT

# Database migration
echo "📊 Running database migrations..."
kubectl exec -n corvus-$ENVIRONMENT deployment/api-gateway -- python manage.py migrate --check
kubectl exec -n corvus-$ENVIRONMENT deployment/api-gateway -- python manage.py migrate

# Rolling deployment
echo "📦 Deploying application..."
kubectl set image deployment/api-gateway api-gateway=corvus/api-gateway:$VERSION -n corvus-$ENVIRONMENT
kubectl set image deployment/worker worker=corvus/worker:$VERSION -n corvus-$ENVIRONMENT
kubectl set image deployment/web-ui web-ui=corvus/web-ui:$VERSION -n corvus-$ENVIRONMENT

# Wait for rollout
echo "⏳ Waiting for rollout to complete..."
kubectl rollout status deployment/api-gateway -n corvus-$ENVIRONMENT --timeout=600s
kubectl rollout status deployment/worker -n corvus-$ENVIRONMENT --timeout=600s
kubectl rollout status deployment/web-ui -n corvus-$ENVIRONMENT --timeout=600s

# Health checks
echo "🏥 Running health checks..."
./scripts/health-check.sh $ENVIRONMENT

# Post-deployment tasks
echo "🧹 Running post-deployment tasks..."
kubectl exec -n corvus-$ENVIRONMENT deployment/api-gateway -- python manage.py collectstatic --noinput
kubectl exec -n corvus-$ENVIRONMENT deployment/api-gateway -- python manage.py clearsessions

# Smoke tests
echo "🧪 Running smoke tests..."
./scripts/smoke-tests.sh $ENVIRONMENT

echo "✅ Deployment completed successfully!"
echo "🌐 Application URL: https://corvus.example.com"
echo "📊 Monitoring: https://grafana.corvus.example.com"
```

### Health Check Script

```bash
#!/bin/bash
# scripts/health-check.sh

ENVIRONMENT=${1:-production}
BASE_URL="https://api.corvus.example.com"

if [ "$ENVIRONMENT" = "development" ]; then
    BASE_URL="http://localhost:8000"
elif [ "$ENVIRONMENT" = "staging" ]; then
    BASE_URL="https://api-staging.corvus.example.com"
fi

echo "🏥 Running health checks against $BASE_URL"

# API Health Check
echo "🔍 Checking API health..."
response=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/health")
if [ $response -eq 200 ]; then
    echo "✅ API health check passed"
else
    echo "❌ API health check failed (HTTP $response)"
    exit 1
fi

# Database Connectivity
echo "🔍 Checking database connectivity..."
response=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/health/db")
if [ $response -eq 200 ]; then
    echo "✅ Database connectivity check passed"
else
    echo "❌ Database connectivity check failed (HTTP $response)"
    exit 1
fi

# Redis Connectivity
echo "🔍 Checking Redis connectivity..."
response=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/health/cache")
if [ $response -eq 200 ]; then
    echo "✅ Redis connectivity check passed"
else
    echo "❌ Redis connectivity check failed (HTTP $response)"
    exit 1
fi

# Basic API Functionality
echo "🔍 Testing basic API functionality..."
response=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/api/v1/algorithms")
if [ $response -eq 200 ]; then
    echo "✅ Basic API functionality check passed"
else
    echo "❌ Basic API functionality check failed (HTTP $response)"
    exit 1
fi

echo "✅ All health checks passed!"
```

---

## Summary

These detailed deployment examples provide:

1. **Development Environment** - Quick setup for developers with hot reload and debugging
2. **Staging Environment** - Production-like testing environment with monitoring
3. **Production Cloud** - Scalable, secure Kubernetes deployment with HA
4. **Multi-Region HA** - Disaster recovery and business continuity
5. **Automation Scripts** - Automated deployment with health checks and rollback

Each scenario is tailored to specific needs and implements ADRs from design-decisions.md.