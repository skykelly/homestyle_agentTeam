"""
SEO-specific data models (Phase 4-6).
ContentBrief, SEOExperiment, KnowledgeItem
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import uuid


@dataclass
class ContentBrief:
    target_url: str
    primary_query_cluster: str
    search_intent: str              # "informational" | "commercial" | "transactional" | "navigational"
    secondary_queries: list[str]
    current_gap: list[str]
    recommended_sections: list[str]
    title_options: list[str]
    meta_description_options: list[str]
    h1_options: list[str]
    faq_items: list[dict]           # [{"question": str, "answer": str}]
    internal_link_suggestions: list[dict]  # [{"url": str, "anchor_text": str}]
    structured_data_suggestions: list[str]
    content_objective: str
    target_audience: str
    confidence_score: float
    risk_level: str                 # "low" | "medium" | "high"
    expected_impact: str

    # Auto-generated
    brief_id: str = field(default_factory=lambda: f"brief_{str(uuid.uuid4())[:8]}")
    status: str = field(default="draft")  # "draft" | "approved" | "in_progress" | "published"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    agent_run_id: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "brief_id": self.brief_id,
            "target_url": self.target_url,
            "primary_query_cluster": self.primary_query_cluster,
            "search_intent": self.search_intent,
            "secondary_queries": self.secondary_queries,
            "current_gap": self.current_gap,
            "recommended_sections": self.recommended_sections,
            "title_options": self.title_options,
            "meta_description_options": self.meta_description_options,
            "h1_options": self.h1_options,
            "faq_items": self.faq_items,
            "internal_link_suggestions": self.internal_link_suggestions,
            "structured_data_suggestions": self.structured_data_suggestions,
            "content_objective": self.content_objective,
            "target_audience": self.target_audience,
            "confidence_score": self.confidence_score,
            "risk_level": self.risk_level,
            "expected_impact": self.expected_impact,
            "status": self.status,
            "created_at": self.created_at,
            "agent_run_id": self.agent_run_id,
        }


@dataclass
class StructuredDataRecommendation:
    target_url: str
    page_type: str                  # "product" | "faq" | "article" | "category" | etc.
    schema_type: str                # "Product" | "FAQPage" | "Article" | etc.
    json_ld_draft: str              # JSON-LD markup string
    missing_properties: list[str]
    required_properties: list[str]
    optional_properties: list[str]
    expected_impact: str
    effort_score: int               # 1-5
    impact_score: int               # 1-5
    rich_result_eligible: bool

    rec_id: str = field(default_factory=lambda: f"schema_{str(uuid.uuid4())[:8]}")
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return {
            "rec_id": self.rec_id,
            "target_url": self.target_url,
            "page_type": self.page_type,
            "schema_type": self.schema_type,
            "json_ld_draft": self.json_ld_draft,
            "missing_properties": self.missing_properties,
            "required_properties": self.required_properties,
            "optional_properties": self.optional_properties,
            "expected_impact": self.expected_impact,
            "effort_score": self.effort_score,
            "impact_score": self.impact_score,
            "rich_result_eligible": self.rich_result_eligible,
            "created_at": self.created_at,
        }


@dataclass
class InternalLinkRecommendation:
    source_url: str
    target_url: str
    anchor_text: str
    placement_hint: str             # "첫 번째 관련 단락", "CTA 섹션 위" 등
    topic_relevance: str
    link_type: str                  # "hub_to_spoke" | "spoke_to_hub" | "cross_link" | "orphan_rescue"
    priority: str                   # "high" | "medium" | "low"
    rationale: str

    rec_id: str = field(default_factory=lambda: f"link_{str(uuid.uuid4())[:8]}")
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return {
            "rec_id": self.rec_id,
            "source_url": self.source_url,
            "target_url": self.target_url,
            "anchor_text": self.anchor_text,
            "placement_hint": self.placement_hint,
            "topic_relevance": self.topic_relevance,
            "link_type": self.link_type,
            "priority": self.priority,
            "rationale": self.rationale,
            "created_at": self.created_at,
        }


@dataclass
class SEOExperiment:
    target_url: str
    change_type: str                # "title_meta" | "content_update" | "schema_add" | "internal_link" | "technical_fix"
    change_description: str
    baseline_metrics: dict          # {"clicks_28d": x, "impressions_28d": x, "ctr": x, "position": x}
    baseline_start_date: str
    baseline_end_date: str

    # Set after running
    experiment_start_date: Optional[str] = None
    experiment_end_date: Optional[str] = None
    result_metrics: Optional[dict] = None
    outcome: Optional[str] = None   # "success" | "neutral" | "regression"
    learning_summary: Optional[str] = None
    recommendation_id: Optional[str] = None

    experiment_id: str = field(default_factory=lambda: f"exp_{str(uuid.uuid4())[:8]}")
    status: str = field(default="baseline_set")  # "baseline_set" | "running" | "completed" | "cancelled"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def compute_delta(self) -> Optional[dict]:
        if not self.result_metrics or not self.baseline_metrics:
            return None
        b, r = self.baseline_metrics, self.result_metrics
        def pct(cur, base): return round((cur - base) / base * 100, 1) if base else 0
        return {
            "clicks_delta_pct": pct(r.get("clicks_28d", 0), b.get("clicks_28d", 0)),
            "impressions_delta_pct": pct(r.get("impressions_28d", 0), b.get("impressions_28d", 0)),
            "ctr_delta_pct": pct(r.get("ctr", 0), b.get("ctr", 0)),
            "position_delta": round(r.get("position", 0) - b.get("position", 0), 1),
        }

    def to_dict(self) -> dict:
        return {
            "experiment_id": self.experiment_id,
            "target_url": self.target_url,
            "change_type": self.change_type,
            "change_description": self.change_description,
            "baseline_metrics": self.baseline_metrics,
            "baseline_start_date": self.baseline_start_date,
            "baseline_end_date": self.baseline_end_date,
            "experiment_start_date": self.experiment_start_date,
            "experiment_end_date": self.experiment_end_date,
            "result_metrics": self.result_metrics,
            "outcome": self.outcome,
            "learning_summary": self.learning_summary,
            "recommendation_id": self.recommendation_id,
            "status": self.status,
            "delta": self.compute_delta(),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


@dataclass
class Recommendation:
    target_url: str
    opportunity_type: str            # "ctr_improvement" | "ranking_boost" | "content_refresh" | "technical" | "cannibalization"
    priority: str                    # "critical" | "high" | "medium" | "low"
    problem: str
    recommendation: str
    evidence: list[str]
    expected_impact: str
    confidence_score: float          # 0.0 – 1.0
    risk_level: str                  # "low" | "medium" | "high"
    effort_score: int                # 1–5
    impact_score: int                # 1–5
    owner: str                       # "content" | "dev" | "seo"
    rollback_plan: str
    target_query_cluster: Optional[str] = None
    current_metrics: Optional[dict] = None
    rule_id: Optional[str] = None

    rec_id: str = field(default_factory=lambda: f"rec_{str(uuid.uuid4())[:8]}")
    status: str = field(default="pending_approval")  # "pending_approval" | "approved" | "rejected" | "in_progress" | "completed"
    approver_notes: Optional[str] = None
    rejection_reason: Optional[str] = None
    approved_at: Optional[str] = None
    rejected_at: Optional[str] = None
    experiment_id: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return {
            "rec_id": self.rec_id,
            "target_url": self.target_url,
            "opportunity_type": self.opportunity_type,
            "priority": self.priority,
            "problem": self.problem,
            "recommendation": self.recommendation,
            "evidence": self.evidence,
            "expected_impact": self.expected_impact,
            "confidence_score": self.confidence_score,
            "risk_level": self.risk_level,
            "effort_score": self.effort_score,
            "impact_score": self.impact_score,
            "owner": self.owner,
            "rollback_plan": self.rollback_plan,
            "target_query_cluster": self.target_query_cluster,
            "current_metrics": self.current_metrics,
            "rule_id": self.rule_id,
            "status": self.status,
            "approver_notes": self.approver_notes,
            "rejection_reason": self.rejection_reason,
            "approved_at": self.approved_at,
            "rejected_at": self.rejected_at,
            "experiment_id": self.experiment_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


@dataclass
class ContentDraft:
    brief_id: str
    target_url: str
    version: int

    # Generated content
    title_before: str
    title_after: str
    meta_before: str
    meta_after: str
    h1_before: str
    h1_after: str
    section_rewrites: list[dict]     # [{"section": str, "before": str, "after": str, "reason": str}]
    faq_additions: list[dict]        # [{"question": str, "answer": str}]
    quality_score: float             # 0.0 – 1.0
    brand_safety_score: float        # 0.0 – 1.0 (set by governance agent)
    governance_flags: list[str]      # issues found by governance agent
    diff_summary: str

    draft_id: str = field(default_factory=lambda: f"draft_{str(uuid.uuid4())[:8]}")
    status: str = field(default="draft")  # "draft" | "governance_checked" | "pending_approval" | "approved" | "rejected"
    recommendation_id: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return {
            "draft_id": self.draft_id,
            "brief_id": self.brief_id,
            "target_url": self.target_url,
            "version": self.version,
            "title_before": self.title_before,
            "title_after": self.title_after,
            "meta_before": self.meta_before,
            "meta_after": self.meta_after,
            "h1_before": self.h1_before,
            "h1_after": self.h1_after,
            "section_rewrites": self.section_rewrites,
            "faq_additions": self.faq_additions,
            "quality_score": self.quality_score,
            "brand_safety_score": self.brand_safety_score,
            "governance_flags": self.governance_flags,
            "diff_summary": self.diff_summary,
            "status": self.status,
            "recommendation_id": self.recommendation_id,
            "created_at": self.created_at,
        }


@dataclass
class KnowledgeItem:
    source_type: str                # "experiment" | "rule_hit" | "llm_insight" | "manual"
    title: str
    summary: str
    content: str
    tags: list[str]
    source_id: Optional[str] = None

    item_id: str = field(default_factory=lambda: f"know_{str(uuid.uuid4())[:8]}")
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return {
            "item_id": self.item_id,
            "source_type": self.source_type,
            "source_id": self.source_id,
            "title": self.title,
            "summary": self.summary,
            "content": self.content,
            "tags": self.tags,
            "created_at": self.created_at,
        }
