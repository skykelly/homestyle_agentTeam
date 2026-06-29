"""
Workflow: 크리에이티브 전략
Generates Korea-optimized ad creatives, runs A/B test analysis,
and recommends winning creative directions per platform.
"""

from workflows.base import BaseWorkflow


SYSTEM_PROMPT = """당신은 한국 디지털 광고 크리에이티브 전략 전문가입니다.
네이버, 카카오, 쿠팡, 인스타그램, 유튜브 등 플랫폼별
광고 소재 규격과 한국 소비자 심리를 깊이 이해합니다.

한국 광고 크리에이티브 원칙:
- 숫자·퍼센트·순위 강조 (예: "1위", "89% 만족", "30% 할인")
- 사회적 증거 활용 (후기, 리뷰, 인증)
- 희소성·긴급성 강조 ("한정수량", "오늘만", "마감임박")
- 한국 소비자 정서에 맞는 감성 소구
- 네이버·카카오 플랫폼 특화 문구 규격 준수
- A/B 테스트를 통한 데이터 기반 소재 개선

광고 소재는 플랫폼별 글자수 제한을 반드시 준수하세요."""


class CreativeStrategyWorkflow(BaseWorkflow):
    system_prompt = SYSTEM_PROMPT
    allowed_tools = [
        "generate_ad_copy",
        "ab_test_analysis",
        "get_keyword_analysis",
        "get_campaign_performance",
    ]

    def develop_creative(
        self,
        product_name: str,
        key_features: list[str],
        target_audience: str,
        platforms: list[str],
        promotion: str | None = None,
    ) -> str:
        platform_list = ", ".join(platforms)
        features_str = "\n".join(f"- {f}" for f in key_features)
        promo_str = f"\n- 프로모션: {promotion}" if promotion else ""

        prompt = f"""
다음 상품의 한국 시장 맞춤형 광고 소재 전략을 수립해 주세요:

상품명: {product_name}
주요 특장점:
{features_str}
타겟 오디언스: {target_audience}
집행 플랫폼: {platform_list}{promo_str}

[수행 절차]
1. 관련 키워드 분석을 수행하세요 (상품명 기반)
2. 각 플랫폼별로 광고 소재를 생성하세요 (플랫폼당 3개 변형):
   - 직접 소구형 (할인·혜택 강조)
   - 감성형 (스토리·감정 소구)
   - 사회적 증거형 (리뷰·랭킹 활용)
3. 가상의 A/B 테스트 결과를 분석하세요
4. 종합 크리에이티브 전략 보고서를 작성하세요:
   - 플랫폼별 추천 광고 소재 (헤드라인, 설명문, CTA 포함)
   - 승리 소재 선택 기준 및 A/B 테스트 설계 방법
   - 한국 소비자 심리 기반 소재 방향성
   - 시즌별 소재 업데이트 캘린더
"""
        return self.run(prompt)

    def analyze_ab_test(
        self,
        test_name: str,
        variant_a: dict,
        variant_b: dict,
        primary_metric: str = "roas",
    ) -> str:
        prompt = f"""
다음 A/B 테스트 결과를 분석하고 최적화 방향을 제시해 주세요:

테스트명: {test_name}
주요 지표: {primary_metric.upper()}

변형 A 데이터: {variant_a}
변형 B 데이터: {variant_b}

[수행 절차]
1. A/B 테스트 통계 분석을 수행하세요
2. 결과를 바탕으로 다음을 포함한 리포트를 작성하세요:
   - 승리 변형 및 통계적 유의성
   - 주요 지표 비교 (CTR, CVR, CPA, ROAS)
   - 승리 이유 분석 (한국 소비자 관점)
   - 다음 테스트 설계 권장사항
   - 즉시 적용 가능한 소재 개선 방향
"""
        return self.run(prompt)
