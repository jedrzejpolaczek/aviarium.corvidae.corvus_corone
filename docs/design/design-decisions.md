# Design Decisions

> **Architectural Decision Records (ADR) for HPO Benchmarking Platform system**

---

## ADR Format

Each architectural decision is documented in standard format:

- **Status:** Proposed | Accepted | Deprecated | Superseded
- **Context:** Situation requiring decision
- **Decision:** What was decided
- **Consequences:** Positive and negative effects of decision

---

## ADR-001: Microservices Architecture

**Status:** Accepted  
**Date:** 2024-01-15  
**Authors:** System Architecture Team

### Context

HPO benchmarking system requires:
- Flexible scaling of different components (API, Workers, Tracking)
- Independent deployment for different teams
- Support for different programming languages (Python algorithms, Web UI)
- Error isolation between components
- A/B testing capabilities for new algorithms

### Decision

We adopt microservices architecture with the following services:
1. **API Gateway** - routing and authentication
2. **Experiment Orchestrator** - experiment management
3. **Worker Pool** - HPO algorithm execution
4. **Experiment Tracking** - storing results
5. **Plugin Manager** - algorithm management
6. **Report Generator** - report creation
7. **Web UI** - user interface

### Consequences

**Positive:**
- Independent scaling of each service
- Technology diversity (Python for algorithms, JavaScript for UI)
- Fault isolation - failure of one service doesn't stop the entire system
- Easier testing and deployment
- Team autonomy - teams can work independently

**Negative:**
- Increased operational complexity
- Network latency between services
- Distributed system challenges (consistency, monitoring)
- More moving parts to manage

### Implementation Notes

```yaml
Service Communication:
  - Synchronous: REST APIs for user-facing operations
  - Asynchronous: Message broker (RabbitMQ primary, Redis fallback) for long-running tasks
  - Event-driven: Pub/sub for system events

Data Management:
  - Database per service pattern
  - Shared read-only reference data via API
  - Event sourcing for audit trail

Message Broker Decision:
  - PC deployment: RabbitMQ (single node)
  - Cloud deployment: Managed RabbitMQ or Redis Streams
  - Rationale: RabbitMQ for reliability, Redis for simplicity
```

---

## ADR-002: Plugin-based Algorithm Architecture

**Status:** Accepted  
**Date:** 2024-01-20  
**Authors:** Algorithm Integration Team

### Context

System must support:
- Rapid addition of new HPO algorithms
- Different programming languages (Python, R, Julia, Java)
- Different dependencies and environment requirements
- Isolation between algorithms (security, resource)
- Algorithm versioning
- Community contributions

### Decision

We implement plugin-based architecture with the following elements:

1. **Plugin Interface:** Standard contract for all algorithms
2. **Container Isolation:** Each algorithm in separate Docker container
3. **Plugin Registry:** Service discovery for available algorithms
4. **Resource Sandbox:** CPU/memory/time limits per plugin
5. **Version Management:** Semantic versioning for algorithms

### Plugin Interface Specification

```python
# Standard plugin interface
class HPOAlgorithm(ABC):
    \"\"\"Base interface for all HPO algorithms.\"\"\"
    
    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> None:
        \"\"\"Initialize algorithm with configuration.\"\"\"
        pass
    
    @abstractmethod  
    def suggest(self, n_suggestions: int = 1) -> List[Dict[str, Any]]:
        \"\"\"Suggest next parameter configurations to evaluate.\"\"\"
        pass
    
    @abstractmethod
    def observe(self, suggestions: List[Dict[str, Any]], 
                      objectives: List[float]) -> None:
        \"\"\"Update algorithm with evaluation results.\"\"\"
        pass
    
    @abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        \"\"\"Return algorithm metadata and capabilities.\"\"\"
        pass
```

### Container Specification

```dockerfile
# Algorithm container template
FROM python:3.9-slim

# Install algorithm dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy algorithm implementation
COPY algorithm/ /opt/algorithm/
WORKDIR /opt/algorithm

# Standard entrypoint
ENTRYPOINT [\"python\", \"main.py\"]

# Metadata labels
LABEL algorithm.name=\"gaussian_process_bo\"
LABEL algorithm.version=\"1.2.0\"
LABEL algorithm.author=\"research_team\"
LABEL algorithm.requires_gpu=\"false\"
```

### Consequences

**Positive:**
- Easy addition of new algorithms
- Strong isolation between algorithms
- Support for different programming languages
- Versioning and rollback capabilities
- Community ecosystem potential
- Security through container isolation

**Negative:**
- Container overhead (startup time, resource usage)
- More complex deployment pipeline
- Network communication overhead
- Container registry management
- Potential performance impact

---

## ADR-003: Event-Driven Architecture for Experiment Tracking

**Status:** Accepted  
**Date:** 2024-02-01  
**Authors:** Data Architecture Team

### Context

Experiment tracking requires:
- Real-time updates on experiment status
- Scalable data ingestion (thousands of runs simultaneously)
- Integration with different components (UI, monitoring, reporting)
- Audit trail of all operations
- Support for batch and streaming analytics
- Data consistency between services

### Decision

We implement event-driven architecture with:

1. **Event Store:** Central repository of all system events
2. **Event Bus:** Message broker for event distribution
3. **Event Projections:** Materialized views for different use cases
4. **CQRS Pattern:** Separated read/write models

### Event Schema

```json
{
  "event_id": "uuid",
  "event_type": "ExperimentStarted|RunCompleted|RunFailed",
  "timestamp": "2024-01-15T10:30:00Z",
  "source_service": "orchestrator",
  "payload": {
    "experiment_id": "uuid",
    "run_id": "uuid", 
    "algorithm_id": "gaussian_process_bo",
    "benchmark_id": "hartmann6d",
    "metrics": {...}
  }
}
```

### Consequences

**Positive:**
- Real-time experiment tracking
- Audit trail of all operations
- Scalable data ingestion
- Loose coupling between components
- Support for analytics and reporting

**Negative:**
- Eventual consistency challenges
- Complex error handling in distributed events
- Storage overhead for event history
- Learning curve for event-driven patterns

---

## ADR-004: Database Strategy (PostgreSQL + ClickHouse)

**Status:** Accepted  
**Data:** 2024-02-10  
**Authors:** Data Architecture Team

### Context

HPO benchmarking system has diverse data requirements:
- OLTP operations: user management, experiment configuration, system metadata
- OLAP analytics: time-series metrics, aggregated statistics, reporting
- Real-time ingestion: thousands of metrics per second during experiments
- Long-term storage: historical data for research reproducibility
- Complex queries: multi-dimensional analysis, statistical calculations

### Decision

Adapt dual-database strategy:

1. **PostgreSQL (Primary OLTP):**
   - Experiments, algorithms, benchmarks, users
   - Transactional consistency for critical operations
   - Rich ecosystem (backup, monitoring, extensions)

2. **ClickHouse (Analytics OLAP):**
   - Time-series metrics, logs, events
   - Column-oriented storage for analytics
   - High-performance aggregations

3. **Data Pipeline:**
   - Real-time streaming PostgreSQL → ClickHouse
   - Change Data Capture (CDC) via Debezium
   - Event-driven synchronization

### Implementation Architecture

```yaml
Data Flow:
  Write Path:
    - Applications → PostgreSQL (primary writes)
    - Event Bus → ClickHouse (metrics, events)
    
  Read Path:
    - Web UI → PostgreSQL (metadata, configuration)
    - Analytics → ClickHouse (metrics, reporting)
    - Reports → Both (join across systems)

Synchronization:
  - CDC: PostgreSQL → Kafka → ClickHouse
  - Event sourcing for audit trail
  - Eventual consistency model
```

### Consequences

**Positive:**
- Optimal performance for different workloads
- Scalable analytics without impact on OLTP
- Rich SQL ecosystem for both systems
- Mature backup and disaster recovery

**Negative:**
- Operational complexity (2 databases)
- Eventual consistency between systems
- Data synchronization challenges
- Increased infrastructure costs

---

## ADR-005: Container Security Strategy

**Status:** Accepted  
**Data:** 2024-02-15  
**Authors:** Security Architecture Team

### Context

Plugin-based architecture requires strong security isolation:
- User-submitted code in HPO plugins
- Potential malicious algorithms
- Resource exhaustion attacks
- Data exfiltration risks
- Compliance requirements (SOC2, GDPR)

### Decision

We implement multi-layered container security:

1. **Container Sandboxing:**
   - gVisor/Kata Containers for strong isolation
   - Non-root containers (USER directive)
   - Read-only root filesystem
   - Minimal base images (distroless)

2. **Resource Limiting:**
   - CPU/Memory/Disk quotas per plugin
   - Network policies (deny egress by default)
   - Execution timeouts
   - File system size limits

3. **Runtime Security:**
   - Seccomp profiles blocking dangerous syscalls
   - AppArmor/SELinux policies
   - Runtime monitoring (Falco)
   - Process monitoring

