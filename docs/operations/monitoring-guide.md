# Monitoring Guide

> **Comprehensive monitoring for HPO Benchmarking Platform system**

---

## Monitoring Overview

Corvus Corone monitoring system provides full observability at three levels:

### **Infrastructure Monitoring**
- System metrics (CPU, RAM, I/O, Network)
- Kubernetes cluster health (if applicable)
- Database performance and connection pools
- Message broker queue lengths

### **Application Monitoring**  
- API response times and error rates
- Worker throughput and success rates
- Experiment execution metrics
- Business KPIs (experiments/day, algorithm usage)

### **User Experience Monitoring**
- Web UI performance
- User journey analytics
- Feature usage statistics
- Error tracking

---

## Monitoring Stack

### Core Components

```mermaid
---
config:
  theme: redux-dark
---
flowchart LR
    APP[\"Applications\"] --> PROM[\"Prometheus\"]
    APP --> JAEGER[\"Jaeger\"]
    APP --> ELK[\"ELK Stack\"]
    
    PROM --> GRAFANA[\"Grafana\"]
    JAEGER --> GRAFANA
    ELK --> GRAFANA
    
    PROM --> AM[\"AlertManager\"]
    AM --> SLACK[\"Slack\"]
    AM --> EMAIL[\"Email\"]
    AM --> PAGER[\"PagerDuty\"]

    subgraph \"Data Collection\"
        PROM
        JAEGER  
        ELK
    end
    
    subgraph \"Visualization\"
        GRAFANA
    end
    
    subgraph \"Alerting\"
        AM
        SLACK
        EMAIL
        PAGER
    end
```

#### Prometheus (Metrics Collection)
- **Rol:** Time-series metryki, alerting rules
- **Port:** 9090
- **Retention:** 30 days (locally), long-term in Thanos/Cortex

#### Grafana (Visualization)  
- **Rol:** Dashboardy, wykresy, alerting UI
- **Port:** 3001 (PC), 80/443 (Cloud)
- **Datasources:** Prometheus, Jaeger, Elasticsearch

#### Jaeger (Distributed Tracing)
- **Rol:** Request tracing, performance debugging
- **Port:** 16686
- **Use case:** Debugging slow API calls, worker issues

#### ELK Stack (Logging)
- **Elasticsearch:** Log storage and indexing (3-node cluster for HA)
- **Logstash:** Log processing and transformation (JSON normalization, field extraction)
- **Kibana:** Log analysis and search UI (port 5601)
- **Fluentd:** Log shipping from containers (structured JSON output)
- **Index Strategy:** Daily indices with 30-day retention policy

---

## Metrics Collection

### Infrastructure Metrics

#### System-level metrics
```yaml
# Collected by node_exporter
Metrics:
  - node_cpu_usage_percent
  - node_memory_usage_bytes
  - node_disk_usage_bytes
  - node_network_transmit_bytes
  - node_filesystem_usage_bytes
  
Labels:
  - instance: hostname/IP
  - job: node_exporter
  - environment: production/staging/development
```

#### Container metrics (Docker/K8s)
```yaml
# Collected by cadvisor/kubelet
Metrics:
  - container_cpu_usage_seconds_total
  - container_memory_working_set_bytes
  - container_network_receive_bytes_total
  - container_fs_usage_bytes
  
Labels:
  - container: container_name
  - pod: pod_name (K8s only)
  - namespace: namespace_name (K8s only)
```

### Application Metrics

#### API Gateway metrics
```python
# Custom metrics in API Gateway
from prometheus_client import Counter, Histogram, Gauge

# Request metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

# Business metrics
active_experiments = Gauge(
    'corvus_active_experiments_total',
    'Number of currently active experiments'
)

# Usage metrics  
algorithm_usage_total = Counter(
    'corvus_algorithm_usage_total',
    'Total algorithm usage count',
    ['algorithm_id', 'algorithm_type']
)
```

