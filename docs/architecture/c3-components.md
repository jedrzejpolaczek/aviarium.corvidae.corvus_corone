# Components

> **Implementation details of main containers in HPO Benchmarking Platform system**

---

## Component Diagram

```mermaid
---
config:
  layout: elk
  theme: redux-dark
---
flowchart TB
 subgraph WebUI["Web UI (container)"]
        WebUI_Designer["ExperimentDesignerUI"]
        WebUI_Tracking["TrackingDashboardUI"]
        WebUI_Comparison["ComparisonViewUI"]
        WebUI_BenchCatalog["BenchmarkCatalogUI"]
        WebUI_AlgoCatalog["AlgorithmCatalogUI"]
        WebUI_Publications["PublicationManagerUI"]
        WebUI_Admin["AdminSettingsUI"]
  end
 subgraph APIGateway["API Gateway / Backend API (container)"]
        APIGateway_Public["Public API"]
        APIGateway_Auth["AuthN/AuthZ"]
        APIGateway_Routing["Routing"]
  end
 subgraph PresentationLayer["Presentation Layer"]
        WebUI
        APIGateway
  end
 subgraph ExperimentOrchestrator["Experiment Orchestrator Service (container)"]
        Orchestrator_Config["ExperimentConfigManager"]
        Orchestrator_Plan["ExperimentPlanBuilder"]
        Orchestrator_Scheduler["RunScheduler"]
        Orchestrator_State["ExperimentStateStore"]
        Orchestrator_Reprod["ReproducibilityManager"]
        Orchestrator_Events["EventPublisher"]
  end
 subgraph BenchmarkDefinitionService["Benchmark Definition Service (container)"]
        Bench_Repo["BenchmarkRepository"]
        Bench_Instances["ProblemInstanceManager"]
        Bench_Versioning["BenchmarkVersioning"]
  end
 subgraph AlgorithmRegistryService["Algorithm Registry Service (container)"]
        Algo_Metadata["AlgorithmMetadataStore"]
        Algo_Versions["AlgorithmVersionManager"]
        Algo_Compat["CompatibilityChecker"]
  end
 subgraph ExperimentTrackingService["Experiment Tracking Service (container)"]
        Track_API["TrackingAPI"]
        Track_Runs["RunLifecycleManager"]
        Track_Search["TaggingAndSearchEngine"]
        Track_Lineage["LineageTracker"]
  end
 subgraph MetricsAnalysisService["MetricsAnalysisService (container)"]
        Metrics_Calc["MetricCalculator"]
        Metrics_Agg["AggregationEngine"]
        Metrics_Stats["StatisticalTestsEngine"]
        Metrics_Query["VisualizationQueryAdapter"]
  end
 subgraph PublicationService["PublicationService (container)"]
        Pub_Catalog["ReferenceCatalog"]
        Pub_Citation["CitationFormatter"]
        Pub_Linker["ReferenceLinker"]
        Pub_External["ExternalBibliographyClient"]
  end
 subgraph ReportGeneratorService["ReportGeneratorService (container)"]
        Report_Template["ReportTemplateEngine"]
        Report_Assembler["ReportAssembler"]
        Report_Exporter["ReportExporter"]
        Report_Metadata["ReportMetadataStore"]
  end
 subgraph BusinessLogicLayer["Business Logic Layer"]
        ExperimentOrchestrator
        BenchmarkDefinitionService
        AlgorithmRegistryService
        ExperimentTrackingService
        MetricsAnalysisService
        PublicationService
        ReportGeneratorService
  end
 subgraph WorkerRuntime["Worker Runtime / Execution Engine (container)"]
        Worker_Executor["RunExecutor"]
        Worker_DataLoader["DatasetLoader"]
        Worker_Reporter["MetricReporter"]
        Worker_Uploader["ArtifactUploader"]
  end
 subgraph PluginRuntime["Algorithm SDK / Plugin Runtime (container)"]
        Plugin_Interface["IAlgorithmPlugin"]
        Plugin_Loader["PluginLoader"]
        Plugin_Sandbox["SandboxManager"]
        Plugin_Validator["PluginValidator"]
  end
 subgraph MessageBroker["Message Broker (container)"]
        Broker_RunQueue["RunJobQueue"]
        Broker_EventBus["EventBus"]
  end
 subgraph ExecutionLayer["Execution Layer"]
        WorkerRuntime
        PluginRuntime
        MessageBroker
  end
 subgraph ResultsStore["Results Store (container)"]
        DAO_Experiments["ExperimentDAO"]
        DAO_Runs["RunDAO"]
        DAO_Metrics["MetricDAO"]
        DAO_Algorithms["AlgorithmDAO"]
        DAO_Benchmarks["BenchmarkDAO"]
        DAO_Publications["PublicationDAO"]
        DAO_Links["LinkDAO"]
  end
 subgraph ObjectStorage["File / Object Storage (container)"]
        Storage_Client["ObjectStorageClient"]
        Storage_Artifacts["ArtifactRepository"]
        Storage_Datasets["DatasetRepository"]
  end
 subgraph DataLayer["Data Layer"]
        ResultsStore
        ObjectStorage
  end
 subgraph AuthServiceC["Auth Service (container)"]
        Auth_TokenValidation["TokenValidation"]
        Auth_RoleMapping["RoleMapping"]
  end
 subgraph MonitoringStack["Monitoring & Logging Stack (container)"]
        Monitoring_LogCollector["LogCollector"]
        Monitoring_MetricsCollector["MetricsCollector"]
        Monitoring_Dashboard["MonitoringDashboard"]
        Monitoring_Alerting["AlertingEngine"]
  end
 subgraph SupportLayer["Support Layer"]
        AuthServiceC
        MonitoringStack
  end
    WebUI_Designer --> APIGateway_Public
    WebUI_Tracking --> APIGateway_Public
    WebUI_Comparison --> APIGateway_Public
    WebUI_BenchCatalog --> APIGateway_Public
    WebUI_AlgoCatalog --> APIGateway_Public
    WebUI_Publications --> APIGateway_Public
    APIGateway_Public --> Orchestrator_Config & Track_API & Metrics_Query & Pub_Catalog & Bench_Repo & Algo_Metadata & Report_Assembler
    Orchestrator_Config --> Bench_Repo & Algo_Metadata
    Orchestrator_Plan --> Bench_Instances
    Orchestrator_Scheduler --> Broker_RunQueue
    Broker_RunQueue --> Worker_Executor
    Orchestrator_State --> Track_API
    Orchestrator_Events --> Broker_EventBus
    Worker_Executor --> Plugin_Interface & Track_Runs
    Worker_Uploader --> Storage_Artifacts
    Worker_DataLoader --> Storage_Datasets
    Track_API --> DAO_Experiments
    Track_Runs --> DAO_Runs
    Track_Search --> DAO_Experiments
    Track_Lineage --> DAO_Links
    Metrics_Calc --> DAO_Metrics
    Metrics_Agg --> DAO_Metrics
    Pub_Catalog --> DAO_Publications
    Pub_Linker --> DAO_Links
    Report_Assembler --> Track_API & Metrics_Agg & Pub_Catalog
    Report_Exporter --> Storage_Artifacts
    Bench_Instances --> Storage_Datasets
    Monitoring_LogCollector --> Worker_Executor
    Monitoring_MetricsCollector --> Orchestrator_State & APIGateway_Public
    Auth_TokenValidation --> APIGateway_Auth
    Auth_RoleMapping --> WebUI_Designer
    classDef presentationLayer fill:#FFE0B2,stroke:#FF6D00,stroke-width:2px
    classDef businessLayer fill:#FFF3E0,stroke:#FF9800,stroke-width:2px
    classDef executionLayer fill:#E8F5E8,stroke:#4CAF50,stroke-width:2px
    classDef dataLayer fill:#F3E5F5,stroke:#9C27B0,stroke-width:2px
    classDef supportLayer fill:#E3F2FD,stroke:#2196F3,stroke-width:2px
    style BusinessLogicLayer stroke:#FFD600
    style SupportLayer stroke:#D50000
    style PresentationLayer stroke:#FF6D00
    style ExecutionLayer stroke:#00C853
    style DataLayer stroke:#2962FF
```

