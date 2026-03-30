import random
from datetime import datetime, timedelta, timezone

from passlib.context import CryptContext
from sqlalchemy.orm import Session

from backend.core.database import SessionLocal, Base, engine
from backend.features.user.model import User
from backend.features.project.model import Project
from backend.features.project.attachment.model import ProjectAttachment
from backend.features.architecture_decision.model import ArchitectureDecision
from backend.features.architecture_decision.status.model import Status
from backend.features.architecture_decision.fields.model import ArchitectureDecisionFieldValue
from backend.features.documentation_template.model import DocumentationTemplate
from backend.features.documentation_template.fields.model import DocumentationTemplateField
from backend.features.architecture_decision.history.model import ArchitectureDecisionHistory
from backend.features.project.enum import PriorityLevel
from backend.features.architecture_decision.history.service import DecisionHistoryService


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

TEST_USER_EMAIL = "test@test.com"
TEST_USER_PASSWORD = "test1234"


SEED_PROJECTS = [
    {
        "name": "Insights",
        "description": "Central analytics and reporting platform for product and usage metrics, providing near-real-time dashboards and self-service insights for internal teams.",
        "tags": ["analytics", "reporting", "dashboards", "internal", "data-platform"],
        "icon": "chart-line",
        "priority": PriorityLevel.MEDIUM,
        "color": "#2563eb",
    },
    {
        "name": "Discovery",
        "description": "Service for automated discovery, cataloging, and ownership tracking of internal services and APIs, including dependency graphs.",
        "tags": ["platform", "inventory", "service-discovery", "internal", "governance"],
        "icon": "search",
        "priority": PriorityLevel.HIGH,
        "color": "#7c3aed",
    },
    {
        "name": "Memory",
        "description": "Context and session memory layer for AI assistants to preserve conversation state, user preferences, and relevant architectural events.",
        "tags": ["ml", "context", "assistant", "platform", "state"],
        "icon": "database",
        "priority": PriorityLevel.MEDIUM,
        "color": "#0ea5e9",
    },
    {
        "name": "Governance",
        "description": "Policy and compliance monitoring suite for services, validating API standards, security rules, and audit readiness.",
        "tags": ["security", "compliance", "policies", "platform", "audit"],
        "icon": "shield",
        "priority": PriorityLevel.CRITICAL,
        "color": "#dc2626",
    },
    {
        "name": "LLMEval",
        "description": "Evaluation pipeline for generative AI models measuring response quality, hallucination rate, latency, and cost per request.",
        "tags": ["ml", "evaluation", "llm", "internal", "quality"],
        "icon": "microchip-ai",
        "priority": PriorityLevel.CRITICAL,
        "color": "#9333ea",
    },
    {
        "name": "Radar",
        "description": "Technology radar for architectural decisions, tracking adoption, maturity, and responsible teams with periodic reviews.",
        "tags": ["architecture", "tech-radar", "visibility", "internal", "decision-log"],
        "icon": "globe",
        "priority": PriorityLevel.LOW,
        "color": "#4b5563",
    },
    {
        "name": "Catalogue",
        "description": "Self-service internal service catalogue for requesting infrastructure, environments, and deployments with consistent metadata.",
        "tags": ["platform", "self-service", "catalog", "internal", "infrastructure"],
        "icon": "sitemap",
        "priority": PriorityLevel.MEDIUM,
        "color": "#0891b2",
    },
    {
        "name": "Outreach",
        "description": "External product communication suite for customer updates, release notes, and marketing campaigns with multi-channel publishing.",
        "tags": ["marketing", "customer-facing", "release-notes", "content", "external"],
        "icon": "megaphone",
        "priority": PriorityLevel.LOW,
        "color": "#d97706",
    },
]

SEED_STATUSES = [
    {"name": "Proposed", "color": "#dfe6f3", "position": 0},
    {"name": "Accepted", "color": "#dcf2e4", "position": 1},
    {"name": "Rejected", "color": "#fbdedf", "position": 2},
]

SEED_TEMPLATES = [
    {
        "name": "ADR – Nygard",
        "description": "Architecture Decision Record following Michael Nygard’s lightweight ADR structure.",
        "fields": [
            {"name": "Title", "isRequired": True},
            {"name": "Status", "isRequired": True},
            {"name": "Context", "isRequired": True},
            {"name": "Decision", "isRequired": True},
            {"name": "Consequences", "isRequired": False},
        ],
    },
    {
        "name": "Tyree & Ackerman Decision Template",
        "description": "Richer decision template capturing rationale, alternatives, and implications.",
        "fields": [
            {"name": "Issue", "isRequired": True},
            {"name": "Decision", "isRequired": True},
            {"name": "Status", "isRequired": True},
            {"name": "Assumptions", "isRequired": True},
            {"name": "Alternatives", "isRequired": True},
            {"name": "Arguments", "isRequired": True},
            {"name": "Implications", "isRequired": True},
        ],
    },
    {
        "name": "MADR – Markdown ADR",
        "description": "Markdown ADR variant with explicit options, drivers, and outcome.",
        "fields": [
            {"name": "Title", "isRequired": True},
            {"name": "Status", "isRequired": True},
            {"name": "Context and Problem Statement", "isRequired": True},
            {"name": "Decision Drivers", "isRequired": True},
            {"name": "Considered Options", "isRequired": True},
            {"name": "Decision Outcome", "isRequired": True},
            {"name": "Consequences", "isRequired": True},
        ],
    },
]