4. **Image Security:**
   - Vulnerability scanning in CI/CD
   - Image signing and verification
   - Base image hardening
   - Regular security updates

### Security Policies

```yaml
Plugin Container Policy:
  Base Image: gcr.io/distroless/python3
  User: 1000:1000 (non-root)
  Filesystem: read-only except /tmp
  Network: deny all egress, allow API calls only
  Resources:
    CPU: 1000m max
    Memory: 2Gi max  
    Disk: 1Gi max
    Runtime: 3600s max
  
Syscalls Blocked:
  - mount, umount
  - setuid, setgid
  - ptrace, personality
  - reboot, syslog
```

### Consequences

**Positive:**
- Strong isolation between plugins
- Defense in depth security model
- Compliance with security standards
- Audit trail of actions

**Negative:**
- Performance overhead (gVisor ~5-10%)
- Complexity in debugging
- Limitations for some algorithms
- Operational overhead

---

## ADR-006: Monitoring and Observability Stack

**Status:** Accepted  
**Data:** 2024-02-20  
**Authors:** SRE Team

### Context

HPO benchmarking platform requires comprehensive observability:
- Distributed system monitoring (microservices)
- Long-running experiment tracking (hours/days)
- Performance debugging (slow algorithms)
- Business metrics (algorithm success rates)
- Cost optimization (cloud resources)
- SLA monitoring (availability, latency)

### Decision

We adopt standard observability stack with 3 pillars:

1. **Metrics (Prometheus Ecosystem):**
   - Prometheus server for metrics collection
   - Node exporter for infrastructure metrics
   - Custom application metrics (business KPIs)
   - Long-term storage in Thanos/Cortex

2. **Logging (ELK Stack):**
   - Elasticsearch for log storage and indexing
   - Logstash for log processing and enrichment
   - Kibana for log analysis and visualization
   - Fluentd for log shipping

3. **Tracing (Jaeger):**
   - Distributed tracing for request flow
   - Performance bottleneck identification
   - Error correlation across services
   - OpenTelemetry instrumentation

4. **Visualization (Grafana):**
   - Unified dashboards for all data sources
   - Alerting and notification management
   - Custom business dashboards
   - SLA monitoring

### Architecture

```yaml
Data Collection:
  - Applications → Prometheus/Jaeger/Logs
  - Infrastructure → Node exporter/cAdvisor
  - Events → Event bus → Metrics pipeline
  
Storage:
  - Metrics: Prometheus (short-term) + Thanos (long-term)
  - Logs: Elasticsearch cluster
  - Traces: Jaeger backend
  
Visualization:
  - Grafana dashboards
  - Kibana for log analysis
  - Jaeger UI for tracing
  
Alerting:
  - Prometheus AlertManager
  - Grafana alerts
  - PagerDuty/Slack integration
```

### Key Metrics

```yaml
Infrastructure:
  - node_cpu_usage_percent
  - node_memory_usage_bytes
  - container_cpu_usage_seconds_total
  
Application:
  - http_request_duration_seconds
  - http_requests_total
  - database_connection_pool_size
  
Business:
  - corvus_experiments_total
  - corvus_algorithm_success_rate
  - corvus_benchmark_execution_time
  - corvus_cost_per_experiment
```

### Consequences

**Positive:**
- Full visibility in distributed system
- Proactive issue detection
- Performance optimization data
- Business intelligence metrics
- Mature, proven technologies

**Negative:**
- High resource consumption (10-15% overhead)
- Complex setup and maintenance
- Data retention costs
- Learning curve for team

---

## ADR-007: Authentication and Authorization Strategy

**Status:** Accepted  
**Data:** 2024-02-25  
**Authors:** Security Team

### Context

HPO benchmarking system needs robust auth system:
- Multi-tenant access (different research organizations)
- Role-based permissions (researcher, admin, plugin-author)
- API access for external systems
- Plugin security (sandbox user algorithms)
- Compliance requirements (audit trail, MFA)
- Integration with existing identity providers

### Decision

We implement OAuth2/OIDC-based authentication with RBAC:

1. **Authentication:**
   - OAuth2/OIDC for Web UI (Authorization Code flow)
   - JWT tokens for API access
   - API keys for programmatic access
   - MFA for privileged operations

2. **Authorization (RBAC):**
   - Role-based access control with fine-grained permissions
   - Hierarchical roles: `admin` > `plugin-author` > `researcher` > `viewer`
   - Resource-level permissions (own experiments vs all experiments)
   - Plugin approval workflow

3. **Identity Providers:**
   - Built-in IdP for PC deployment (local accounts)
   - External IdP integration for enterprise (SAML, OIDC)
   - Service-to-service authentication (mTLS)

### Role Definitions

```yaml
Roles:
  viewer:
    permissions:
      - read:public_experiments
      - read:public_algorithms
      - read:benchmarks
      
  researcher:
    inherits: viewer
    permissions:
      - create:experiments
      - read:own_experiments
      - update:own_experiments
      - export:own_results
      
  plugin-author:
    inherits: researcher  
    permissions:
      - create:plugins
      - update:own_plugins
      - read:plugin_metrics
      
  admin:
    inherits: plugin-author
    permissions:
      - manage:users
      - approve:plugins
      - manage:benchmarks
      - read:all_experiments
      - manage:system_config
```

### Token Strategy

```yaml
JWT Tokens:
  Access Token:
    TTL: 15 minutes
    Claims: [sub, roles, permissions, org_id]
    
  Refresh Token:
    TTL: 30 days  
    Secure storage: httpOnly cookie
    
  API Keys:
    Long-lived credentials
    Scoped permissions
    Rate limited
```

### Consequences

**Positive:**
- Standards-based authentication (OAuth2/OIDC)
- Fine-grained authorization control
- Scalable for multi-tenant usage
- External IdP integration capability
- Audit trail for compliance

**Negative:**
- Additional complexity in development
- Token management overhead
- Potential single point of failure
- Learning curve for developers

---

## ADR-008: Plugin SDK Architecture

**Status:** Accepted  
**Data:** 2024-03-01  
**Authors:** Algorithm Integration Team

### Context

Plugin system must be:
- Easy to use for algorithm developers
- Language agnostic (Python, R, Julia, Java)
- Secure and isolated
- Performant for compute-intensive algorithms
- Extensible for future algorithm types
- Well documented with examples

### Decision

We implement container-based plugin SDK with standardized interface:

1. **Plugin Interface:**
   - Abstract base classes for each language
   - Standardized lifecycle: init → suggest → observe → finalize
   - Type-safe parameter definitions
   - Metadata specification (requirements, capabilities)

2. **Container Runtime:**
   - Docker containers for isolation
   - Standard base images per language
   - Resource limits and monitoring
   - Health checks and crash recovery

3. **Communication Protocol:**
   - gRPC for high-performance communication
   - JSON-RPC as fallback
   - Streaming for real-time metrics
   - Async message patterns

4. **SDK Components:**
   - Code generation tooling
   - Local testing framework
   - Performance profiling tools
   - Documentation generator

### Plugin Lifecycle

```yaml
Plugin Lifecycle:
  Development:
    1. corvus-cli init algorithm --lang python
    2. Implement IAlgorithmPlugin interface
    3. corvus-cli test local --dataset iris
    4. corvus-cli package --build
    
  Registration:  
    5. corvus-cli register --package algorithm.tar.gz
    6. Automatic security scanning
    7. Admin approval workflow
    8. Publication in registry
    
  Execution:
    9. Container instantiation
    10. Initialization with config
    11. Suggest/observe loop
    12. Results collection
    13. Container cleanup
```

### Interface Definition

```python
# Python SDK example
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class HPOAlgorithm(ABC):
    
    @abstractmethod
    def initialize(self, 
                  config_space: Dict[str, Any],
                  seed: int,
                  resources: ResourceLimits) -> None:
        """Initialize algorithm with problem definition."""
        pass
    
    @abstractmethod  
    def suggest(self, n_suggestions: int = 1) -> List[Dict[str, Any]]:
        """Generate parameter configurations to evaluate."""
        pass
    
    @abstractmethod
    def observe(self, 
               suggestions: List[Dict[str, Any]], 
               objectives: List[float],
               metadata: Optional[Dict[str, Any]] = None) -> None:
        """Update algorithm with evaluation results."""
        pass
    
    @abstractmethod
    def get_metadata(self) -> AlgorithmMetadata:
        """Return algorithm capabilities and requirements."""
        pass
```

### Consequences

**Positive:**
- Easy algorithm development and integration
- Strong security isolation
- Language flexibility
- Standardized testing and validation
- Community ecosystem potential

**Negative:**
- Container overhead (startup latency)
- Complex debugging across container boundary
- Network serialization costs
- Platform-specific container issues

---

## Summary ADR Status

