"""
Korea Performance Marketing Agent
Orchestrates all workflows and provides a unified conversational interface.
"""

import anthropic
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

from config.settings import settings
from tools.definitions import TOOLS
from tools.handlers import dispatch
from workflows.campaign_analysis import CampaignAnalysisWorkflow
from workflows.budget_optimization import BudgetOptimizationWorkflow
from workflows.creative_strategy import CreativeStrategyWorkflow
from workflows.campaign_planning import CampaignPlanningWorkflow
from workflows.reporting import ReportingWorkflow

console = Console()

AGENT_SYSTEM_PROMPT = """당신은 한국 시장 전문 퍼포먼스 마케팅 AI 에이전트입니다.
네이버, 카카오, 쿠팡, 메타, 유튜브 등 한국 주요 광고 플랫폼의 전문가로,
데이터 기반 마케팅 전략과 실행을 지원합니다.

## 핵심 역량
- 한국 시장 광고 플랫폼 (네이버광고, 카카오모먼트, 쿠팡광고) 전문 운영
- 성과 분석: ROAS, CPA, CTR, CVR 최적화
- 예산 배분: 시즌·카테고리·목표 기반 최적 배분
- 크리에이티브 전략: 한국 소비자 맞춤형 광고 소재 기획
- 캠페인 기획: 풀 퍼널 통합 마케팅 플랜

## 사용 가능한 기능
1. 캠페인 성과 조회 및 분석
2. 키워드 분석 (검색량, CPC, 경쟁도)
3. 예산 최적화 배분 계산
4. 경쟁사 분석
5. 광고 소재(카피) 생성
6. 한국 시장 이벤트 캘린더 조회
7. 캠페인 플랜 수립
8. 성과 보고서 생성
9. A/B 테스트 분석

## 응답 원칙
- 한국어로 응답하되, 마케팅 전문 용어(ROAS, CPA, CTR 등)는 영문 유지
- 모든 수치에 구체적인 숫자와 단위 포함
- 즉시 실행 가능한 액션 아이템 제공
- 한국 소비자 행동 패턴과 문화적 맥락 반영

무엇을 도와드릴까요?"""


class KoreaPerformanceMarketingAgent:
    """
    Main conversational agent that maintains session history
    and routes complex tasks to specialized workflows.
    """

    def __init__(self, verbose: bool = False):
        self.client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.verbose = verbose
        self.messages: list[dict] = []

        # Specialized workflows
        self.campaign_analysis = CampaignAnalysisWorkflow(verbose=verbose)
        self.budget_optimization = BudgetOptimizationWorkflow(verbose=verbose)
        self.creative_strategy = CreativeStrategyWorkflow(verbose=verbose)
        self.campaign_planning = CampaignPlanningWorkflow(verbose=verbose)
        self.reporting = ReportingWorkflow(verbose=verbose)

    def chat(self, user_input: str) -> str:
        """Single-turn conversational interface with full tool access."""
        self.messages.append({"role": "user", "content": user_input})

        for _ in range(15):
            response = self.client.messages.create(
                model=settings.MODEL,
                max_tokens=8096,
                system=AGENT_SYSTEM_PROMPT,
                tools=TOOLS,
                messages=self.messages,
            )

            if response.stop_reason == "end_turn":
                text = "\n".join(
                    b.text for b in response.content if b.type == "text"
                )
                self.messages.append({"role": "assistant", "content": response.content})
                return text

            if response.stop_reason == "tool_use":
                self.messages.append({"role": "assistant", "content": response.content})
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        if self.verbose:
                            console.print(f"[dim]  → {block.name}({str(block.input)[:80]}...)[/dim]")
                        result = dispatch(block.name, block.input)
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result,
                        })
                self.messages.append({"role": "user", "content": tool_results})

        return "죄송합니다. 처리 중 오류가 발생했습니다. 다시 시도해 주세요."

    def reset(self) -> None:
        """Clear conversation history."""
        self.messages = []


def run_interactive_session():
    """Interactive CLI session with the Korea Performance Marketing Agent."""
    console.print(Panel.fit(
        "[bold cyan]🇰🇷 한국 시장 퍼포먼스 마케팅 AI 에이전트[/bold cyan]\n"
        "[dim]네이버·카카오·쿠팡·메타·유튜브 통합 마케팅 전문가[/dim]\n\n"
        "명령어: [bold]quit[/bold] (종료) | [bold]reset[/bold] (대화 초기화) | "
        "[bold]demo[/bold] (데모 실행)",
        title="Korea Performance Marketing Agent",
        border_style="cyan",
    ))

    agent = KoreaPerformanceMarketingAgent(verbose=True)

    while True:
        try:
            user_input = console.input("\n[bold green]You:[/bold green] ").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[dim]에이전트를 종료합니다. 감사합니다![/dim]")
            break

        if not user_input:
            continue

        if user_input.lower() == "quit":
            console.print("[dim]에이전트를 종료합니다. 감사합니다![/dim]")
            break

        if user_input.lower() == "reset":
            agent.reset()
            console.print("[yellow]대화 기록이 초기화되었습니다.[/yellow]")
            continue

        if user_input.lower() == "demo":
            run_demo(agent)
            continue

        with console.status("[bold cyan]분석 중...[/bold cyan]"):
            response = agent.chat(user_input)

        console.print("\n[bold blue]Agent:[/bold blue]")
        console.print(Markdown(response))


def run_demo(agent: KoreaPerformanceMarketingAgent | None = None):
    """Run a demonstration of all major features."""
    if agent is None:
        agent = KoreaPerformanceMarketingAgent(verbose=True)

    demos = [
        (
            "캠페인 성과 분석",
            "2024년 11월 1일부터 30일까지 전체 플랫폼의 광고 성과를 분석해줘. "
            "뷰티 카테고리 기준으로 분석해줘.",
        ),
        (
            "예산 최적화",
            "월 예산 5천만원으로 뷰티 카테고리 ROAS 최대화 목표의 "
            "최적 예산 배분안을 만들어줘. 현재 11월이야.",
        ),
        (
            "광고 소재 생성",
            "상품명 '프리미엄 콜라겐 세럼', 특장점: 피부 탄력 30% 개선, 히알루론산 함유, 무방부제. "
            "30-45세 여성 대상으로 네이버 검색광고와 인스타그램 광고 소재를 만들어줘. "
            "지금 블랙프라이데이 30% 할인 프로모션 중이야.",
        ),
    ]

    console.print("\n[bold cyan]═══ 데모 모드 실행 ═══[/bold cyan]\n")

    for title, question in demos:
        console.print(Panel(f"[bold]{title}[/bold]\n\n[dim]{question}[/dim]", border_style="yellow"))
        with console.status(f"[bold cyan]{title} 실행 중...[/bold cyan]"):
            response = agent.chat(question)
        console.print("\n[bold blue]Agent 응답:[/bold blue]")
        console.print(Markdown(response))
        console.print("\n" + "─" * 60 + "\n")
