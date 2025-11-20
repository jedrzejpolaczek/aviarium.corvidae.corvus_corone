# Kod - Corvus Corone (C4-4)

> **Szczegóły implementacyjne kluczowych komponentów systemu HPO Benchmarking Platform na poziomie kodu**

---

## Diagramy klas komponentów systemu

### 4.1 Experiment Orchestrator - Class Diagram

```mermaid
---
config:
  layout: elk
  theme: redux-dark
---
classDiagram
    class ExperimentConfigManager {
        -benchmarkService: BenchmarkService
        -algorithmService: AlgorithmService
        +validateConfiguration(config: ExperimentConfig) ExperimentValidationResult
        +checkCompatibility(algorithms: List~AlgorithmId~, benchmarks: List~BenchmarkId~) CompatibilityResult
        +validateBudgets(budget: BudgetConfig) ValidationResult
        -validateResourceLimits(limits: ResourceLimits) boolean
    }
    
    class ExperimentPlanBuilder {
        -configManager: ExperimentConfigManager
        +buildPlan(config: ExperimentConfig) ExperimentPlan
        +createRunMatrix(algorithms: List~Algorithm~, instances: List~BenchmarkInstance~) RunMatrix
        +optimizeExecutionOrder(runs: List~RunConfig~) List~RunConfig~
        -calculateEstimatedDuration(plan: ExperimentPlan) Duration
    }
    
    class RunScheduler {
        -messageQueue: MessageQueue
        -priorityManager: PriorityManager
        +scheduleRuns(plan: ExperimentPlan) SchedulingResult
        +cancelExperiment(experimentId: ExperimentId) CancellationResult
        +retryFailedRuns(experimentId: ExperimentId) RetryResult
        -createJobMessage(runConfig: RunConfig) JobMessage
    }
    
    class ExperimentConfig {
        +experimentId: ExperimentId
        +name: string
        +algorithms: List~AlgorithmId~
        +benchmarks: List~BenchmarkId~
        +budget: BudgetConfig
        +seeds: List~int~
        +metadata: Map~string, any~
    }
    
    class RunConfig {
        +runId: RunId
        +experimentId: ExperimentId
        +algorithmVersionId: AlgorithmVersionId
        +benchmarkInstanceId: BenchmarkInstanceId
        +seed: int
        +budget: BudgetConfig
        +priority: Priority
    }
    
    ExperimentConfigManager --> ExperimentConfig
    ExperimentPlanBuilder --> ExperimentConfigManager
    ExperimentPlanBuilder --> RunConfig
    RunScheduler --> RunConfig
```

### 4.2 Algorithm Plugin Runtime - Class Diagram

```mermaid
---
config:
  layout: elk
  theme: redux-dark
---
classDiagram
    class IAlgorithmPlugin {
        <<interface>>
        +init(config: AlgorithmConfig) void
        +suggest(budget_remaining: int) ParameterConfiguration
        +observe(config: ParameterConfiguration, result: EvaluationResult) void
        +get_best_configuration() ParameterConfiguration
        +cleanup() void
    }
    
    class PluginLoader {
        -storageClient: ObjectStorageClient
        -versionManager: AlgorithmVersionManager
        +loadPlugin(algorithmVersionId: AlgorithmVersionId) IAlgorithmPlugin
        +validatePlugin(plugin: IAlgorithmPlugin) ValidationResult
        +unloadPlugin(pluginId: PluginId) void
        -resolveDependencies(requirements: List~Dependency~) DependencyResult
        -downloadPluginArtifact(location: string) Path
    }
    
    class SandboxManager {
        -resourceLimiter: ResourceLimiter
        -securityContext: SecurityContext
        +executeSuggest(plugin: IAlgorithmPlugin, budget: int) ParameterConfiguration
        +executeObserve(plugin: IAlgorithmPlugin, config: ParameterConfiguration, result: EvaluationResult) void
        +enforceTimeLimit(operation: Callable, timeout: Duration) Result
        +enforceMemoryLimit(operation: Callable, maxMemory: int) Result
        -createIsolatedEnvironment() Environment
    }
    
    class BayesianOptimizationPlugin {
        -acquisitionFunction: AcquisitionFunction
        -gaussianProcess: GaussianProcess
        -observedConfigs: List~ParameterConfiguration~
        -observedResults: List~EvaluationResult~
        +init(config: AlgorithmConfig) void
        +suggest(budget_remaining: int) ParameterConfiguration
        +observe(config: ParameterConfiguration, result: EvaluationResult) void
        +get_best_configuration() ParameterConfiguration
        +cleanup() void
        -updateGaussianProcess() void
        -optimizeAcquisition() ParameterConfiguration
    }
    
    class RandomSearchPlugin {
        -parameterSpace: ParameterSpace
        -randomGenerator: Random
        -bestConfig: ParameterConfiguration
        -bestScore: float
        +init(config: AlgorithmConfig) void
        +suggest(budget_remaining: int) ParameterConfiguration
        +observe(config: ParameterConfiguration, result: EvaluationResult) void
        +get_best_configuration() ParameterConfiguration
        +cleanup() void
        -sampleFromSpace(space: ParameterSpace) ParameterConfiguration
    }
    
    IAlgorithmPlugin <|-- BayesianOptimizationPlugin
    IAlgorithmPlugin <|-- RandomSearchPlugin
    PluginLoader --> IAlgorithmPlugin
    SandboxManager --> IAlgorithmPlugin
```

### 4.3 Tracking Service - Class Diagram

```mermaid
---
config:
  layout: elk
  theme: redux-dark
---
classDiagram
    class TrackingAPI {
        -runDAO: RunDAO
        -metricDAO: MetricDAO
        -lifecycleManager: RunLifecycleManager
        +createRun(request: CreateRunRequest) RunResponse
        +logMetrics(runId: RunId, metrics: List~Metric~) MetricResponse
        +updateRunStatus(runId: RunId, status: RunStatus) StatusResponse
        +getRun(runId: RunId) RunDetails
        +searchRuns(query: RunQuery) List~RunSummary~
        -validateMetrics(metrics: List~Metric~) ValidationResult
    }
    
    class RunLifecycleManager {
        -eventPublisher: EventPublisher
        -stateValidator: StateValidator
        +createRun(config: RunConfig) Run
        +startRun(runId: RunId) RunStatus
        +completeRun(runId: RunId, result: RunResult) RunStatus
        +failRun(runId: RunId, error: Error) RunStatus
        +cancelRun(runId: RunId) RunStatus
        -transitionState(run: Run, newState: RunStatus) Run
        -publishEvent(event: RunEvent) void
    }
    
    class MetricCollector {
        -buffer: MetricBuffer
        -batchProcessor: BatchProcessor
        +collectMetric(runId: RunId, metric: Metric) void
        +collectBatch(runId: RunId, metrics: List~Metric~) void
        +flush(runId: RunId) void
        -validateMetric(metric: Metric) boolean
        -aggregateMetrics(metrics: List~Metric~) AggregatedMetrics
    }
    
    class Run {
        +runId: RunId
        +experimentId: ExperimentId
        +algorithmVersionId: AlgorithmVersionId
        +benchmarkInstanceId: BenchmarkInstanceId
        +seed: int
        +status: RunStatus
        +startTime: DateTime
        +endTime: DateTime
        +resourceUsage: ResourceUsage
        +environmentSnapshot: EnvironmentSnapshot
        +metrics: List~Metric~
        +artifacts: List~Artifact~
    }
    
    class Metric {
        +metricId: MetricId
        +runId: RunId
        +name: string
        +value: float
        +step: int
        +timestamp: DateTime
        +metadata: Map~string, any~
    }
    
    TrackingAPI --> RunLifecycleManager
    TrackingAPI --> MetricCollector
    RunLifecycleManager --> Run
    MetricCollector --> Metric
    Run --> Metric
```

### 4.4 Benchmark Definition Service - Class Diagram