| ADR | Title | Status | Key For |
|-----|-------|---------|--------------|
| ADR-001 | Microservices Architecture | ✅ Accepted | General Architecture |
| ADR-002 | Plugin-based Algorithm Architecture | ✅ Accepted | Extensibility |
| ADR-003 | Event-Driven Architecture | ✅ Accepted | Experiment Tracking |
| ADR-004 | Database Strategy | ✅ Accepted | Data Management |
| ADR-005 | Container Security Strategy | ✅ Accepted | Security, Plugin Isolation |
| ADR-006 | Monitoring Stack | ✅ Accepted | Observability |
| ADR-007 | Authentication/Authorization | ✅ Accepted | Security, Multi-tenancy |
| ADR-008 | Plugin SDK Architecture | ✅ Accepted | Developer Experience |

---

---

## ADR-009: Cost Optimization Strategy

**Status:** Accepted  
**Data:** 2024-03-05  
**Authors:** FinOps Team

### Context

HPO benchmarking can be expensive, especially in cloud:
- Long-running experiments (hours/days)
- Compute-intensive algorithms (CPU/GPU)
- Large dataset storage and transfer
- Multi-region replication for DR
- Operational overhead (monitoring, backup)

### Decision

We implement multi-layer cost optimization:

1. **Intelligent Auto-scaling:**
   - Predictive scaling based on queue length and historical patterns
   - Spot instances for non-critical workloads
   - Reserved instances for baseline capacity
   - Right-sizing recommendations based on utilization metrics

2. **Data Lifecycle Management:**
   - Automated tiering: Hot → Warm → Cold → Archive
   - Compression and deduplication for artifacts
   - Intelligent caching strategies
   - Cost-aware data retention policies

3. **Resource Optimization:**
   - Algorithm-specific resource profiles
   - Container resource right-sizing
   - Shared GPU pools for compatible algorithms
   - Network optimization (data locality)

### Implementation Strategy

```yaml
Auto-scaling Rules:
  Scale Up Triggers:
    - Queue length >10 jobs for >5min
    - CPU utilization >80% for >10min
    - Memory pressure >85%
    
  Scale Down Triggers:  
    - Queue length <3 jobs for >15min
    - CPU utilization <30% for >20min
    - After completion of large experiments

Instance Strategy:
  Baseline: Reserved instances (30% capacity)
  Burst: On-demand instances (50% capacity)  
  Best-effort: Spot instances (20% capacity)
  
Data Tiering:
  Hot (SSD): Active experiments (7 days)
  Warm (SSD): Recent results (30 days)
  Cold (HDD): Historical data (1 year)
  Archive (Glacier): Long-term storage (7+ years)
```

### Cost Monitoring

```yaml
KPIs:
  - Cost per experiment execution
  - Cost per evaluation (algorithm run)
  - Storage cost per TB per month
  - Compute cost per CPU-hour
  - Network cost per GB transferred

Budgets:
  - Monthly budget alerts at 80%, 90%, 100%
  - Cost allocation by team/project
  - Chargeback reporting
  - ROI analysis per algorithm/benchmark
```

### Consequences

**Positive:**
- 30-50% cost reduction in cloud deployments
- Predictable cost structure
- Resource waste elimination
- Better ROI visibility

**Negative:**
- Complexity in resource management
- Potential performance impact (spot interruptions)
- Learning curve for cost optimization

---

## ADR-010: Disaster Recovery Strategy

**Status:** Accepted  
**Data:** 2024-03-10  
**Authors:** Infrastructure Team

### Context

Research data and experiment results are critical business assets:
- Years of research work
- Irreproducible experimental conditions
- Compliance requirements (audit trails)
- Business continuity for research teams
- Reputation risk with data loss

### Decision

We implement comprehensive DR strategy with different protection tiers:

1. **Tier 1 - Critical Data (RPO: 15min, RTO: 1h):**
   - Experiment metadata and configurations
   - User accounts and permissions
   - System configuration
   - Synchronous cross-region replication

2. **Tier 2 - Important Data (RPO: 1h, RTO: 4h):**
   - Experiment results and metrics
   - Algorithm implementations
   - Benchmark definitions
   - Asynchronous replication with frequent snapshots

3. **Tier 3 - Bulk Data (RPO: 24h, RTO: 24h):**
   - Large artifacts (models, datasets)
   - Historical logs
   - Archive data
   - Weekly backups with cross-region copy

### Implementation Architecture

```yaml
Backup Strategy:
  PostgreSQL:
    - Continuous WAL archiving
    - Daily full backups
    - Point-in-time recovery capability
    - Cross-region backup replication
    
  Object Storage:
    - Cross-region replication (99.999999999% durability)
    - Versioning enabled
    - Object lifecycle policies
    - Immutable backups (Object Lock)
    
  Application State:
    - GitOps approach (infrastructure as code)
    - Configuration management in version control
    - Container image registry replication
    - Secrets backup in encrypted vault

Failover Procedures:
  Automatic:
    - Database failover (30s detection + 2min switchover)
    - Application traffic routing
    - DNS failover
    
  Manual:
    - Cross-region infrastructure activation
    - Data consistency verification
    - Application health validation
```

### Recovery Testing

```yaml
Testing Schedule:
  Monthly: Backup integrity verification
  Quarterly: Partial failover simulation
  Bi-annually: Full DR drill
  
Test Scenarios:
  - Primary database failure
  - Complete region failure
  - Ransomware/corruption scenario
  - Extended network partition
  
Success Criteria:
  - RTO/RPO targets met
  - Data integrity verified
  - All critical functions restored
  - Documentation updated
```

### Consequences

**Positive:**
- Research data protection
- Business continuity assurance
- Compliance readiness
- Confidence in system reliability

**Negative:**
- 20-30% increase in infrastructure costs
- Operational complexity
- Regular testing overhead

---

## ADR-011: Performance Testing Strategy

**Status:** Accepted  
**Data:** 2024-03-15  
**Authors:** QA Performance Team

### Context

HPO benchmarking system has unique performance characteristics:
- Highly variable workloads (different algorithms, different budgets)
- Long-running operations (experiments run for hours/days)
- Resource-intensive algorithms
- Multi-tenant usage patterns
- Critical for research productivity

### Decision

We implement comprehensive performance testing strategy:

1. **Baseline Performance Testing:**
   - Load testing for API endpoints
   - Stress testing for database operations
   - Volume testing for metrics ingestion
   - Endurance testing for long-running experiments

2. **Algorithm-Specific Testing:**
   - Performance profiling per algorithm type
   - Resource utilization benchmarks
   - Scalability testing (1-100 concurrent algorithms)
   - Memory leak detection for long-running processes

3. **End-to-End Testing:**
   - Realistic experiment simulation
   - Multi-user concurrent testing
   - Cross-component performance impact
   - Failure scenario testing

### Testing Framework

```yaml
Load Testing (API):
  Tools: K6, Artillery
  Test Scenarios:
    - Normal load: 100 concurrent users
    - Peak load: 500 concurrent users  
    - Stress load: 1000+ concurrent users
    
  Key Metrics:
    - Response time (p50, p95, p99)
    - Throughput (requests/second)
    - Error rate (<1% target)
    - Resource utilization

Algorithm Performance:
  Tools: py-spy, memory_profiler, cProfile
  Metrics:
    - CPU utilization per evaluation
    - Memory usage patterns
    - I/O operations
    - Network calls
    
Database Performance:
  Tools: pgbench, pg_stat_statements
  Tests:
    - Connection pool stress
    - Query performance under load
    - Write throughput testing
    - Lock contention analysis
```

### Performance Baselines

```yaml
API Response Times:
  GET /experiments: p95 <300ms, p99 <500ms
  POST /experiments: p95 <500ms, p99 <1000ms
  GET /experiments/{id}/runs: p95 <400ms, p99 <800ms
  POST /runs/{id}/metrics: p95 <100ms, p99 <200ms

Worker Performance:
  Algorithm startup: <30s for complex algorithms
  Throughput: 10-500 evaluations/hour (algorithm-dependent)
  Memory: <2GB per active algorithm
  CPU: 70-90% utilization target

Database Performance:
  Metrics ingestion: 1000 metrics/second sustained
  Query response: <200ms for dashboard queries
  Concurrent connections: 100+ without degradation
  Storage growth: <10GB per 100k evaluations
```

### Continuous Performance Monitoring

```yaml
CI/CD Integration:
  - Performance regression testing per PR
  - Automated performance benchmarks
  - Performance budgets enforcement
  - Trend analysis and alerting

Production Monitoring:
  - Real-time performance dashboards
  - SLA compliance tracking
  - Anomaly detection
  - Capacity planning metrics
```

### Consequences

**Positive:**
- Predictable system performance
- Early regression detection
- Capacity planning data
- User experience optimization

**Negative:**
- Significant testing infrastructure cost
- Maintenance overhead
- Expertise requirements

---

## ADR-012: Documentation Strategy

**Status:** Accepted  
**Data:** 2024-03-20  
**Authors:** Documentation Team

### Context