#### Worker metrics
```python
# Worker-specific metrics
worker_job_duration_seconds = Histogram(
    'corvus_worker_job_duration_seconds',
    'Job execution duration in seconds',
    ['worker_id', 'algorithm_id', 'benchmark_id']
)

worker_job_status_total = Counter(
    'corvus_worker_job_status_total',
    'Job completion status count',
    ['worker_id', 'status']  # status: success, failed, timeout
)

worker_queue_length = Gauge(
    'corvus_worker_queue_length',
    'Current queue length',
    ['queue_name']
)

worker_resource_usage = Gauge(
    'corvus_worker_resource_usage_percent',
    'Worker resource utilization',
    ['worker_id', 'resource_type']  # resource_type: cpu, memory, gpu
)
```

#### Database metrics
```yaml
# PostgreSQL metrics (via postgres_exporter)
Metrics:
  - pg_stat_database_tup_inserted
  - pg_stat_database_tup_updated  
  - pg_stat_database_tup_deleted
  - pg_stat_activity_count
  - pg_stat_database_conflicts
  - pg_locks_count
  
# Connection pool metrics
  - pg_pool_active_connections
  - pg_pool_waiting_connections
  - pg_pool_max_connections
```

### Business Metrics

#### Research productivity metrics
```python
# High-level KPIs
experiments_created_total = Counter(
    'corvus_experiments_created_total',
    'Total experiments created',
    ['user_id', 'experiment_type']
)

experiments_completed_total = Counter(
    'corvus_experiments_completed_total', 
    'Total experiments completed successfully',
    ['user_id', 'duration_bucket']  # <1h, 1-4h, 4-24h, >24h
)

publications_referenced_total = Counter(
    'corvus_publications_referenced_total',
    'Publications referenced in experiments',
    ['publication_id', 'doi']
)

# User engagement
user_session_duration_seconds = Histogram(
    'corvus_user_session_duration_seconds',
    'User session duration',
    ['user_id']
)

feature_usage_total = Counter(
    'corvus_feature_usage_total',
    'Feature usage count',
    ['feature_name', 'user_role']
)
```

---

## Dashboards

### System Overview Dashboard

#### Infrastructure panel
```json
{
  \"dashboard\": {
    \"title\": \"Corvus Corone - System Overview\",
    \"panels\": [
      {
        \"title\": \"System Health\",
        \"type\": \"stat\",
        \"targets\": [
          {
            \"expr\": \"up{job='corvus-api'}\",
            \"legendFormat\": \"API Gateway\"
          },
          {
            \"expr\": \"up{job='corvus-worker'}\", 
            \"legendFormat\": \"Workers\"
          }
        ]
      },
      {
        \"title\": \"Request Rate\",
        \"type\": \"graph\",
        \"targets\": [
          {
            \"expr\": \"rate(http_requests_total[5m])\",
            \"legendFormat\": \"{{method}} {{endpoint}}\"
          }
        ]
      }
    ]
  }
}
```

#### Key panels
- **Service Health:** Up/down status of all services
- **Request Volume:** HTTP requests per second with breakdown by endpoint
- **Response Times:** P50, P95, P99 latency
- **Error Rates:** 4xx, 5xx errors as % of total requests
- **Resource Usage:** CPU, Memory, Disk usage per service

### Experiment Monitoring Dashboard

#### Experiment execution metrics
```yaml
Panels:
  - Active Experiments: Gauge showing currently running experiments
  - Experiment Queue: Length of pending experiments
  - Success Rate: % experiments completed successfully (last 24h)
  - Worker Utilization: % busy workers across the cluster
  - Algorithm Popularity: Top 10 most used algorithms
  - Benchmark Usage: Most frequently used benchmarks
```

#### Performance tracking
```yaml
Panels:
  - Average Run Duration: Mean time per algorithm run
  - Queue Wait Time: Time experiments wait before execution
  - Resource Efficiency: CPU/Memory utilization during runs
  - Throughput: Completed runs per hour/day
```

### Business Intelligence Dashboard

#### Research productivity
```yaml
Panels:
  - Experiments per Day: Time series of experiment creation
  - User Activity: Active researchers per week/month
  - Algorithm Adoption: Adoption rate of new algorithms
  - Publication Impact: Most cited publications in system
  - Research Areas: Breakdown by problem types/domains
```

#### System usage patterns
```yaml  
Panels:
  - Peak Usage Hours: Busy times during day/week
  - Geographic Usage: User distribution (if available)
  - Feature Adoption: Usage of different system features
  - Collaboration Patterns: Shared experiments/algorithms
```