SEED_DECISIONS = [
    {
        "project_name": "Insights",
        "template_name": "ADR – Nygard",
        "title": "Introduce event-driven ingestion with Kafka",
        "status": "Accepted",
        "fields": [
            {"field_name": "Title", "value": "Introduce event-driven ingestion with Kafka"},
            {"field_name": "Status", "value": "Accepted"},
            {"field_name": "Context", "value": "Batch ETL causes latency > 30 minutes; product teams require dashboards within 5 minutes."},
            {"field_name": "Decision", "value": "Adopt Kafka for streaming ingestion and replace nightly ETL with continuous processing."},
            {"field_name": "Consequences", "value": "Higher operational complexity, but near-real-time insights and horizontal scalability."},
        ],
    },
    {
        "project_name": "Insights",
        "template_name": "Tyree & Ackerman Decision Template",
        "title": "Adopt dbt for analytics transformations",
        "status": "Proposed",
        "fields": [
            {"field_name": "Issue", "value": "SQL transformations are duplicated across teams and hard to test."},
            {"field_name": "Decision", "value": "Standardize on dbt for versioned, tested transformations in CI/CD."},
            {"field_name": "Status", "value": "Proposed"},
            {"field_name": "Assumptions", "value": "Teams can maintain models in Git and accept code review workflow."},
            {"field_name": "Alternatives", "value": "Keep ad-hoc SQL, use Airflow DAG macros, or build custom transformation framework."},
            {"field_name": "Arguments", "value": "dbt provides lineage, tests, docs, and fits existing GitOps."},
            {"field_name": "Implications", "value": "Requires onboarding and model governance; improves reliability and reuse."},
        ],
    },
    {
        "project_name": "Insights",
        "template_name": "MADR – Markdown ADR",
        "title": "Use Trino as federated query engine",
        "status": "Accepted",
        "fields": [
            {"field_name": "Title", "value": "Use Trino as federated query engine"},
            {"field_name": "Status", "value": "Accepted"},
            {"field_name": "Context and Problem Statement", "value": "Analysts need to join data across S3, Postgres, and ClickHouse without copy jobs."},
            {"field_name": "Decision Drivers", "value": "Low latency, ANSI SQL support, multiple connectors, strong community."},
            {"field_name": "Considered Options", "value": "PrestoDB, Spark SQL over lake, custom federation using ETL."},
            {"field_name": "Decision Outcome", "value": "Adopt Trino cluster with S3, Postgres, ClickHouse connectors."},
            {"field_name": "Consequences", "value": "New cluster to operate; simplifies cross-source analytics and reduces ETL."},
        ],
    },
    {
        "project_name": "Insights",
        "template_name": "ADR – Nygard",
        "title": "Standardize metric definitions via semantic layer",
        "status": "Proposed",
        "fields": [
            {"field_name": "Title", "value": "Standardize metric definitions via semantic layer"},
            {"field_name": "Status", "value": "Proposed"},
            {"field_name": "Context", "value": "Different teams compute KPIs differently, leading to inconsistent reports."},
            {"field_name": "Decision", "value": "Introduce a shared semantic layer for certified metrics and dimensions."},
            {"field_name": "Consequences", "value": "Initial modeling effort; consistent KPI usage across dashboards."},
        ],
    },
    {
        "project_name": "Insights",
        "template_name": "Tyree & Ackerman Decision Template",
        "title": "Partition ClickHouse by tenant",
        "status": "Accepted",
        "fields": [
            {"field_name": "Issue", "value": "Single shared partitions cause noisy neighbors and slow queries."},
            {"field_name": "Decision", "value": "Partition core fact tables by tenant_id and month."},
            {"field_name": "Status", "value": "Accepted"},
            {"field_name": "Assumptions", "value": "Tenants are stable and query patterns align with time windows."},
            {"field_name": "Alternatives", "value": "Shard by hash, keep single partition, or move to BigQuery."},
            {"field_name": "Arguments", "value": "Tenant partitions isolate workloads and improve pruning."},
            {"field_name": "Implications", "value": "More partitions to manage; improved P95 query latency."},
        ],
    },
    {
        "project_name": "Discovery",
        "template_name": "ADR – Nygard",
        "title": "Adopt Consul for service discovery",
        "status": "Accepted",
        "fields": [
            {"field_name": "Title", "value": "Adopt Consul for service discovery"},
            {"field_name": "Status", "value": "Accepted"},
            {"field_name": "Context", "value": "Static endpoints break during blue/green deployments and autoscaling."},
            {"field_name": "Decision", "value": "Use Consul as central registry with health checks and DNS interface."},
            {"field_name": "Consequences", "value": "Adds infrastructure component; improves resilience and dynamic routing."},
        ],
    },
    {
        "project_name": "Discovery",
        "template_name": "Tyree & Ackerman Decision Template",
        "title": "Model ownership via team registry",
        "status": "Proposed",
        "fields": [
            {"field_name": "Issue", "value": "Services lack clear owners, slowing incident response."},
            {"field_name": "Decision", "value": "Integrate a team registry and require owner metadata for each service."},
            {"field_name": "Status", "value": "Proposed"},
            {"field_name": "Assumptions", "value": "Teams will maintain metadata as part of CI checks."},
            {"field_name": "Alternatives", "value": "Manual wiki tracking or CMDB-only ownership."},
            {"field_name": "Arguments", "value": "Automated enforcement yields up-to-date ownership for on-call."},
            {"field_name": "Implications", "value": "Needs governance and tooling; reduces MTTR."},
        ],
    },
    {
        "project_name": "Discovery",
        "template_name": "MADR – Markdown ADR",
        "title": "Use OpenTelemetry for dependency tracing",
        "status": "Accepted",
        "fields": [
            {"field_name": "Title", "value": "Use OpenTelemetry for dependency tracing"},
            {"field_name": "Status", "value": "Accepted"},
            {"field_name": "Context and Problem Statement", "value": "Discovery accuracy limited without runtime traces of cross-service calls."},
            {"field_name": "Decision Drivers", "value": "Vendor-neutral, SDK coverage, compatible with existing Grafana Tempo."},
            {"field_name": "Considered Options", "value": "Jaeger SDK, proprietary APM, log-based inference."},
            {"field_name": "Decision Outcome", "value": "Instrument services with OpenTelemetry and export traces to Tempo."},
            {"field_name": "Consequences", "value": "Requires rollout plan; boosts topology correctness and change impact analysis."},
        ],
    },
    {
        "project_name": "Discovery",
        "template_name": "ADR – Nygard",
        "title": "Cache catalog results in Redis",
        "status": "Rejected",
        "fields": [
            {"field_name": "Title", "value": "Cache catalog results in Redis"},
            {"field_name": "Status", "value": "Rejected"},
            {"field_name": "Context", "value": "UI requests cause spikes; caching considered to reduce DB load."},
            {"field_name": "Decision", "value": "Do not add Redis now; optimize queries and add indexes first."},
            {"field_name": "Consequences", "value": "Lower operational overhead; may revisit if load increases."},
        ],
    },
    {
        "project_name": "Discovery",
        "template_name": "Tyree & Ackerman Decision Template",
        "title": "Store service metadata in Postgres",
        "status": "Accepted",
        "fields": [
            {"field_name": "Issue", "value": "Current JSON-file based storage lacks concurrency and querying."},
            {"field_name": "Decision", "value": "Persist normalized metadata in Postgres with JSONB extension."},
            {"field_name": "Status", "value": "Accepted"},
            {"field_name": "Assumptions", "value": "Metadata volume stays under 50M rows with acceptable indexing cost."},
            {"field_name": "Alternatives", "value": "MongoDB, Elastic-only storage, or S3 + Athena."},
            {"field_name": "Arguments", "value": "Postgres offers strong consistency and familiar ops."},
            {"field_name": "Implications", "value": "Schema migrations needed; enables ad-hoc queries and joins."},
        ],
    },
    {
        "project_name": "Memory",
        "template_name": "ADR – Nygard",
        "title": "Use vector store for semantic memory",
        "status": "Accepted",
        "fields": [
            {"field_name": "Title", "value": "Use vector store for semantic memory"},
            {"field_name": "Status", "value": "Accepted"},
            {"field_name": "Context", "value": "Assistants need similarity search over past conversations and documents."},
            {"field_name": "Decision", "value": "Adopt pgvector-backed Postgres for embeddings and semantic retrieval."},
            {"field_name": "Consequences", "value": "Slightly higher DB load; unified operational stack."},
        ],
    },
    {
        "project_name": "Memory",
        "template_name": "Tyree & Ackerman Decision Template",
        "title": "Encrypt memory payloads at rest",
        "status": "Proposed",
        "fields": [
            {"field_name": "Issue", "value": "Long-lived PII in memory store increases compliance risk."},
            {"field_name": "Decision", "value": "Apply envelope encryption for all stored memory blobs."},
            {"field_name": "Status", "value": "Proposed"},
            {"field_name": "Assumptions", "value": "Key management via Vault is available organization-wide."},
            {"field_name": "Alternatives", "value": "Rely on disk encryption only or store no PII."},
            {"field_name": "Arguments", "value": "Envelope encryption protects backups and reduces blast radius."},
            {"field_name": "Implications", "value": "Adds latency to writes; improves auditability."},
        ],
    },
    {
        "project_name": "Memory",
        "template_name": "MADR – Markdown ADR",
        "title": "Define memory retention tiers",
        "status": "Accepted",
        "fields": [
            {"field_name": "Title", "value": "Define memory retention tiers"},
            {"field_name": "Status", "value": "Accepted"},
            {"field_name": "Context and Problem Statement", "value": "One-size retention causes high costs and unclear UX."},
            {"field_name": "Decision Drivers", "value": "Cost control, user privacy, predictable retrieval."},
            {"field_name": "Considered Options", "value": "Single TTL, user-defined TTL only, or tiered retention."},
            {"field_name": "Decision Outcome", "value": "Introduce short-, mid-, long-term tiers with explicit TTLs."},
            {"field_name": "Consequences", "value": "Requires UI support; lowers storage cost and clarifies behavior."},
        ],
    },
    {
        "project_name": "Memory",
        "template_name": "ADR – Nygard",
        "title": "Use async processing for summarization",
        "status": "Rejected",
        "fields": [
            {"field_name": "Title", "value": "Use async processing for summarization"},
            {"field_name": "Status", "value": "Rejected"},
            {"field_name": "Context", "value": "Summaries at write-time add latency to chat responses."},
            {"field_name": "Decision", "value": "Keep synchronous summaries for now to guarantee consistency."},
            {"field_name": "Consequences", "value": "Slight latency overhead; simpler consistency model."},
        ],
    },
    {
        "project_name": "Memory",
        "template_name": "Tyree & Ackerman Decision Template",
        "title": "Expose memory via internal SDK",
        "status": "Accepted",
        "fields": [
            {"field_name": "Issue", "value": "Multiple clients integrate memory inconsistently."},
            {"field_name": "Decision", "value": "Provide a typed internal SDK with caching and retries."},
            {"field_name": "Status", "value": "Accepted"},
            {"field_name": "Assumptions", "value": "All consumers can migrate within two releases."},
            {"field_name": "Alternatives", "value": "Keep REST-only, generate clients per language."},
            {"field_name": "Arguments", "value": "SDK reduces integration bugs and standardizes telemetry."},
            {"field_name": "Implications", "value": "SDK maintenance needed; lowers support burden."},
        ],
    },
    {
        "project_name": "Governance",
        "template_name": "ADR – Nygard",
        "title": "Centralize policy definitions in Git",
        "status": "Accepted",
        "fields": [
            {"field_name": "Title", "value": "Centralize policy definitions in Git"},
            {"field_name": "Status", "value": "Accepted"},
            {"field_name": "Context", "value": "Policies are spread over wikis and repos, causing drift."},
            {"field_name": "Decision", "value": "Move all service policies into a single versioned Git repository."},
            {"field_name": "Consequences", "value": "Better traceability; requires PR-based governance."},
        ],
    },
    {
        "project_name": "Governance",
        "template_name": "Tyree & Ackerman Decision Template",
        "title": "Run policy linter in CI",
        "status": "Accepted",
        "fields": [
            {"field_name": "Issue", "value": "Teams miss policy updates until audits."},
            {"field_name	": "Decision", "value": "Add mandatory policy linting step to CI pipelines."},
            {"field_name": "Status", "value": "Accepted"},
            {"field_name": "Assumptions", "value": "CI runners can access policy repo and linter container."},
            {"field_name": "Alternatives", "value": "Manual review or periodic batch scans."},
            {"field_name": "Arguments", "value": "Shift-left enforcement catches violations early."},
            {"field_name": "Implications", "value": "CI time increases slightly; compliance improves."},
        ],
    },
    {
        "project_name": "Governance",
        "template_name": "MADR – Markdown ADR",
        "title": "Adopt OPA for runtime authorization",
        "status": "Proposed",
        "fields": [
            {"field_name": "Title", "value": "Adopt OPA for runtime authorization"},
            {"field_name": "Status", "value": "Proposed"},
            {"field_name": "Context and Problem Statement", "value": "Authorization rules are duplicated across services."},
            {"field_name": "Decision Drivers", "value": "Consistent policy evaluation, language-agnostic integration."},
            {"field_name": "Considered Options", "value": "Custom middleware, JWT claims only, or OPA sidecar."},
            {"field_name": "Decision Outcome", "value": "Pilot OPA sidecars for critical services."},
            {"field_name": "Consequences", "value": "Needs rollout and training; improves uniform enforcement."},
        ],
    },
    {
        "project_name": "Governance",
        "template_name": "ADR – Nygard",
        "title": "Standardize API versioning rules",
        "status": "Accepted",
        "fields": [
            {"field_name": "Title", "value": "Standardize API versioning rules"},
            {"field_name": "Status", "value": "Accepted"},
            {"field_name": "Context", "value": "Breaking changes reach consumers without notice."},
            {"field_name": "Decision", "value": "Enforce semantic versioning and deprecation windows."},
            {"field_name": "Consequences", "value": "Requires tooling support; reduces consumer incidents."},
        ],
    },
    {
        "project_name": "Governance",
        "template_name": "Tyree & Ackerman Decision Template",
        "title": "Track audits in decision log",
        "status": "Rejected",
        "fields": [
            {"field_name": "Issue", "value": "Audit evidence scattered across ticketing systems."},
            {"field_name": "Decision", "value": "Do not couple audits to decision log; keep in GRC tool."},
            {"field_name": "Status", "value": "Rejected"},
            {"field_name": "Assumptions", "value": "GRC tool remains primary source of truth."},
            {"field_name": "Alternatives", "value": "Mirror evidence in both systems."},
            {"field_name": "Arguments", "value": "Duplication increases maintenance and inconsistency."},
            {"field_name": "Implications", "value": "Decision log stays lightweight; audits stay centralized."},
        ],
    },
    {
        "project_name": "LLMEval",
        "template_name": "ADR – Nygard",
        "title": "Define standard LLM evaluation metrics",
        "status": "Accepted",
        "fields": [
            {"field_name": "Title", "value": "Define standard LLM evaluation metrics"},
            {"field_name": "Status", "value": "Accepted"},
            {"field_name": "Context", "value": "Teams use incompatible metrics making model comparison impossible."},
            {"field_name": "Decision", "value": "Adopt a unified suite: EM, BLEU, cost/request, hallucination rate."},
            {"field_name": "Consequences", "value": "Slight migration effort; enables cross-team benchmarking."},
        ],
    },
    {
        "project_name": "LLMEval",
        "template_name": "Tyree & Ackerman Decision Template",
        "title": "Store eval runs in immutable artifacts",
        "status": "Proposed",
        "fields": [
            {"field_name": "Issue", "value": "Historical evaluation results can be overwritten."},
            {"field_name": "Decision", "value": "Persist runs as immutable artifacts in S3 with signed manifests."},
            {"field_name": "Status", "value": "Proposed"},
            {"field_name": "Assumptions", "value": "Artifact size stays manageable with pruning."},
            {"field_name": "Alternatives", "value": "Mutable DB storage or logging-only."},
            {"field_name": "Arguments", "value": "Immutability ensures reproducibility and auditability."},
            {"field_name": "Implications", "value": "Increases storage costs; improves trust in benchmarks."},
        ],
    },
    {
        "project_name": "LLMEval",
        "template_name": "MADR – Markdown ADR",
        "title": "Use synthetic test sets for regression",
        "status": "Accepted",
        "fields": [
            {"field_name": "Title", "value": "Use synthetic test sets for regression"},
            {"field_name": "Status", "value": "Accepted"},
            {"field_name": "Context and Problem Statement", "value": "Real user data is sparse for edge-case evaluation."},
            {"field_name": "Decision Drivers", "value": "Coverage, privacy, low labeling cost."},
            {"field_name": "Considered Options", "value": "Only real data, manual authoring, or synthetic generation."},
            {"field_name": "Decision Outcome", "value": "Generate synthetic cases and validate with human spot checks."},
            {"field_name": "Consequences", "value": "Needs generator maintenance; improves regression protection."},
        ],
    },
    {
        "project_name": "LLMEval",
        "template_name": "ADR – Nygard",
        "title": "Adopt GPU spot workers for eval",
        "status": "Rejected",
        "fields": [
            {"field_name": "Title", "value": "Adopt GPU spot workers for eval"},
            {"field_name": "Status", "value": "Rejected"},
            {"field_name": "Context", "value": "Evaluation compute costs are rising."},
            {"field_name": "Decision", "value": "Avoid spot instances due to interrupt risk; negotiate reserved capacity."},
            {"field_name": "Consequences", "value": "Higher baseline cost; stable throughput."},
        ],
    },
    {
        "project_name": "LLMEval",
        "template_name": "Tyree & Ackerman Decision Template",
        "title": "Expose results via GraphQL",
        "status": "Accepted",
        "fields": [
            {"field_name": "Issue", "value": "REST endpoints require multiple round-trips for dashboards."},
            {"field_name": "Decision", "value": "Provide GraphQL API for flexible client queries."},
            {"field_name": "Status", "value": "Accepted"},
            {"field_name": "Assumptions", "value": "Clients can migrate to GraphQL without breaking changes."},
            {"field_name": "Alternatives", "value": "Add REST aggregations or use gRPC."},
            {"field_name": "Arguments", "value": "GraphQL reduces over/under-fetching and speeds UI building."},
            {"field_name": "Implications", "value": "Requires schema governance; improves UX."},
        ],
    },
    {
        "project_name": "Radar",
        "template_name": "ADR – Nygard",
        "title": "Quarterly tech radar cadence",
        "status": "Accepted",
        "fields": [
            {"field_name": "Title", "value": "Quarterly tech radar cadence"},
            {"field_name": "Status", "value": "Accepted"},
            {"field_name": "Context", "value": "Ad-hoc updates lead to stale radar information."},
            {"field_name": "Decision", "value": "Set a quarterly review cadence with dedicated owner rotation."},
            {"field_name": "Consequences", "value": "Predictable updates; requires time allocation per quarter."},
        ],
    },
    {
        "project_name": "Radar",
        "template_name": "Tyree & Ackerman Decision Template",
        "title": "Use four-ring radar model",
        "status": "Accepted",
        "fields": [
            {"field_name": "Issue", "value": "Teams interpret maturity categories inconsistently."},
            {"field_name": "Decision", "value": "Adopt the four rings: Adopt, Trial, Assess, Hold."},
            {"field_name": "Status", "value": "Accepted"},
            {"field_name": "Assumptions", "value": "Stakeholders accept a simple maturity vocabulary."},
            {"field_name": "Alternatives", "value": "More granular levels or numeric scoring."},
            {"field_name": "Arguments", "value": "Four rings align with industry practice and keep radar readable."},
            {"field_name": "Implications", "value": "Requires mapping existing items; improves clarity."},
        ],
    },
    {
        "project_name": "Radar",
        "template_name": "MADR – Markdown ADR",
        "title": "Automate radar data ingestion",
        "status": "Proposed",
        "fields": [
            {"field_name": "Title", "value": "Automate radar data ingestion"},
            {"field_name": "Status", "value": "Proposed"},
            {"field_name": "Context and Problem Statement", "value": "Manual entry leads to missing tech items and low adoption."},
            {"field_name": "Decision Drivers", "value": "Low effort, accuracy, integration with CI."},
            {"field_name": "Considered Options", "value": "Manual only, semi-automatic scripts, or CI-based automation."},
            {"field_name": "Decision Outcome", "value": "Build CI job that syncs tags and decisions into radar."},
            {"field_name": "Consequences", "value": "Engineering effort needed; higher data freshness."},
        ],
    },
    {
        "project_name": "Radar",
        "template_name": "ADR – Nygard",
        "title": "Public vs internal radar split",
        "status": "Rejected",
        "fields": [
            {"field_name": "Title", "value": "Public vs internal radar split"},
            {"field_name": "Status", "value": "Rejected"},
            {"field_name": "Context", "value": "Some stakeholders want a public-facing radar."},
            {"field_name": "Decision", "value": "Keep radar internal due to competitive sensitivity."},
            {"field_name": "Consequences", "value": "No external publication; avoids disclosure risk."},
        ],
    },
    {
        "project_name": "Radar",
        "template_name": "Tyree & Ackerman Decision Template",
        "title": "Link radar items to ADRs",
        "status": "Accepted",
        "fields": [
            {"field_name": "Issue", "value": "Radar entries lack decision context and ownership."},
            {"field_name": "Decision", "value": "Require ADR link for each radar item."},
            {"field_name": "Status", "value": "Accepted"},
            {"field_name": "Assumptions", "value": "Architecture teams maintain ADRs as part of normal workflow."},
            {"field_name": "Alternatives", "value": "Free-text notes or ticket links."},
            {"field_name": "Arguments", "value": "ADRs provide durable rationale and traceability."},
            {"field_name": "Implications", "value": "Slight overhead; much better knowledge management."},
        ],
    },
    {
        "project_name": "Catalogue",
        "template_name": "ADR – Nygard",
        "title": "Single portal for service requests",
        "status": "Accepted",
        "fields": [
            {"field_name": "Title", "value": "Single portal for service requests"},
            {"field_name": "Status", "value": "Accepted"},
            {"field_name": "Context", "value": "Teams use different portals, causing confusion."},
            {"field_name": "Decision", "value": "Provide one consolidated catalogue frontend."},
            {"field_name": "Consequences", "value": "Requires migration; improves discoverability."},
        ],
    },
    {
        "project_name": "Catalogue",
        "template_name": "Tyree & Ackerman Decision Template",
        "title": "Adopt Backstage as base UI",
        "status": "Proposed",
        "fields": [
            {"field_name": "Issue", "value": "Custom UI is costly to maintain."},
            {"field_name": "Decision", "value": "Evaluate Backstage as extensible base for catalogue UI."},
            {"field_name": "Status", "value": "Proposed"},
            {"field_name": "Assumptions", "value": "Plugins cover most required features."},
            {"field_name": "Alternatives", "value": "Continue custom UI or buy SaaS."},
            {"field_name": "Arguments", "value": "Backstage provides strong ecosystem and templates."},
            {"field_name": "Implications", "value": "Needs pilot; may speed delivery significantly."},
        ],
    },
    {
        "project_name": "Catalogue",
        "template_name": "MADR – Markdown ADR",
        "title": "Add scorecards for service quality",
        "status": "Accepted",
        "fields": [
            {"field_name": "Title", "value": "Add scorecards for service quality"},
            {"field_name": "Status", "value": "Accepted"},
            {"field_name": "Context and Problem Statement", "value": "No consistent way to compare service maturity."},
            {"field_name": "Decision Drivers", "value": "Transparency, governance, self-improvement."},
            {"field_name": "Considered Options", "value": "No scores, manual audits, automated scorecards."},
            {"field_name": "Decision Outcome", "value": "Introduce automated scorecards fed by CI and monitoring."},
            {"field_name": "Consequences", "value": "Requires rules and data sources; increases accountability."},
        ],
    },
    {
        "project_name": "Catalogue",
        "template_name": "ADR – Nygard",
        "title": "Keep catalogue metadata in YAML",
        "status": "Rejected",
        "fields": [
            {"field_name": "Title", "value": "Keep catalogue metadata in YAML"},
            {"field_name": "Status", "value": "Rejected"},
            {"field_name": "Context", "value": "YAML per repo is simple but inconsistent."},
            {"field_name": "Decision", "value": "Move to centralized metadata service instead."},
            {"field_name": "Consequences", "value": "More infra; better consistency."},
        ],
    },
    {
        "project_name": "Catalogue",
        "template_name": "Tyree & Ackerman Decision Template",
        "title": "Search powered by OpenSearch",
        "status": "Accepted",
        "fields": [
            {"field_name": "Issue", "value": "Existing search is slow and lacks facets."},
            {"field_name": "Decision", "value": "Index catalogue items into OpenSearch."},
            {"field_name": "Status", "value": "Accepted"},
            {"field_name": "Assumptions", "value": "Index updates can be near-real-time."},
            {"field_name": "Alternatives", "value": "Postgres full-text or hosted Algolia."},
            {"field_name": "Arguments", "value": "OpenSearch supports facets and scaling."},
            {"field_name": "Implications", "value": "New cluster ops; search UX improves."},
        ],
    },
    {
        "project_name": "Outreach",
        "template_name": "ADR – Nygard",
        "title": "Multi-channel publishing pipeline",
        "status": "Accepted",
        "fields": [
            {"field_name": "Title", "value": "Multi-channel publishing pipeline"},
            {"field_name": "Status", "value": "Accepted"},
            {"field_name": "Context", "value": "Release notes are duplicated for email, web, and social."},
            {"field_name": "Decision", "value": "Build a pipeline that publishes content to multiple channels from one source."},
            {"field_name": "Consequences", "value": "More automation; reduced manual work and inconsistencies."},
        ],
    },
    {
        "project_name": "Outreach",
        "template_name": "Tyree & Ackerman Decision Template",
        "title": "Use feature flags for staged announcements",
        "status": "Proposed",
        "fields": [
            {"field_name": "Issue", "value": "Announcements sometimes precede stable rollout."},
            {"field_name": "Decision", "value": "Integrate feature-flag state into publishing workflow."},
            {"field_name": "Status", "value": "Proposed"},
            {"field_name": "Assumptions", "value": "Feature-flag platform exposes reliable APIs."},
            {"field_name": "Alternatives", "value": "Manual checks or fixed calendars."},
            {"field_name": "Arguments", "value": "Flags align communication with actual availability."},
            {"field_name": "Implications", "value": "Extra integration work; fewer customer surprises."},
        ],
    },
    {
        "project_name": "Outreach",
        "template_name": "MADR – Markdown ADR",
        "title": "Adopt Notion as editorial workspace",
        "status": "Accepted",
        "fields": [
            {"field_name": "Title", "value": "Adopt Notion as editorial workspace"},
            {"field_name": "Status", "value": "Accepted"},
            {"field_name": "Context and Problem Statement", "value": "Content drafts are scattered across docs and chats."},
            {"field_name": "Decision Drivers", "value": "Collaboration, versioning, integrations."},
            {"field_name": "Considered Options", "value": "Google Docs, Confluence, Notion."},
            {"field_name": "Decision Outcome", "value": "Standardize drafting and review in Notion."},
            {"field_name": "Consequences", "value": "Licensing costs; faster editorial cycle."},
        ],
    },
    {
        "project_name": "Outreach",
        "template_name": "ADR – Nygard",
        "title": "Do not add SMS channel",
        "status": "Rejected",
        "fields": [
            {"field_name": "Title", "value": "Do not add SMS channel"},
            {"field_name": "Status", "value": "Rejected"},
            {"field_name": "Context", "value": "Some customers request SMS updates for incidents."},
            {"field_name": "Decision", "value": "Reject SMS for now; focus on email and in-app notifications."},
            {"field_name": "Consequences", "value": "No SMS costs; may revisit for premium tier."},
        ],
    },
    {
        "project_name": "Outreach",
        "template_name": "Tyree & Ackerman Decision Template",
        "title": "Store templates in headless CMS",
        "status": "Accepted",
        "fields": [
            {"field_name": "Issue", "value": "Hard-coded templates slow down marketing iterations."},
            {"field_name": "Decision", "value": "Move templates to headless CMS with approval flow."},
            {"field_name": "Status", "value": "Accepted"},
            {"field_name": "Assumptions", "value": "CMS uptime meets publishing SLAs."},
            {"field_name": "Alternatives", "value": "Keep in Git or allow free-form HTML."},
            {"field_name": "Arguments", "value": "CMS enables non-dev edits with governance."},
            {"field_name": "Implications", "value": "New dependency; far quicker content updates."},
        ],
    },
    {
        "project_name": "Catalogue",
        "template_name": "ADR – Nygard",
        "title": "Adopt internal golden path templates",
        "status": "Accepted",
        "fields": [
            {"field_name": "Title", "value": "Adopt internal golden path templates"},
            {"field_name": "Status", "value": "Accepted"},
            {"field_name": "Context", "value": "New services start with inconsistent scaffolding and metadata."},
            {"field_name": "Decision", "value": "Provide golden path templates in catalogue for common stacks."},
            {"field_name": "Consequences", "value": "Needs upkeep; speeds onboarding and standardization."},
        ],
    },
    {
        "project_name": "Insights",
        "template_name": "MADR – Markdown ADR",
        "title": "Move long-term storage to Iceberg",
        "status": "Proposed",
        "fields": [
            {"field_name": "Title", "value": "Move long-term storage to Iceberg"},
            {"field_name": "Status", "value": "Proposed"},
            {"field_name": "Context and Problem Statement", "value": "S3 parquet tables lack schema evolution and time travel."},
            {"field_name": "Decision Drivers", "value": "Schema evolution, ACID on lake, open format."},
            {"field_name": "Considered Options", "value": "Delta Lake, Hudi, Iceberg."},
            {"field_name": "Decision Outcome", "value": "Pilot Iceberg tables for event archive."},
            {"field_name": "Consequences", "value": "New tooling; better governance and query performance."},
        ],
    },
    {
        "project_name": "Discovery",
        "template_name": "ADR – Nygard",
        "title": "Introduce contract tests for APIs",
        "status": "Proposed",
        "fields": [
            {"field_name": "Title", "value": "Introduce contract tests for APIs"},
            {"field_name": "Status", "value": "Proposed"},
            {"field_name": "Context", "value": "Breaking changes in APIs are detected too late in discovery graphs."},
            {"field_name": "Decision", "value": "Require consumer-driven contract tests for catalogued APIs."},
            {"field_name": "Consequences", "value": "More CI load; fewer runtime incompatibilities."},
        ],
    },
    {
        "project_name": "Memory",
        "template_name": "MADR – Markdown ADR",
        "title": "Add user-controlled memory reset",
        "status": "Accepted",
        "fields": [
            {"field_name": "Title", "value": "Add user-controlled memory reset"},
            {"field_name": "Status", "value": "Accepted"},
            {"field_name": "Context and Problem Statement", "value": "Users need a clear way to remove stored context."},
            {"field_name": "Decision Drivers", "value": "Privacy, trust, compliance."},
            {"field_name": "Considered Options", "value": "Admin-only delete, per-item delete, full reset."},
            {"field_name": "Decision Outcome", "value": "Provide UI action to reset all memory for a user."},
            {"field_name": "Consequences", "value": "Requires confirmation UX; improves user trust."},
        ],
    },
    {
        "project_name": "Governance",
        "template_name": "Tyree & Ackerman Decision Template",
        "title": "Adopt SBOM generation",
        "status": "Proposed",
        "fields": [
            {"field_name": "Issue", "value": "Security teams require component transparency."},
            {"field_name": "Decision", "value": "Generate SBOMs for all services during CI builds."},
            {"field_name": "Status", "value": "Proposed"},
            {"field_name": "Assumptions", "value": "Build systems support CycloneDX exporters."},
            {"field_name": "Alternatives", "value": "Manual inventories or periodic scans only."},
            {"field_name": "Arguments", "value": "Automated SBOMs enable faster vulnerability triage."},
            {"field_name": "Implications", "value": "Adds build step; improves compliance posture."},
        ],
    },
    {
        "project_name": "LLMEval",
        "template_name": "ADR – Nygard",
        "title": "Cache prompts and completions for evaluation",
        "status": "Rejected",
        "fields": [
            {"field_name": "Title", "value": "Cache prompts and completions for evaluation"},
            {"field_name": "Status", "value": "Rejected"},
            {"field_name": "Context", "value": "Repeated evals may reuse identical requests."},
            {"field_name": "Decision", "value": "Reject caching due to risk of masking model drift."},
            {"field_name": "Consequences", "value": "Higher cost; more faithful eval results."},
        ],
    },
    {
        "project_name": "Radar",
        "template_name": "MADR – Markdown ADR",
        "title": "Tag deprecated technologies automatically",
        "status": "Proposed",
        "fields": [
            {"field_name": "Title", "value": "Tag deprecated technologies automatically"},
            {"field_name": "Status", "value": "Proposed"},
            {"field_name": "Context and Problem Statement", "value": "Hold-ring items are not propagated to teams."},
            {"field_name": "Decision Drivers", "value": "Automation, low friction, visibility."},
            {"field_name": "Considered Options", "value": "Manual tagging, weekly scripts, CI-based automation."},
            {"field_name": "Decision Outcome", "value": "Implement CI job that tags repos referencing hold items."},
            {"field_name": "Consequences", "value": "Needs dependency scanning; higher awareness of deprecations."},
        ],
    },
    {
        "project_name": "Outreach",
        "template_name": "ADR – Nygard",
        "title": "Use localization library for release notes",
        "status": "Accepted",
        "fields": [
            {"field_name": "Title", "value": "Use localization library for release notes"},
            {"field_name": "Status", "value": "Accepted"},
            {"field_name": "Context", "value": "Global customers need localized announcements."},
            {"field_name": "Decision", "value": "Adopt i18n library and translation workflow for content."},
            {"field_name": "Consequences", "value": "More content ops; better international reach."},
        ],
    },
    {
        "project_name": "Catalogue",
        "template_name": "Tyree & Ackerman Decision Template",
        "title": "Require SLOs for new services",
        "status": "Accepted",
        "fields": [
            {"field_name": "Issue", "value": "Catalogue entries lack reliability expectations."},
            {"field_name": "Decision", "value": "Make SLO definition mandatory for new catalogue items."},
            {"field_name": "Status", "value": "Accepted"},
            {"field_name": "Assumptions", "value": "Teams can define a minimal SLO set."},
            {"field_name": "Alternatives", "value": "Optional SLOs or central SRE-defined SLOs."},
            {"field_name": "Arguments", "value": "SLOs drive ownership and objective reliability targets."},
            {"field_name": "Implications", "value": "Adds onboarding effort; improves operational quality."},
        ],
    },
]


