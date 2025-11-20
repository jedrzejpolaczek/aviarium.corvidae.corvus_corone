# Infrastructure Support

This directory contains all infrastructure-related configurations and scripts for the Corvus Corone HPO Benchmarking Platform as part of the **Support Layer**.

## Structure

```
support-layer/infrastructure/
├── k8s/                    <- Kubernetes deployment manifests
│   └── namespace.yaml      <- Kubernetes namespace configuration
├── monitoring/             <- Monitoring and observability configs
│   └── prometheus.yml      <- Prometheus monitoring configuration
└── scripts/                <- Infrastructure automation scripts
    ├── init-db.sql         <- Database initialization script
    ├── init-db-simple.sql  <- Simple database setup
    ├── setup-dev.sh        <- Development environment setup
    ├── validate-architecture.py <- Architecture validation runner
    └── verify-structure.ps1 <- Structure verification script
```

## Usage

### Architecture Validation
```bash
# From project root
python src/support-layer/infrastructure/scripts/validate-architecture.py
```

### Database Setup
The database initialization scripts are automatically mounted in Docker containers via docker-compose.yml.

### Development Setup
```bash
# From project root
./src/support-layer/infrastructure/scripts/setup-dev.sh
```

### Kubernetes Deployment
```bash
# Apply namespace
kubectl apply -f src/support-layer/infrastructure/k8s/namespace.yaml
```

### Monitoring
The Prometheus configuration is automatically loaded by the monitoring container.

## Support Layer Architecture Alignment

This infrastructure support follows the project's **Layers → Containers → Components** architecture:
- **Layer**: Support Layer (cross-cutting operational concerns)
- **Container**: Infrastructure (operational infrastructure)
- **Components**: k8s, monitoring, scripts (specific infrastructure concerns)

This organization properly places infrastructure concerns within the support layer alongside other cross-cutting services like authentication, maintaining clear architectural boundaries.