Below is a description of components divided by the containers they belong to.

---

## 3.1 Experiment Orchestrator Service

**Responsible for:** Experiment orchestration, run planning, state management

| Component | Responsibilities | Interactions |
|-----------|-------------------|-------------|
| **ExperimentConfigManager** | • Validates experiment configuration<br>• Checks algorithm compatibility with benchmarks<br>• Validates budgets and resource limits | ↔ Benchmark Definition Service<br>↔ Algorithm Registry |
| **ExperimentPlanBuilder** | • Creates run plan (configuration matrix)<br>• Algorithm × instance × seed × budget<br>• Optimizes execution order | ← ExperimentConfigManager<br>→ RunScheduler |
| **RunScheduler** | • Translates plan into queue tasks<br>• Manages priorities<br>• Handles retry and cancel | ← ExperimentPlanBuilder<br>→ Message Broker<br>↔ Worker Runtime |
| **ExperimentStateStore** | • Experiment state management<br>• Run statuses: PENDING, RUNNING, FAILED, COMPLETED<br>• **No own database** - all data through Tracking Service API | ↔ Experiment Tracking Service<br>↔ Web UI (dashboards) |
| **ReproducibilityManager** | • Seed management<br>• Image versions, configuration snapshots<br>• Ensuring reproducibility | ↔ Experiment Tracking Service<br>↔ Results Store (indirectly) |
| **EventPublisher** | • Publishes system events<br>• ExperimentStarted/Completed/Failed<br>• Integration events | → Message Broker/Event Bus<br>→ Monitoring, Web UI, ReportGenerator |

