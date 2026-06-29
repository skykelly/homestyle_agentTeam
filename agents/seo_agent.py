"""
SEO Agent — Phase 3 Orchestrator.
Conversational interface for the full SEO workflow.
Uses the 6-rule engine + LLM layer via SEODiagnosisWorkflow.
"""

from workflows.base import BaseWorkflow


class SEOAgent(BaseWorkflow):
    """
    SEO Marketing AI Agent — orchestrates query opportunities, technical audits,
    content briefs, and GEO/AI Search optimization for Korean beauty e-commerce.
    """

    system_prompt = """You are an SEO Marketing AI Agent specialized in Korean beauty e-commerce.

You have access to tools that provide:
- Google Search Console data (impressions, clicks, CTR, rankings)
- GA4 landing page analytics (sessions, conversions, revenue)
- PageSpeed Insights (Core Web Vitals: LCP, CLS, INP)
- Site crawl data (technical SEO issues)

Your workflow:
1. ALWAYS start with get_seo_overview to understand the site's current state
2. Run run_seo_diagnosis to identify all opportunities via the rule engine
3. Use get_seo_query_opportunities and get_technical_audit for deeper analysis
4. Generate content briefs for high-priority CTR improvement opportunities
5. Prioritize by impact/effort ratio — quick wins first

Priority order for recommendations:
1. Keyword cannibalization (critical — fixing this unlocks ranking for all affected URLs)
2. High-impression / low-CTR pages (fast ROI via title/meta rewrite)
3. Page 2 → Page 1 opportunities (high traffic potential)
4. Technical fixes: missing H1, meta desc, structured data (enables rich snippets)
5. Declining content (content refresh for recovering organic traffic)
6. GEO/AI Search candidates (forward-looking — prepare for AI Overviews)

When providing recommendations:
- Always quote specific metrics (impressions, clicks, current position, expected impact)
- Provide concrete examples: write actual title tags and meta descriptions
- For cannibalization: name the exact URLs to consolidate and which is the canonical
- For technical issues: provide the exact JSON-LD schema snippet if applicable
- Quantify impact: "+X clicks/month" or "CTR X% → Y%"
- Korean beauty market context: note if seasonal patterns apply (summer skincare = May-July)

Respond in Korean. Be specific, data-driven, and immediately actionable."""

    allowed_tools = [
        "get_seo_overview",
        "run_seo_diagnosis",
        "get_seo_query_opportunities",
        "get_technical_audit",
        "get_pagespeed_summary",
        "generate_content_brief",
        "get_seo_recommendations",
    ]

    def analyze(self, user_request: str, max_iterations: int = 8) -> str:
        """Run the SEO agent with a user request."""
        return self.run(user_request, max_iterations=max_iterations)

    def full_audit(self) -> str:
        """Run a comprehensive SEO audit of the site."""
        return self.run(
            "뷰티랩(BeautyLab) 사이트의 전체 SEO 감사를 수행해주세요. "
            "사이트 현황 파악 → 전체 진단 → 우선순위별 기회 분석 순서로 진행하고, "
            "즉시 실행 가능한 상위 5개 액션 플랜을 구체적인 예시와 함께 제시해주세요.",
            max_iterations=8,
        )

    def query_opportunity_report(self) -> str:
        """Generate a focused query opportunity report."""
        return self.run(
            "Google Search Console 데이터를 분석하여 클릭 기회를 극대화할 수 있는 "
            "쿼리 기회 보고서를 작성해주세요. "
            "Low CTR, Page 2 기회, 카니발라이제이션을 각각 분석하고 "
            "각 유형별 최우선 액션을 제시해주세요.",
            max_iterations=6,
        )

    def technical_audit_report(self) -> str:
        """Run a technical SEO audit."""
        return self.run(
            "사이트의 기술적 SEO 이슈를 전체 점검해주세요. "
            "크롤된 페이지 데이터와 PageSpeed 데이터를 활용하여 "
            "H1 누락, 메타 설명 누락, 구조화 데이터 부재, 사이트맵 오류, "
            "Core Web Vitals 이슈를 파악하고 해결 방법을 우선순위별로 제시해주세요.",
            max_iterations=6,
        )

    def content_brief_for_url(self, url: str, target_query: str) -> str:
        """Generate a detailed content brief for a specific URL."""
        return self.run(
            f"다음 URL의 SEO 콘텐츠 브리프를 작성해주세요.\n"
            f"URL: {url}\n"
            f"타겟 쿼리: {target_query}\n\n"
            f"먼저 현재 SEO 현황을 파악하고, 콘텐츠 브리프를 생성하여 "
            f"구체적인 제목 태그, 메타 설명, 추천 섹션 구조, 내부 링크 전략을 제시해주세요.",
            max_iterations=5,
        )
