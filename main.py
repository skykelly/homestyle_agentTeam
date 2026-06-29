#!/usr/bin/env python3
"""
Korea Performance Marketing Agent — Entry Point

Usage:
  python main.py                          # Interactive chat mode
  python main.py demo                     # Run built-in demo
  python main.py analyze --start 2024-11-01 --end 2024-11-30 --category 뷰티
  python main.py budget --budget 50000000 --category 뷰티 --objective roas_maximize
  python main.py plan --brand MyBrand --category 패션 --budget 30000000 --weeks 4
  python main.py report --start 2024-11-01 --end 2024-11-30 --type weekly
  python main.py creative --product "콜라겐 세럼" --audience "30대 여성"
"""

import sys
import typer
from typing import Optional
from rich.console import Console

app = typer.Typer(
    name="korea-marketing-agent",
    help="🇰🇷 한국 시장 퍼포먼스 마케팅 AI 에이전트",
    add_completion=False,
)
console = Console()


@app.command(name="chat", help="대화형 에이전트 모드 (기본값)")
def chat_mode():
    from agents.performance_marketing_agent import run_interactive_session
    run_interactive_session()


@app.command(name="demo", help="주요 기능 데모 실행")
def demo_mode():
    from agents.performance_marketing_agent import run_demo
    run_demo()


@app.command(name="analyze", help="캠페인 성과 분석")
def analyze_campaign(
    start: str = typer.Option(..., "--start", "-s", help="시작일 (YYYY-MM-DD)"),
    end: str = typer.Option(..., "--end", "-e", help="종료일 (YYYY-MM-DD)"),
    category: str = typer.Option("패션", "--category", "-c", help="상품 카테고리"),
    platforms: Optional[str] = typer.Option(None, "--platforms", "-p", help="플랫폼 (쉼표 구분)"),
):
    from workflows.campaign_analysis import CampaignAnalysisWorkflow
    platform_list = platforms.split(",") if platforms else None
    workflow = CampaignAnalysisWorkflow(verbose=True)

    console.print(f"[cyan]캠페인 성과 분석 실행 중... ({start} ~ {end})[/cyan]")
    result = workflow.analyze(start, end, platform_list, category)

    from rich.markdown import Markdown
    console.print(Markdown(result))


@app.command(name="budget", help="예산 최적화 플랜 수립")
def budget_optimization(
    budget: int = typer.Option(..., "--budget", "-b", help="총 예산 (KRW)"),
    category: str = typer.Option("패션", "--category", "-c", help="상품 카테고리"),
    objective: str = typer.Option("roas_maximize", "--objective", "-o",
                                   help="목표 (roas_maximize/cpa_minimize/awareness/traffic)"),
    month: int = typer.Option(None, "--month", "-m", help="현재 월 (기본값: 현재 월)"),
    platforms: Optional[str] = typer.Option(None, "--platforms", "-p", help="플랫폼 (쉼표 구분)"),
):
    from workflows.budget_optimization import BudgetOptimizationWorkflow
    from datetime import datetime
    current_month = month or datetime.now().month
    platform_list = platforms.split(",") if platforms else None
    workflow = BudgetOptimizationWorkflow(verbose=True)

    console.print(f"[cyan]예산 최적화 분석 중... (총 {budget:,}원)[/cyan]")
    result = workflow.optimize(budget, category, objective, current_month, platform_list)

    from rich.markdown import Markdown
    console.print(Markdown(result))


@app.command(name="plan", help="캠페인 플랜 수립")
def campaign_plan(
    brand: str = typer.Option(..., "--brand", help="브랜드명"),
    category: str = typer.Option(..., "--category", "-c", help="상품 카테고리"),
    budget: int = typer.Option(..., "--budget", "-b", help="총 예산 (KRW)"),
    weeks: int = typer.Option(4, "--weeks", "-w", help="캠페인 기간 (주)"),
    objective: str = typer.Option("sales_conversion", "--objective", "-o",
                                   help="목표 (brand_awareness/sales_conversion/app_install/lead_generation)"),
    audience: str = typer.Option("20-40대 소비자", "--audience", "-a", help="타겟 오디언스"),
    messages: Optional[str] = typer.Option(None, "--messages", help="핵심 메시지 (쉼표 구분)"),
):
    from workflows.campaign_planning import CampaignPlanningWorkflow
    message_list = messages.split(",") if messages else None
    workflow = CampaignPlanningWorkflow(verbose=True)

    console.print(f"[cyan]캠페인 플랜 수립 중... ({brand} / {category})[/cyan]")
    result = workflow.plan(brand, category, objective, budget, weeks, audience, message_list)

    from rich.markdown import Markdown
    console.print(Markdown(result))


@app.command(name="report", help="성과 보고서 생성")
def generate_report(
    start: str = typer.Option(..., "--start", "-s", help="시작일 (YYYY-MM-DD)"),
    end: str = typer.Option(..., "--end", "-e", help="종료일 (YYYY-MM-DD)"),
    report_type: str = typer.Option("weekly", "--type", "-t", help="보고서 유형 (weekly/monthly)"),
    category: str = typer.Option("패션", "--category", "-c", help="카테고리"),
    budget: int = typer.Option(10_000_000, "--budget", "-b", help="월 예산 (KRW, monthly 보고서용)"),
):
    from workflows.reporting import ReportingWorkflow
    workflow = ReportingWorkflow(verbose=True)

    console.print(f"[cyan]{report_type} 보고서 생성 중... ({start} ~ {end})[/cyan]")
    if report_type == "monthly":
        result = workflow.generate_monthly_report(start, end, category, budget)
    else:
        result = workflow.generate_weekly_report(start, end, category)

    from rich.markdown import Markdown
    console.print(Markdown(result))


@app.command(name="creative", help="광고 소재 전략 수립")
def creative_strategy(
    product: str = typer.Option(..., "--product", "-p", help="상품명"),
    audience: str = typer.Option(..., "--audience", "-a", help="타겟 오디언스"),
    features: Optional[str] = typer.Option(None, "--features", "-f", help="특장점 (쉼표 구분)"),
    platforms: str = typer.Option("naver_search,kakao_moment", "--platforms", help="플랫폼 (쉼표 구분)"),
    promotion: Optional[str] = typer.Option(None, "--promo", help="프로모션 내용"),
):
    from workflows.creative_strategy import CreativeStrategyWorkflow
    feature_list = features.split(",") if features else ["고품질", "합리적 가격", "빠른 배송"]
    platform_list = platforms.split(",")
    workflow = CreativeStrategyWorkflow(verbose=True)

    console.print(f"[cyan]크리에이티브 전략 수립 중... ({product})[/cyan]")
    result = workflow.develop_creative(product, feature_list, audience, platform_list, promotion)

    from rich.markdown import Markdown
    console.print(Markdown(result))


def main():
    if len(sys.argv) == 1:
        # No subcommand: default to interactive chat
        from agents.performance_marketing_agent import run_interactive_session
        run_interactive_session()
    else:
        app()


if __name__ == "__main__":
    main()
