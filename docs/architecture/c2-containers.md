# Containers

> **Decomposition of HPO Benchmarking Platform system into containers (applications, services, databases)**

---

## Container Architecture Diagram

```mermaid
---
config:
  look: neo
  layout: elk
  theme: redux-dark
---
flowchart TB
 subgraph Client["Client"]
        Ext["External AutoML / Analysis systems"]
  end
 subgraph PresentationLayer["PresentationLayer"]
        UI["Web UI / Frontend"]
        APIGW["API Gateway"]
  end
 subgraph BusinessLogicLayer["BusinessLogicLayer"]
        ORCH["Experiment Orchestrator Service"]
        TRK["Experiment Tracking Service"]
        ANALYTICS["MetricsAnalysisService"]
        BENCH["Benchmark Definition Service"]
        ALGREG["Algorithm Registry Service"]
        PUB["PublicationService"]
        RGS["ReportGeneratorService"]
  end
 subgraph ExecLayer["Execution Layer"]
        MB["Message Broker"]
        WORKER["Worker Runtime / Execution Engine"]
        PLUGIN["Algorithm SDK / Plugin Runtime"]
  end
 subgraph Core["HPO Benchmarking Platform"]
        PresentationLayer
        BusinessLogicLayer
        ExecLayer
  end
 subgraph DataLayer["DataLayer"]
        DB[("Results Store - DB")]
        OBJ[("Object Storage")]
  end
 subgraph SupportLayer["SupportLayer"]
        AUTH["AuthService / Identity"]
        MON["Monitoring & Logging Stack"]
  end
    UI -- HTTP --> APIGW
    Ext -- HTTP API --> APIGW
    APIGW --> ORCH & TRK & ANALYTICS & BENCH & ALGREG & PUB & AUTH & RGS
    ORCH --> MB
    WORKER --> MB & TRK & BENCH & ALGREG & OBJ & PLUGIN
    RGS --> TRK & ANALYTICS & PUB & OBJ
    TRK --> DB
    BENCH --> DB
    ALGREG --> DB
    PUB --> DB
    Core --> MON
     DB:::Sky
     OBJ:::Sky
     AUTH:::Sky
     MON:::Sky
    classDef Sky stroke-width:1px, stroke-dasharray:none, stroke:#374D7C, fill:#E2EBFF, color:#374D7C
    style PresentationLayer stroke:#FFD600
    style BusinessLogicLayer stroke:#FF6D00
    style ExecLayer stroke:#00C853
    style Core stroke:#C8E6C9
    style Client stroke:#FFE0B2
    style SupportLayer stroke:#2962FF
    style DataLayer stroke:#AA00FF
    linkStyle 0 stroke:#FFD600,fill:none
    linkStyle 2 stroke:#FFD600,fill:none
    linkStyle 3 stroke:#FFD600,fill:none
    linkStyle 4 stroke:#FFD600,fill:none
    linkStyle 5 stroke:#FFD600,fill:none
    linkStyle 6 stroke:#FFD600,fill:none
    linkStyle 7 stroke:#FFD600,fill:none
    linkStyle 8 stroke:#FFD600,fill:none
    linkStyle 9 stroke:#FFD600,fill:none
    linkStyle 10 stroke:#FFD600,fill:none
    linkStyle 11 stroke:#00C853,fill:none
    linkStyle 12 stroke:#00C853,fill:none
    linkStyle 13 stroke:#00C853,fill:none
    linkStyle 14 stroke:#00C853,fill:none
    linkStyle 15 stroke:#00C853,fill:none
    linkStyle 16 stroke:#00C853,fill:none
    linkStyle 17 stroke:#D50000,fill:none
    linkStyle 18 stroke:#D50000,fill:none
    linkStyle 19 stroke:#D50000,fill:none
    linkStyle 20 stroke:#D50000,fill:none
    linkStyle 21 stroke:#AA00FF,fill:none
    linkStyle 22 stroke:#FF6D00,fill:none
    linkStyle 24 stroke:#2962FF,fill:none
```

---

## Container Overview

### 🎨 Presentation Layer
- **Web UI (Frontend)** - User interface React/Vue/Angular
- **API Gateway** - Single HTTP/REST/GraphQL entry point

### 🧠 Business Logic Layer (Core Services)
- **Experiment Orchestrator** - Experiment orchestration and planning
- **Experiment Tracking** - Run and metrics tracking
- **MetricsAnalysisService** - Results analysis and aggregation
- **Benchmark Definition Service** - Benchmark and problem definitions
- **Algorithm Registry Service** - HPO algorithm catalog
- **PublicationService** - Publication and reference management
- **ReportGeneratorService** - Report generation

### ⚡ Execution Layer
- **Worker Runtime** - Individual run execution
- **Algorithm SDK/Plugin Runtime** - Algorithm plugin execution
- **Message Broker** - Task and event queuing

### 💾 Data Layer
- **Results Store (Database)** - Relational database (PostgreSQL)
- **File/Object Storage** - Artifacts, datasets, models