```mermaid
---
config:
  layout: elk
  theme: redux-dark
---
classDiagram
    class BenchmarkRepository {
        -benchmarkDAO: BenchmarkDAO
        -validator: BenchmarkValidator
        +createBenchmark(benchmark: Benchmark) BenchmarkId
        +getBenchmark(benchmarkId: BenchmarkId) Benchmark
        +updateBenchmark(benchmark: Benchmark) void
        +deleteBenchmark(benchmarkId: BenchmarkId) void
        +listBenchmarks(filter: BenchmarkFilter) List~Benchmark~
        -validateBenchmark(benchmark: Benchmark) ValidationResult
    }
    
    class ProblemInstanceManager {
        -instanceDAO: BenchmarkInstanceDAO
        -datasetRepository: DatasetRepository
        +createInstance(instance: BenchmarkInstance) InstanceId
        +getInstance(instanceId: InstanceId) BenchmarkInstance
        +updateInstance(instance: BenchmarkInstance) void
        +listInstances(benchmarkId: BenchmarkId) List~BenchmarkInstance~
        +validateDataset(datasetRef: DatasetReference) ValidationResult
        -generateInstanceConfig(dataset: Dataset, params: Map~string, any~) InstanceConfig
    }
    
    class BenchmarkVersioning {
        -versionDAO: BenchmarkVersionDAO
        -changeTracker: ChangeTracker
        +createVersion(benchmarkId: BenchmarkId, changes: ChangeSet) VersionId
        +getVersion(versionId: VersionId) BenchmarkVersion
        +setCanonicalVersion(benchmarkId: BenchmarkId, versionId: VersionId) void
        +listVersions(benchmarkId: BenchmarkId) List~BenchmarkVersion~
        +compareVersions(v1: VersionId, v2: VersionId) VersionDiff
        -trackChanges(oldVersion: BenchmarkVersion, newVersion: BenchmarkVersion) ChangeSet
    }
    
    class Benchmark {
        +benchmarkId: BenchmarkId
        +name: string
        +description: string
        +problemType: ProblemType
        +parameterSpace: ParameterSpace
        +evaluationMetrics: List~string~
        +canonicalVersion: VersionId
        +created: DateTime
        +lastModified: DateTime
    }
    
    class BenchmarkInstance {
        +instanceId: InstanceId
        +benchmarkId: BenchmarkId
        +datasetRef: DatasetReference
        +config: InstanceConfig
        +bestKnownValue: float
        +difficulty: DifficultyLevel
        +tags: List~string~
    }
    
    BenchmarkRepository --> Benchmark
    ProblemInstanceManager --> BenchmarkInstance
    ProblemInstanceManager --> BenchmarkRepository
    BenchmarkVersioning --> Benchmark
    Benchmark --> BenchmarkInstance
```

### 4.5 Algorithm Registry Service - Class Diagram

```mermaid
---
config:
  layout: elk
  theme: redux-dark
---
classDiagram
    class AlgorithmMetadataStore {
        -algorithmDAO: AlgorithmDAO
        -publicationLinker: PublicationLinker
        +registerAlgorithm(algorithm: Algorithm) AlgorithmId
        +getAlgorithm(algorithmId: AlgorithmId) Algorithm
        +updateAlgorithm(algorithm: Algorithm) void
        +searchAlgorithms(query: AlgorithmQuery) List~Algorithm~
        +linkPublication(algorithmId: AlgorithmId, publicationId: PublicationId) void
        -validateAlgorithmMetadata(algorithm: Algorithm) ValidationResult
    }
    
    class AlgorithmVersionManager {
        -versionDAO: AlgorithmVersionDAO
        -artifactStorage: ArtifactStorage
        +createVersion(version: AlgorithmVersion) VersionId
        +getVersion(versionId: VersionId) AlgorithmVersion
        +updateVersionStatus(versionId: VersionId, status: VersionStatus) void
        +listVersions(algorithmId: AlgorithmId) List~AlgorithmVersion~
        +uploadPluginArtifact(versionId: VersionId, artifact: PluginArtifact) string
        -validatePlugin(artifact: PluginArtifact) ValidationResult
    }
    
    class CompatibilityChecker {
        -algorithmDAO: AlgorithmDAO
        -benchmarkDAO: BenchmarkDAO
        +checkCompatibility(algorithmId: AlgorithmId, benchmarkId: BenchmarkId) CompatibilityResult
        +getCompatibleBenchmarks(algorithmId: AlgorithmId) List~BenchmarkId~
        +getCompatibleAlgorithms(benchmarkId: BenchmarkId) List~AlgorithmId~
        +validateParameterSpace(algoSpace: ParameterSpace, benchSpace: ParameterSpace) boolean
        -analyzeTypeCompatibility(algoType: AlgorithmType, problemType: ProblemType) boolean
    }
    
    class Algorithm {
        +algorithmId: AlgorithmId
        +name: string
        +type: AlgorithmType
        +description: string
        +isBuiltin: boolean
        +supportedProblemTypes: List~ProblemType~
        +primaryPublicationId: PublicationId
        +created: DateTime
        +lastModified: DateTime
    }
    
    class AlgorithmVersion {
        +versionId: VersionId
        +algorithmId: AlgorithmId
        +version: string
        +pluginLocation: string
        +sdkVersion: string
        +status: VersionStatus
        +requirements: List~Dependency~
        +created: DateTime
    }
    
    AlgorithmMetadataStore --> Algorithm
    AlgorithmVersionManager --> AlgorithmVersion
    AlgorithmVersionManager --> Algorithm
    CompatibilityChecker --> Algorithm
```

### 4.6 Worker Runtime - Class Diagram

```mermaid
---
config:
  layout: elk
  theme: redux-dark
---
classDiagram
    class RunExecutor {
        -pluginLoader: PluginLoader
        -benchmarkLoader: BenchmarkLoader
        -trackingClient: TrackingClient
        -logger: Logger
        +executeRun(config: RunExecutionConfig) RunResult
        +cancelRun(runId: RunId) CancellationResult
        +getRunStatus(runId: RunId) RunStatus
        -setupRunEnvironment(config: RunExecutionConfig) Environment
        -cleanupRun(runId: RunId) void
    }
    
    class DatasetLoader {
        -objectStorageClient: ObjectStorageClient
        -datasetRepository: DatasetRepository
        -cache: DatasetCache
        +loadDataset(datasetRef: DatasetReference) Dataset
        +preloadDatasets(datasetRefs: List~DatasetReference~) void
        +validateDataset(dataset: Dataset) ValidationResult
        +cacheDataset(datasetRef: DatasetReference) void
        -downloadDataset(datasetRef: DatasetReference) Path
    }
    
    class MetricReporter {
        -trackingClient: TrackingClient
        -buffer: MetricBuffer
        -batchProcessor: BatchProcessor
        +reportMetric(runId: RunId, metric: Metric) void
        +reportBatch(runId: RunId, metrics: List~Metric~) void
        +flushMetrics(runId: RunId) void
        +reportRunResult(runId: RunId, result: RunResult) void
        -bufferMetric(metric: Metric) void
    }
    
    class ArtifactUploader {
        -objectStorageClient: ObjectStorageClient
        -artifactRepository: ArtifactRepository
        +uploadArtifact(runId: RunId, artifact: Artifact) ArtifactLocation
        +uploadBatch(runId: RunId, artifacts: List~Artifact~) List~ArtifactLocation~
        +getArtifactUrl(location: ArtifactLocation) string
        -generateArtifactPath(runId: RunId, artifactName: string) string
        -validateArtifact(artifact: Artifact) ValidationResult
    }
    
    class JobMessage {
        +jobId: JobId
        +runId: RunId
        +algorithmVersionId: AlgorithmVersionId
        +benchmarkInstanceId: BenchmarkInstanceId
        +seed: int
        +budget: BudgetConfig
        +priority: Priority
        +timeout: Duration
        +retryCount: int
    }
    
    RunExecutor --> DatasetLoader
    RunExecutor --> MetricReporter
    RunExecutor --> ArtifactUploader
    RunExecutor --> JobMessage
```

### 4.7 Metrics Analysis Service - Class Diagram

