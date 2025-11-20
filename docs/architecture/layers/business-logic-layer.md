# Business Logic Layer Documentation

The **Business Logic Layer** contains the core domain services and business rules for the Corvus Corone HPO Benchmarking Platform. This layer implements the primary functionality of the platform while remaining independent of presentation and data storage concerns.

## Layer Responsibilities

### Primary Functions:
- **Experiment Management**: End-to-end experiment lifecycle management
- **Algorithm Operations**: HPO algorithm registration, versioning, and metadata management
- **Benchmark Management**: Problem instance definition and versioning
- **Performance Analysis**: Statistical analysis and comparison of optimization results
- **Publication Management**: Research publication tracking and citation formatting
- **Report Generation**: Automated report creation and export

### Services in this Layer:

## 🎯 Experiment Orchestrator (`experiment-orchestrator`)
**Purpose**: Manages experiment configuration, planning, and execution coordination

### Components:
- **ExperimentConfigManager**: Validates and manages experiment configurations
- **ExperimentPlanBuilder**: Creates detailed execution plans from configurations  
- **RunScheduler**: Schedules and queues individual experiment runs
- **ReproducibilityManager**: Ensures experiment reproducibility and seed management
- **EventPublisher**: Publishes experiment lifecycle events

### Shared Utilities:
- **OrchestratorConfig**: Configuration management and environment settings
- **ServiceClient**: HTTP client for inter-service communication
- **Response Models**: Standardized response formats for orchestration operations

### Key Features:
- **Experiment Validation**: Comprehensive validation of experiment configurations
- **Execution Planning**: Intelligent scheduling of experiment runs across resources
- **Progress Tracking**: Real-time monitoring of experiment execution progress
- **Error Recovery**: Automatic retry and failure handling for runs
- **Resource Management**: Efficient allocation and utilization of compute resources

## 📊 Experiment Tracking (`experiment-tracking`)
**Purpose**: Manages experiment lifecycle, metadata, and run results

### Components:
- **TrackingAPI**: REST API for experiment and run management
- **RunLifecycleManager**: Handles run state transitions and metadata
- **TaggingAndSearchEngine**: Flexible tagging and search capabilities
- **LineageTracker**: Tracks experiment lineage and relationships

### Key Features:
- **Metadata Management**: Comprehensive metadata storage and retrieval
- **Run Tracking**: Detailed tracking of individual algorithm runs
- **Search and Discovery**: Advanced search capabilities across experiments
- **Data Lineage**: Track relationships between experiments and derived results

## 📈 Metrics Analysis (`metrics-analysis`)
**Purpose**: Statistical analysis and comparison of HPO algorithm performance

### Components:
- **MetricCalculator**: Computes performance metrics and aggregations
- **AggregationEngine**: Statistical aggregation across multiple runs
- **StatisticalTestsEngine**: Significance testing and comparative analysis
- **VisualizationQueryAdapter**: Data formatting for visualization components

### Key Features:
- **Performance Metrics**: Comprehensive performance metric calculation
- **Statistical Analysis**: Rigorous statistical testing and comparison
- **Trend Analysis**: Performance trends over time and parameter spaces
- **Comparative Studies**: Side-by-side algorithm comparisons with significance testing

## 🧮 Algorithm Registry (`algorithm-registry`)
**Purpose**: Catalog and versioning system for HPO algorithms

### Components:
- **AlgorithmMetadataStore**: Algorithm metadata and documentation management
- **AlgorithmVersionManager**: Version control and compatibility tracking
- **CompatibilityChecker**: Algorithm-benchmark compatibility validation

### Key Features:
- **Algorithm Catalog**: Searchable catalog of available HPO algorithms
- **Version Management**: Semantic versioning and compatibility tracking
- **Metadata Management**: Rich metadata including parameters, requirements, and documentation
- **Compatibility Matrix**: Algorithm-benchmark compatibility validation

## 🎲 Benchmark Definition (`benchmark-definition`)  
**Purpose**: Problem instance management and benchmark versioning

### Components:
- **BenchmarkRepository**: Storage and retrieval of benchmark definitions
- **ProblemInstanceManager**: Management of specific problem instances
- **BenchmarkVersioning**: Version control for benchmark problems

### Key Features:
- **Problem Catalog**: Comprehensive catalog of optimization problems
- **Instance Management**: Multiple instances per benchmark with different characteristics
- **Metadata Standards**: Standardized metadata format for benchmark problems
- **Difficulty Assessment**: Automatic difficulty assessment and categorization

## 📚 Publication Service (`publication-service`)
**Purpose**: Research publication management and citation handling

### Components:
- **ReferenceCatalog**: Database of research papers and publications
- **CitationFormatter**: Multiple citation format support (APA, IEEE, etc.)
- **ReferenceLinker**: Automatic linking between experiments and publications
- **ExternalBibliographyClient**: Integration with external bibliography services