### API Experiment Orchestrator Service

**Configuration validation:**
```json
POST /api/v1/experiments/validate
{
  "benchmarks": ["benchmark_id_1", "benchmark_id_2"],
  "algorithms": ["algorithm_id_1", "algorithm_id_2"],
  "budget_config": {
    "max_evaluations": 100,
    "time_limit_minutes": 60
  },
  "seeds": [42, 123, 456]
}
```

**Starting experiment:**
```json
POST /api/v1/experiments/{experiment_id}/start
{
  "priority": "NORMAL",
  "retry_policy": {
    "max_retries": 3,
    "retry_delay_seconds": 30
  }
}
```

---

## 3.2 Benchmark Definition Service

**Responsible for:** Benchmark definitions, problem instances, versioning

| Component | Responsibilities | Interactions |
|-----------|-------------------|-------------|
| **BenchmarkRepository** | • Benchmark CRUD operations<br>• Metadata and descriptions<br>• Linking with publications | ↔ Results Store (BenchmarkDAO)<br>↔ Experiment Orchestrator |
| **ProblemInstanceManager** | • Manages instances (dataset + configuration)<br>• Mapping to datasets in Object Storage<br>• Checking compatibility with algorithms | ↔ DatasetRepository<br>↔ Algorithm Registry |
| **BenchmarkVersioning** | • Benchmark versioning<br>• Marking canonical versions<br>• Migration paths between versions | ↔ BenchmarkRepository<br>↔ ExperimentConfigManager |

---

## 3.3 Algorithm Registry Service

**Responsible for:** HPO algorithm catalog, versioning, compatibility

| Component | Responsibilities | Interactions |
|-----------|-------------------|-------------|
| **AlgorithmMetadataStore** | • Algorithm description: name, type, parameters<br>• Links to publications<br>• Environment requirements | ↔ Results Store (AlgorithmDAO)<br>↔ Web UI (AlgorithmCatalogUI) |
| **AlgorithmVersionManager** | • Algorithm implementation versions<br>• Status: draft, approved, deprecated<br>• Approval workflow | ↔ PluginLoader/PluginValidator<br>↔ Experiment Orchestrator |
| **CompatibilityChecker** | • Checks algorithm compatibility with benchmarks<br>• Resource requirements analysis<br>• Problem type matching | ↔ Benchmark Definition Service |

### API Algorithm Registry

**Algorithm registration:**
```json
POST /api/v1/algorithms
{
  "name": "Custom Bayesian Optimizer",
  "type": "BAYESIAN",
  "parameter_space": {
    "acquisition_function": {
      "type": "categorical",
      "values": ["EI", "UCB", "PI"]
    }
  },
  "compatible_problem_types": ["CLASSIFICATION", "REGRESSION"]
}
```

**Version management:**
```json
POST /api/v1/algorithms/{algorithm_id}/versions
{
  "version": "1.1.0",
  "plugin_location": "s3://plugins/custom-bayes-opt-v1.1.0.whl",
  "changelog": "Fixed memory leak, improved convergence"
}
```

