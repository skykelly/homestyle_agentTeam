"""
SEO Structured Data Workflow — Phase 4.
Generates Schema.org JSON-LD recommendations for each page type.
Identifies rich result opportunities and produces ready-to-deploy markup drafts.
"""

import json
from datetime import datetime

from data.seo_mock_data import get_crawled_pages, get_gsc_queries, get_ga4_landing, SITE_BENCHMARKS
from models.agent_run import AgentRun
from models.seo_models import StructuredDataRecommendation
from storage.repository import save_agent_run
from storage.seo_repository import save_schema_recommendation
from workflows.base import BaseWorkflow


# Schema config per page type
SCHEMA_CONFIG = {
    "product": {
        "primary_schema": "Product",
        "sub_schemas": ["Offer", "AggregateRating", "Review"],
        "required_properties": ["name", "description", "image", "brand", "sku", "offers"],
        "optional_properties": ["aggregateRating", "review", "gtin", "mpn"],
        "rich_results": ["Product snippet", "Price", "Rating stars"],
        "effort": 2,
        "impact": 5,
    },
    "faq": {
        "primary_schema": "FAQPage",
        "sub_schemas": [],
        "required_properties": ["mainEntity", "name", "acceptedAnswer"],
        "optional_properties": ["datePublished", "author"],
        "rich_results": ["FAQ rich result", "People Also Ask"],
        "effort": 1,
        "impact": 4,
    },
    "article": {
        "primary_schema": "Article",
        "sub_schemas": ["BreadcrumbList", "Person"],
        "required_properties": ["headline", "image", "datePublished", "author"],
        "optional_properties": ["dateModified", "publisher", "description"],
        "rich_results": ["Article snippet", "Author knowledge panel"],
        "effort": 1,
        "impact": 3,
    },
    "category": {
        "primary_schema": "CollectionPage",
        "sub_schemas": ["BreadcrumbList", "ItemList"],
        "required_properties": ["name", "url", "hasPart"],
        "optional_properties": ["description", "breadcrumb"],
        "rich_results": ["Site links", "Breadcrumb"],
        "effort": 2,
        "impact": 3,
    },
    "home": {
        "primary_schema": "Organization",
        "sub_schemas": ["WebSite", "SiteLinksSearchBox"],
        "required_properties": ["name", "url", "logo", "contactPoint"],
        "optional_properties": ["sameAs", "address"],
        "rich_results": ["Organization knowledge panel", "Site links search box"],
        "effort": 1,
        "impact": 3,
    },
}

# JSON-LD templates
PRODUCT_JSONLD = """{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "뷰티랩 프리미엄 콜라겐 세럼 50ml",
  "description": "히알루론산·레티놀 함유 고농도 콜라겐 세럼. 피부 탄력 30% 개선 임상 완료.",
  "image": "https://beautylab.co.kr/images/collagen-serum-50ml.jpg",
  "brand": {
    "@type": "Brand",
    "name": "뷰티랩"
  },
  "sku": "BL-SERUM-001",
  "offers": {
    "@type": "Offer",
    "url": "https://beautylab.co.kr/product/collagen-serum-50ml",
    "priceCurrency": "KRW",
    "price": "58000",
    "priceValidUntil": "2026-12-31",
    "availability": "https://schema.org/InStock",
    "seller": {
      "@type": "Organization",
      "name": "뷰티랩"
    }
  },
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "4.8",
    "reviewCount": "2847",
    "bestRating": "5"
  }
}"""

FAQPAGE_JSONLD = """{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "세럼이랑 앰플 차이가 뭔가요?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "세럼은 고농도 활성 성분을 담은 스킨케어 필수 단계이며, 앰플은 세럼보다 더 고농도의 집중 케어 제품입니다. 세럼은 매일, 앰플은 집중 케어 기간에 사용합니다."
      }
    },
    {
      "@type": "Question",
      "name": "세럼 바르는 순서가 어떻게 되나요?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "클렌징 → 토너 → 세럼/앰플 → 에센스 → 수분 크림 순으로 바릅니다. 여러 세럼 사용 시 질감이 가벼운 제품부터 시작합니다."
      }
    }
  ]
}"""

ARTICLE_JSONLD = """{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "콜라겐 세럼 추천 가이드 2026",
  "image": "https://beautylab.co.kr/images/collagen-serum-guide-hero.jpg",
  "datePublished": "2026-01-15",
  "dateModified": "2026-06-29",
  "author": {
    "@type": "Person",
    "name": "뷰티랩 편집팀",
    "url": "https://beautylab.co.kr/about/team"
  },
  "publisher": {
    "@type": "Organization",
    "name": "뷰티랩",
    "logo": {
      "@type": "ImageObject",
      "url": "https://beautylab.co.kr/images/logo.png"
    }
  },
  "description": "히알루론산·레티놀 함유 콜라겐 세럼 선택 방법과 피부 타입별 추천을 정리했습니다."
}"""

JSONLD_TEMPLATES = {
    "product": PRODUCT_JSONLD,
    "faq": FAQPAGE_JSONLD,
    "article": ARTICLE_JSONLD,
}


