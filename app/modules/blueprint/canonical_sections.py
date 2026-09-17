"""
Canonical Roster of the 18 Solution Blueprint Sections.
Strictly conforms to DOC-PRD-005 Section 3 & 4.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class SectionDefinition:
    index: int
    key: str
    title: str
    description: str


CANONICAL_BLUEPRINT_SECTIONS: list[SectionDefinition] = [
    SectionDefinition(
        index=1,
        key="executive_summary",
        title="Executive Summary",
        description="High-level systems intervention brief and anticipated commercial return.",
    ),
    SectionDefinition(
        index=2,
        key="problem_understanding",
        title="Problem Understanding",
        description="Deconstruction of the business problem, separating symptoms from root causes.",
    ),
    SectionDefinition(
        index=3,
        key="current_state_assumptions",
        title="Current-State Assumptions",
        description="Operational parameters inferred from user intake to be verified.",
    ),
    SectionDefinition(
        index=4,
        key="target_state_vision",
        title="Target-State Vision",
        description="Target operating model once the technology intervention is operational.",
    ),
    SectionDefinition(
        index=5,
        key="recommended_technical_approach",
        title="Recommended Technical Approach",
        description="Macro-architecture (Python-first Modular Monolith, FastAPI, SQL Server).",
    ),
    SectionDefinition(
        index=6,
        key="core_functional_capabilities",
        title="Core Functional Capabilities",
        description="Feature breakdown categorized by user role.",
    ),
    SectionDefinition(
        index=7,
        key="ai_intelligence_components",
        title="AI & Intelligence Components",
        description="Prompt pipelines, structured schemas, model tiers, and zero-retention parameters.",
    ),
    SectionDefinition(
        index=8,
        key="workflow_automations",
        title="Workflow Automations",
        description="Event-driven automation rules specified as Trigger -> Filter -> Action -> Notification.",
    ),
    SectionDefinition(
        index=9,
        key="third_party_api_integrations",
        title="Third-Party API Integrations",
        description="Enumeration of required external APIs and authentication protocols.",
    ),
    SectionDefinition(
        index=10,
        key="data_modeling_storage_strategy",
        title="Data Modeling & Storage Strategy",
        description="Relational ER summary enforcing ACID integrity and snapshot isolation.",
    ),
    SectionDefinition(
        index=11,
        key="security_privacy_pii_guardrails",
        title="Security, Privacy & PII Guardrails",
        description="Cryptographic session rules, PII scrubbers, and encryption boundaries.",
    ),
    SectionDefinition(
        index=12,
        key="deployment_topology_devops_strategy",
        title="Deployment Topology & DevOps Strategy",
        description="Local-first development baseline and containerized production topology.",
    ),
    SectionDefinition(
        index=13,
        key="project_delivery_milestones",
        title="Project Delivery Milestones",
        description="Proposed 4-phase delivery sequence from schema design to hypercare.",
    ),
    SectionDefinition(
        index=14,
        key="architectural_dependencies",
        title="Architectural Dependencies",
        description="External prerequisites that must be provided by the client organization.",
    ),
    SectionDefinition(
        index=15,
        key="identified_technical_business_risks",
        title="Identified Technical & Business Risks",
        description="Technical risks, rate limits, legacy schema stability, and mitigation strategies.",
    ),
    SectionDefinition(
        index=16,
        key="open_unknowns_requiring_discovery",
        title="Open Unknowns Requiring Discovery",
        description="Specific architectural questions requiring deep investigation during scoping.",
    ),
    SectionDefinition(
        index=17,
        key="indicative_planning_parameters",
        title="Indicative Planning Parameters",
        description="Confidence-banded budget and timeline ranges with non-binding disclaimer.",
    ),
    SectionDefinition(
        index=18,
        key="human_review_gate_commercial_next_step",
        title="Human Review Gate & Commercial Next Step",
        description="Principal Architect triage handoff committing 24-business-hour turnaround.",
    ),
]