---

## 3.4 Algorithm SDK / Plugin Runtime

**Responsible for:** Running algorithm plugins, sandboxing, validation

| Component | Responsibilities | Interactions |
|-----------|-------------------|-------------|
| **IAlgorithmPlugin** | • Plugin interface<br>• Methods: `suggest()`, `observe()`, `init()`<br>• Input/output contract | Implemented by plugins<br>Called by SandboxManager |
| **PluginLoader** | • Loads plugins (wheel, Python modules, gRPC)<br>• Dependency resolution<br>• Version management | ↔ AlgorithmVersionManager<br>↔ ObjectStorageClient |
| **SandboxManager** | • **Container isolation:** gVisor/Kata Containers dla strong isolation (patrz ADR-005)<br>• **Security policies:** Seccomp profiles, AppArmor/SELinux policies<br>• **Resource limits:** CPU/Memory/Disk quotas per plugin (1000m CPU, 2Gi RAM max)<br>• **Runtime monitoring:** Falco syscall monitoring, blocked syscalls<br>• **Filesystem:** Read-only root filesystem, write tylko /tmp<br>• **Network policies:** Deny all egress, allow API calls only<br>• **Image security:** Vulnerability scanning, distroless base images | ↔ Worker Runtime<br>↔ PluginLoader<br>↔ Security Policy Engine<br>↔ Container Runtime (gVisor/Kata) |
| **PluginValidator** | • Checks plugin implementation<br>• Test run<br>• Interface compliance | ↔ IAlgorithmPlugin<br>↔ Algorithm Registry |

---

## 3.5 Experiment Tracking Service

**Responsible for:** Tracking runs, metrics, relationships, experiment history

| Component | Responsibilities | Interactions |
|-----------|-------------------|-------------|
| **TrackingAPI** | • Public API for logging<br>• Runs, metrics, artifacts, tags<br>• Real-time and batch updates | ← Worker Runtime/plugins/Web UI<br>↔ RunLifecycleManager, DAOs |
| **RunLifecycleManager** | • Creates runs, updates statuses<br>• Lifecycle management<br>• Event emission | ↔ Experiment Orchestrator<br>↔ Results Store (RunDAO)<br>↔ EventPublisher |
| **TaggingAndSearchEngine** | • Filtering and tagging<br>• Full-text search<br>• Query optimization | ↔ Results Store<br>↔ Web UI (dashboards) |
| **LineageTracker** | • Relationships: experiment→run→algorithm→benchmark<br>• Data lineage<br>• Provenance tracking | ↔ Results Store (LinkDAO)<br>↔ PublicationService<br>↔ ReportGenerator |

### API Experiment Tracking

**Run logging:**
```json
POST /api/v1/runs
{
  "experiment_id": "exp_123",
  "algorithm_version_id": "alg_v1.2.3",
  "benchmark_instance_id": "bench_inst_456",
  "seed": 42
}
```

**Metrics logging:**
```json
POST /api/v1/runs/{run_id}/metrics
{
  "metrics": [
    {
      "name": "best_score",
      "value": 0.9234,
      "step": 10,
      "timestamp": "2025-11-18T14:35:00Z"
    }
  ]
}
```

---

## 3.6 MetricsAnalysisService

**Responsible for:** Results aggregation, statistical analyses, visualizations

| Component | Responsibilities | Interactions |
|-----------|-------------------|-------------|
| **MetricCalculator** | • Calculates metrics from raw results<br>• Accuracy, regret, convergence rate<br>• Custom metrics | ↔ TrackingAPI/MetricDAO<br>↔ AggregationEngine |
| **AggregationEngine** | • Aggregates results by benchmarks/algorithms<br>• Statistical summaries<br>• Ranking computations | ↔ MetricCalculator<br>↔ StatisticalTestsEngine |
| **StatisticalTestsEngine** | • Statistical tests (Friedman/Nemenyi)<br>• Significance testing<br>• Effect size calculations | ↔ AggregationEngine<br>↔ ReportGenerator<br>↔ Web UI |
| **VisualizationQueryAdapter** | • Prepares data for charts<br>• Chart data formatting<br>• Interactive queries | ← Web UI<br>↔ MetricDAO, AggregationEngine |

---

## 3.7 PublicationService

**Responsible for:** Publication management, bibliography, citations

