# Wymagania niefunkcjonalne - Corvus Corone

> **Non-functional requirements dla systemu HPO Benchmarking Platform**

---

## 📈 RNF1 – Skalowalność

**Wymaganie:** System musi skalować się od pojedynczego PC do klastra cloudowego.

**Kryteria akceptacji:**
- PC deployment: 1-10 użytkowników, 1-4 workerów
- Cloud deployment: 100+ użytkowników, 50+ workerów  
- Auto-scaling workerów na podstawie queue length
- Horizontal scaling wszystkich bezstanowych serwisów

---

## 🛡️ RNF2 – Niezawodność  

**Wymaganie:** System musi być odporny na awarie i zapewniać wysoką dostępność.

**Kryteria akceptacji:**
- Uptime ≥ 99.5% (43.8h downtime/year max)
- Graceful degradation przy awarii części komponentów
- Automatic retry dla transient failures
- Circuit breaker patterns dla external dependencies
- Health checks dla wszystkich serwisów

---

## 🔒 RNF3 – Bezpieczeństwo

**Wymaganie:** System musi chronić dane i zapewniać bezpieczny dostęp.

**Kryteria akceptacji podstawowe:**
- Multi-tenant isolation (organization-level)
- Role-based access control (RBAC)
- API authentication (JWT + API keys)
- Algorithm sandboxing (container isolation)
- Audit logging wszystkich operacji
- Encryption in transit (HTTPS/TLS)
- Secure secret management

### RNF3.1 Security Patterns (szczegółowe)

**Autoryzacja i uwierzytelnianie:**
- **Zero Trust Architecture** - każde połączenie między serwisami autoryzowane
- **RBAC (Role-Based Access Control)** z granularnymi uprawnieniami:
  - `researcher`: read experiments, create experiments, read algorithms
  - `plugin-author`: researcher + register plugins, manage own algorithms  
  - `admin`: wszystkie uprawnienia + manage system, approve plugins
- **JWT tokens** z krótkim TTL (15 min) + refresh tokens
- **mTLS** dla komunikacji service-to-service w K8s
- **MFA** dla kont administratorskich

**Plugin Security (Sandboxing):**
- **Container isolation** - każdy plugin w oddzielnym kontenerze
- **Resource limits** - CPU/Memory/Network/Storage quotas per plugin
- **Restricted filesystem** - read-only root, write tylko do /tmp
- **Network policies** - blokada dostępu do internetu, tylko do API systemu
- **Code scanning** - static analysis podczas rejestracji pluginu
- **Runtime monitoring** - wykrywanie podejrzanych operacji (syscalls)

**Data Protection:**
- **Encryption at rest** - wszystkie dane w DB i Object Storage
- **Encryption in transit** - TLS 1.3 dla wszystkich połączeń HTTP
- **PII handling** - osobne szyfrowanie danych użytkowników
- **Audit logging** - kompletny trail wszystkich operacji CRUD
- **Data retention policies** - automatyczne usuwanie po N latach
- **GDPR compliance** - right to be forgotten, data portability

**Infrastructure Security:**
- **Network segmentation** - oddzielne subnets dla DB, aplikacji, workerów
- **WAF (Web Application Firewall)** przed Web UI
- **DDoS protection** na poziomie load balancera  
- **Vulnerability scanning** obrazów kontenerów w CI/CD
- **Security hardening** - minimal base images, non-root users
- **SIEM integration** - centralne logowanie zdarzeń bezpieczeństwa