def seed_users(db: Session) -> User:
    db.query(User).delete()
    db.commit()

    hashed = pwd_context.hash(TEST_USER_PASSWORD)
    user = User(email=TEST_USER_EMAIL, passwordHash=hashed)
    db.add(user)
    db.commit()
    db.refresh(user)

    print(f"[seed] test user inserted: {user.email}")
    return user


def seed_statuses(db: Session):
    db.query(Status).delete()
    db.commit()
    for data in SEED_STATUSES:
        status = Status(
            name=data["name"],
            color=data["color"],
            position=data["position"],
        )
        db.add(status)
    db.commit()
    print(f"[seed] {len(SEED_STATUSES)} status entries inserted (overwritten).")


def seed_projects(db: Session, user_id: int):
    now = datetime.now(timezone.utc)
    db.query(Project).delete()
    db.commit()
    for idx, data in enumerate(SEED_PROJECTS, start=1):
        created_at = now - timedelta(days=random.randint(5, 40))
        updated_at = created_at + timedelta(hours=random.randint(2, 300))
        project = Project(
            userID=user_id,
            name=data["name"],
            description=data["description"],
            priority=data["priority"],
            position=idx - 1,
            icon=data["icon"],
            color=data["color"],
            creationDate=created_at,
            lastUpdated=updated_at,
            tags=data["tags"],
        )
        db.add(project)
    db.commit()
    print(f"[seed] {len(SEED_PROJECTS)} projects inserted (overwritten).")