| Component | Responsibilities | Interactions |
|-----------|-------------------|-------------|
| **ReferenceCatalog** | • Publication database (metadata, DOIs)<br>• CRUD operations<br>• Search and filtering | ↔ Results Store (PublicationDAO)<br>↔ Web UI |
| **CitationFormatter** | • Generates citations and BibTeX<br>• Multiple citation styles<br>• Export formats | ↔ ReferenceCatalog<br>↔ ReportGenerator |
| **ReferenceLinker** | • Links publications with algorithms/benchmarks<br>• Relationship management<br>• Impact tracking | ↔ LineageTracker<br>↔ Results Store (LinkDAO) |
| **ExternalBibliographyClient** | • Integration with CrossRef/arXiv/DOI<br>• Metadata enrichment<br>• Auto-import | → External services<br>↔ ReferenceCatalog |

---

## 3.8 Results Store

**Responsible for:** Data access layer (DAO pattern)

| Component | Responsibilities | Interactions |
|-----------|-------------------|-------------|
| **ExperimentDAO** | • Access to experiment data<br>• CRUD + queries<br>• Filtering, sorting | ↔ Experiment Tracking Service<br>↔ Web UI (indirectly) |
| **RunDAO** | • Access to run data<br>• Status management<br>• Metrics linking | ↔ RunLifecycleManager<br>↔ MetricsAnalysisService |
| **MetricDAO** | • Access to metrics data<br>• Time series queries<br>• Aggregation support | ↔ TrackingAPI<br>↔ MetricCalculator |
| **AlgorithmDAO** | • Access to algorithm data<br>• Version management<br>• Metadata queries | ↔ AlgorithmMetadataStore |
| **BenchmarkDAO** | • Access to benchmark data<br>• Instance management<br>• Compatibility queries | ↔ BenchmarkRepository |
| **PublicationDAO** | • Access to publication data<br>• Citation management<br>• Search support | ↔ ReferenceCatalog |
| **LinkDAO** | • Relationships between entities<br>• Relationship queries<br>• Lineage tracking | ↔ LineageTracker<br>↔ ReferenceLinker |

---

## 3.9 Web UI

**Responsible for:** User interfaces (all interactions through API Gateway)

| Component | Responsibilities | Usage Purpose |
|-----------|-------------------|--------------|
| **ExperimentDesignerUI** | • Experiment configuration wizard<br>• Wizard workflow<br>• Validation feedback | Researchers configuring experiments |
| **TrackingDashboardUI** | • Experiment/run panel<br>• Real-time monitoring<br>• Status tracking | Monitoring experiment progress |
| **ComparisonViewUI** | • Charts and algorithm comparisons<br>• Statistical analysis<br>• Interactive visualizations | Benchmark results analysis |
| **BenchmarkCatalogUI** | • Benchmark catalog<br>• Browse and search<br>• Metadata viewing | Problem instance selection |
| **AlgorithmCatalogUI** | • Algorithm catalog<br>• Version management<br>• Compatibility checking | HPO algorithm selection |
| **PublicationManagerUI** | • Publication management<br>• Bibliography management<br>• Citation tools | Links to scientific literature |
| **AdminSettingsUI** | • Administrative panel<br>• System configuration<br>• User management | System configuration |

---

## 3.10 File / Object Storage

**Responsible for:** Storing artifacts, datasets, models

| Component | Responsibilities | Interactions |
|-----------|-------------------|-------------|
| **ObjectStorageClient** | • Low-level client (S3/MinIO/GCS)<br>• Upload/download operations<br>• Authentication handling | Used by other storage components |
| **ArtifactRepository** | • Logical layer over ObjectStorageClient<br>• Path conventions<br>• Versioning support | ← Worker Runtime<br>↔ TrackingAPI<br>↔ ReportGenerator |
| **DatasetRepository** | • Datasets in Object Storage<br>• Location and versioning<br>• Access control | ↔ ProblemInstanceManager<br>↔ Worker Runtime |

---

## 3.11 ReportGeneratorService

**Responsible for:** Generating reports from experiment results