### 🔧 Support Layer
- **Auth Service** - Authorization and authentication
- **Monitoring & Logging** - Observability and diagnostics

---

## Detailed Container Description

| Container | Layer | Responsibilities | Communication | PC vs Cloud | Role in benchmarking |
|----------|---------|-------------------|-------------|--------------|---------------------|
| **Web UI (Frontend)** | **Presentation** | • Interface for benchmark and experiment definition<br>• HPO algorithm catalog viewing<br>• Experiment tracking panel<br>• Results comparison<br>• Publication management<br>• Report generation<br>• Basic administration | • REST/GraphQL/WebSocket z **API Gateway** (sync) | **PC:** local container or static files<br>**Cloud:** frontend (CDN/storage) | Presentation of experiment goals, configuration, results and statistics |
| **API Gateway / Backend API** | **Presentation** | • Single entry point for Web UI and external systems<br>• Request routing to domain services<br>• Authorization/authentication<br>• Rate limiting, CORS | • Z klientami: HTTP REST/GraphQL (sync)<br>• Z usługami: HTTP/gRPC (sync) + Message Broker (async) | **PC:** single container (monolith/gateway)<br>**Cloud:** API Gateway + microservices | Central integration point and function exposure |
| **Experiment Orchestrator Service** | **Business Logic** | • Accepting experiment definitions<br>• Plan validation (algorithms, instances)<br>• Creating run plans (algorithm × instance × seed)<br>• Assigning runs to workers<br>• Experiment state management<br>• Reproducibility control | • Sync: z API Gateway<br>• Async: do Worker Runtime (Message Broker)<br>• Events: RunCompleted/RunFailed | **PC:** single instance<br>**Cloud:** scalable microservice, HA | Implements **experiment plan** and budget control |
| **Worker Runtime / Execution Engine** | **Execution** | • Executing individual runs<br>• Loading benchmark and instances<br>• Running HPO algorithm<br>• Reporting metrics<br>• Error handling and retry | • Async: odbiór zadań z Message Broker<br>• Sync/Async: zapisy do Tracking Service<br>• Dostęp do Object Storage | **PC:** 1-N workers (docker-compose)<br>**Cloud:** worker pods, autoscaling | Ensures reproducibility and comparability of runs |
| **Benchmark Definition Service** | **Business Logic** | • Storing benchmark definitions<br>• Benchmark versioning<br>• Dataset and problem lists<br>• Metrics, known optimum/best-known | • Sync: API for Orchestrator and Web UI | **PC/Cloud:** single container | Implements problem instance selection
| **Algorithm Registry Service** | **Business Logic** | • HPO algorithm registry (built-in + plugins)<br>• Metadata: name, type, parameters<br>• Algorithm versioning<br>• Compatibility validation | • Sync: API for Web UI, Orchestrator, Plugin Runtime | **PC/Cloud:** single container/service | Conscious algorithm and configuration selection |
| **Algorithm SDK / Plugin Runtime** | **Execution** | • Loading and isolating plugins<br>• Plugin API contract<br>• Input/output validation<br>• Results reporting | • Locally with Worker Runtime<br>• API or language calls | **PC/Cloud:** same code, different environment | Easy algorithm addition in unified environment |
| **Experiment Tracking Service** | **Business Logic** | • API for logging runs, metrics, tags<br>• Relationships: experiment→run→algorithm→benchmark<br>• Parameter change history<br>• Search and filtering | • Sync: API for Worker Runtime, Orchestrator, Web UI | **PC:** 1 container<br>**Cloud:** scalable microservice | Tracking panel, results analysis, reproducibility |
| **MetricsAnalysisService** | **Business Logic** | • Results aggregation<br>• Complex metrics (time to error level)<br>• Statistical tests<br>• Comparative charts | • Sync: API for Web UI<br>• Async: listening to RunCompleted events | **PC:** 1 container<br>**Cloud:** scalable microservice | **Analysis and presentation of benchmark results** |
| **PublicationService** | **Business Logic** | • Publication catalog (DOI, BibTeX)<br>• Links to algorithms/benchmarks<br>• Bibliography generation<br>• CrossRef/arXiv integration | • Sync: API for Web UI, other services<br>• Sync/Async: calls to bibliographic systems | **PC/Cloud:** integration service | Links results to scientific literature |
| **Results Store (Database)** | **Data** | • Domain data: Experiments, Runs, Metrics<br>• Algorithms, Benchmarks, Publications<br>• Relationships and configurations<br>• ACID transactions | • Internal: through DAO from domain services<br>• Orchestrator: only indirectly through API | **PC:** local PostgreSQL<br>**Cloud:** managed database | Central repository for reproducibility |
| **Object Storage** | **Data** | • Large artifacts: datasets, models<br>• File logs<br>• Generated reports<br>• Versioning and lifecycle | • S3/File API from workers and services | **PC:** local disk/MinIO<br>**Cloud:** S3/GCS/Azure Blob | Reproducible artifact storage |
| **Message Broker (RabbitMQ/Redis)** | **Execution** | • Run task queue<br>• System events<br>• RunStarted/Completed/Failed<br>• ExperimentCompleted | • Async: messages between services<br>• Pub/Sub pattern | **PC:** RabbitMQ (primary), Redis (fallback)<br>**Cloud:** Managed RabbitMQ or Redis Streams | Flexible experiment plan and scaling |
| **Monitoring & Logging Stack** | **Support** | • **Metrics:** Prometheus + Thanos (long-term)<br>• **Logging:** ELK Stack (Elasticsearch/Logstash/Kibana)<br>• **Tracing:** Jaeger distributed tracing<br>• **Dashboards:** Grafana unified visualization<br>• Business KPIs and SLA monitoring | • OpenTelemetry instrumentation<br>• Fluentd log shipping<br>• AlertManager notifications | **PC:** Prometheus+Grafana+basic logging<br>**Cloud:** Full observability stack with clustering | Three pillars observability (metrics/logs/traces) |
| **Auth Service** | **Support** | • OAuth2/OIDC authentication<br>• RBAC with role hierarchy (admin/plugin-author/researcher/viewer)<br>• JWT token management (15min TTL)<br>• MFA for privileged operations<br>• API keys for programmatic access | • Sync: OAuth2 flows, token validation<br>• Integration with external IdP | **PC:** built-in IdP with local accounts<br>**Cloud:** SAML/OIDC integration | Multi-tenant access control and compliance |
| **ReportGeneratorService** | **Business Logic** | • HTML/PDF/LaTeX reports<br>• Data aggregation from multiple sources<br>• Templates and styling<br>• Bibliography and citations | • Sync: API from Web UI and Orchestrator<br>• Data fetch from Tracking/Results Store | **PC/Cloud:** Python/Node.js service | Consistent, repeatable benchmark reports |

