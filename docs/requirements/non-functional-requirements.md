# Non-functional Requirements

> **Non-functional requirements for the HPO Benchmarking Platform system**

---

## 📈 RNF1 – Scalability

**Requirement:** System must scale from a single PC to a cloud cluster.

**Acceptance criteria:**
- PC deployment: 1-10 users, 1-4 workers
- Cloud deployment: 100+ users, 50+ workers  
- Auto-scaling of workers based on queue length
- Horizontal scaling of all stateless services

---

## 🛡️ RNF2 – Reliability  

**Requirement:** System must be resilient to failures and provide high availability.

**Acceptance criteria:**
- Uptime ≥ 99.5% (43.8h downtime/year max)
- Graceful degradation during component failures
- Automatic retry for transient failures
- Circuit breaker patterns for external dependencies
- Health checks for all services

---

## 🔒 RNF3 – Security

**Requirement:** System must protect data and ensure secure access.

**Basic acceptance criteria:**
- Multi-tenant isolation (organization-level)
- Role-based access control (RBAC)
- API authentication (JWT + API keys)
- Algorithm sandboxing (container isolation)
- Audit logging of all operations
- Encryption in transit (HTTPS/TLS)
- Secure secret management

### RNF3.1 Security Patterns

**Authorization and authentication:**
- **Zero Trust Architecture** - every connection between services authorized
- **RBAC (Role-Based Access Control)** with granular permissions:
  - `researcher`: read experiments, create experiments, read algorithms
  - `plugin-author`: researcher + register plugins, manage own algorithms  
  - `admin`: all permissions + manage system, approve plugins
- **JWT tokens** with short TTL (15 min) + refresh tokens
- **mTLS** for service-to-service communication in K8s
- **MFA** for administrative accounts

**Plugin Security (Sandboxing):**
- **Container isolation** - each plugin in separate container
- **Resource limits** - CPU/Memory/Network/Storage quotas per plugin
- **Restricted filesystem** - read-only root, write only to /tmp
- **Network policies** - block internet access, only to system API
- **Code scanning** - static analysis during plugin registration
- **Runtime monitoring** - detection of suspicious operations (syscalls)

**Data Protection:**
- **Encryption at rest** - all data in DB and Object Storage
- **Encryption in transit** - TLS 1.3 for all HTTP connections
- **PII handling** - separate encryption of user data
- **Audit logging** - complete trail of all CRUD operations
- **Data retention policies** - automatic deletion after N years
- **GDPR compliance** - right to be forgotten, data portability

**Infrastructure Security:**
- **Network segmentation** - separate subnets for DB, applications, workers
- **WAF (Web Application Firewall)** in front of Web UI
- **DDoS protection** at load balancer level  
- **Vulnerability scanning** of container images in CI/CD
- **Security hardening** - minimal base images, non-root users
- **SIEM integration** - centralized security event logging