---

## Alerting

### Alert Rules

#### Critical alerts (immediate response)
```yaml
# API Gateway down
- alert: APIGatewayDown
  expr: up{job=\"corvus-api\"} == 0
  for: 1m
  labels:
    severity: critical
  annotations:
    summary: \"Corvus API Gateway is down\"
    description: \"API Gateway has been down for more than 1 minute\"

# Database connection failures  
- alert: DatabaseConnectionFailure
  expr: pg_up == 0
  for: 2m
  labels:
    severity: critical
  annotations:
    summary: \"Database connection failed\"
    description: \"Cannot connect to PostgreSQL database\"

# High error rate
- alert: HighErrorRate  
  expr: rate(http_requests_total{status_code=~\"5..\"}[5m]) > 0.1
  for: 5m
  labels:
    severity: critical
  annotations:
    summary: \"High error rate detected\"
    description: \"5xx error rate is {{ $value }} requests/sec\"
```

#### Warning alerts (24h response)
```yaml
# High response time
- alert: HighResponseTime
  expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1.0
  for: 10m
  labels:
    severity: warning
  annotations:
    summary: \"High API response time\"
    description: \"95th percentile response time is {{ $value }}s\"

# Worker queue backup
- alert: WorkerQueueHigh
  expr: corvus_worker_queue_length > 1000
  for: 15m
  labels:
    severity: warning
  annotations:
    summary: \"Worker queue is backing up\"
    description: \"Queue length is {{ $value }} jobs\"

# Low experiment success rate
- alert: LowExperimentSuccessRate
  expr: rate(corvus_experiments_completed_total[1h]) / rate(corvus_experiments_created_total[1h]) < 0.9
  for: 30m
  labels:
    severity: warning
  annotations:
    summary: \"Low experiment success rate\"
    description: \"Success rate is {{ $value | humanizePercentage }}\"
```

#### Info alerts (monitoring only)
```yaml
# High disk usage
- alert: HighDiskUsage
  expr: (node_filesystem_size_bytes - node_filesystem_avail_bytes) / node_filesystem_size_bytes > 0.8
  for: 1h
  labels:
    severity: info
  annotations:
    summary: \"High disk usage\"
    description: \"Disk usage is {{ $value | humanizePercentage }}\"

# New algorithm registered
- alert: NewAlgorithmRegistered
  expr: increase(corvus_algorithm_registrations_total[1h]) > 0
  labels:
    severity: info
  annotations:
    summary: \"New algorithm registered\"
    description: \"{{ $value }} new algorithms registered in last hour\"
```

### Notification Channels

#### Slack integration
```yaml
# alertmanager.yml
route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'web.hook'
  routes:
  - match:
      severity: critical
    receiver: 'slack-critical'
  - match:
      severity: warning  
    receiver: 'slack-warnings'

receivers:
- name: 'slack-critical'
  slack_configs:
  - api_url: 'https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK'
    channel: '#corvus-alerts'
    title: 'Corvus Critical Alert'
    text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'
    color: 'danger'
```

#### Email notifications
```yaml
- name: 'email-ops'
  email_configs:
  - to: 'ops-team@your-domain.com'
    from: 'corvus-alerts@your-domain.com'
    smarthost: 'smtp.your-domain.com:587'
    subject: 'Corvus Alert: {{ .GroupLabels.alertname }}'
    body: |
      {{ range .Alerts }}
      Alert: {{ .Annotations.summary }}
      Description: {{ .Annotations.description }}
      {{ end }}
```

#### PagerDuty integration
```yaml
- name: 'pagerduty-critical'
  pagerduty_configs:
  - routing_key: 'YOUR_PAGERDUTY_INTEGRATION_KEY'
    description: 'Corvus Critical Alert: {{ .GroupLabels.alertname }}'
```

---

## Distributed Tracing

### Jaeger Configuration

