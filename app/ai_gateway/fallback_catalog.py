"""
Deterministic Heuristic Fallback Catalog for [STUDIO_NAME]
Activated when external AI providers timeout, error, or produce invalid schemas (DOC-ARCH-010).
"""

from app.ai_gateway.schemas import (
    ClarificationQuestionsDTO,
    OpportunityItemDTO,
    OpportunityMapDTO,
    QuestionItemDTO,
    StructuredContextDTO,
)

DEFAULT_FALLBACK_QUESTIONS = ClarificationQuestionsDTO(
    questions=[
        QuestionItemDTO(
            question_id="fallback_q1",
            prompt="What is the primary operational software or database holding this process data?",
            type="single_choice",
            options=[
                "Accounting / ERP (QuickBooks, SAP, Tally, Zoho)",
                "Spreadsheets & Shared Drives (Excel, Google Sheets)",
                "Custom Internal Database (SQL Server, Postgres)",
                "Legacy Windows / On-Premise Application",
            ],
        ),
        QuestionItemDTO(
            question_id="fallback_q2",
            prompt="Approximately how many transactions, files, or records are manually handled each day?",
            type="single_choice",
            options=[
                "Low volume (< 25 per day)",
                "Moderate volume (25 – 100 per day)",
                "High volume (> 100 per day)",
            ],
        ),
        QuestionItemDTO(
            question_id="fallback_q3",
            prompt="What is the primary constraint or risk for implementing a solution?",
            type="single_choice",
            options=[
                "Security & on-premise firewall boundaries",
                "Speed of delivery (< 4 weeks target)",
                "Legacy system lack of modern APIs",
                "User adoption & staff workflow retraining",
            ],
        ),
    ]
)

DEFAULT_FALLBACK_OPPORTUNITY_MAP = OpportunityMapDTO(
    opportunities=[
        OpportunityItemDTO(
            id="opp_fb_001",
            category="QUICK_WIN",
            title="Automated Data Ingestion & Validation Gateway",
            description="Eliminates repetitive manual copy-pasting through structured webhooks and automated background verification.",
            impact="HIGH",
            complexity="LOW",
            estimated_effort="2 – 3 Weeks",
        ),
        OpportunityItemDTO(
            id="opp_fb_002",
            category="INTEGRATION",
            title="Direct Systems Synchronization Pipeline",
            description="Establishes automated bi-directional data flow between disparate tools, eliminating double data entry.",
            impact="HIGH",
            complexity="MEDIUM",
            estimated_effort="3 – 5 Weeks",
        ),
        OpportunityItemDTO(
            id="opp_fb_003",
            category="SYSTEM_RISK",
            title="Audit Logging & Data Reconciliation Monitor",
            description="Continuously audits operational records to identify discrepancies and synchronization failures before reporting deadlines.",
            impact="MEDIUM",
            complexity="LOW",
            estimated_effort="1 – 2 Weeks",
        ),
    ]
)

DEFAULT_FALLBACK_CONTEXT = StructuredContextDTO(
    core_challenge="Operational data bottlenecks resulting from manual cross-system transcription.",
    complexity_tier="MEDIUM",
    flagged_unknowns=["Third-party API rate limits and export schema stability"],
    impacted_workflows=["Operational data entry", "Cross-system reporting"],
)


def get_heuristic_questions(problem_text: str) -> ClarificationQuestionsDTO:
    """Returns deterministic clarification questions based on heuristic text inspection."""
    # Custom keyword heuristics can tailor fallback questions
    lower = problem_text.lower()
    if "invoice" in lower or "accounting" in lower or "quickbooks" in lower:
        return ClarificationQuestionsDTO(
            questions=[
                QuestionItemDTO(
                    question_id="fb_fin_q1",
                    prompt="Which financial or accounting system is the primary system of record?",
                    type="single_choice",
                    options=["QuickBooks", "Zoho Books", "TallyPrime", "SAP / Other"],
                ),
                QuestionItemDTO(
                    question_id="fb_fin_q2",
                    prompt="How are invoices currently received and transcribed?",
                    type="single_choice",
                    options=["Email PDF attachments", "Paper / Scans", "Customer portal uploads"],
                ),
            ]
        )
    return DEFAULT_FALLBACK_QUESTIONS


def get_heuristic_opportunity_map(problem_text: str) -> OpportunityMapDTO:
    """Returns deterministic opportunity map nodes based on heuristic text inspection."""
    return DEFAULT_FALLBACK_OPPORTUNITY_MAP