class SEOStructuredDataWorkflow(BaseWorkflow):
    """
    Analyzes pages and generates structured data recommendations with JSON-LD drafts.
    Prioritizes by rich result potential and business impact.
    """

    system_prompt = """You are a Schema.org Structured Data Specialist for Korean e-commerce.

Your role is to recommend and draft JSON-LD markup for SEO rich results.

Key principles:
- Always use the most specific schema type applicable
- Include all required properties per Google's Rich Results requirements
- For Product pages: always include Offer + price + availability + rating
- For FAQ pages: format questions exactly as users would search them
- For Article pages: include dateModified — recency signals matter for rankings
- Korean market: use KRW (Korean Won) for prices, ko-KR for language
- Rich result eligibility: check Google's supported features list

Output structured JSON-LD that can be directly inserted into <script type="application/ld+json"> tags."""

    allowed_tools = ["get_technical_audit", "get_seo_query_opportunities"]

    def audit_and_recommend(self, llm_augment: bool = True) -> dict:
        """
        Run structured data audit and generate recommendations for all crawled pages.
        """
        run = AgentRun(
            workflow_name="seo_structured_data",
            trigger="manual",
            input_params={"llm_augment": llm_augment},
        )
        save_agent_run(run)

        pages = get_crawled_pages()
        recommendations = []

        for page in pages:
            if page.status_code != 200:
                continue

            config = SCHEMA_CONFIG.get(page.page_type)
            if not config:
                continue

            schema_type = config["primary_schema"]

            # Check what's missing
            missing_props = []
            if not page.has_structured_data:
                missing_props = config["required_properties"][:]
            else:
                # Already has schema — check for recommended additions
                missing_props = config.get("optional_properties", [])[:3]

            if not missing_props and page.has_structured_data:
                continue  # Skip — already complete

            json_ld = JSONLD_TEMPLATES.get(page.page_type, self._build_generic_jsonld(page, config))

            rec = StructuredDataRecommendation(
                target_url=page.url,
                page_type=page.page_type,
                schema_type=schema_type,
                json_ld_draft=json_ld,
                missing_properties=missing_props,
                required_properties=config["required_properties"],
                optional_properties=config.get("optional_properties", []),
                expected_impact=f"리치 스니펫 획득 시 CTR 20-35% 향상. 대상: {', '.join(config['rich_results'])}",
                effort_score=config["effort"],
                impact_score=config["impact"],
                rich_result_eligible=not page.has_structured_data,
            )

            save_schema_recommendation(rec)
            recommendations.append(rec)
            run.recommendations_generated.append(rec.rec_id)
            self._log(f"  [Schema] {page.url} → {schema_type} | impact={config['impact']}")

        # LLM: generate custom JSON-LD for highest-impact pages
        llm_output = ""
        if llm_augment and recommendations:
            top = sorted(recommendations, key=lambda r: r.impact_score, reverse=True)[:3]
            urls_str = "\n".join(
                f"  - {r.target_url} [{r.page_type}] → {r.schema_type}: 누락={r.missing_properties}"
                for r in top
            )
            prompt = f"""다음 페이지들에 대한 구조화 데이터 개선 전략을 제시해주세요.

사이트: {SITE_BENCHMARKS['site_name']} ({SITE_BENCHMARKS['site_url']})
카테고리: {SITE_BENCHMARKS['category']}

우선순위 페이지 (임팩트 순):
{urls_str}

각 페이지에 대해:
1. Google Rich Results에서 노출될 때의 예상 SERP 변화 (구체적으로)
2. 현재 누락된 핵심 property와 그 중요성
3. 구현 시 주의사항 (Google 가이드라인 준수)
4. 예상 CTR 개선 수치와 근거

한국어로 답변하세요."""
            llm_output = self.run(prompt, max_iterations=2)

        run.complete(output_summary=f"{len(recommendations)}개 구조화 데이터 권고사항 생성")
        save_agent_run(run)

        return {
            "run_id": run.run_id,
            "analyzed_at": datetime.now().isoformat(),
            "pages_analyzed": len(pages),
            "recommendations_generated": len(recommendations),
            "recommendations": [r.to_dict() for r in recommendations],
            "priority_sorted": sorted(
                [r.to_dict() for r in recommendations],
                key=lambda x: x["impact_score"],
                reverse=True,
            ),
            "llm_strategy": llm_output,
        }

    def _build_generic_jsonld(self, page, config: dict) -> str:
        return json.dumps({
            "@context": "https://schema.org",
            "@type": config["primary_schema"],
            "name": page.title or page.url,
            "url": f"{SITE_BENCHMARKS['site_url']}{page.url}",
            "description": page.meta_description or "",
            "breadcrumb": {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "홈", "item": SITE_BENCHMARKS["site_url"]},
                    {"@type": "ListItem", "position": 2, "name": page.title or "페이지", "item": f"{SITE_BENCHMARKS['site_url']}{page.url}"},
                ],
            },
        }, ensure_ascii=False, indent=2)