#### Trace collection
```python
# Instrumentation in Python services
from jaeger_client import Config
from opentracing.ext import tags
import opentracing

# Initialize tracer
config = Config(
    config={
        'sampler': {'type': 'const', 'param': 1},
        'logging': True,
        'local_agent': {
            'reporting_host': 'jaeger-agent',
            'reporting_port': 6831,
        }
    },
    service_name='corvus-api-gateway'
)
tracer = config.initialize_tracer()

# Trace API requests
@tracer.trace()
def handle_experiment_request(experiment_config):
    span = tracer.active_span
    span.set_tag(tags.HTTP_METHOD, 'POST')
    span.set_tag('experiment.id', experiment_config.id)
    
    # Trace downstream calls
    with tracer.start_span('validate_config', child_of=span) as child_span:
        result = validate_experiment_config(experiment_config)
        child_span.set_tag('validation.success', result.is_valid)
    
    return result
```

#### Trace analysis patterns
```yaml
Common Traces:
  - \"Experiment Creation\": Web UI → API → Orchestrator → Tracking
  - \"Run Execution\": Orchestrator → Message Broker → Worker → Plugin
  - \"Results Retrieval\": Web UI → API → Tracking → Database
  - \"Report Generation\": Web UI → API → ReportGenerator → Multiple services

Key Metrics from Traces:
  - End-to-end latency per operation
  - Service dependency mapping
  - Error propagation patterns  
  - Performance bottlenecks identification
```

---

## Log Management

### Logging Strategy

#### Log levels and structure
```python
# Structured logging example
import structlog

logger = structlog.get_logger()

# Info: Normal operations
logger.info(
    \"experiment_started\",
    experiment_id=\"exp_123\",
    user_id=\"user_456\", 
    algorithm_count=3,
    benchmark_count=5
)

# Warning: Recoverable issues
logger.warning(
    \"worker_retry_attempt\",
    worker_id=\"worker_001\",
    run_id=\"run_789\",
    attempt=2,
    max_attempts=3,
    error=\"timeout\"
)

# Error: Failed operations
logger.error(
    \"algorithm_execution_failed\",
    run_id=\"run_789\",
    algorithm_id=\"alg_456\",
    error_type=\"PluginError\",
    error_message=\"Memory allocation failed\",
    stack_trace=exc_info()
)
```

#### Log aggregation with ELK
```yaml
# Logstash pipeline configuration
input {
  beats {
    port => 5044
  }
}

filter {
  if [fields][service] == \"corvus-api\" {
    json {
      source => \"message\"
    }
    
    date {
      match => [ \"timestamp\", \"ISO8601\" ]
    }
    
    mutate {
      add_field => { \"service_type\" => \"api_gateway\" }
    }
  }
  
  if [fields][service] == \"corvus-worker\" {
    json {
      source => \"message\"
    }
    
    if [level] == \"ERROR\" {
      mutate {
        add_tag => [ \"error\", \"requires_attention\" ]
      }
    }
  }
}

output {
  elasticsearch {
    hosts => [\"elasticsearch:9200\"]
    index => \"corvus-logs-%{+YYYY.MM.dd}\"
  }
}
```

### Log Analysis Patterns

#### Common search queries (Kibana)
```javascript
// High-level experiment flow
service:\"corvus-api\" AND message:\"experiment_started\" 
  AND experiment_id:\"exp_123\"

// Worker execution issues
service:\"corvus-worker\" AND level:\"ERROR\" 
  AND @timestamp:[now-1h TO now]

// Performance debugging
service:\"corvus-api\" AND duration:>1000 
  AND endpoint:\"/api/v1/experiments\"

// Plugin-specific errors
service:\"corvus-worker\" AND error_type:\"PluginError\" 
  AND algorithm_id:\"custom_bayes_opt\"

// Database connection issues
message:\"database\" AND (level:\"ERROR\" OR level:\"WARNING\")
  AND @timestamp:[now-24h TO now]
```

#### Log-based alerts
```yaml
# Logstash can send metrics to Prometheus based on log patterns
output {
  prometheus {
    increment => {
      \"corvus_log_errors_total\" => {
        \"service\" => \"%{[fields][service]}\"
        \"level\" => \"%{level}\"
      }
    }
  }
}

# Then alert on log-derived metrics
- alert: HighLogErrorRate
  expr: rate(corvus_log_errors_total{level=\"ERROR\"}[5m]) > 0.5
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: \"High error rate in logs\"
    description: \"{{ $value }} errors/sec in {{ $labels.service }}\"
```

---

## Performance Monitoring

### Key Performance Indicators