```mermaid
---
config:
  layout: elk
  theme: redux-dark
---
classDiagram
    class MetricCalculator {
        -metricDAO: MetricDAO
        -calculationEngine: CalculationEngine
        +calculateMetric(runId: RunId, metricName: string) MetricValue
        +calculateBatchMetrics(runIds: List~RunId~, metricNames: List~string~) Map~RunId, Map~string, MetricValue~~
        +getAvailableMetrics() List~MetricDefinition~
        +registerCustomMetric(definition: MetricDefinition) void
        -validateMetricDefinition(definition: MetricDefinition) ValidationResult
    }
    
    class AggregationEngine {
        -metricCalculator: MetricCalculator
        -statisticsEngine: StatisticsEngine
        +aggregateByBenchmark(experimentId: ExperimentId) BenchmarkAggregation
        +aggregateByAlgorithm(experimentId: ExperimentId) AlgorithmAggregation
        +compareAlgorithms(algorithmIds: List~AlgorithmId~, benchmarkId: BenchmarkId) ComparisonResult
        +generateRankings(experimentId: ExperimentId) AlgorithmRanking
        -calculateStatistics(values: List~float~) StatisticsSummary
    }
    
    class StatisticalTestsEngine {
        -testRegistry: TestRegistry
        -resultValidator: ResultValidator
        +performFriedmanTest(data: ComparisonMatrix) FriedmanTestResult
        +performNemenyiTest(data: ComparisonMatrix) NemenyiTestResult
        +performWilcoxonTest(group1: List~float~, group2: List~float~) WilcoxonTestResult
        +calculateEffectSize(group1: List~float~, group2: List~float~) EffectSize
        +validateTestAssumptions(data: ComparisonMatrix, test: TestType) ValidationResult
    }
    
    class VisualizationQueryAdapter {
        -aggregationEngine: AggregationEngine
        -chartDataFormatter: ChartDataFormatter
        +getComparisonChartData(experimentId: ExperimentId) ChartData
        +getConvergenceData(runId: RunId) ConvergenceData
        +getRankingData(experimentId: ExperimentId) RankingData
        +getPerformanceProfileData(experimentIds: List~ExperimentId~) ProfileData
        -formatForChart(data: AggregationResult, chartType: ChartType) ChartData
    }
    
    class ComparisonResult {
        +algorithmIds: List~AlgorithmId~
        +benchmarkId: BenchmarkId
        +meanPerformances: Map~AlgorithmId, float~
        +standardDeviations: Map~AlgorithmId, float~
        +rankings: Map~AlgorithmId, int~
        +statisticalTests: List~TestResult~
        +confidenceIntervals: Map~AlgorithmId, ConfidenceInterval~
    }
    
    MetricCalculator --> AggregationEngine
    AggregationEngine --> StatisticalTestsEngine
    AggregationEngine --> VisualizationQueryAdapter
    StatisticalTestsEngine --> ComparisonResult
```

### 4.8 Publication Service - Class Diagram

```mermaid
---
config:
  layout: elk
  theme: redux-dark
---
classDiagram
    class ReferenceCatalog {
        -publicationDAO: PublicationDAO
        -metadataValidator: MetadataValidator
        +addPublication(publication: Publication) PublicationId
        +getPublication(publicationId: PublicationId) Publication
        +searchPublications(query: PublicationQuery) List~Publication~
        +updatePublication(publication: Publication) void
        +deletePublication(publicationId: PublicationId) void
        -validatePublication(publication: Publication) ValidationResult
    }
    
    class CitationFormatter {
        -formatterRegistry: FormatterRegistry
        +formatCitation(publicationId: PublicationId, style: CitationStyle) string
        +generateBibTeX(publicationId: PublicationId) string
        +formatReferenceList(publicationIds: List~PublicationId~, style: CitationStyle) string
        +registerFormatter(style: CitationStyle, formatter: Formatter) void
        -loadCitationStyle(style: CitationStyle) StyleDefinition
    }
    
    class ReferenceLinker {
        -linkDAO: LinkDAO
        -entityValidator: EntityValidator
        +linkToAlgorithm(publicationId: PublicationId, algorithmId: AlgorithmId) LinkId
        +linkToBenchmark(publicationId: PublicationId, benchmarkId: BenchmarkId) LinkId
        +linkToExperiment(publicationId: PublicationId, experimentId: ExperimentId) LinkId
        +getLinkedEntities(publicationId: PublicationId) List~EntityLink~
        +getLinkedPublications(entityType: EntityType, entityId: string) List~PublicationId~
        -validateLink(link: EntityLink) ValidationResult
    }
    
    class ExternalBibliographyClient {
        -crossRefClient: CrossRefClient
        -arXivClient: ArXivClient
        -doiResolver: DOIResolver
        +fetchByDOI(doi: string) Publication  
        +fetchByArXivId(arXivId: string) Publication
        +searchCrossRef(query: string) List~Publication~
        +enrichMetadata(publication: Publication) Publication
        -mapToInternalFormat(externalPublication: ExternalPublication) Publication
    }
    
    class Publication {
        +publicationId: PublicationId
        +title: string
        +authors: List~string~
        +year: int
        +venue: string
        +doi: string
        +bibtex: string
        +url: string
        +abstract: string
        +keywords: List~string~
    }
    
    ReferenceCatalog --> Publication
    CitationFormatter --> Publication
    ReferenceLinker --> Publication
    ExternalBibliographyClient --> Publication
```

### 4.9 Report Generator Service - Class Diagram

```mermaid
---
config:
  layout: elk
  theme: redux-dark
---
classDiagram
    class ReportTemplateEngine {
        -templateRepository: TemplateRepository
        -renderingEngine: RenderingEngine
        +createTemplate(template: ReportTemplate) TemplateId
        +getTemplate(templateId: TemplateId) ReportTemplate
        +renderTemplate(templateId: TemplateId, data: ReportData) RenderedContent
        +listTemplates(filter: TemplateFilter) List~ReportTemplate~
        +validateTemplate(template: ReportTemplate) ValidationResult
        -loadTemplateAssets(templateId: TemplateId) TemplateAssets
    }
    
    class ReportAssembler {
        -trackingService: TrackingService
        -metricsService: MetricsAnalysisService
        -publicationService: PublicationService
        +assembleReport(request: ReportRequest) ReportData
        +gatherExperimentData(experimentIds: List~ExperimentId~) ExperimentData
        +gatherComparisonData(comparisonConfig: ComparisonConfig) ComparisonData
        +generateExecutiveSummary(data: ReportData) Summary
        -collectMetadata(experimentIds: List~ExperimentId~) ReportMetadata
    }
    
    class ReportExporter {
        -pdfGenerator: PDFGenerator
        -htmlGenerator: HTMLGenerator
        -markdownGenerator: MarkdownGenerator
        -artifactRepository: ArtifactRepository
        +exportToPDF(content: RenderedContent) PDFDocument
        +exportToHTML(content: RenderedContent) HTMLDocument
        +exportToMarkdown(content: RenderedContent) MarkdownDocument
        +saveReport(document: Document, location: string) ReportLocation
        -applyReportStyling(content: RenderedContent, format: ExportFormat) StyledContent
    }
    
    class ReportMetadataStore {
        -reportDAO: ReportDAO
        -indexer: ReportIndexer
        +saveReportMetadata(metadata: ReportMetadata) ReportId
        +getReportMetadata(reportId: ReportId) ReportMetadata
        +searchReports(query: ReportQuery) List~ReportMetadata~
        +deleteReport(reportId: ReportId) void
        +indexReport(reportId: ReportId) void
        -generateReportSummary(metadata: ReportMetadata) ReportSummary
    }
    
    class ReportRequest {
        +experimentIds: List~ExperimentId~
        +templateId: TemplateId
        +format: ExportFormat
        +includeComparisons: boolean
        +includeStatistics: boolean
        +includePublications: boolean
        +customSections: List~SectionConfig~
    }
    
    ReportTemplateEngine --> ReportAssembler
    ReportAssembler --> ReportExporter
    ReportExporter --> ReportMetadataStore
    ReportAssembler --> ReportRequest
```

### 4.10 Results Store (Data Access Layer) - Class Diagram