### Key Features:
- **Publication Database**: Comprehensive database of HPO research papers
- **Citation Management**: Automatic citation generation in multiple formats
- **Reference Linking**: Link experiments to relevant publications
- **Impact Tracking**: Track citations and research impact metrics

## 📋 Report Generator (`report-generator`)
**Purpose**: Automated report generation and export

### Components:
- **ReportTemplateEngine**: Configurable report templates and layouts
- **ReportAssembler**: Combines data from multiple sources into cohesive reports
- **ReportExporter**: Multiple export formats (PDF, HTML, LaTeX, etc.)
- **ReportMetadataStore**: Report metadata and generation history

### Key Features:
- **Template System**: Flexible template system for different report types
- **Multi-format Export**: Support for PDF, HTML, Word, and LaTeX formats
- **Automated Generation**: Scheduled and event-triggered report generation
- **Custom Reports**: User-defined custom report templates and layouts

## Architecture Patterns

### Domain-Driven Design:
- **Aggregates**: Experiment, Algorithm, Benchmark, Publication as core aggregates
- **Value Objects**: Metrics, Configuration, Metadata as value objects
- **Domain Services**: Cross-aggregate operations and complex business logic
- **Domain Events**: Publish events for significant business occurrences

### Inter-Service Communication:
- **Synchronous**: HTTP APIs for immediate data needs
- **Asynchronous**: Message queues for event-driven updates
- **Event Sourcing**: Event history for audit and replay capabilities
- **CQRS**: Command Query Responsibility Segregation for read/write optimization

### Business Rules:
- **Validation**: Comprehensive input validation and business rule enforcement
- **Invariants**: Maintain business invariants across service boundaries
- **Workflows**: Complex business workflows with proper state management
- **Compensation**: Compensating transactions for distributed operations

## Configuration

### Environment Variables:
```bash
# Inter-service Communication
TRACKING_SERVICE_URL=http://experiment-tracking:8002
ALGORITHM_REGISTRY_URL=http://algorithm-registry:8004
BENCHMARK_SERVICE_URL=http://benchmark-definition:8003

# Message Broker
RABBITMQ_URL=amqp://admin:admin@rabbitmq:5672
MESSAGE_BROKER_TYPE=rabbitmq

# Execution Limits
MAX_CONCURRENT_RUNS=10
MAX_EXPERIMENTS_PER_USER=10
MAX_RUNS_PER_EXPERIMENT=1000

# Performance
DEFAULT_RUN_TIMEOUT=3600
QUEUE_CHECK_INTERVAL=30
METRICS_RETENTION_DAYS=365

# Features
STATISTICAL_TESTING_ENABLED=true
REPRODUCIBILITY_ENFORCEMENT=strict
AUTO_REPORT_GENERATION=true
```

## Dependencies

### Layer Dependencies:
- **Execution Layer**: For algorithm execution and runtime services
- **Data Layer**: For persistent storage and retrieval
- **Support Layer**: For authentication and monitoring

### Technology Dependencies:
- **FastAPI**: Web framework for service APIs
- **SQLAlchemy**: ORM for database operations
- **Celery**: Task queue for background processing
- **SciPy**: Statistical analysis and scientific computing
- **Pandas**: Data manipulation and analysis
- **RabbitMQ**: Message broker for asynchronous communication

## Development Guidelines

### Domain Modeling:
1. **Rich Domain Models**: Encapsulate business logic within domain objects
2. **Aggregate Boundaries**: Clear boundaries around related entities
3. **Domain Events**: Publish events for significant business occurrences
4. **Business Rules**: Explicit business rule validation and enforcement

### Service Design:
1. **Single Responsibility**: Each service has one clear business responsibility
2. **Loose Coupling**: Minimize dependencies between services
3. **High Cohesion**: Related functionality grouped within services
4. **API Design**: Well-defined APIs with clear contracts

### Error Handling:
1. **Business Exceptions**: Custom exceptions for business rule violations
2. **Graceful Degradation**: Fallback behavior when dependencies are unavailable
3. **Compensation**: Compensating actions for failed distributed operations
4. **Audit Trail**: Complete audit trail for business operations

## Quality Assurance

### Testing Strategy:
- **Unit Tests**: Test individual components and business logic
- **Integration Tests**: Test service interactions and workflows
- **Contract Tests**: Validate API contracts between services
- **Business Logic Tests**: Comprehensive testing of business rules

### Performance Considerations:
- **Caching**: Strategic caching of frequently accessed data
- **Batch Processing**: Efficient batch operations for bulk data
- **Async Processing**: Non-blocking operations for improved throughput
- **Resource Pooling**: Connection pooling and resource management

### Monitoring and Observability:
- **Business Metrics**: Track key business indicators and KPIs
- **Performance Metrics**: Service response times and throughput
- **Error Tracking**: Comprehensive error logging and alerting
- **Distributed Tracing**: End-to-end request tracing across services