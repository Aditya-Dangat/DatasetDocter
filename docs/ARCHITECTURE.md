# DatasetDoctor Architecture

## System Overview

DatasetDoctor is a multi-agent system that uses specialized AI agents to diagnose and fix data quality issues.

```
┌─────────────────────────────────────────────────────────────┐
│                    DatasetDoctor System                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────┐
        │     OrchestratorAgent (Manager)     │
        │  - Coordinates all agents            │
        │  - Manages workflow                  │
        │  - Handles observability             │
        └─────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  Ingestor    │    │   Scanner    │    │    Fixer     │
│   Agent      │───▶│   Agent      │───▶│   Agent      │
│              │    │              │    │              │
│ Loads data   │    │ Finds issues │    │ Fixes issues │
└──────────────┘    └──────────────┘    └──────────────┘
                              │
                              ▼
                    ┌──────────────┐
                    │  Validator   │
                    │   Agent      │
                    │              │
                    │ Validates    │
                    │   fixes      │
                    └──────────────┘
                              │
                              ▼
                    ┌──────────────┐
                    │  Reporter    │
                    │   Agent      │
                    │              │
                    │ Generates    │
                    │   reports    │
                    └──────────────┘
```

## Agent Workflow

```
User Uploads Dataset
        │
        ▼
┌───────────────────┐
│  IngestorAgent    │  Loads and validates dataset
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│  ScannerAgent     │  Detects issues:
│                   │  - Missing values
│                   │  - Type inconsistencies
│                   │  - Duplicates
│                   │  - Outliers
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│  FixerAgent       │  Applies fixes:
│                   │  - Imputation
│                   │  - Type conversion
│                   │  - Duplicate removal
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│  ValidatorAgent   │  Re-scans to verify fixes
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│  ReporterAgent    │  Generates:
│                   │  - Cleaned dataset
│                   │  - HTML report
│                   │  - JSON report
│                   │  - Python script
└───────────────────┘
```

## Component Architecture

### Core Components

```
┌─────────────────────────────────────────────────────────┐
│                      Core Layer                           │
├─────────────────────────────────────────────────────────┤
│  Dataset          │  DiagnosticReport  │  Config         │
│  - Data wrapper   │  - Issue tracking  │  - Settings     │
│  - Metadata       │  - Fix tracking    │  - Paths        │
└─────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────┐
│                    Agent Layer                           │
├─────────────────────────────────────────────────────────┤
│  Orchestrator │ Ingestor │ Scanner │ Fixer │ Validator │
│               │ Reporter │         │       │           │
└─────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────┐
│                  Support Layer                           │
├─────────────────────────────────────────────────────────┤
│  LLM (Gemini) │ MCP Tools │ Memory │ Observability     │
│               │           │         │ - Logging         │
│               │           │         │ - Tracing          │
│               │           │         │ - Metrics          │
└─────────────────────────────────────────────────────────┘
```

## MCP Tools Integration

```
┌─────────────────────────────────────────────────────────┐
│                  MCP Tool Registry                      │
├─────────────────────────────────────────────────────────┤
│  Data Tools (7)    │  Validation (2)  │  File Tools (5) │
│  - detect_missing  │  - validate_schema│  - read_csv     │
│  - impute_median  │  - check_quality │  - write_csv    │
│  - convert_numeric│                  │  - get_file_info │
│  - remove_dups    │                  │  - read_json     │
│  - detect_outliers│                  │  - write_json    │
│  - get_stats      │                  │                  │
└─────────────────────────────────────────────────────────┘
                              │
                              ▼
                    Used by Agents
```

## Memory & Session Management

```
┌─────────────────────────────────────────────────────────┐
│              Memory & Context Management                 │
├─────────────────────────────────────────────────────────┤
│  SessionService          │  MemoryBank                  │
│  - Session tracking      │  - Learned patterns          │
│  - State management      │  - Common fixes              │
│  - Workflow state        │  - User preferences          │
│                          │                              │
│  ContextManager          │  A2A Protocol                │
│  - Dataset summarization │  - Agent communication       │
│  - Context compaction    │  - Message routing          │
└─────────────────────────────────────────────────────────┘
```

## Observability Stack

```
┌─────────────────────────────────────────────────────────┐
│                    Observability                         │
├─────────────────────────────────────────────────────────┤
│  StructuredLogger        │  Tracer                      │
│  - JSON logs             │  - Trace IDs                 │
│  - Contextual info       │  - Span tracking             │
│  - Error tracking        │  - Performance tracking       │
│                          │                              │
│  MetricsCollector        │                              │
│  - Operation timing      │                              │
│  - Success rates         │                              │
│  - Resource usage        │                              │
└─────────────────────────────────────────────────────────┘
```

## Data Flow

```
User Upload
    │
    ▼
┌──────────────┐
│  Flask UI    │  Receives file upload
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Orchestrator │  Creates session, starts trace
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Ingestor    │  Loads dataset → Dataset object
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Scanner     │  Scans dataset → List[Issue]
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Fixer       │  Applies fixes → List[Fix]
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Validator   │  Re-validates → ValidationResult
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Reporter    │  Generates reports → ReportFiles
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Flask UI    │  Returns JSON response
└──────────────┘
```

## Technology Stack

```
┌─────────────────────────────────────────────────────────┐
│                    Technology Stack                      │
├─────────────────────────────────────────────────────────┤
│  Backend:                                                │
│  - Python 3.11                                           │
│  - Flask (Web Framework)                                │
│  - Pandas (Data Processing)                             │
│                                                          │
│  AI/ML:                                                  │
│  - Google Gemini API (LLM)                              │
│  - Vertex AI (Optional)                                 │
│                                                          │
│  Frontend:                                               │
│  - HTML5, CSS3, JavaScript                              │
│  - Anime.js (Animations)                                │
│                                                          │
│  Infrastructure:                                         │
│  - Docker (Containerization)                            │
│  - Google Cloud Run (Deployment)                        │
│  - Cloud Build (CI/CD)                                  │
└─────────────────────────────────────────────────────────┘
```

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Cloud Run Deployment                  │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  User Request                                            │
│      │                                                   │
│      ▼                                                   │
│  ┌─────────────┐                                         │
│  │ Cloud Run   │  Auto-scales based on traffic          │
│  │  Service    │  - 0 to N instances                   │
│  └─────┬───────┘  - HTTPS enabled                       │
│        │                                                 │
│        ▼                                                 │
│  ┌─────────────┐                                         │
│  │  Container  │  Docker container                      │
│  │  (DatasetDoctor)│  - Flask app                       │
│  └─────┬───────┘  - All dependencies                    │
│        │                                                 │
│        ▼                                                 │
│  ┌─────────────┐                                         │
│  │  Storage    │  Ephemeral storage                     │
│  │  (uploads/  │  - Files cleaned automatically         │
│  │   outputs/) │                                        │
│  └─────────────┘                                         │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## Key Design Principles

1. **Multi-Agent Architecture**: Specialized agents for each task
2. **Separation of Concerns**: Each agent has a single responsibility
3. **Observability First**: Built-in logging, tracing, and metrics
4. **Tool-Based Operations**: MCP-compliant tools for reusability
5. **Memory & Context**: Session and memory management for learning
6. **Scalable Design**: Cloud-ready with Docker and auto-scaling