```mermaid
---
config:
  layout: elk
  theme: redux-dark
---
classDiagram
    class ExperimentDAO {
        -connectionPool: ConnectionPool
        -queryBuilder: QueryBuilder
        +create(experiment: ExperimentEntity) ExperimentEntity
        +getById(experimentId: ExperimentId) ExperimentEntity
        +update(experiment: ExperimentEntity) ExperimentEntity
        +delete(experimentId: ExperimentId) void
        +search(query: ExperimentQuery) List~ExperimentEntity~
        +findByUser(userId: UserId) List~ExperimentEntity~
        -buildSearchQuery(query: ExperimentQuery) SQLQuery
    }
    
    class RunDAO {
        -connectionPool: ConnectionPool
        -batchProcessor: BatchProcessor
        +create(run: RunEntity) RunEntity
        +getById(runId: RunId) RunEntity
        +update(run: RunEntity) RunEntity
        +delete(runId: RunId) void
        +findByExperiment(experimentId: ExperimentId) List~RunEntity~
        +findByStatus(status: RunStatus) List~RunEntity~
        +batchCreate(runs: List~RunEntity~) List~RunEntity~
    }
    
    class MetricDAO {
        -connectionPool: ConnectionPool
        -timeSeriesOptimizer: TimeSeriesOptimizer
        +create(metric: MetricEntity) MetricEntity
        +getById(metricId: MetricId) MetricEntity
        +findByRun(runId: RunId) List~MetricEntity~
        +findByRunAndName(runId: RunId, metricName: string) List~MetricEntity~
        +batchInsert(metrics: List~MetricEntity~) void
        +aggregateMetrics(query: AggregationQuery) AggregationResult
        -optimizeTimeSeriesStorage(metrics: List~MetricEntity~) void
    }
    
    class AlgorithmDAO {
        -connectionPool: ConnectionPool
        -versionTracker: VersionTracker
        +create(algorithm: AlgorithmEntity) AlgorithmEntity
        +getById(algorithmId: AlgorithmId) AlgorithmEntity
        +update(algorithm: AlgorithmEntity) AlgorithmEntity
        +search(query: AlgorithmQuery) List~AlgorithmEntity~
        +findCompatible(problemType: ProblemType) List~AlgorithmEntity~
        -trackVersionChanges(old: AlgorithmEntity, new: AlgorithmEntity) void
    }
    
    class BenchmarkDAO {
        -connectionPool: ConnectionPool
        -instanceManager: InstanceManager
        +create(benchmark: BenchmarkEntity) BenchmarkEntity
        +getById(benchmarkId: BenchmarkId) BenchmarkEntity
        +update(benchmark: BenchmarkEntity) BenchmarkEntity
        +search(query: BenchmarkQuery) List~BenchmarkEntity~
        +findByProblemType(problemType: ProblemType) List~BenchmarkEntity~
        +getInstances(benchmarkId: BenchmarkId) List~BenchmarkInstanceEntity~
    }
    
    class PublicationDAO {
        -connectionPool: ConnectionPool
        -fullTextSearchEngine: FullTextSearchEngine
        +create(publication: PublicationEntity) PublicationEntity
        +getById(publicationId: PublicationId) PublicationEntity
        +update(publication: PublicationEntity) PublicationEntity
        +search(query: PublicationQuery) List~PublicationEntity~
        +findByAuthor(author: string) List~PublicationEntity~
        +fullTextSearch(query: string) List~PublicationEntity~
    }
    
    class LinkDAO {
        -connectionPool: ConnectionPool
        -relationshipMapper: RelationshipMapper
        +createLink(link: LinkEntity) LinkEntity
        +getLinksForEntity(entityType: EntityType, entityId: string) List~LinkEntity~
        +deleteLink(linkId: LinkId) void
        +findRelatedEntities(entityType: EntityType, entityId: string) List~EntityReference~
        +buildLineageGraph(rootEntity: EntityReference) LineageGraph
        -mapRelationshipType(sourceType: EntityType, targetType: EntityType) RelationshipType
    }
    
    ExperimentDAO --> RunDAO
    RunDAO --> MetricDAO
    AlgorithmDAO --> PublicationDAO
    BenchmarkDAO --> PublicationDAO
    LinkDAO --> ExperimentDAO
    LinkDAO --> AlgorithmDAO
    LinkDAO --> BenchmarkDAO
    LinkDAO --> PublicationDAO
```

### 4.11 Object Storage - Class Diagram

```mermaid
---
config:
  layout: elk
  theme: redux-dark
---
classDiagram
    class ObjectStorageClient {
        -config: StorageConfig
        -credentials: Credentials
        -httpClient: HttpClient
        +putObject(bucket: string, key: string, data: bytes) PutResult
        +getObject(bucket: string, key: string) ObjectData
        +deleteObject(bucket: string, key: string) void
        +listObjects(bucket: string, prefix: string) List~ObjectMetadata~
        +generatePresignedUrl(bucket: string, key: string, expiration: Duration) string
        -buildRequestHeaders(operations: Operation) Map~string, string~
    }
    
    class ArtifactRepository {
        -storageClient: ObjectStorageClient
        -pathGenerator: PathGenerator
        -metadataStore: ArtifactMetadataStore
        +storeArtifact(runId: RunId, artifact: Artifact) ArtifactLocation
        +getArtifact(location: ArtifactLocation) Artifact
        +listArtifacts(runId: RunId) List~ArtifactMetadata~
        +generateDownloadUrl(location: ArtifactLocation) string
        +deleteArtifact(location: ArtifactLocation) void
        -generateArtifactPath(runId: RunId, artifactName: string) string
    }
    
    class DatasetRepository {
        -storageClient: ObjectStorageClient
        -compressionManager: CompressionManager
        -checksumValidator: ChecksumValidator
        +storeDataset(dataset: Dataset) DatasetReference
        +getDataset(datasetRef: DatasetReference) Dataset
        +validateDataset(datasetRef: DatasetReference) ValidationResult
        +getDatasetMetadata(datasetRef: DatasetReference) DatasetMetadata
        +listDatasets(filter: DatasetFilter) List~DatasetReference~
        -compressDataset(dataset: Dataset) CompressedDataset
        -validateChecksum(dataset: Dataset, expectedChecksum: string) boolean
    }
    
    class Dataset {
        +datasetId: DatasetId
        +name: string
        +format: DatasetFormat
        +size: long
        +checksum: string
        +metadata: DatasetMetadata
        +created: DateTime
        +lastModified: DateTime
    }
    
    class Artifact {
        +artifactId: ArtifactId
        +runId: RunId
        +name: string
        +type: ArtifactType
        +size: long
        +contentType: string
        +metadata: Map~string, any~
        +created: DateTime
    }
    
    ObjectStorageClient --> ArtifactRepository
    ObjectStorageClient --> DatasetRepository
    ArtifactRepository --> Artifact
    DatasetRepository --> Dataset
```

### 4.12 Web UI Components - Class Diagram

```mermaid
---
config:
  layout: elk
  theme: redux-dark
---
classDiagram
    class ExperimentDesignerUI {
        -apiClient: APIClient
        -validator: ConfigValidator
        -formBuilder: FormBuilder
        +createExperiment(config: ExperimentConfig) ExperimentId
        +validateConfiguration(config: ExperimentConfig) ValidationResult
        +getAvailableAlgorithms() List~Algorithm~
        +getAvailableBenchmarks() List~Benchmark~
        +previewExperimentPlan(config: ExperimentConfig) ExperimentPlan
        -buildConfigurationForm() FormDefinition
    }
    
    class TrackingDashboardUI {
        -trackingAPI: TrackingAPIClient
        -chartRenderer: ChartRenderer
        -filterManager: FilterManager
        +displayExperiments(filter: ExperimentFilter) void
        +displayRunDetails(runId: RunId) void
        +renderMetricCharts(runId: RunId) ChartCollection
        +exportResults(experimentId: ExperimentId, format: ExportFormat) void
        +realTimeMonitoring(experimentId: ExperimentId) void
        -updateCharts(data: ChartData) void
    }
    
    class ComparisonViewUI {
        -metricsAPI: MetricsAPIClient
        -statisticsRenderer: StatisticsRenderer
        -comparisonEngine: ComparisonEngine
        +compareAlgorithms(algorithmIds: List~AlgorithmId~, benchmarkId: BenchmarkId) ComparisonView
        +renderStatisticalTests(testResults: List~TestResult~) void
        +generateRankingTable(rankings: AlgorithmRanking) RankingTable
        +exportComparison(comparison: ComparisonResult, format: ExportFormat) void
        -renderSignificanceMatrix(matrix: SignificanceMatrix) void
    }
    
    class BenchmarkCatalogUI {
        -benchmarkAPI: BenchmarkAPIClient
        -metadataRenderer: MetadataRenderer
        +displayBenchmarks(filter: BenchmarkFilter) void
        +showBenchmarkDetails(benchmarkId: BenchmarkId) void
        +manageBenchmarkVersions(benchmarkId: BenchmarkId) void
        +uploadDataset(benchmarkId: BenchmarkId, dataset: Dataset) void
        +validateBenchmarkDefinition(definition: BenchmarkDefinition) ValidationResult
    }
    
    class AlgorithmCatalogUI {
        -algorithmAPI: AlgorithmAPIClient
        -compatibilityChecker: CompatibilityDisplayer
        +displayAlgorithms(filter: AlgorithmFilter) void
        +showAlgorithmDetails(algorithmId: AlgorithmId) void
        +manageAlgorithmVersions(algorithmId: AlgorithmId) void
        +uploadPlugin(algorithmId: AlgorithmId, plugin: PluginArtifact) void
        +checkCompatibility(algorithmId: AlgorithmId) CompatibilityMatrix
    }
    
    class PublicationManagerUI {
        -publicationAPI: PublicationAPIClient
        -citationFormatter: CitationDisplayer
        +displayPublications(filter: PublicationFilter) void
        +addPublication(publication: Publication) PublicationId
        +editPublication(publication: Publication) void
        +linkToEntity(publicationId: PublicationId, entityId: string, entityType: EntityType) void
        +generateBibliography(publicationIds: List~PublicationId~, style: CitationStyle) string
    }
    
    class AdminSettingsUI {
        -adminAPI: AdminAPIClient
        -configManager: UIConfigManager
        +manageUsers() void
        +configureSystem(settings: SystemSettings) void
        +monitorSystemHealth() SystemHealthView
        +manageResourceLimits(limits: ResourceLimits) void
        +viewAuditLogs(filter: AuditFilter) List~AuditEvent~
    }
    
    ExperimentDesignerUI --> TrackingDashboardUI
    TrackingDashboardUI --> ComparisonViewUI
    ComparisonViewUI --> BenchmarkCatalogUI
    BenchmarkCatalogUI --> AlgorithmCatalogUI
    AlgorithmCatalogUI --> PublicationManagerUI
```