Documentation is critical for adoption and maintenance:
- Multiple audiences (developers, researchers, admins)
- Rapidly evolving system
- Complex domain knowledge (HPO, benchmarking)
- Open source community contributions
- Compliance and audit requirements

### Decision

We implement docs-as-code strategy with automated tooling:

1. **Documentation Architecture:**
   - Structured documentation (C4 model approach)
   - Living documentation (auto-generated from code)
   - Multi-format publishing (web, PDF, mobile)
   - Internationalization support

2. **Content Strategy:**
   - Layered documentation (overview → details → implementation)
   - Task-oriented user guides
   - API documentation auto-generation
   - Interactive tutorials and examples

3. **Maintenance Strategy:**
   - Documentation in same repo as code
   - Automated testing documentation examples
   - Review process for documentation changes
   - Analytics and user feedback integration

### Implementation Framework

```yaml
Documentation Stack:
  Primary: Markdown in Git (source of truth)
  Generation: MkDocs/GitBook/Sphinx
  API Docs: OpenAPI/Swagger auto-generation
  Diagrams: Mermaid, PlantUML (as code)
  
Publishing:
  Web: Static site generation
  PDF: Automated generation for offline use
  Mobile: Progressive web app
  
Quality Assurance:
  - Link checking automation
  - Code example testing
  - Screenshot automation
  - Accessibility compliance
```

### Documentation Structure

```yaml
User Documentation:
  Getting Started:
    - Quick start guide (15 minutes)
    - Installation tutorial
    - First experiment walkthrough
    
  User Guides:
    - Experiment design best practices
    - Algorithm selection guide
    - Results analysis tutorial
    - Troubleshooting guide
    
  Reference:
    - API documentation (auto-generated)
    - Configuration reference
    - CLI command reference
    - Error codes reference

Developer Documentation:
  Architecture:
    - System overview (C4 model)
    - ADR documentation
    - Database schema
    - API specifications
    
  Development:
    - Setup development environment
    - Coding standards and guidelines
    - Testing procedures
    - Deployment procedures
    
  Plugin Development:
    - SDK documentation
    - Plugin examples
    - Security guidelines
    - Publishing procedure
```

### Content Maintenance

```yaml
Review Process:
  - Documentation PR reviews
  - Technical accuracy validation
  - User experience testing
  - Regular content audits

Metrics & Analytics:
  - Page views and user paths
  - Search queries analysis
  - User feedback collection
  - Documentation effectiveness metrics

Update Triggers:
  - Code changes → API docs update
  - Feature releases → user guide updates
  - Bug fixes → troubleshooting updates
  - Architecture changes → developer docs update
```

### Consequences

**Positive:**
- Reduced support burden
- Faster developer onboarding
- Better user adoption
- Compliance readiness

**Negative:**
- Documentation maintenance overhead
- Tooling complexity
- Content quality management challenges

---

## Summary ADR Status (Updated)

| ADR | Title | Status | Implementation | Key For |
|-----|-------|---------|---------------|--------------|
| ADR-001 | Microservices Architecture | ✅ Accepted | Core | General Architecture |
| ADR-002 | Plugin-based Algorithm Architecture | ✅ Accepted | Core | Extensibility |
| ADR-003 | Event-Driven Architecture | ✅ Accepted | Core | Experiment Tracking |
| ADR-004 | Database Strategy | ✅ Accepted | Core | Data Management |
| ADR-005 | Container Security Strategy | ✅ Accepted | Core | Security, Plugin Isolation |
| ADR-006 | Monitoring Stack | ✅ Accepted | Core | Observability |
| ADR-007 | Authentication/Authorization | ✅ Accepted | Core | Security, Multi-tenancy |
| ADR-008 | Plugin SDK Architecture | ✅ Accepted | Core | Developer Experience |
| ADR-009 | Cost Optimization Strategy | ✅ Accepted | Phase 2 | Cloud Economics |
| ADR-010 | Disaster Recovery Strategy | ✅ Accepted | Phase 2 | Business Continuity |
| ADR-011 | Performance Testing Strategy | ✅ Accepted | Phase 2 | Quality Assurance |
| ADR-012 | Documentation Strategy | ✅ Accepted | Phase 1 | User Adoption |

---

## Related Documents