**Implementacja (patrz [ADR-005: Container Security Strategy](../design/design-decisions.md#adr-005-container-security-strategy)):**
- **Container Sandboxing:** gVisor/Kata Containers dla strong isolation
- **Resource Limiting:** CPU/Memory/Disk quotas per plugin (1000m CPU, 2Gi RAM, 1Gi Disk max)
- **Runtime Security:** Seccomp profiles, AppArmor/SELinux, Falco monitoring
- **Image Security:** Vulnerability scanning, image signing, distroless base images
- **Network Security:** Deny all egress by default, allow only API communication

**Dodatkowe kryteria akceptacji:**
- ✅ Zero privileged containers w produkcji
- ✅ Wszystkie komunikacje szyfrowane (TLS 1.3+)
- ✅ Regular penetration testing (co 6 miesięcy)
- ✅ SOC2 Type II compliance dla środowisk enterprise
- ✅ Plugin isolation verified przez security audit
- ✅ gVisor/Kata isolation performance overhead <10%

---

## 👁️ RNF4 – Obserwowalność

**Wymaganie:** System musi zapewniać pełną observability dla debugging i monitoring.

**Implementacja (patrz [ADR-006: Monitoring and Observability Stack](../design/design-decisions.md#adr-006-monitoring-and-observability-stack)):**
- **Three Pillars Observability:** Metrics (Prometheus), Logs (ELK), Traces (Jaeger)
- **Unified Visualization:** Grafana dashboards z multiple data sources
- **Business Metrics:** Algorithm success rates, experiment costs, SLA monitoring
- **Long-term Storage:** Thanos dla metrics retention, Elasticsearch dla logs

**Kryteria akceptacji:**
- Structured logging (JSON, centralized w ELK)
- Metrics collection (Prometheus + custom business KPIs)
- Distributed tracing (Jaeger z OpenTelemetry)
- Real-time dashboards (Grafana z alerting)
- SLA monitoring (availability ≥99.5%, latency p95 <500ms)
- Performance profiling (CPU/Memory per algorithm)
- Monitoring overhead <15% total system resources

---

## 🔧 RNF5 – Rozszerzalność (pluginy)

**Wymaganie:** System musi umożliwiać łatwe dodawanie nowych algorytmów HPO.

**Kryteria akceptacji:**
- Plugin SDK dla różnych języków (Python, R, Julia)
- Container-based isolation
- Plugin versioning i rollback
- Plugin discovery i registration
- Resource limits per plugin
- Plugin metadata i compatibility checking

---

## ☁️ RNF6 – Cloud-ready, PC-first

**Wymaganie:** Architektura PC-first z łatwą migracją do cloud.

**Kryteria akceptacji:**
- Docker Compose deployment dla PC
- Kubernetes manifests dla cloud
- Environment-agnostic configuration
- External service discovery
- Stateless services (gdzie możliwe)
- Cloud storage integration (S3, GCS, Azure Blob)

---

## 🔄 RNF7 – Reprodukowalność

**Wymaganie:** Wszystkie eksperymenty muszą być w pełni reprodukowalne.

**Kryteria akceptacji:**
- Deterministic random number generation
- Environment isolation (containers)
- Complete configuration capture
- Data versioning i checksums
- Algorithm versioning
- Execution environment metadata

---

## 🎨 RNF8 – Użyteczność

**Wymaganie:** System musi być intuicyjny dla użytkowników z różnym background.

**Kryteria akceptacji:**
- Web UI dla non-technical users
- CLI dla power users
- REST API dla programmatic access
- Interactive tutorials i documentation
- Error messages z actionable guidance
- Progress tracking dla long-running tasks

---

## 💾 RNF9 – Backup i Disaster Recovery

**Wymaganie:** System musi zapewniać ochronę przed utratą danych.

**Strategia backup:**

**Results Store (PostgreSQL):**
- Automatyczne daily snapshots z retention 30 dni
- Point-in-time recovery (PITR) z WAL archiving  
- Cross-region replication dla środowisk produkcyjnych
- Encrypted backups z rotacją kluczy

**Object Storage (artefakty, datasety):**
- Versioning włączone dla wszystkich obiektów
- Cross-region replication z 99.999999999% durability
- Lifecycle policies (archiving po 1 roku, deletion po 7 latach)
- Immutable backups przez Object Lock

**Konfiguracja systemu:**
- GitOps approach - wszystkie manifesty/charts w git
- Encrypted backup secrets i konfiguracji w HashiCorp Vault
- Infrastructure as Code (Terraform) w wersjonowanym repo

**Disaster Recovery:**
- **RTO (Recovery Time Objective): 4 godziny** dla pełnego przywrócenia
- **RPO (Recovery Point Objective): 1 godzina** maksymalna utrata danych  
- **Multi-region deployment** z automatic failover dla krytycznych usług
- **Runbook** z procedurami odtwarzania dla każdego komponentu
- **Quarterly DR drills** z dokumentacją wyników

**Kryteria akceptacji:**
- ✅ Automated daily backups z weryfikacją integralności
- ✅ Successful restore test co kwartał
- ✅ Dokumentacja procedur DR dostępna 24/7
- ✅ Cross-region failover <4h RTO, <1h RPO

---

## 🚀 RNF10 – Performance

**Wymaganie:** System musi zapewniać odpowiednie performance dla workloads HPO.

**Kryteria akceptacji:**
- API response time: P95 < 1s, P99 < 3s
- Experiment queue throughput: 1000+ jobs/hour
- Database query performance: P95 < 100ms
- UI load time: < 3s initial, < 1s subsequent
- Worker startup time: < 30s
- Resource utilization: 70-80% target

---

## 📊 Macierz wymagań vs komponenty

| Komponent | RNF1 | RNF2 | RNF3 | RNF4 | RNF5 | RNF6 | RNF7 | RNF8 | RNF9 | RNF10 |
|-----------|------|------|------|------|------|------|------|------|------|-------|
| API Gateway | ✅ | ✅ | ⭐ | ✅ | - | ✅ | - | ✅ | - | ⭐ |
| Orchestrator | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ⭐ | ✅ | ✅ | ✅ |
| Worker Pool | ⭐ | ✅ | ✅ | ✅ | ⭐ | ✅ | ⭐ | - | - | ⭐ |
| Tracking | ✅ | ✅ | ✅ | ⭐ | - | ✅ | ⭐ | ✅ | ⭐ | ✅ |
| Plugin Manager | - | ✅ | ⭐ | ✅ | ⭐ | ✅ | ⭐ | ✅ | ✅ | ✅ |
| Web UI | ✅ | ✅ | ✅ | ✅ | - | ✅ | - | ⭐ | - | ⭐ |

**Legenda:**
- ⭐ = Krytyczne wymaganie dla komponentu
- ✅ = Ważne wymaganie 
- - = Nie dotyczy

---

## Powiązane dokumenty

- **Requirements**: [Functional Requirements](functional-requirements.md), [Use Cases](use-cases.md)
- **Architektura**: [Kontekst (C4-1)](../architecture/c1-context.md), [Kontenery (C4-2)](../architecture/c2-containers.md)
- **Operations**: [Deployment Guide](../operations/deployment-guide.md), [Monitoring Guide](../operations/monitoring-guide.md)
- **Design**: [Design Decisions](../design/design-decisions.md)