### 4.13 Message Broker - Class Diagram

```mermaid
---
config:
  layout: elk
  theme: redux-dark
---
classDiagram
    class RunJobQueue {
        -messageQueue: MessageQueue
        -priorityManager: PriorityManager
        -dlqHandler: DeadLetterQueueHandler
        +enqueueRun(jobMessage: JobMessage) void
        +dequeueRun() JobMessage
        +requeueRun(jobMessage: JobMessage, delay: Duration) void
        +moveToDeadLetter(jobMessage: JobMessage, reason: string) void
        +getQueueStats() QueueStatistics
        -managePriorities() void
    }
    
    class EventBus {
        -eventRouter: EventRouter
        -subscriberRegistry: SubscriberRegistry
        -eventStore: EventStore
        +publishEvent(event: SystemEvent) void
        +subscribe(eventType: EventType, handler: EventHandler) SubscriptionId
        +unsubscribe(subscriptionId: SubscriptionId) void
        +replayEvents(fromTimestamp: DateTime, eventTypes: List~EventType~) List~SystemEvent~
        -routeEvent(event: SystemEvent) void
    }
    
    class MessageQueue {
        -queueConfig: QueueConfig
        -persistence: MessagePersistence
        -connectionManager: ConnectionManager
        +send(message: Message, queue: QueueName) void
        +receive(queue: QueueName, timeout: Duration) Message
        +acknowledge(messageId: MessageId) void
        +reject(messageId: MessageId, requeue: boolean) void
        +createQueue(queueName: QueueName, config: QueueConfig) void
        -handleConnectionFailure() void
    }
    
    class EventRouter {
        -routingTable: RoutingTable
        -filterEngine: FilterEngine
        +addRoute(eventType: EventType, subscriber: EventSubscriber) void
        +removeRoute(eventType: EventType, subscriber: EventSubscriber) void
        +routeEvent(event: SystemEvent) List~EventSubscriber~
        +applyFilters(event: SystemEvent, subscribers: List~EventSubscriber~) List~EventSubscriber~
        -updateRoutingTable() void
    }
    
    class SystemEvent {
        +eventId: EventId
        +eventType: EventType
        +source: string
        +timestamp: DateTime
        +payload: EventPayload
        +correlationId: string
        +causationId: string
    }
    
    RunJobQueue --> MessageQueue
    EventBus --> EventRouter
    EventBus --> SystemEvent
    EventRouter --> SystemEvent
```

### 4.14 Authentication & Authorization - Class Diagram

```mermaid
---
config:
  layout: elk
  theme: redux-dark
---
classDiagram
    class TokenValidation {
        -jwtValidator: JWTValidator
        -keyStore: KeyStore
        -blacklistCache: BlacklistCache
        +validateToken(token: string) ValidationResult
        +extractClaims(token: string) TokenClaims
        +isTokenBlacklisted(tokenId: string) boolean
        +blacklistToken(tokenId: string, expiry: DateTime) void
        +refreshToken(refreshToken: string) TokenPair
        -validateSignature(token: string) boolean
    }
    
    class RoleMapping {
        -roleDefinitions: RoleDefinitionStore
        -permissionEngine: PermissionEngine
        +getUserRoles(userId: UserId) List~Role~
        +hasPermission(userId: UserId, resource: Resource, action: Action) boolean
        +assignRole(userId: UserId, role: Role) void
        +revokeRole(userId: UserId, role: Role) void
        +createRole(role: RoleDefinition) RoleId
        -evaluatePermissions(roles: List~Role~, resource: Resource, action: Action) boolean
    }
    
    class AuthenticationService {
        -userStore: UserStore
        -passwordHasher: PasswordHasher
        -tokenGenerator: TokenGenerator
        +authenticate(credentials: UserCredentials) AuthenticationResult
        +createUser(userInfo: UserInfo) UserId
        +changePassword(userId: UserId, oldPassword: string, newPassword: string) void
        +resetPassword(userId: UserId) TemporaryPassword
        +enableTwoFactor(userId: UserId) void
        -hashPassword(password: string) string
    }
    
    class AuthorizationMiddleware {
        -tokenValidation: TokenValidation
        -roleMapping: RoleMapping
        -auditLogger: AuditLogger
        +authorize(request: HttpRequest) AuthorizationResult
        +extractUserContext(request: HttpRequest) UserContext
        +logAccess(userId: UserId, resource: Resource, action: Action, result: AccessResult) void
        -checkResourceAccess(userContext: UserContext, resource: Resource) boolean
    }
    
    class UserContext {
        +userId: UserId
        +username: string
        +roles: List~Role~
        +permissions: List~Permission~
        +sessionId: string
        +tokenExpiration: DateTime
    }
    
    TokenValidation --> AuthenticationService
    RoleMapping --> AuthorizationMiddleware
    AuthenticationService --> UserContext
    AuthorizationMiddleware --> UserContext
```

### 4.15 Monitoring & Logging - Class Diagram

```mermaid
---
config:
  layout: elk
  theme: redux-dark
---
classDiagram
    class LogCollector {
        -logBuffer: LogBuffer
        -logForwarder: LogForwarder
        -logParser: LogParser
        +collectLog(source: string, logEntry: LogEntry) void
        +collectBatch(logs: List~LogEntry~) void
        +flushLogs() void
        +setLogLevel(source: string, level: LogLevel) void
        +searchLogs(query: LogQuery) List~LogEntry~
        -parseLogEntry(rawLog: string) LogEntry
    }
    
    class MetricsCollector {
        -metricsRegistry: MetricsRegistry
        -timeSeriesDB: TimeSeriesDatabase
        -alertEvaluator: AlertEvaluator
        +recordMetric(name: string, value: float, tags: Map~string, string~) void
        +recordCounter(name: string, increment: int, tags: Map~string, string~) void
        +recordHistogram(name: string, value: float, tags: Map~string, string~) void
        +getMetric(name: string, timeRange: TimeRange) MetricSeries
        +evaluateAlerts() List~AlertEvent~
        -aggregateMetrics(metrics: List~Metric~, aggregationType: AggregationType) AggregatedMetric
    }
    
    class MonitoringDashboard {
        -dashboardRenderer: DashboardRenderer
        -widgetFactory: WidgetFactory
        -dataSource: MonitoringDataSource
        +createDashboard(config: DashboardConfig) DashboardId
        +updateDashboard(dashboardId: DashboardId, config: DashboardConfig) void
        +renderDashboard(dashboardId: DashboardId) DashboardView
        +addWidget(dashboardId: DashboardId, widget: Widget) WidgetId
        +getSystemOverview() SystemOverviewData
        -refreshWidgetData(widget: Widget) WidgetData
    }
    
    class AlertingEngine {
        -alertRules: AlertRuleStore
        -notificationService: NotificationService
        -alertHistory: AlertHistoryStore
        +createAlertRule(rule: AlertRule) AlertRuleId
        +updateAlertRule(ruleId: AlertRuleId, rule: AlertRule) void
        +evaluateRules() List~AlertEvent~
        +sendAlert(alert: AlertEvent) void
        +acknowledgeAlert(alertId: AlertId, userId: UserId) void
        +getActiveAlerts() List~ActiveAlert~
        -evaluateCondition(rule: AlertRule, currentMetrics: MetricSnapshot) boolean
    }
    
    class SystemHealthMonitor {
        -healthChecks: List~HealthCheck~
        -serviceRegistry: ServiceRegistry
        +performHealthCheck() SystemHealthStatus
        +registerHealthCheck(healthCheck: HealthCheck) void
        +getServiceStatus(serviceName: string) ServiceStatus
        +getSystemMetrics() SystemMetrics
        -checkServiceHealth(service: Service) ServiceHealthStatus
    }
    
    LogCollector --> MetricsCollector
    MetricsCollector --> MonitoringDashboard
    MonitoringDashboard --> AlertingEngine
    AlertingEngine --> SystemHealthMonitor
```

---

## Model danych (ERD)