- **Requirements**: [Non-functional Requirements](../requirements/non-functional-requirements.md) - implementation RNF3, RNF4
- **Architecture**: [Containers (C4-2)](../architecture/c2-containers.md) - ADR mapping to components
- **Architecture**: [Components (C4-3)](../architecture/c3-components.md) - implementation details
- **Operations**: [Deployment Guide](../operations/deployment-guide.md) - basic configurations
- **Operations**: [Deployment Examples](../operations/deployment-examples.md) - detailed examples for all scenarios
- **Operations**: [Monitoring Guide](../operations/monitoring-guide.md) - observability stack
- **Operations**: [Performance & SLA](../operations/performance-sla.md) - benchmarks and service level agreements
- **User Guides**: [Workflows](../user-guides/workflows.md) - security in plugin development
{
  \"eventType\": \"ExperimentRunCompleted\",
  \"eventId\": \"uuid-here\",
  \"timestamp\": \"2024-02-01T10:30:00Z\",
  \"aggregateId\": \"experiment-123\",
  \"aggregateType\": \"Experiment\",
  \"version\": 1,
  \"data\": {
    \"runId\": \"run-456\",
    \"algorithmId\": \"gaussian_process_bo\",
    \"benchmarkId\": \"hartmann6d\",
    \"finalObjective\": 0.398,
    \"evaluationCount\": 150,
    \"executionTime\": 1245.67,
    \"status\": \"completed\",
    \"metadata\": {
      \"workerId\": \"worker-003\",
      \"resourceUsage\": {
        \"cpuTime\": 1200.45,
        \"memoryPeak\": 2048576,
        \"gpuTime\": 0
      }
    }
  },
  \"metadata\": {
    \"userId\": \"user-789\",
    \"correlationId\": \"correlation-abc\",
    \"source\": \"worker-service\"
  }
}
```

### Event Projections

```python
# Example projection for real-time dashboard
class ExperimentDashboardProjection:
    \"\"\"Real-time experiment status for dashboard.\"\"\"
    
    def handle_experiment_started(self, event):
        self.redis_client.hset(
            f\"experiment:{event.aggregate_id}\",
            mapping={
                \"status\": \"running\",
                \"startTime\": event.timestamp,
                \"algorithmCount\": len(event.data[\"algorithms\"]),
                \"totalRuns\": event.data[\"totalExpectedRuns\"]
            }
        )
    
    def handle_run_completed(self, event):
        experiment_key = f\"experiment:{event.aggregate_id}\"
        self.redis_client.hincrby(experiment_key, \"completedRuns\", 1)
        
        # Update best objective if better
        current_best = self.redis_client.hget(experiment_key, \"bestObjective\")
        if current_best is None or event.data[\"finalObjective\"] < float(current_best):
            self.redis_client.hset(experiment_key, \"bestObjective\", 
                                 event.data[\"finalObjective\"])

# Analytical projection for research insights
class ResearchInsightsProjection:
    \"\"\"Long-term analytical data for research.\"\"\"
    
    def handle_run_completed(self, event):
        # Store in analytical database (ClickHouse/BigQuery)
        analytical_record = {
            \"experiment_id\": event.aggregate_id,
            \"run_id\": event.data[\"runId\"],
            \"algorithm_id\": event.data[\"algorithmId\"],
            \"benchmark_id\": event.data[\"benchmarkId\"],
            \"final_objective\": event.data[\"finalObjective\"],
            \"evaluation_count\": event.data[\"evaluationCount\"],
            \"execution_time\": event.data[\"executionTime\"],
            \"completion_timestamp\": event.timestamp,
            \"convergence_curve\": event.data.get(\"convergenceCurve\", []),
            \"hyperparameters\": event.data.get(\"hyperparameters\", {}),
            \"resource_usage\": event.data.get(\"resourceUsage\", {})
        }
        
        self.analytical_db.insert(\"experiment_runs\", analytical_record)
```

### Consequences

**Positive:**
- Scalable data ingestion
- Real-time updates for UI
- Complete audit trail
- Loose coupling between components
- Easy to add new data consumers
- Better analytics capabilities

**Negative:**
- Eventual consistency challenges
- Increased system complexity
- Event schema evolution challenges
- Debugging distributed events

---

## ADR-004: Multi-Database Strategy

**Status:** Accepted  
**Data:** 2024-02-10  
**Authors:** Data Architecture Team

### Context

System has different data access patterns:
- **Transactional:** User management, experiment configuration
- **Analytical:** Performance analysis, research insights
- **Cache:** Real-time dashboard, session data
- **Time-series:** Monitoring metrics, system performance
- **Object storage:** Algorithm artifacts, large datasets
- **Search:** Algorithm discovery, benchmark search

### Decision

Adoptujemy polyglot persistence approach:

1. **PostgreSQL** - Primary transactional data
2. **ClickHouse** - Analytical workloads and historical data
3. **Redis** - Caching and real-time dashboard data
4. **InfluxDB** - Monitoring metrics and time-series data
5. **S3/MinIO** - Object storage for artifacts
6. **Elasticsearch** - Full-text search and discovery

### Database Allocation

```yaml
PostgreSQL (Primary OLTP):
  Tables:
    - users, organizations, permissions
    - experiment_definitions, algorithm_registry
    - benchmark_definitions, dataset_metadata
    - system_configuration
  
  Characteristics:
    - ACID compliance required
    - Complex relationships
    - Moderate write volume (<1000 TPS)
    - Strong consistency needs

ClickHouse (Analytics OLAP):
  Tables:
    - experiment_runs (fact table)
    - algorithm_performance_metrics
    - benchmark_results_history
    - aggregated_statistics
  
  Characteristics:
    - High insert volume (>10k TPS)
    - Complex analytical queries
    - Historical data retention
    - Column-oriented storage

Redis (Cache/Real-time):
  Data Types:
    - Session data (user sessions)
    - Real-time experiment status
    - Algorithm recommendation cache
    - Rate limiting counters
    - Pub/sub för real-time updates

InfluxDB (Monitoring):
  Measurements:
    - system_metrics (CPU, memory, disk)
    - application_metrics (request rates, latencies)
    - business_metrics (experiments/hour)
    - resource_utilization

S3/MinIO (Object Storage):
  Buckets:
    - algorithm-artifacts (code, models)
    - experiment-data (input datasets)
    - result-exports (reports, visualizations)
    - system-backups
```

### Data Synchronization Strategy

```python
# Event-driven data synchronization
class DataSynchronizer:
    \"\"\"Synchronize data between different databases.\"\"\"
    
    def handle_experiment_completed(self, event):
        # Primary data to PostgreSQL
        self.postgres.update_experiment_status(
            event.aggregate_id, \"completed\"
        )
        
        # Analytical data to ClickHouse
        self.clickhouse.insert_run_results(
            event.data[\"detailedResults\"]
        )
        
        # Cache invalidation
        self.redis.delete(f\"experiment_cache:{event.aggregate_id}\")
        
        # Search index update
        self.elasticsearch.index_experiment_results(
            event.aggregate_id, event.data[\"searchableMetadata\"]
        )

# Cross-database queries through service layer
class ExperimentService:
    \"\"\"Service layer abstracting database complexity.\"\"\"
    
    def get_experiment_summary(self, experiment_id):
        # Configuration from PostgreSQL
        config = self.postgres.get_experiment_config(experiment_id)
        
        # Performance data from ClickHouse
        performance = self.clickhouse.get_performance_summary(experiment_id)
        
        # Real-time status form Redis
        status = self.redis.get_experiment_status(experiment_id)
        
        return {
            \"configuration\": config,
            \"performance\": performance,
            \"status\": status
        }
```

### Consequences

**Positive:**
- Optimized performance per use case
- Scalability per data type
- Technology best-fit for each pattern
- Better resource utilization

**Negative:**
- Increased operational complexity
- Data consistency challenges
- Multiple backup/recovery procedures
- More technologies to maintain
- Cross-database query complexity

---

## ADR-005: Kubernetes for Container Orchestration

**Status:** Accepted  
**Data:** 2024-02-15  
**Authors:** DevOps Team

### Context

System needs:
- Dynamic scaling for worker nodes
- Service discovery and load balancing
- Rolling deployments for continuous delivery
- Resource management and quotas
- Health checking and auto-recovery
- Multi-environment support (dev/staging/prod)
- Hybrid cloud capability

### Decision

Kubernetes as primary container orchestration platform:

1. **Workload Management:** Deployments, StatefulSets, Jobs
2. **Service Mesh:** Istio for advanced networking
3. **Auto-scaling:** HPA and VPA for dynamic resource allocation
4. **Storage:** Persistent volumes for stateful services
5. **Monitoring:** Prometheus + Grafana stack
6. **GitOps:** ArgoCD for deployment automation

### Kubernetes Resource Architecture

```yaml
# Namespace organization
apiVersion: v1
kind: Namespace
metadata:
  name: corvus-system
  labels:
    istio-injection: enabled
---
# API Gateway deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-gateway
  namespace: corvus-system
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api-gateway
  template:
    metadata:
      labels:
        app: api-gateway
        version: v1
    spec:
      containers:
      - name: api-gateway
        image: corvus/api-gateway:1.2.0
        ports:
        - containerPort: 8080
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: database-credentials
              key: url
        resources:
          requests:
            memory: \"512Mi\"
            cpu: \"250m\"
          limits:
            memory: \"1Gi\"
            cpu: \"500m\"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
---
# Worker pool with auto-scaling
apiVersion: apps/v1
kind: Deployment
metadata:
  name: worker-pool
  namespace: corvus-system
spec:
  replicas: 5
  selector:
    matchLabels:
      app: worker-pool
  template:
    metadata:
      labels:
        app: worker-pool
    spec:
      containers:
      - name: worker
        image: corvus/worker:1.2.0
        resources:
          requests:
            memory: \"2Gi\"
            cpu: \"1000m\"
          limits:
            memory: \"4Gi\"
            cpu: \"2000m\"
        env:
        - name: WORKER_CONCURRENCY
          value: \"4\"
---
# Horizontal Pod Autoscaler for workers
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: worker-pool-hpa
  namespace: corvus-system
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: worker-pool
  minReplicas: 2
  maxReplicas: 50
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Pods
    pods:
      metric:
        name: queue_length
      target:
        type: AverageValue
        averageValue: \"5\"
```

### Service Mesh Configuration

```yaml
# Istio VirtualService for traffic management
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: api-gateway-vs
  namespace: corvus-system
spec:
  hosts:
  - api.corvus.local
  http:
  - match:
    - uri:
        prefix: \"/api/v1/\"
    route:
    - destination:
        host: api-gateway
        port:
          number: 8080
    timeout: 30s
    retries:
      attempts: 3
      perTryTimeout: 10s
  - match:
    - uri:
        prefix: \"/\"
    route:
    - destination:
        host: web-ui
        port:
          number: 3000
```

### Consequences

**Positive:**
- Auto-scaling capabilities
- Service discovery and load balancing
- Rolling deployments zero-downtime
- Resource efficiency and isolation
- Declarative infrastructure
- Multi-cloud portability
- Strong ecosystem

**Negative:**
- Steep learning curve
- Increased operational complexity
- Resource overhead for small workloads
- YAML configuration complexity
- Debugging challenges w distributed environment

---

## ADR-006: Asynchronous Processing with Message Queues

**Status:** Accepted  
**Data:** 2024-02-20  
**Authors:** System Integration Team

### Context

HPO experiments are characterized by:
- Long-running tasks (minutes to hours)
- Variable execution times
- High throughput requirements
- Need for load balancing
- Reliability requirements (retry logic)
- Priority-based scheduling
- Resource allocation coordination

### Decision

RabbitMQ as message broker with the following patterns:

1. **Work Queues:** Task distribution do worker pool
2. **Priority Queues:** Urgent experiments prioritization
3. **Dead Letter Queues:** Failed task handling
4. **Delayed Messages:** Scheduled experiments
5. **Topic Exchanges:** Event routing

### Queue Architecture

```python
# Queue configuration
QUEUE_CONFIG = {
    \"experiment_runs\": {
        \"routing_key\": \"experiment.run\",
        \"priority\": True,
        \"max_priority\": 10,
        \"ttl\": 86400000,  # 24 hours
        \"max_length\": 100000,
        \"dead_letter_exchange\": \"failed_experiments\"
    },
    \"algorithm_suggestions\": {
        \"routing_key\": \"algorithm.suggest\",
        \"priority\": False,
        \"ttl\": 3600000,  # 1 hour
        \"max_length\": 50000
    },
    \"report_generation\": {
        \"routing_key\": \"report.generate\",
        \"priority\": True,
        \"max_priority\": 5,
        \"ttl\": 7200000  # 2 hours
    }
}

# Message publisher
class MessagePublisher:
    def __init__(self, connection):
        self.connection = connection
        self.channel = connection.channel()
        
    def publish_experiment_run(self, experiment_config, priority=5):
        message = {
            \"experiment_id\": experiment_config[\"id\"],
            \"algorithm_id\": experiment_config[\"algorithm\"][\"id\"],
            \"benchmark_id\": experiment_config[\"benchmark\"][\"id\"],
            \"config\": experiment_config,
            \"timestamp\": datetime.utcnow().isoformat(),
            \"retry_count\": 0
        }
        
        self.channel.basic_publish(
            exchange=\"experiment_exchange\",
            routing_key=\"experiment.run\",
            body=json.dumps(message),
            properties=pika.BasicProperties(
                priority=priority,
                delivery_mode=2,  # Persistent
                correlation_id=str(uuid.uuid4()),
                timestamp=int(time.time())
            )
        )

# Message consumer with retry logic
class WorkerConsumer:
    def __init__(self, connection):
        self.connection = connection
        self.channel = connection.channel()
        self.max_retries = 3
        
    def start_consuming(self):
        self.channel.basic_qos(prefetch_count=1)  # Fair dispatch
        self.channel.basic_consume(
            queue=\"experiment_runs\",
            on_message_callback=self.process_experiment,
            auto_ack=False
        )
        self.channel.start_consuming()
    
    def process_experiment(self, channel, method, properties, body):
        try:
            message = json.loads(body)
            
            # Execute experiment
            result = self.execute_experiment(message[\"config\"])
            
            # Acknowledge successful processing
            channel.basic_ack(delivery_tag=method.delivery_tag)
            
            # Publish result
            self.publish_result(result, properties.correlation_id)
            
        except Exception as e:
            retry_count = message.get(\"retry_count\", 0)
            
            if retry_count < self.max_retries:
                # Retry with exponential backoff
                message[\"retry_count\"] = retry_count + 1
                delay = 2 ** retry_count * 1000  # milliseconds
                
                self.republish_with_delay(message, delay)
                channel.basic_ack(delivery_tag=method.delivery_tag)
            else:
                # Send to dead letter queue
                channel.basic_nack(
                    delivery_tag=method.delivery_tag,
                    requeue=False
                )
                logger.error(f\"Failed to process experiment after {self.max_retries} retries: {e}\")
```

### Message Flow Patterns

```mermaid
---
config:
  theme: redux-dark
---
flowchart TD
    UI[\"Web UI\"] --> API[\"API Gateway\"]
    API --> ORCH[\"Orchestrator\"]
    
    ORCH --> EQ[\"Experiment Queue\"]
    EQ --> W1[\"Worker 1\"]
    EQ --> W2[\"Worker 2\"]
    EQ --> W3[\"Worker N\"]
    
    W1 --> RESULT[\"Result Queue\"]
    W2 --> RESULT
    W3 --> RESULT
    
    RESULT --> TRACK[\"Tracking Service\"]
    TRACK --> DB[(\"Database\")]
    
    EQ --> DLQ[\"Dead Letter Queue\"]
    DLQ --> RETRY[\"Retry Handler\"]
    RETRY --> EQ
    
    ORCH --> SCHED[\"Scheduler Queue\"]
    SCHED --> DELAY[\"Delayed Processing\"]
    DELAY --> EQ
```

### Consequences

**Positive:**
- Scalable task processing
- Load balancing across workers
- Reliability through message persistence
- Priority-based processing
- Retry logic for failed tasks
- Decoupling between producers and consumers

**Negative:**
- Message broker dependency
- Added latency for async operations
- Message ordering challenges
- Monitoring complexity
- Potential message loss scenarios

---

## ADR-007: API Versioning Strategy

**Status:** Accepted  
**Data:** 2024-03-01  
**Authors:** API Design Team

### Context

API must support:
- Backward compatibility for existing clients
- Gradual migration path for breaking changes
- Multiple client types (Web UI, CLI, SDK)
- Third-party integrations
- Research reproducibility (stable API contracts)
- Feature experimentation (beta endpoints)

### Decision

URI-based versioning with semantic versioning:

1. **Version in URL:** `/api/v1/`, `/api/v2/`
2. **Semantic Versioning:** Major.Minor.Patch
3. **Deprecation Policy:** 12-month support window
4. **Beta Endpoints:** `/api/beta/` for experimental features
5. **Content Negotiation:** Accept headers for response format

### API Versioning Implementation

```python
# Version-aware routing
@app.route('/api/v1/experiments', methods=['POST'])
def create_experiment_v1():
    \"\"\"Legacy experiment creation API.\"\"\"
    schema = ExperimentSchemaV1()
    data = schema.load(request.json)
    
    # Convert to internal format
    internal_config = convert_v1_to_internal(data)
    experiment = experiment_service.create(internal_config)
    
    # Convert response to v1 format
    response = schema.dump(experiment)
    return jsonify(response)

@app.route('/api/v2/experiments', methods=['POST'])
def create_experiment_v2():
    \"\"\"Enhanced experiment creation with new features.\"\"\"
    schema = ExperimentSchemaV2()
    data = schema.load(request.json)
    
    experiment = experiment_service.create(data)
    response = schema.dump(experiment)
    return jsonify(response)

# Schema evolution
class ExperimentSchemaV1(Schema):
    \"\"\"Legacy schema for backward compatibility.\"\"\"
    name = fields.Str(required=True)
    algorithm = fields.Str(required=True)  # Single algorithm
    benchmark = fields.Str(required=True)  # Single benchmark
    budget = fields.Int(required=True)
    replications = fields.Int(missing=10)

class ExperimentSchemaV2(Schema):
    \"\"\"Enhanced schema with new capabilities.\"\"\"
    name = fields.Str(required=True)
    description = fields.Str(missing=\"\")
    algorithms = fields.List(fields.Dict(), required=True)  # Multiple algorithms
    benchmarks = fields.List(fields.Dict(), required=True)  # Multiple benchmarks
    resource_limits = fields.Dict(missing={})
    tags = fields.List(fields.Str(), missing=[])
    collaboration_settings = fields.Dict(missing={})

# Version detection middleware
@app.before_request
def detect_api_version():
    \"\"\"Detect API version from URL path.\"\"\"
    path_parts = request.path.split('/')
    
    if len(path_parts) >= 3 and path_parts[2].startswith('v'):
        version = path_parts[2]
        g.api_version = version
    else:
        # Default to latest stable version
        g.api_version = 'v2'
    
    # Check if version is supported
    if g.api_version not in SUPPORTED_VERSIONS:
        return jsonify({
            'error': 'Unsupported API version',
            'supported_versions': SUPPORTED_VERSIONS,
            'deprecated_versions': DEPRECATED_VERSIONS
        }), 400

# Deprecation warnings
def add_deprecation_headers(response, version):
    \"\"\"Add deprecation headers to older API versions.\"\"\"
    deprecation_info = DEPRECATION_SCHEDULE.get(version)
    
    if deprecation_info:
        response.headers['Deprecation'] = deprecation_info['deprecation_date']
        response.headers['Link'] = f'</api/{deprecation_info["replacement_version"]}/docs>; rel=\"successor-version\"'
        response.headers['Warning'] = f'299 \"API version {version} is deprecated\"'
    
    return response
```

### API Documentation Versioning

```yaml
# OpenAPI specification versioning
openapi: 3.0.3
info:
  title: Corvus Corone API
  version: 2.1.0
  description: |
    HPO Benchmarking Platform API
    
    ## Version History
    - v2.1: Added collaboration features
    - v2.0: Multi-algorithm/benchmark support
    - v1.0: Initial release (deprecated)
    
  termsOfService: https://corvus.ai/terms
  contact:
    name: API Support
    url: https://corvus.ai/support
    email: api-support@corvus.ai

servers:
  - url: https://api.corvus.ai/v2
    description: Production server (v2)
  - url: https://api.corvus.ai/v1
    description: Legacy server (v1 - deprecated)
  - url: https://api.corvus.ai/beta
    description: Beta features

# Backwards compatibility mapping
x-version-compatibility:
  v1_to_v2_mapping:
    algorithm: 
      target: algorithms[0]
      transform: \"single_to_array\"
    benchmark:
      target: benchmarks[0] 
      transform: \"single_to_array\"
    budget:
      target: benchmarks[*].budget
      transform: \"distribute_to_all\"
```

### Migration Strategy

```python
class APIMigrationService:
    \"\"\"Handle API version migrations and compatibility.\"\"\"
    
    def __init__(self):
        self.migration_rules = self._load_migration_rules()
        
    def migrate_request_v1_to_v2(self, v1_request):
        \"\"\"Migrate v1 request format to v2.\"\"\"
        
        v2_request = {
            \"name\": v1_request[\"name\"],
            \"description\": \"\",
            \"algorithms\": [
                {
                    \"id\": v1_request[\"algorithm\"],
                    \"version\": \"latest\",
                    \"config\": {}
                }
            ],
            \"benchmarks\": [
                {
                    \"id\": v1_request[\"benchmark\"],
                    \"budget\": v1_request[\"budget\"],
                    \"config\": {}
                }
            ],
            \"replications\": v1_request.get(\"replications\", 10),
            \"resource_limits\": {},
            \"tags\": [],
            \"collaboration_settings\": {\"public\": False}
        }
        
        return v2_request
    
    def migrate_response_v2_to_v1(self, v2_response):
        \"\"\"Migrate v2 response to v1 format for backward compatibility.\"\"\"
        
        v1_response = {
            \"id\": v2_response[\"id\"],
            \"name\": v2_response[\"name\"],
            \"algorithm\": v2_response[\"algorithms\"][0][\"id\"],
            \"benchmark\": v2_response[\"benchmarks\"][0][\"id\"], 
            \"budget\": v2_response[\"benchmarks\"][0][\"budget\"],
            \"replications\": v2_response[\"replications\"],
            \"status\": v2_response[\"status\"],
            \"created_at\": v2_response[\"created_at\"],
            \"results\": self._simplify_results_for_v1(v2_response[\"results\"])
        }
        
        return v1_response
```

### Consequences

**Positive:**
- Clear versioning for clients
- Backward compatibility support
- Graceful deprecation path
- Flexibility for new features
- Research reproducibility

**Negative:**
- Maintenance overhead for multiple versions
- Code complexity with version handling  
- Testing burden across versions
- Documentation complexity

---

## ADR-008: Security and Authentication Model

**Status:** Accepted  
**Data:** 2024-03-10  
**Authors:** Security Team

### Context

System requires:
- Multi-tenant organization support
- Role-based access control (RBAC)
- API key management for programmatic access
- Integration with external identity providers
- Audit logging for compliance
- Data privacy and isolation
- Algorithm IP protection

### Decision

OAuth 2.0 + JWT dengan RBAC:

1. **Authentication:** OAuth 2.0 with OIDC
2. **Authorization:** JWT tokens with role claims
3. **Multi-tenancy:** Organization-based isolation
4. **API Access:** API keys for automated clients
5. **Audit:** Comprehensive security logging

### Authentication Flow

```python
# JWT token structure
JWT_PAYLOAD = {
    \"sub\": \"user_123\",  # User ID
    \"org\": \"org_456\",   # Organization ID
    \"roles\": [\"researcher\", \"algorithm_developer\"],
    \"permissions\": [
        \"experiments:create\",
        \"experiments:read:own\",
        \"algorithms:read:public\",
        \"results:export:own\"
    ],
    \"iat\": 1647123456,
    \"exp\": 1647209856,
    \"iss\": \"corvus-auth\",
    \"aud\": \"corvus-api\"
}

# Role definitions
ROLES = {
    \"admin\": {
        \"description\": \"System administrator\",
        \"permissions\": [\"*\"]  # All permissions
    },
    \"researcher\": {
        \"description\": \"Research scientist\",
        \"permissions\": [
            \"experiments:create\",
            \"experiments:read:own\",
            \"experiments:update:own\",
            \"experiments:delete:own\",
            \"algorithms:read:public\",
            \"benchmarks:read:all\",
            \"results:read:own\",
            \"results:export:own\"
        ]
    },
    \"algorithm_developer\": {
        \"description\": \"Algorithm contributor\",
        \"permissions\": [
            \"algorithms:create\",
            \"algorithms:read:own\", 
            \"algorithms:update:own\",
            \"algorithms:publish\",
            \"experiments:read:public\"
        ]
    },
    \"viewer\": {
        \"description\": \"Read-only access\",
        \"permissions\": [
            \"experiments:read:public\",
            \"algorithms:read:public\",
            \"benchmarks:read:all\",
            \"results:read:public\"
        ]
    }
}

# Authorization middleware
class AuthorizationMiddleware:
    def __init__(self, required_permission):
        self.required_permission = required_permission
    
    def __call__(self, f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = self._extract_token(request)
            
            if not token:
                return jsonify({'error': 'Authentication required'}), 401
            
            try:
                payload = jwt.decode(token, current_app.config['JWT_SECRET'], 
                                  algorithms=['HS256'])
                
                # Check permission
                if not self._has_permission(payload, self.required_permission):
                    return jsonify({'error': 'Insufficient permissions'}), 403
                
                # Add user context
                g.current_user = payload['sub']
                g.current_org = payload['org']
                g.user_roles = payload['roles']
                
                return f(*args, **kwargs)
                
            except jwt.InvalidTokenError:
                return jsonify({'error': 'Invalid token'}), 401
        
        return decorated_function
    
    def _has_permission(self, payload, required_permission):
        user_permissions = payload.get('permissions', [])
        
        # Check direct permission
        if required_permission in user_permissions:
            return True
        
        # Check wildcard permissions
        if '*' in user_permissions:
            return True
        
        # Check pattern matching (e.g., experiments:* matches experiments:read)
        for permission in user_permissions:
            if permission.endswith('*'):
                pattern = permission[:-1]
                if required_permission.startswith(pattern):
                    return True
        
        return False

# Usage in API endpoints
@app.route('/api/v2/experiments', methods=['POST'])
@AuthorizationMiddleware('experiments:create')
def create_experiment():
    # User is authenticated and authorized
    experiment_data = request.json
    experiment_data['organization_id'] = g.current_org
    experiment_data['created_by'] = g.current_user
    
    experiment = experiment_service.create(experiment_data)
    return jsonify(experiment)
```

### Multi-tenancy Implementation

```python
class TenantIsolationMiddleware:
    \"\"\"Ensure data isolation between organizations.\"\"\"
    
    @staticmethod
    def apply_tenant_filter(query, model_class):
        \"\"\"Apply organization filter to database queries.\"\"\"
        
        if hasattr(model_class, 'organization_id'):
            return query.filter(
                model_class.organization_id == g.current_org
            )
        return query
    
    @staticmethod
    def check_resource_access(resource_id, resource_type):
        \"\"\"Check if current user can access specific resource.\"\"\"
        
        resource = db.session.query(resource_type).filter(
            resource_type.id == resource_id
        ).first()
        
        if not resource:
            raise NotFound(\"Resource not found\")
        
        # Check organization access
        if hasattr(resource, 'organization_id'):
            if resource.organization_id != g.current_org:
                raise Forbidden(\"Access denied to organization resource\")
        
        # Check visibility settings
        if hasattr(resource, 'visibility'):
            if resource.visibility == 'private' and resource.created_by != g.current_user:
                # Check if user has admin role
                if 'admin' not in g.user_roles:
                    raise Forbidden(\"Access denied to private resource\")
        
        return resource

# Database models with tenant isolation
class Experiment(db.Model):
    __tablename__ = 'experiments'
    
    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    organization_id = db.Column(db.String(36), nullable=False, index=True)
    created_by = db.Column(db.String(36), nullable=False)
    visibility = db.Column(db.Enum('private', 'organization', 'public'), 
                          default='private')
    
    # Automatically filter by organization
    @classmethod
    def query_for_org(cls, org_id):
        return cls.query.filter(cls.organization_id == org_id)
```

### API Key Management

```python
class APIKeyManager:
    \"\"\"Manage API keys for programmatic access.\"\"\"
    
    @staticmethod
    def generate_api_key(user_id, organization_id, permissions, expires_at=None):
        \"\"\"Generate new API key with specific permissions.\"\"\"
        
        key_id = str(uuid.uuid4())
        secret = secrets.token_urlsafe(32)
        
        api_key = APIKey(
            id=key_id,
            user_id=user_id,
            organization_id=organization_id,
            key_hash=hashlib.sha256(secret.encode()).hexdigest(),
            permissions=permissions,
            expires_at=expires_at,
            created_at=datetime.utcnow()
        )
        
        db.session.add(api_key)
        db.session.commit()
        
        # Return key only once (never stored in plain text)
        return f\"ck_{key_id}_{secret}\"
    
    @staticmethod
    def validate_api_key(key_string):
        \"\"\"Validate API key and return associated permissions.\"\"\"
        
        try:
            parts = key_string.split('_')
            if len(parts) != 3 or parts[0] != 'ck':
                return None
            
            key_id = parts[1]
            secret = parts[2]
            
            api_key = APIKey.query.filter(APIKey.id == key_id).first()
            if not api_key:
                return None
                
            # Verify secret
            if api_key.key_hash != hashlib.sha256(secret.encode()).hexdigest():
                return None
            
            # Check expiration
            if api_key.expires_at and api_key.expires_at < datetime.utcnow():
                return None
            
            # Update last used
            api_key.last_used_at = datetime.utcnow()
            db.session.commit()
            
            return {
                'user_id': api_key.user_id,
                'organization_id': api_key.organization_id,
                'permissions': api_key.permissions
            }
            
        except Exception:
            return None

# API key authentication
@app.before_request
def authenticate_request():
    \"\"\"Authenticate requests using JWT or API key.\"\"\"
    
    # Check for API key first
    api_key = request.headers.get('X-API-Key')
    if api_key:
        key_info = APIKeyManager.validate_api_key(api_key)
        if key_info:
            g.current_user = key_info['user_id']
            g.current_org = key_info['organization_id']
            g.auth_method = 'api_key'
            g.permissions = key_info['permissions']
            return
    
    # Fall back to JWT authentication
    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header[7:]
        try:
            payload = jwt.decode(token, current_app.config['JWT_SECRET'],
                               algorithms=['HS256'])
            g.current_user = payload['sub']
            g.current_org = payload['org']
            g.auth_method = 'jwt'
            g.permissions = payload['permissions']
        except jwt.InvalidTokenError:
            pass
```

### Consequences

**Positive:**
- Strong authentication and authorization
- Multi-tenant data isolation
- Flexible permission system
- API key support for automation
- Audit trail capabilities

**Negative:**
- Implementation complexity
- Performance overhead for permission checks
- Token management challenges
- Key rotation complexity

---

## ADR-009: Monitoring and Observability Strategy

**Status:** Accepted  
**Data:** 2024-03-15  
**Authors:** DevOps Team

### Context

System requires comprehensive observability:
- Performance monitoring across microservices
- Business metrics for research productivity
- Real-time alerting for critical issues
- Distributed tracing for debugging
- Log aggregation and analysis
- Cost monitoring for cloud resources
- User experience monitoring

### Decision

Three pillars of observability:

1. **Metrics:** Prometheus + Grafana
2. **Logging:** ELK Stack (Elasticsearch, Logstash, Kibana)
3. **Tracing:** Jaeger for distributed tracing
4. **APM:** Custom application performance monitoring
5. **Alerting:** AlertManager + PagerDuty integration

### Metrics Collection Strategy

```python
# Custom metrics for business logic
from prometheus_client import Counter, Histogram, Gauge, generate_latest

# Business metrics
experiments_created_total = Counter(
    'corvus_experiments_created_total',
    'Total number of experiments created',
    ['organization_id', 'algorithm_type', 'user_role']
)

experiment_duration_seconds = Histogram(
    'corvus_experiment_duration_seconds',
    'Time taken to complete experiments',
    ['algorithm_id', 'benchmark_category'],
    buckets=[60, 300, 900, 1800, 3600, 7200, 14400, 86400]
)

active_experiments_gauge = Gauge(
    'corvus_active_experiments',
    'Number of currently running experiments',
    ['status', 'priority']
)

# Application performance metrics  
api_request_duration = Histogram(
    'corvus_api_request_duration_seconds',
    'API request duration',
    ['method', 'endpoint', 'status_code']
)

database_query_duration = Histogram(
    'corvus_database_query_duration_seconds',
    'Database query execution time',
    ['query_type', 'table']
)

# Resource utilization metrics
worker_resource_usage = Gauge(
    'corvus_worker_resource_usage_percent',
    'Worker resource utilization',
    ['worker_id', 'resource_type']  # cpu, memory, gpu
)

# Instrumentation decorator
def monitor_performance(metric_name, labels=None):
    \"\"\"Decorator to automatically monitor function performance.\"\"\"
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                status = 'success'
                return result
            except Exception as e:
                status = 'error'
                raise
            finally:
                duration = time.time() - start_time
                
                # Record metrics
                if metric_name == 'api_request':
                    api_request_duration.labels(
                        method=request.method,
                        endpoint=request.endpoint,
                        status_code=getattr(g, 'response_status', 'unknown')
                    ).observe(duration)
                elif metric_name == 'experiment_execution':
                    experiment_duration_seconds.labels(
                        algorithm_id=kwargs.get('algorithm_id', 'unknown'),
                        benchmark_category=kwargs.get('benchmark_category', 'unknown')
                    ).observe(duration)
        
        return wrapper
    return decorator

# Usage in application code
@app.route('/api/v2/experiments', methods=['POST'])
@monitor_performance('api_request')
def create_experiment():
    # Track business metrics
    experiments_created_total.labels(
        organization_id=g.current_org,
        algorithm_type=request.json.get('algorithm_type', 'unknown'),
        user_role=g.user_roles[0] if g.user_roles else 'unknown'
    ).inc()
    
    # Application logic
    result = experiment_service.create(request.json)
    return jsonify(result)
```

### Distributed Tracing Implementation

```python
# Jaeger tracing configuration
from jaeger_client import Config
import opentracing

def init_tracer(service_name):
    \"\"\"Initialize Jaeger tracer for service.\"\"\"
    config = Config(
        config={
            'sampler': {
                'type': 'const',
                'param': 1,  # Sample all requests in development
            },
            'logging': True,
            'local_agent': {
                'reporting_host': os.getenv('JAEGER_AGENT_HOST', 'localhost'),
                'reporting_port': int(os.getenv('JAEGER_AGENT_PORT', 6831)),
            }
        },
        service_name=service_name,
        validate=True
    )
    
    return config.initialize_tracer()

# Tracing decorator
def trace_function(operation_name=None):
    \"\"\"Decorator to trace function execution.\"\"\"
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            tracer = opentracing.tracer
            
            op_name = operation_name or f\"{func.__module__}.{func.__name__}\"
            
            with tracer.start_span(op_name) as span:
                # Add function metadata
                span.set_tag('function.name', func.__name__)
                span.set_tag('function.module', func.__module__)
                
                # Add request context if available
                if hasattr(g, 'current_user'):
                    span.set_tag('user.id', g.current_user)
                    span.set_tag('organization.id', g.current_org)
                
                try:
                    result = func(*args, **kwargs)
                    span.set_tag('success', True)
                    return result
                except Exception as e:
                    span.set_tag('success', False)
                    span.set_tag('error.type', type(e).__name__)
                    span.set_tag('error.message', str(e))
                    raise
        
        return wrapper
    return decorator

# Service-to-service tracing
class TracedHTTPClient:
    \"\"\"HTTP client with automatic tracing.\"\"\"
    
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()
    
    def post(self, endpoint, data=None, **kwargs):
        tracer = opentracing.tracer
        
        with tracer.start_span(f'http_post_{endpoint}') as span:
            # Inject trace context into headers
            headers = kwargs.get('headers', {})
            tracer.inject(span, opentracing.Format.HTTP_HEADERS, headers)
            kwargs['headers'] = headers
            
            # Add span tags
            span.set_tag('http.method', 'POST')
            span.set_tag('http.url', f'{self.base_url}{endpoint}')
            
            try:
                response = self.session.post(
                    f'{self.base_url}{endpoint}',
                    json=data,
                    **kwargs
                )
                
                span.set_tag('http.status_code', response.status_code)
                
                if response.status_code >= 400:
                    span.set_tag('error', True)
                
                return response
                
            except Exception as e:
                span.set_tag('error', True)
                span.set_tag('error.message', str(e))
                raise
```

### Structured Logging

```python
import structlog

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt=\"iso\"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Enhanced logging with context
class ContextualLogger:
    \"\"\"Logger that automatically includes request context.\"\"\"
    
    def __init__(self):
        self.logger = structlog.get_logger()
    
    def _add_context(self, event_dict):
        \"\"\"Add request context to log events.\"\"\"
        if hasattr(g, 'current_user'):
            event_dict['user_id'] = g.current_user
            event_dict['organization_id'] = g.current_org
            
        if hasattr(g, 'request_id'):
            event_dict['request_id'] = g.request_id
            
        if opentracing.tracer.active_span:
            span = opentracing.tracer.active_span
            event_dict['trace_id'] = span.context.trace_id
            event_dict['span_id'] = span.context.span_id
            
        return event_dict
    
    def info(self, event, **kwargs):
        kwargs = self._add_context(kwargs)
        self.logger.info(event, **kwargs)
    
    def error(self, event, **kwargs):
        kwargs = self._add_context(kwargs)
        self.logger.error(event, **kwargs)
    
    def warning(self, event, **kwargs):
        kwargs = self._add_context(kwargs)
        self.logger.warning(event, **kwargs)

# Usage in application
contextual_logger = ContextualLogger()

@trace_function('experiment_creation')
def create_experiment(experiment_config):
    contextual_logger.info(
        \"experiment_creation_started\",
        experiment_name=experiment_config['name'],
        algorithm_count=len(experiment_config['algorithms']),
        benchmark_count=len(experiment_config['benchmarks'])
    )
    
    try:
        experiment = experiment_service.create(experiment_config)
        
        contextual_logger.info(
            \"experiment_creation_completed\",
            experiment_id=experiment.id,
            estimated_duration=experiment.estimated_duration
        )
        
        return experiment
        
    except Exception as e:
        contextual_logger.error(
            \"experiment_creation_failed\",
            error_type=type(e).__name__,
            error_message=str(e),
            experiment_config=experiment_config
        )
        raise
```

### Consequences

**Positive:**
- Comprehensive system visibility
- Proactive issue detection
- Performance optimization insights  
- Debugging capabilities through tracing
- Business intelligence from metrics

**Negative:**
- Infrastructure overhead
- Data storage costs
- Monitoring complexity
- Performance impact from instrumentation

---

## Related Documents

- **Architecture**: [Context (C4-1)](../architecture/c1-context.md), [Containers (C4-2)](../architecture/c2-containers.md), [Components (C4-3)](../architecture/c3-components.md)
- **Operations**: [Deployment Guide](../operations/deployment-guide.md), [Monitoring Guide](../operations/monitoring-guide.md)
- **Methodology**: [Benchmarking Practices](../methodology/benchmarking-practices.md)
- **Requirements**: [Functional Requirements](../requirements/functional-requirements.md), [Use Cases](../requirements/use-cases.md)
- **User Guides**: [Workflows](../user-guides/workflows.md)
