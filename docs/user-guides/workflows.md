# Key Activities

> **Workflows and processes supporting HPO algorithm benchmarking**

---

## Activities Overview

Corvus Corone system supports research teams through defined processes and workflows that ensure effective HPO algorithm benchmarking.

### Research Activities
- **Experiment Design** - Systematic approach to benchmark planning
- **Results Analysis** - Statistical algorithm comparison  
- **Experiment Reproduction** - Ensuring result reproducibility
- **Results Publishing** - Report and documentation generation

### Technical Activities  
- **Algorithm Development** - Plugin development workflow
- **Data Management** - Dataset management and versioning
- **Experiment Monitoring** - Real-time tracking and alerting
- **Capacity Planning** - Resource scaling and optimization

### Administrative Activities
- **Governance** - Algorithm and benchmark approval
- **Backup & Recovery** - Disaster recovery procedures  
- **Security Management** - Security and audit
- **User Management** - Roles and permissions

---

## Workflow: Benchmark Experiment Design

| Benchmark Goal | Description / role in system |
|----------------|------------------------------|
| **G1 – Evaluation** | Quality assessment of individual HPO algorithms on well-defined benchmarks and metrics |
| **G2 – Comparison** | Comparison of multiple HPO algorithms (including custom ones) on the same benchmarks and metrics |
| **G3 – Sensitivity** | Sensitivity analysis of results to changes in configuration, seeds, benchmark instances and parameters | 
| **G4 – Extrapolation** | Study of HPO algorithm behavior on diverse problem instances (scalability, difficulty, size) |
| **G5 – Theory and development** | Support for developing new HPO algorithms and linking results to theory and scientific literature |

### Planning Phase

#### 1. Research Objectives Definition
```
Inputs: Research question, hypothesis
Process: 
- Define specific research questions
- Choose appropriate goals G1-G5 from benchmarking framework
- Define experiment success criteria
Outputs: Research objectives document
```

#### 2. Benchmark and Algorithm Selection
```
Inputs: Research objectives  
Process:
- Analyze catalog of available benchmarks
- Check problem representativeness
- Select algorithms for comparison
- Check algorithm-benchmark compatibility
Outputs: Experiment configuration draft
```

#### 3. Resource Planning
```
Inputs: Configuration draft
Process:
- Estimate computational requirements
- Plan experiment time budget  
- Check worker availability
- Configure retry and timeout policies
Outputs: Resource allocation plan
```

### ⚡ Execution Phase

#### 4. Configuration and Validation
```
Process Flow:
1. Use Experiment Designer UI for configuration
2. System validates configuration automatically
3. Review run plan (algorithm × benchmark × seed)
4. Approve and save experiment configuration
```

#### 5. Experiment Launch
```
Process Flow:
1. Launch experiment through Web UI
2. Orchestrator creates RunJob tasks
3. Workers fetch and execute tasks
4. Monitor progress in Tracking Dashboard
5. React to errors and anomalies
```

#### 6. Monitoring and Interventions
```
Monitoring checklist:
□ Check run status every hour
□ Monitor resource utilization  
□ React to failed run alerts
□ Check quality gates (>95% success rate)
□ Document anomalies and interventions
```

### 📊 Analysis Phase

#### 7. Results Analysis
```
Process Flow:
1. Use Comparison View UI for visualization
2. Perform statistical tests
3. Generate algorithm rankings
4. Identify patterns and insights
5. Validate results against research objectives
```

#### 8. Reproduction and Validation
```
Validation checklist:
□ Check experiment completeness (all runs)
□ Compare with baseline results (if available)
□ Perform sanity checks on results
□ Test reproducibility on sample runs
□ Document discovered issues
```

---

## Workflow: HPO Algorithm Development and Registration

### 🧩 Development Phase

#### 1. Environment Setup
```bash
# Download Corvus Corone SDK
pip install corvus-corone-sdk

# Create new algorithm project
corvus-cli init algorithm --name MyBayesianOpt --type BAYESIAN

# Setup local development environment  
corvus-cli dev setup
```

#### 2. Algorithm Implementation
```python
# Implement IAlgorithmPlugin interface
class MyBayesianOptimizer(IAlgorithmPlugin):
    def init(self, config_space, seed, resources):
        # Algorithm initialization
        pass
        
    def suggest(self, history):
        # Suggest new configurations
        pass
        
    def observe(self, config, result):
        # Update model based on result
        pass
```

#### 3. Local Testing
```bash
# Run local tests
corvus-cli test local --algorithm MyBayesianOpt --benchmark iris_classification

# Debug algorithm
corvus-cli debug --run-id local_run_123

# Profile performance
corvus-cli profile --algorithm MyBayesianOpt
```

### 📦 Registration Phase

#### 4. Package and Upload
```bash
# Create algorithm package
corvus-cli package --algorithm MyBayesianOpt --version 1.0.0

# Upload to system
corvus-cli upload --package MyBayesianOpt-1.0.0.wheel --registry production
```

#### 5. Review and Approval
```
Process Flow:
1. **Automated Security Scanning** (ADR-005):
   - Container image vulnerability scanning
   - Static code analysis
   - Dependency security checks
   - Seccomp/AppArmor policy validation
   
2. **Functional Validation:**
   - Algorithm passes automated tests
   - Performance benchmarks on standard suite
   - Resource utilization validation
   
3. **Manual Review:**
   - Administrator receives notification
   - Code review for security concerns
   - Documentation completeness check
   
4. **Approval Workflow (ADR-007):**
   - plugin-author role can submit
   - admin role must approve
   - RBAC enforcement at each step
   
5. **Publication:**
   - Approved plugin in Algorithm Registry
   - Container image in secure registry
   - Metadata update in catalogue
```