```mermaid
---
config:
  layout: elk  
  theme: redux-dark
---
erDiagram
    EXPERIMENT {
        string  id
        string  name
        string  description
        string  goal_type
        string  created_by_user
        datetime created_at
        json    config_json
        string  tags
    }
    RUN {
        string  id
        string  experiment_id
        string  algorithm_version_id
        string  benchmark_instance_id
        int     seed
        string  status
        datetime start_time
        datetime end_time
        json    resource_usage_json
        string  environment_snapshot_id
    }
    METRIC {
        string  id
        string  run_id
        string  name
        float   value
        int     step
        datetime timestamp
    }
    ALGORITHM {
        string  id
        string  name
        string  type
        bool    is_builtin
        string  primary_publication_id
    }
    ALGORITHM_VERSION {
        string  id
        string  algorithm_id
        string  version
        string  plugin_location
        string  sdk_version
        string  status
    }
    BENCHMARK {
        string  id
        string  name
        string  description
        string  problem_type
        string  canonical_version
    }
    BENCHMARK_INSTANCE {
        string  id
        string  benchmark_id
        string  dataset_ref
        json    config_json
        float   best_known_value
    }
    PUBLICATION {
        string  id
        string  title
        string  authors
        int     year
        string  venue
        string  doi
        string  bibtex
        string  url
    }
    PUBLICATION_LINK {
        string  id
        string  publication_id
        string  entity_type
        string  entity_id
    }
    ENVIRONMENT_SNAPSHOT {
        string  id
        json    environment_json
    }
    
    EXPERIMENT        ||--o{ RUN                : has
    RUN               ||--o{ METRIC             : logs
    EXPERIMENT        }o--o{ BENCHMARK          : uses
    EXPERIMENT        }o--o{ ALGORITHM          : compares
    ALGORITHM         ||--o{ ALGORITHM_VERSION  : has
    BENCHMARK         ||--o{ BENCHMARK_INSTANCE : has
    ALGORITHM_VERSION ||--o{ RUN                : used_in
    BENCHMARK_INSTANCE||--o{ RUN                : evaluated_in
    ENVIRONMENT_SNAPSHOT ||--o{ RUN             : used_by
    PUBLICATION       ||--o{ PUBLICATION_LINK   : has
```

---

## Interfejsy API - implementacja

### 4.4 Python SDK dla pluginów algorytmów

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
import json

@dataclass
class ParameterConfiguration:
    """Konfiguracja parametrów dla pojedynczej ewaluacji"""
    parameters: Dict[str, Any]
    configuration_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'parameters': self.parameters,
            'configuration_id': self.configuration_id
        }

@dataclass
class EvaluationResult:
    """Wynik ewaluacji konfiguracji parametrów"""
    objective_value: float
    additional_metrics: Dict[str, float]
    evaluation_time: float
    success: bool
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'objective_value': self.objective_value,
            'additional_metrics': self.additional_metrics,
            'evaluation_time': self.evaluation_time,
            'success': self.success,
            'error_message': self.error_message
        }

@dataclass
class AlgorithmConfig:
    """Konfiguracja algorytmu HPO"""
    algorithm_params: Dict[str, Any]
    parameter_space: Dict[str, Any]
    optimization_direction: str  # 'minimize' or 'maximize'
    random_seed: Optional[int] = None
    
class IAlgorithmPlugin(ABC):
    """Interfejs dla pluginów algorytmów HPO"""
    
    @abstractmethod
    def init(self, config: AlgorithmConfig) -> None:
        """
        Inicjalizacja algorytmu z podaną konfiguracją
        
        Args:
            config: Konfiguracja algorytmu i przestrzeni parametrów
        """
        pass
    
    @abstractmethod
    def suggest(self, budget_remaining: int) -> ParameterConfiguration:
        """
        Zasugeruj następną konfigurację parametrów do ewaluacji
        
        Args:
            budget_remaining: Pozostały budżet ewaluacji
            
        Returns:
            Konfiguracja parametrów do przetestowania
        """
        pass
    
    @abstractmethod
    def observe(self, config: ParameterConfiguration, result: EvaluationResult) -> None:
        """
        Zaobserwuj wynik ewaluacji konfiguracji
        
        Args:
            config: Konfiguracja która została przetestowana
            result: Wynik ewaluacji tej konfiguracji
        """
        pass
    
    @abstractmethod
    def get_best_configuration(self) -> ParameterConfiguration:
        """
        Zwróć najlepszą dotychczas znalezioną konfigurację
        
        Returns:
            Najlepsza konfiguracja parametrów
        """
        pass
    
    @abstractmethod
    def cleanup(self) -> None:
        """Oczyść zasoby algorytmu"""
        pass

# Przykład implementacji - Random Search
class RandomSearchPlugin(IAlgorithmPlugin):
    """Implementacja algorytmu Random Search"""
    
    def __init__(self):
        self.config: Optional[AlgorithmConfig] = None
        self.best_config: Optional[ParameterConfiguration] = None
        self.best_score: Optional[float] = None
        self.observed_configs: List[ParameterConfiguration] = []
        self.observed_results: List[EvaluationResult] = []
        
    def init(self, config: AlgorithmConfig) -> None:
        self.config = config
        self.best_config = None
        self.best_score = None
        self.observed_configs = []
        self.observed_results = []
        
        # Ustaw generator losowy
        if config.random_seed is not None:
            import random
            random.seed(config.random_seed)
            import numpy as np
            np.random.seed(config.random_seed)
    
    def suggest(self, budget_remaining: int) -> ParameterConfiguration:
        import random
        
        parameters = {}
        for param_name, param_config in self.config.parameter_space.items():
            if param_config['type'] == 'uniform':
                parameters[param_name] = random.uniform(
                    param_config['low'], 
                    param_config['high']
                )
            elif param_config['type'] == 'choice':
                parameters[param_name] = random.choice(param_config['choices'])
            elif param_config['type'] == 'int':
                parameters[param_name] = random.randint(
                    param_config['low'], 
                    param_config['high']
                )
                
        return ParameterConfiguration(
            parameters=parameters,
            configuration_id=f"random_{len(self.observed_configs)}"
        )
    
    def observe(self, config: ParameterConfiguration, result: EvaluationResult) -> None:
        self.observed_configs.append(config)
        self.observed_results.append(result)
        
        if result.success:
            is_better = False
            if self.best_score is None:
                is_better = True
            elif self.config.optimization_direction == 'minimize':
                is_better = result.objective_value < self.best_score
            else:  # maximize
                is_better = result.objective_value > self.best_score
                
            if is_better:
                self.best_score = result.objective_value
                self.best_config = config
    
    def get_best_configuration(self) -> ParameterConfiguration:
        if self.best_config is None:
            raise RuntimeError("No successful evaluations observed yet")
        return self.best_config
    
    def cleanup(self) -> None:
        self.observed_configs.clear()
        self.observed_results.clear()
```

### 4.5 TrackingAPI Client SDK

```python
import requests
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class CreateRunRequest:
    experiment_id: str
    algorithm_version_id: str
    benchmark_instance_id: str
    seed: int
    environment_snapshot_id: Optional[str] = None

@dataclass
class MetricData:
    name: str
    value: float
    step: int
    timestamp: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