def seed_documentation_templates(db: Session):
    db.query(DocumentationTemplateField).delete()
    db.query(DocumentationTemplate).delete()
    db.commit()
    for tmpl in SEED_TEMPLATES:
        template = DocumentationTemplate(
            name=tmpl["name"],
            description=tmpl["description"],
        )
        db.add(template)
        db.flush()
        for field in tmpl["fields"]:
            tf = DocumentationTemplateField(
                templateID=template.templateID,
                name=field["name"],
                isRequired=field["isRequired"],
            )
            db.add(tf)
    db.commit()
    print(f"[seed] {len(SEED_TEMPLATES)} documentation templates inserted (overwritten).")


def seed_decisions(db: Session):
    db.query(ArchitectureDecisionFieldValue).delete()
    db.query(ArchitectureDecision).delete()
    db.commit()
    statuses_by_name = {s.name: s for s in db.query(Status).all()}
    projects_by_name = {p.name: p for p in db.query(Project).all()}
    templates_by_name = {t.name: t for t in db.query(DocumentationTemplate).all()}
    all_fields = db.query(DocumentationTemplateField).all()
    fields_by_template_and_name = {(f.templateID, f.name): f for f in all_fields}
    now = datetime.now(timezone.utc)
    inserted = 0
    for data in SEED_DECISIONS:
        project = projects_by_name.get(data["project_name"])
        status = statuses_by_name.get(data["status"])
        template = templates_by_name.get(data["template_name"])
        if project is None or status is None or template is None:
            continue
        created_at = now - timedelta(days=random.randint(1, 30))
        updated_at = created_at + timedelta(hours=random.randint(1, 240))
        decision = ArchitectureDecision(
            projectID=project.projectID,
            templateID=template.templateID,
            statusID=status.statusID,
            title=data["title"],
            createdAt=created_at,
            lastUpdated=updated_at,
        )
        db.add(decision)
        db.flush()
        for field in data.get("fields", []):
            field_name = field.get("field_name") or field.get("name")
            value = field.get("value")

            if not field_name:
                continue

            tf = fields_by_template_and_name.get((template.templateID, field_name))
            if tf is None:
                continue

            fv = ArchitectureDecisionFieldValue(
                decisionID=decision.decisionID,
                fieldID=tf.fieldID,
                value=value,
            )
            db.add(fv)
        inserted += 1
    db.commit()
    print(f"[seed] {inserted} architecture decisions inserted (overwritten).")


def seed_history(db: Session, user_id: int):
    db.query(ArchitectureDecisionHistory).delete()
    db.commit()
    decisions = db.query(ArchitectureDecision).all()
    for decision in decisions:
        DecisionHistoryService.add_created_entry(db, decision.decisionID, user_id=user_id)
        DecisionHistoryService.add_status_change_entry(db, decision.decisionID, user_id=user_id)
    print(f"[seed] 2 history entries per decision inserted for {len(decisions)} decisions.")


def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        user = seed_users(db)
        seed_statuses(db)
        seed_projects(db, user.userID)
        seed_documentation_templates(db)
        seed_decisions(db)
        seed_history(db, user.userID)
    finally:
        db.close()


if __name__ == "__main__":
    main()