---

## Communication Patterns

### 🔄 Synchronous (Request/Response)
- **Web UI ↔ API Gateway**: REST/GraphQL
- **API Gateway ↔ Core Services**: HTTP/gRPC
- **Worker ↔ Tracking Service**: REST API
- **Services ↔ Results Store**: Database queries

### ⚡ Asynchronous (Event-driven)
- **Orchestrator → Workers**: Task queue (RabbitMQ primary, Redis fallback)
- **Workers → Analytics**: RunCompleted events
- **System events**: ExperimentStarted/Completed/Failed (via Event Bus)
- **Notifications**: Alerts, status updates

### 📊 Batch Processing
- **Metrics aggregation**: Scheduled batch jobs
- **Report generation**: On-demand/scheduled
- **Data export**: Bulk operations

---

## Scaling and Availability

### 📈 Scaling strategies

| Layer | PC | Cloud | Bottlenecks |
|---------|-------|-------|-------------|
| **Frontend** | 1 instance | CDN + multiple replicas | N/A (stateless) |
| **API Gateway** | 1 container | Load balancer + replicas | Rate limiting |
| **Core Services** | 1 each | Auto-scaling groups | Database connections |
| **Workers** | 1-N containers | HPA based on queue length | CPU/Memory intensive |
| **Database** | Single instance | Read replicas, sharding | Concurrent writes |
| **Object Storage** | Local disk/MinIO | Distributed storage | Network I/O |

### 🛡️ High Availability (HA)

**Critical components:**
- **Results Store**: Master-slave replication
- **Message Broker**: Clustered setup
- **API Gateway**: Load balancing
- **Workers**: Stateless, easy replacement

**Recovery strategies:**
- **Database**: Point-in-time recovery, backups
- **Object Storage**: Cross-region replication
- **Services**: Health checks, auto-restart
- **Workers**: Retry policies, dead letter queues

---

## Container Monitoring

### 📊 Key Metrics
- **Performance**: CPU, Memory, Network, Disk I/O
- **Business**: Run duration, success/failure rates
- **System**: Queue lengths, connection pools
- **Custom**: Algorithm-specific metrics

### 🚨 Alerting
- **Infrastructure**: Container down, resource exhaustion
- **Application**: High error rates, long-running jobs
- **Business**: Experiment failures, data quality issues

### 📈 Dashboards
- **System overview**: All containers health
- **Experiment tracking**: Active runs, queue status
- **Performance**: Latency, throughput per service
- **Business**: Benchmark results, algorithm comparisons

---

## Related Documents

- **Previous level**: [Context (C4-1)](c1-context.md)
- **Next level**: [Components (C4-3)](c3-components.md)
- **Implementation details**: [Code (C4-4)](c4-code.md)
- **Requirements**: [Functional Requirements](../requirements/functional-requirements.md), [Use Cases](../requirements/use-cases.md)
- **Deployment**: [Deployment Guide](../operations/deployment-guide.md)
- **Monitoring**: [Monitoring Guide](../operations/monitoring-guide.md)