class TrackingClient:
    """Klient do komunikacji z Tracking Service"""
    
    def __init__(self, base_url: str, api_key: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        
        if api_key:
            self.session.headers.update({'Authorization': f'Bearer {api_key}'})
    
    def create_run(self, request: CreateRunRequest) -> str:
        """
        Utwórz nowy run eksperymentu
        
        Returns:
            run_id: Identyfikator utworzonego runu
        """
        response = self.session.post(
            f"{self.base_url}/api/v1/runs",
            json=asdict(request)
        )
        response.raise_for_status()
        return response.json()['run_id']
    
    def log_metrics(self, run_id: str, metrics: List[MetricData]) -> None:
        """Zaloguj metryki dla runu"""
        metrics_data = []
        for metric in metrics:
            metric_dict = asdict(metric)
            if metric_dict['timestamp']:
                metric_dict['timestamp'] = metric.timestamp.isoformat()
            metrics_data.append(metric_dict)
        
        response = self.session.post(
            f"{self.base_url}/api/v1/runs/{run_id}/metrics",
            json={'metrics': metrics_data}
        )
        response.raise_for_status()
    
    def update_run_status(self, run_id: str, status: str) -> None:
        """Zaktualizuj status runu"""
        response = self.session.patch(
            f"{self.base_url}/api/v1/runs/{run_id}/status",
            json={'status': status}
        )
        response.raise_for_status()
    
    def complete_run(self, run_id: str, final_result: Dict[str, Any]) -> None:
        """Oznacz run jako ukończony z finalnym wynikiem"""
        response = self.session.post(
            f"{self.base_url}/api/v1/runs/{run_id}/complete",
            json={'result': final_result}
        )
        response.raise_for_status()

# Przykład użycia TrackingClient
def example_usage():
    tracking = TrackingClient("http://localhost:8080", api_key="your-api-key")
    
    # Utwórz run
    run_request = CreateRunRequest(
        experiment_id="exp_123",
        algorithm_version_id="bayesian_opt_v1.0",
        benchmark_instance_id="rosenbrock_2d",
        seed=42
    )
    run_id = tracking.create_run(run_request)
    
    # Loguj metryki podczas eksperymentu
    metrics = [
        MetricData(name="best_score", value=0.85, step=10),
        MetricData(name="current_score", value=0.82, step=10),
        MetricData(name="evaluation_time", value=1.5, step=10)
    ]
    tracking.log_metrics(run_id, metrics)
    
    # Zakończ run
    tracking.complete_run(run_id, {
        "final_best_score": 0.92,
        "total_evaluations": 100,
        "convergence_achieved": True
    })
```

### 4.6 Worker Runtime - implementacja runu

```python
import asyncio
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass
import time

@dataclass
class RunExecutionConfig:
    run_id: str
    algorithm_version_id: str
    benchmark_instance_id: str
    seed: int
    budget: Dict[str, Any]
    timeout_seconds: int = 3600

class RunExecutor:
    """Executor odpowiedzialny za wykonanie pojedynczego runu"""
    
    def __init__(self, 
                 plugin_loader: 'PluginLoader',
                 benchmark_loader: 'BenchmarkLoader', 
                 tracking_client: TrackingClient,
                 logger: logging.Logger):
        self.plugin_loader = plugin_loader
        self.benchmark_loader = benchmark_loader
        self.tracking_client = tracking_client
        self.logger = logger
    
    async def execute_run(self, config: RunExecutionConfig) -> Dict[str, Any]:
        """
        Wykonaj pojedynczy run eksperymentu
        
        Returns:
            Wynik wykonania runu z metrykami
        """
        run_id = config.run_id
        start_time = time.time()
        
        try:
            # 1. Załaduj plugin algorytmu
            self.logger.info(f"Loading algorithm plugin: {config.algorithm_version_id}")
            algorithm_plugin = await self.plugin_loader.load_plugin(
                config.algorithm_version_id
            )
            
            # 2. Załaduj benchmark
            self.logger.info(f"Loading benchmark: {config.benchmark_instance_id}")
            benchmark = await self.benchmark_loader.load_benchmark(
                config.benchmark_instance_id
            )
            
            # 3. Inicjalizuj algorytm
            algorithm_config = AlgorithmConfig(
                algorithm_params=benchmark.get_default_algorithm_params(),
                parameter_space=benchmark.get_parameter_space(),
                optimization_direction=benchmark.get_optimization_direction(),
                random_seed=config.seed
            )
            algorithm_plugin.init(algorithm_config)
            
            # 4. Wykonaj pętlę optymalizacji
            evaluation_count = 0
            max_evaluations = config.budget.get('max_evaluations', 100)
            best_score = None
            
            while evaluation_count < max_evaluations:
                # Zasugeruj konfigurację
                suggested_config = algorithm_plugin.suggest(
                    max_evaluations - evaluation_count
                )
                
                # Ewaluuj konfigurację
                evaluation_result = await benchmark.evaluate(
                    suggested_config.parameters
                )
                
                # Przekaż wynik algorytmowi
                algorithm_plugin.observe(suggested_config, evaluation_result)
                
                # Zaloguj metryki
                metrics = [
                    MetricData(
                        name="objective_value",
                        value=evaluation_result.objective_value,
                        step=evaluation_count
                    ),
                    MetricData(
                        name="evaluation_time",
                        value=evaluation_result.evaluation_time,
                        step=evaluation_count
                    )
                ]
                
                # Dodaj dodatkowe metryki
                for metric_name, metric_value in evaluation_result.additional_metrics.items():
                    metrics.append(MetricData(
                        name=metric_name,
                        value=metric_value,
                        step=evaluation_count
                    ))
                
                await self.tracking_client.log_metrics(run_id, metrics)
                
                # Aktualizuj najlepszy wynik
                if best_score is None or evaluation_result.objective_value > best_score:
                    best_score = evaluation_result.objective_value
                
                evaluation_count += 1
                
                # Sprawdź timeout
                if time.time() - start_time > config.timeout_seconds:
                    self.logger.warning(f"Run {run_id} timed out after {config.timeout_seconds}s")
                    break
            
            # 5. Pobierz najlepszą konfigurację
            best_config = algorithm_plugin.get_best_configuration()
            
            # 6. Przygotuj wynik
            execution_result = {
                "success": True,
                "total_evaluations": evaluation_count,
                "best_score": best_score,
                "best_configuration": best_config.to_dict(),
                "execution_time": time.time() - start_time,
                "terminated_reason": "budget_exhausted" if evaluation_count >= max_evaluations else "timeout"
            }
            
            # 7. Oznacz run jako ukończony
            await self.tracking_client.complete_run(run_id, execution_result)
            
            return execution_result
            
        except Exception as e:
            self.logger.error(f"Run {run_id} failed: {str(e)}")
            
            # Oznacz run jako nieudany
            await self.tracking_client.update_run_status(run_id, "FAILED")
            
            return {
                "success": False,
                "error": str(e),
                "execution_time": time.time() - start_time
            }
        
        finally:
            # Oczyść zasoby
            if 'algorithm_plugin' in locals():
                algorithm_plugin.cleanup()
            if 'benchmark' in locals():
                await benchmark.cleanup()
```

---

## Wzorce architektoniczne

### 🏗️ Architektura
- **Styl:** Microservices z możliwością pakowania w monolit modułowy (PC)
- **Communication:** REST/GraphQL + gRPC między usługami
- **Messaging:** Message Broker (RabbitMQ/Kafka) dla asynchronicznych operacji

### 💾 Technologie
- **Database:** PostgreSQL (Results Store)
- **Object Storage:** S3/MinIO (artefakty, datasety)
- **Containerization:** Docker + docker-compose (PC) / Kubernetes (Cloud)
- **Plugins:** Python SDK z interfejsem IAlgorithmPlugin

### 🔄 Reprodukowalność
- **Configuration snapshots:** Pełna konfiguracja eksperymentu (JSON)
- **Version tracking:** Datasety, algorytmy, pluginy, obrazy kontenerów
- **Seed management:** Losowe seedy dla każdego runu
- **Environment snapshots:** Opis środowiska uruchomieniowego
- **Code references:** Commit hash/tag repozytorium lub wersja pluginu

---

## Wzorce projektowe w implementacji

### 4.7 Strategy Pattern - Algorytmy HPO

```python
from abc import ABC, abstractmethod
from enum import Enum

class OptimizationStrategy(Enum):
    RANDOM_SEARCH = "random_search"
    BAYESIAN_OPTIMIZATION = "bayesian_optimization"  
    GENETIC_ALGORITHM = "genetic_algorithm"
    GRID_SEARCH = "grid_search"

class AlgorithmFactory:
    """Factory do tworzenia instancji algorytmów HPO"""
    
    _algorithms = {
        OptimizationStrategy.RANDOM_SEARCH: RandomSearchPlugin,
        OptimizationStrategy.BAYESIAN_OPTIMIZATION: BayesianOptimizationPlugin,
        # Inne algorytmy...
    }
    
    @classmethod
    def create_algorithm(cls, strategy: OptimizationStrategy) -> IAlgorithmPlugin:
        """Utwórz instancję algorytmu na podstawie strategii"""
        if strategy not in cls._algorithms:
            raise ValueError(f"Unsupported optimization strategy: {strategy}")
        
        algorithm_class = cls._algorithms[strategy]
        return algorithm_class()
    
    @classmethod
    def register_algorithm(cls, strategy: OptimizationStrategy, 
                          algorithm_class: type) -> None:
        """Zarejestruj nowy algorytm"""
        cls._algorithms[strategy] = algorithm_class
```

### 4.8 Observer Pattern - Event System

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from enum import Enum

class EventType(Enum):
    RUN_STARTED = "run_started"
    RUN_COMPLETED = "run_completed"
    RUN_FAILED = "run_failed"
    EXPERIMENT_COMPLETED = "experiment_completed"

class Event:
    """Klasa bazowa dla zdarzeń systemowych"""
    
    def __init__(self, event_type: EventType, data: Dict[str, Any]):
        self.event_type = event_type
        self.data = data
        self.timestamp = datetime.now()

class EventObserver(ABC):
    """Interfejs dla obserwatorów zdarzeń"""
    
    @abstractmethod
    async def handle_event(self, event: Event) -> None:
        pass

class EventPublisher:
    """Publisher zdarzeń systemowych"""
    
    def __init__(self):
        self.observers: Dict[EventType, List[EventObserver]] = {}
    
    def subscribe(self, event_type: EventType, observer: EventObserver) -> None:
        """Subskrybuj zdarzenia danego typu"""
        if event_type not in self.observers:
            self.observers[event_type] = []
        self.observers[event_type].append(observer)
    
    def unsubscribe(self, event_type: EventType, observer: EventObserver) -> None:
        """Usuń subskrypcję"""
        if event_type in self.observers:
            self.observers[event_type].remove(observer)
    
    async def publish(self, event: Event) -> None:
        """Opublikuj zdarzenie do wszystkich obserwatorów"""
        if event.event_type in self.observers:
            for observer in self.observers[event.event_type]:
                try:
                    await observer.handle_event(event)
                except Exception as e:
                    # Log error but don't stop other observers
                    logging.error(f"Observer {observer} failed to handle event: {e}")

# Przykład implementacji obserwatora
class MetricsCollectorObserver(EventObserver):
    """Obserwator zbierający metryki z zdarzeń"""
    
    def __init__(self, metrics_service: 'MetricsService'):
        self.metrics_service = metrics_service
    
    async def handle_event(self, event: Event) -> None:
        if event.event_type == EventType.RUN_COMPLETED:
            # Zbierz metryki z ukończonego runu
            run_id = event.data['run_id']
            execution_time = event.data['execution_time']
            
            await self.metrics_service.record_metric(
                'run_execution_time', 
                execution_time,
                tags={'run_id': run_id}
            )
```

### 4.9 Repository Pattern - Dostęp do danych

```python
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
import asyncpg
from dataclasses import dataclass

@dataclass
class RunEntity:
    run_id: str
    experiment_id: str
    algorithm_version_id: str
    benchmark_instance_id: str
    seed: int
    status: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    resource_usage: Optional[Dict[str, Any]] = None

class IRunRepository(ABC):
    """Interfejs repozytorium dla encji Run"""
    
    @abstractmethod
    async def create(self, run: RunEntity) -> RunEntity:
        pass
    
    @abstractmethod
    async def get_by_id(self, run_id: str) -> Optional[RunEntity]:
        pass
    
    @abstractmethod
    async def update(self, run: RunEntity) -> RunEntity:
        pass
    
    @abstractmethod
    async def find_by_experiment(self, experiment_id: str) -> List[RunEntity]:
        pass

class PostgreSQLRunRepository(IRunRepository):
    """Implementacja repozytorium dla PostgreSQL"""
    
    def __init__(self, connection_pool: asyncpg.Pool):
        self.pool = connection_pool
    
    async def create(self, run: RunEntity) -> RunEntity:
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO runs (run_id, experiment_id, algorithm_version_id, 
                                benchmark_instance_id, seed, status, start_time)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
            """, run.run_id, run.experiment_id, run.algorithm_version_id,
                run.benchmark_instance_id, run.seed, run.status, run.start_time)
        
        return run
    
    async def get_by_id(self, run_id: str) -> Optional[RunEntity]:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT run_id, experiment_id, algorithm_version_id,
                       benchmark_instance_id, seed, status, start_time, 
                       end_time, resource_usage_json
                FROM runs WHERE run_id = $1
            """, run_id)
            
            if row:
                return RunEntity(
                    run_id=row['run_id'],
                    experiment_id=row['experiment_id'],
                    algorithm_version_id=row['algorithm_version_id'],
                    benchmark_instance_id=row['benchmark_instance_id'],
                    seed=row['seed'],
                    status=row['status'],
                    start_time=row['start_time'],
                    end_time=row['end_time'],
                    resource_usage=row['resource_usage_json']
                )
            return None
    
    async def update(self, run: RunEntity) -> RunEntity:
        async with self.pool.acquire() as conn:
            await conn.execute("""
                UPDATE runs 
                SET status = $2, end_time = $3, resource_usage_json = $4
                WHERE run_id = $1
            """, run.run_id, run.status, run.end_time, run.resource_usage)
        
        return run
    
    async def find_by_experiment(self, experiment_id: str) -> List[RunEntity]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT run_id, experiment_id, algorithm_version_id,
                       benchmark_instance_id, seed, status, start_time,
                       end_time, resource_usage_json
                FROM runs WHERE experiment_id = $1
                ORDER BY start_time
            """, experiment_id)
            
            return [RunEntity(
                run_id=row['run_id'],
                experiment_id=row['experiment_id'],
                algorithm_version_id=row['algorithm_version_id'],
                benchmark_instance_id=row['benchmark_instance_id'],
                seed=row['seed'],
                status=row['status'],
                start_time=row['start_time'],
                end_time=row['end_time'],
                resource_usage=row['resource_usage_json']
            ) for row in rows]
```

---

## Deployment patterns

### 🖥️ PC-First (Development/Small teams)
```yaml
# docker-compose.yml przykład
services:
  web-ui: # Static files / Node.js dev server
  api-gateway: # Single backend container
  orchestrator: # Single instance
  worker: # 1-N containers
  postgres: # Local database
  minio: # Local object storage
  rabbitmq: # Message broker
```

### ☁️ Cloud-Ready (Production/Scale)
```yaml
# Kubernetes example
- API Gateway: Load balanced, multiple replicas
- Core Services: Microservices, auto-scaling
- Workers: Job-based pods, HPA
- Database: Managed PostgreSQL (RDS/CloudSQL)
- Object Storage: S3/GCS/Azure Blob
- Message Broker: Managed (SQS/Pub-Sub/EventHub)
```

---

## Bezpieczeństwo na poziomie kodu

### 🔐 Input Validation

```python
from pydantic import BaseModel, validator
from typing import Dict, Any, List

class ExperimentConfigValidator(BaseModel):
    """Walidator konfiguracji eksperymentu"""
    
    experiment_id: str
    name: str
    algorithms: List[str]
    benchmarks: List[str]
    budget: Dict[str, Any]
    seeds: List[int]
    
    @validator('experiment_id')
    def validate_experiment_id(cls, v):
        if not v or len(v) < 3:
            raise ValueError('Experiment ID must be at least 3 characters')
        return v
    
    @validator('algorithms')
    def validate_algorithms(cls, v):
        if not v:
            raise ValueError('At least one algorithm must be specified')
        return v
    
    @validator('budget')
    def validate_budget(cls, v):
        if 'max_evaluations' not in v or v['max_evaluations'] <= 0:
            raise ValueError('Budget must specify positive max_evaluations')
        return v

# Użycie walidatora
def validate_experiment_config(config_data: Dict[str, Any]) -> ExperimentConfigValidator:
    try:
        return ExperimentConfigValidator(**config_data)
    except Exception as e:
        raise ValueError(f"Invalid experiment configuration: {e}")
```

### 🛡️ Plugin Security

```python
import subprocess
import tempfile
import os
from typing import Any, Dict
import resource

class SecurePluginExecutor:
    """Bezpieczne wykonywanie pluginów w izolowanym środowisku"""
    
    def __init__(self, max_memory_mb: int = 512, max_cpu_time_s: int = 300):
        self.max_memory = max_memory_mb * 1024 * 1024  # Convert to bytes
        self.max_cpu_time = max_cpu_time_s
    
    def set_resource_limits(self):
        """Ustaw limity zasobów dla procesu"""
        # Limit pamięci
        resource.setrlimit(resource.RLIMIT_AS, (self.max_memory, self.max_memory))
        
        # Limit czasu CPU
        resource.setrlimit(resource.RLIMIT_CPU, (self.max_cpu_time, self.max_cpu_time))
        
        # Limit liczby plików
        resource.setrlimit(resource.RLIMIT_NOFILE, (100, 100))
    
    def execute_plugin_method(self, plugin_code: str, method_name: str, 
                            args: Dict[str, Any]) -> Any:
        """Wykonaj metodę pluginu w bezpiecznym środowisku"""
        
        # Utwórz tymczasowy plik z kodem pluginu
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(plugin_code)
            plugin_file = f.name
        
        try:
            # Wykonaj plugin w subprocess z ograniczeniami
            cmd = ['python', plugin_file, method_name, str(args)]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.max_cpu_time,
                preexec_fn=self.set_resource_limits
            )
            
            if result.returncode != 0:
                raise RuntimeError(f"Plugin execution failed: {result.stderr}")
            
            return result.stdout
            
        finally:
            # Usuń tymczasowy plik
            os.unlink(plugin_file)
```

---

## Powiązane dokumenty

- **Poprzedni poziom**: [Komponenty (C4-3)](c3-components.md)
- **Kontekst**: [Kontekst (C4-1)](c1-context.md), [Kontenery (C4-2)](c2-containers.md)
- **Wymagania**: [Functional Requirements](../requirements/functional-requirements.md), [Use Cases](../requirements/use-cases.md)
- **Design**: [Data Model](../design/data-model.md), [Design Decisions](../design/design-decisions.md)
- **Deployment**: [Deployment Guide](../operations/deployment-guide.md)