**Implementation (see [ADR-005: Container Security Strategy](../design/design-decisions.md#adr-005-container-security-strategy)):**
- **Container Sandboxing:** gVisor/Kata Containers for strong isolation
- **Resource Limiting:** CPU/Memory/Disk quotas per plugin (1000m CPU, 2Gi RAM, 1Gi Disk max)
- **Runtime Security:** Seccomp profiles, AppArmor/SELinux, Falco monitoring
- **Image Security:** Vulnerability scanning, image signing, distroless base images
- **Network Security:** Deny all egress by default, allow only API communication

**Additional acceptance criteria:**
- ✅ Zero privileged containers in production
- ✅ All communications encrypted (TLS 1.3+)
- ✅ Regular penetration testing (every 6 months)
- ✅ SOC2 Type II compliance for enterprise environments
- ✅ Plugin isolation verified by security audit
- ✅ gVisor/Kata isolation performance overhead <10%

---

## 👁️ RNF4 – Observability

**Requirement:** System must provide full observability for debugging and monitoring.

**Implementation (see [ADR-006: Monitoring and Observability Stack](../design/design-decisions.md#adr-006-monitoring-and-observability-stack)):**
- **Three Pillars Observability:** Metrics (Prometheus), Logs (ELK), Traces (Jaeger)
- **Unified Visualization:** Grafana dashboards with multiple data sources
- **Business Metrics:** Algorithm success rates, experiment costs, SLA monitoring
- **Long-term Storage:** Thanos for metrics retention, Elasticsearch for logs

**Acceptance criteria:**
- Structured logging (JSON, centralized in ELK)
- Metrics collection (Prometheus + custom business KPIs)
- Distributed tracing (Jaeger with OpenTelemetry)
- Real-time dashboards (Grafana with alerting)
- SLA monitoring (availability ≥99.5%, latency p95 <500ms)
- Performance profiling (CPU/Memory per algorithm)
- Monitoring overhead <15% total system resources

---

## 🔧 RNF5 – Extensibility (plugins)

**Requirement:** System must enable easy addition of new HPO algorithms.

**Acceptance criteria:**
- Plugin SDK for different languages (Python, R, Julia)
- Container-based isolation
- Plugin versioning and rollback
- Plugin discovery and registration
- Resource limits per plugin
- Plugin metadata and compatibility checking

---

## ☁️ RNF6 – Cloud-ready, PC-first

**Requirement:** PC-first architecture with easy migration to cloud.

**Acceptance criteria:**
- Docker Compose deployment for PC
- Kubernetes manifests for cloud
- Environment-agnostic configuration
- External service discovery
- Stateless services (where possible)
- Cloud storage integration (S3, GCS, Azure Blob)

---

## 🔄 RNF7 – Reproducibility

**Requirement:** All experiments must be fully reproducible.

**Acceptance criteria:**
- Deterministic random number generation
- Environment isolation (containers)
- Complete configuration capture
- Data versioning and checksums
- Algorithm versioning
- Execution environment metadata

---

## 🎨 RNF8 – Usability

**Requirement:** System must be intuitive for users with different backgrounds.

**Acceptance criteria:**
- Web UI for non-technical users
- CLI for power users
- REST API for programmatic access
- Interactive tutorials and documentation
- Error messages with actionable guidance
- Progress tracking for long-running tasks

---

## 💾 RNF9 – Backup and Disaster Recovery

**Requirement:** System must provide protection against data loss.

**Backup strategy:**

**Results Store (PostgreSQL):**
- Automatic daily snapshots with 30 day retention
- Point-in-time recovery (PITR) with WAL archiving  
- Cross-region replication for production environments
- Encrypted backups with key rotation

**Object Storage (artifacts, datasets):**
- Versioning enabled for all objects
- Cross-region replication with 99.999999999% durability
- Lifecycle policies (archiving after 1 year, deletion after 7 years)
- Immutable backups through Object Lock

**System configuration:**
- GitOps approach - all manifests/charts in git
- Encrypted backup of secrets and configuration in HashiCorp Vault
- Infrastructure as Code (Terraform) in versioned repo

**Disaster Recovery:**
- **RTO (Recovery Time Objective): 4 hours** for full restoration
- **RPO (Recovery Point Objective): 1 hour** maximum data loss  
- **Multi-region deployment** with automatic failover for critical services
- **Runbook** with recovery procedures for each component
- **Quarterly DR drills** with documented results

**Acceptance criteria:**
- ✅ Automated daily backups with integrity verification
- ✅ Successful restore test every quarter
- ✅ DR procedure documentation available 24/7
- ✅ Cross-region failover <4h RTO, <1h RPO

---

## 🚀 RNF10 – Performance

**Requirement:** System must provide appropriate performance for HPO workloads.

**Acceptance criteria:**
- API response time: P95 < 1s, P99 < 3s
- Experiment queue throughput: 1000+ jobs/hour
- Database query performance: P95 < 100ms
- UI load time: < 3s initial, < 1s subsequent
- Worker startup time: < 30s
- Resource utilization: 70-80% target

---

## 📊 Requirements vs Components Matrix

| Component | RNF1 | RNF2 | RNF3 | RNF4 | RNF5 | RNF6 | RNF7 | RNF8 | RNF9 | RNF10 |
|-----------|------|------|------|------|------|------|------|------|------|-------|
| API Gateway | ✅ | ✅ | ⭐ | ✅ | - | ✅ | - | ✅ | - | ⭐ |
| Orchestrator | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ⭐ | ✅ | ✅ | ✅ |
| Worker Pool | ⭐ | ✅ | ✅ | ✅ | ⭐ | ✅ | ⭐ | - | - | ⭐ |
| Tracking | ✅ | ✅ | ✅ | ⭐ | - | ✅ | ⭐ | ✅ | ⭐ | ✅ |
| Plugin Manager | - | ✅ | ⭐ | ✅ | ⭐ | ✅ | ⭐ | ✅ | ✅ | ✅ |
| Web UI | ✅ | ✅ | ✅ | ✅ | - | ✅ | - | ⭐ | - | ⭐ |

**Legend:**
- ⭐ = Critical requirement for component
- ✅ = Important requirement 
- - = Not applicable

---

## Related Documents

- **Requirements**: [Functional Requirements](functional-requirements.md), [Use Cases](use-cases.md)
- **Architecture**: [Context (C4-1)](../architecture/c1-context.md), [Containers (C4-2)](../architecture/c2-containers.md)
- **Operations**: [Deployment Guide](../operations/deployment-guide.md), [Monitoring Guide](../operations/monitoring-guide.md)
- **Design**: [Design Decisions](../design/design-decisions.md)