| Component | Responsibilities | Interactions |
|-----------|-------------------|-------------|
| **ReportTemplateEngine** | • Report templates (HTML/PDF/LaTeX)<br>• Template management<br>• Customization support | ↔ ReportAssembler<br>↔ Web UI |
| **ReportAssembler** | • Assembles data from multiple sources<br>• Data aggregation<br>• Content generation | ↔ TrackingAPI<br>↔ MetricsAnalysisService<br>↔ PublicationService |
| **ReportExporter** | • Generates report files<br>• Multiple formats<br>• URL generation | ↔ ArtifactRepository<br>↔ Web UI |
| **ReportMetadataStore** | • Report metadata<br>• Report catalog<br>• Access tracking | ↔ Results Store<br>↔ Web UI |

---

## 3.12 Message Broker

**Responsible for:** Task and system event queuing

| Component | Responsibilities | Main Relationships |
|-----------|-------------------|-------------------|
| **RunJobQueue** | • Experiment run task queue<br>• Priority handling<br>• Dead letter queue | ← RunScheduler<br>→ Worker Runtime |
| **EventBus** | • Domain event channel<br>• Pub/Sub pattern<br>• Event routing | ← EventPublisher<br>→ Web UI, Monitoring |

---

## 3.13 Worker Runtime / Execution Engine

**Responsible for:** Executing individual experiment runs

| Component | Responsibilities | Main Relationships |
|-----------|-------------------|-------------------|
| **RunExecutor** | • Coordinates run execution<br>• Plugin orchestration<br>• Error handling | ← RunJobQueue<br>→ Plugin Runtime<br>→ Tracking |
| **DatasetLoader** | • Loads datasets from Object Storage<br>• Data preparation<br>• Cache management | ← Benchmark Definition Service<br>→ RunExecutor |
| **MetricReporter** | • Sends metrics to Tracking Service<br>• Real-time/batch reporting<br>• Retry logic | → Experiment Tracking<br>→ MetricsAnalysisService |
| **ArtifactUploader** | • Upload models and artifacts<br>• Progress tracking<br>• URL generation | → File/Object Storage |

---

## 3.14 API Gateway / Backend API

**Responsible for:** HTTP/REST/GraphQL entry point

| Component | Responsibilities | Main Relationships |
|-----------|-------------------|-------------------|
| **REST/GraphQL API** | • Public backend API<br>• Request routing<br>• Response formatting | ← Web UI, external systems<br>→ Domain services |
| **AuthN/AuthZ** | • Authentication and authorization<br>• Token validation<br>• RBAC enforcement | ↔ Auth Service<br>↔ Web UI |
| **Routing** | • Endpoint mapping to services<br>• Load balancing<br>• Circuit breaker | → Orchestrator, Tracking, Metrics, Catalogs |

---

## 3.15 Auth Service

**Responsible for:** Authorization and identity integration

| Component | Responsibilities | Main Relationships |
|-----------|-------------------|-------------------|
| **TokenValidation** | • Access token validation<br>• JWT handling<br>• Session management | ← API Gateway, Web UI |
| **RoleMapping** | • User to role mapping<br>• Permission checking<br>• RBAC implementation | → All services using roles/permissions |

---

## 3.16 Monitoring & Logging Stack

**Responsible for:** System observability, metrics, alerting

| Component | Responsibilities | Main relationships |
|-----------|-------------------|-------------------|
| **LogCollector** | • Collects logs from containers<br>• Log aggregation<br>• Structured logging | ← All containers (Orchestrator, API, Workers, etc.) |
| **MetricsCollector** | • Collects technical and domain metrics<br>• Prometheus-style metrics<br>• Custom metrics | ← Orchestrator, Workers, API Gateway, Results Store |
| **MonitoringDashboard** | • UI for browsing metrics<br>• Custom dashboards<br>• Query interface | ↔ Administrator, Researchers |
| **AlertingEngine** | • Defining alert rules<br>• Notification delivery<br>• Escalation policies | ← Metrics/LogCollector<br>→ External channels (email, Slack) |

---

## Related Documents

- **Previous level**: [Containers (C4-2)](c2-containers.md)
- **Next level**: [Code (C4-4)](c4-code.md)
- **Context**: [Context (C4-1)](c1-context.md)
- **Requirements**: [Functional Requirements](../requirements/functional-requirements.md), [Use Cases](../requirements/use-cases.md)
- **Deployment**: [Deployment Guide](../operations/deployment-guide.md)
- **Design decisions**: [Design Decisions](../design/design-decisions.md)