#### Response time SLIs/SLOs
```yaml
Service Level Indicators:
  API Gateway:
    - P50 response time: <100ms
    - P95 response time: <300ms  
    - P99 response time: <1000ms
    
  Worker Execution:
    - Job pickup latency: <30s
    - Algorithm init time: <60s
    - Result reporting latency: <10s
    
  Database Operations:
    - Query response time P95: <50ms
    - Connection acquisition: <100ms
    - Transaction commit time: <200ms

Service Level Objectives:
  - 99.9% of API requests under 1s response time
  - 95% of experiments complete successfully  
  - 99% system uptime (8.76h downtime/year max)
```

#### Throughput metrics
```python
# Throughput tracking
experiments_per_hour = Gauge(
    'corvus_experiments_per_hour',
    'Experiments completed per hour'
)

runs_per_second = Gauge(
    'corvus_runs_per_second', 
    'Algorithm runs completed per second'
)

# Efficiency metrics
resource_efficiency = Gauge(
    'corvus_resource_efficiency_percent',
    'Resource utilization efficiency',
    ['resource_type']  # cpu, memory, gpu, storage
)
```

### Performance Dashboards

#### Real-time performance panel
```yaml
Panels:
  - Request Rate: Current requests/second with 5min trend
  - Response Time Distribution: Histogram of response times
  - Error Rate: Current error percentage with alert threshold
  - Active Users: Current active user sessions
  - Worker Efficiency: Busy vs idle workers ratio
  - Queue Health: Pending jobs and processing rate
```

#### Historical analysis panel  
```yaml
Panels:
  - Weekly Performance Trends: Response times over 7 days
  - Capacity Planning: Resource usage growth trends
  - Experiment Patterns: Peak usage times and seasonality
  - Algorithm Performance: Comparative execution times
  - System Reliability: Uptime and MTBF trends
```

---

## Troubleshooting Workflows

### Common Issue Patterns

#### High response times
```bash
# Investigation workflow
1. Check Grafana \"API Performance\" dashboard
2. Identify slow endpoints from Prometheus metrics
3. Use Jaeger to trace slow requests end-to-end
4. Analyze database slow query log:
   kubectl exec postgres-0 -- psql -c \"SELECT query, mean_time FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;\"
5. Check resource utilization:
   kubectl top pods -n corvus-system
6. Review application logs for errors:
   kubectl logs -f deployment/corvus-api | grep ERROR
```

#### Worker execution failures
```bash
# Debugging workflow  
1. Check worker dashboard for failure patterns
2. Identify failing algorithms/benchmarks:
   curl -s localhost:9090/api/v1/query?query='corvus_worker_job_status_total{status=\"failed\"}'
3. Examine worker logs:
   kubectl logs -f deployment/corvus-worker --previous
4. Check plugin isolation issues:
   kubectl exec corvus-worker-pod -- ps aux | grep python
5. Verify resource limits:
   kubectl describe pod corvus-worker-pod | grep -A5 Limits
6. Test algorithm locally:
   corvus-cli test local --algorithm failing_algorithm --debug
```

#### Database performance issues
```bash
# Investigation steps
1. Check connection pool status:
   kubectl exec postgres-0 -- psql -c \"SELECT state, count(*) FROM pg_stat_activity GROUP BY state;\"
2. Identify lock contention:
   kubectl exec postgres-0 -- psql -c \"SELECT query, query_start FROM pg_stat_activity WHERE state = 'active' AND query_start < now() - interval '1 minute';\"
3. Analyze slow queries:
   kubectl exec postgres-0 -- psql -c \"SELECT query, calls, mean_time FROM pg_stat_statements ORDER BY mean_time DESC;\"
4. Check index usage:
   kubectl exec postgres-0 -- psql -c \"SELECT schemaname, tablename, attname, n_distinct, correlation FROM pg_stats WHERE tablename IN ('experiments', 'runs', 'metrics');\"
```

### Emergency Procedures