---

## Workflow: Comparative Algorithm Analysis

### 📈 Statistical Analysis Pipeline

#### 1. Data Preparation
```
Process:
- Aggregate results from multiple experiments
- Check data completeness
- Identify outliers and anomalies
- Prepare datasets for statistical tests
```

#### 2. Comparative Analysis
```
Statistical Tests Pipeline:
1. Friedman test (overall significance)
2. Nemenyi post-hoc test (pairwise comparisons)  
3. Effect size calculations (Cohen's d, Cliff's delta)
4. Confidence intervals for rankings
5. Multiple testing corrections (Bonferroni, FDR)
```

#### 3. Visualization and Reporting
```
Visualization Types:
- Box plots for distribution comparisons
- Line plots for convergence analysis  
- Critical difference diagrams for rankings
- Heatmaps for pairwise comparisons
- Radar charts for multi-metric analysis
```

---

## Monitoring and SLA

### 🎯 Service Level Objectives

| Metric | Target | Measurement | Alert Threshold |
|---------|--------|-------------|-----------------|
| **API Response Time** | 95% < 200ms, 99% < 500ms | P95, P99 latency | P95 > 300ms |
| **System Availability** | 99.9% uptime | Health check success rate | < 99.5% |
| **Experiment Success Rate** | >95% runs successful | Failed runs / Total runs | < 90% |
| **Data Durability** | 99.999999999% | Backup validation | Backup failure |

### 📊 Key Performance Indicators

#### Operational Metrics
- **Queue Depth:** RunJob queue length (target < 100, alert > 1000)
- **Worker Utilization:** CPU/Memory usage (target 70-80%, alert <50% or >90%)
- **Database Performance:** Connection pool usage (alert >80%)
- **Storage Growth:** Object Storage usage trends

#### Business Metrics  
- **Experiment Velocity:** Experiments per week
- **Algorithm Adoption:** Usage statistics per algorithm
- **User Engagement:** Active researchers per month
- **Research Impact:** Publications referencing system

### 🚨 Alerting Strategy

#### Critical Alerts (immediate response)
- System down / API unavailable
- Database connection failures
- Data corruption detected
- Security breaches

#### Warning Alerts (24h response)
- High error rates (>5%)
- Performance degradation
- Resource utilization high
- Failed experiment rate increasing

#### Info Alerts (monitoring only)
- Capacity planning triggers
- Usage pattern changes
- Successful deployments
- Backup completions

---

## Capacity Planning

### 📈 Scaling Triggers

#### Horizontal Scaling (Workers)
```yaml
Trigger: Queue depth > 100 pending jobs for > 5 minutes
Action: Scale out workers by 50%
Max Scale: 5x base capacity  
Cool-down: 10 minutes
```

#### Vertical Scaling (Database)
```yaml  
Trigger: CPU > 80% for > 10 minutes OR connection pool > 90%
Action: Upgrade instance size
Notification: Send alert to ops team
```

#### Auto-scaling (API Gateway)
```yaml
Trigger: Average response time > 300ms for > 2 minutes
Action: Add API gateway replicas
Target: Response time < 200ms
```

### 💰 Resource Estimation

#### Worker Capacity
- **1 Worker Unit:** 2 CPU cores, 4GB RAM
- **Throughput:** ~10 concurrent jobs per worker
- **Cost Model:** $0.10/hour per worker unit

#### Storage Projection
- **Database:** 1GB per 10k experiments (+indexes ~2x)
- **Object Storage:** 100MB average per run (models + logs)
- **Growth Rate:** 20% monthly increase in experiments

#### Peak Load Planning
- **Normal Load:** 100 concurrent experiments
- **Peak Load:** 3x during conference seasons (ML conferences)  
- **Budget Reserve:** Max 5x base capacity for auto-scaling

---

## Backup and Disaster Recovery

### 💾 Backup Strategy

#### Automated Backups
```yaml
Results Store (PostgreSQL):
  - Daily full snapshots (retention: 30 days)
  - Point-in-time recovery (WAL archiving)
  - Cross-region replication for production

Object Storage:
  - Versioning enabled for all objects
  - Cross-region replication (99.999999999% durability)
  - Lifecycle policies (archive after 1 year)

System Configuration:
  - GitOps approach (all manifests in git)
  - Encrypted secrets backup in HashiCorp Vault
```

#### Recovery Procedures
```yaml
RTO (Recovery Time Objective): 4 hours
RPO (Recovery Point Objective): 1 hour max data loss
Runbook: Step-by-step recovery procedures per component
Testing: Monthly disaster recovery drills
```

### 🔐 Security Operations

#### Access Management
```yaml
Authentication: OIDC/SAML integration
Authorization: RBAC with granular permissions
Audit: Complete trail of all CRUD operations
Secrets: Rotation policies (quarterly)
```

#### Infrastructure Security
```yaml
Network: Segmentation, WAF, DDoS protection
Containers: Vulnerability scanning in CI/CD
Runtime: Security monitoring, anomaly detection
Compliance: SOC 2, GDPR compliance procedures
```

---

## Related Documents

- **Architecture**: [Context (C4-1)](../architecture/c1-context.md), [Containers (C4-2)](../architecture/c2-containers.md)
- **Requirements**: [Functional Requirements](../requirements/functional-requirements.md), [Use Cases](../requirements/use-cases.md)
- **Operations**: [Deployment Guide](../operations/deployment-guide.md), [Monitoring Guide](../operations/monitoring-guide.md)
- **Methodology**: [Benchmarking Practices](../methodology/benchmarking-practices.md)
- **Design**: [Design Decisions](../design/design-decisions.md)