#### Service degradation response
```yaml
Steps:
  1. Assess Impact:
     - Check service health dashboard
     - Identify affected users/experiments
     - Estimate business impact
     
  2. Immediate Mitigation:
     - Scale up affected services
     - Enable maintenance mode if needed
     - Redirect traffic if possible
     
  3. Root Cause Analysis:
     - Gather logs and metrics from incident timeframe
     - Identify the triggering event
     - Document timeline and impact
     
  4. Recovery:
     - Apply fixes incrementally
     - Monitor for regression
     - Communicate status to users
     
  5. Post-Incident:
     - Conduct blameless post-mortem
     - Update runbooks and alerts
     - Implement prevention measures
```

---

## Health Checks

### Application Health Endpoints

#### API Gateway health check
```python
# /health endpoint implementation
@app.route('/health')
def health_check():
    health_status = {
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': app.config['VERSION'],
        'checks': {}
    }
    
    # Database connectivity
    try:
        db.engine.execute('SELECT 1')
        health_status['checks']['database'] = 'healthy'
    except Exception as e:
        health_status['checks']['database'] = f'unhealthy: {str(e)}'
        health_status['status'] = 'degraded'
    
    # Message broker connectivity
    try:
        connection = pika.BlockingConnection(broker_params)
        connection.close()
        health_status['checks']['message_broker'] = 'healthy'
    except Exception as e:
        health_status['checks']['message_broker'] = f'unhealthy: {str(e)}'
        health_status['status'] = 'degraded'
    
    # Object storage connectivity
    try:
        s3_client.head_bucket(Bucket=config.S3_BUCKET)
        health_status['checks']['object_storage'] = 'healthy' 
    except Exception as e:
        health_status['checks']['object_storage'] = f'unhealthy: {str(e)}'
        health_status['status'] = 'degraded'
    
    status_code = 200 if health_status['status'] == 'healthy' else 503
    return jsonify(health_status), status_code
```

#### Worker health monitoring
```python
# Worker heartbeat system
class WorkerHealthMonitor:
    def __init__(self):
        self.last_heartbeat = {}
        self.worker_status = {}
    
    def send_heartbeat(self, worker_id):
        self.last_heartbeat[worker_id] = time.time()
        self.worker_status[worker_id] = 'healthy'
        
        # Send metrics to Prometheus
        worker_heartbeat_timestamp.labels(worker_id=worker_id).set(time.time())
    
    def check_worker_health(self):
        current_time = time.time()
        for worker_id, last_seen in self.last_heartbeat.items():
            if current_time - last_seen > 300:  # 5 minutes timeout
                self.worker_status[worker_id] = 'stale'
                logger.warning('Worker heartbeat missing', worker_id=worker_id)
```

### Deep Health Checks

#### End-to-end system health
```python
# Comprehensive health check that exercises full system
@app.route('/health/deep')  
def deep_health_check():
    start_time = time.time()
    checks = {}
    
    # Test experiment creation flow
    try:
        test_config = create_test_experiment_config()
        experiment_id = orchestrator.validate_experiment(test_config)
        orchestrator.cleanup_test_experiment(experiment_id)
        checks['experiment_flow'] = 'healthy'
    except Exception as e:
        checks['experiment_flow'] = f'failed: {str(e)}'
    
    # Test worker availability
    try:
        queue_length = message_broker.get_queue_length('run_jobs')
        available_workers = worker_manager.get_available_workers()
        if available_workers > 0:
            checks['worker_capacity'] = 'healthy'
        else:
            checks['worker_capacity'] = 'no_available_workers'
    except Exception as e:
        checks['worker_capacity'] = f'failed: {str(e)}'
    
    # Test data retrieval
    try:
        recent_experiments = tracking_service.get_recent_experiments(limit=1)
        checks['data_retrieval'] = 'healthy'
    except Exception as e:
        checks['data_retrieval'] = f'failed: {str(e)}'
    
    duration = time.time() - start_time
    
    return jsonify({
        'status': 'healthy' if all('failed' not in check for check in checks.values()) else 'unhealthy',
        'duration_seconds': duration,
        'checks': checks
    })
```

---

## Related Documents

- **Deployment**: [Deployment Guide](deployment-guide.md)
- **Architecture**: [Containers (C4-2)](../architecture/c2-containers.md), [Components (C4-3)](../architecture/c3-components.md)
- **Workflows**: [Workflows](../user-guides/workflows.md)
- **Methodology**: [Benchmarking Practices](../methodology/benchmarking-practices.md)
- **Design**: [Design Decisions](../design/design-decisions.md)
