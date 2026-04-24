"""Evaluation script for AI Tax Buddy using golden dataset."""

import logging
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from aitaxbuddy.agent import create_agent
from tests.golden_dataset import GOLDEN_DATASET, evaluate_response

logging.basicConfig(level=logging.WARNING)
console = Console()


def run_evaluation(user_id: str = "test_user") -> dict:
    """
    Run evaluation against the golden dataset.
    
    Args:
        user_id: User ID for the test agent
    
    Returns:
        Evaluation results summary
    """
    console.print("\n[bold cyan]🧪 AI Tax Buddy Evaluation[/bold cyan]\n")
    console.print(f"Running {len(GOLDEN_DATASET)} test cases...\n")
    
    agent = create_agent(user_id)
    results = []
    
    for i, golden in enumerate(GOLDEN_DATASET, 1):
        console.print(f"[yellow]Test {i}/{len(GOLDEN_DATASET)}:[/yellow] {golden.query[:60]}...")
        
        try:
            response = agent.process_message(golden.query)
            evaluation = evaluate_response(golden.query, response, golden)
            results.append(evaluation)
            
            status = "✅ PASS" if evaluation["passed"] else "❌ FAIL"
            score = evaluation["overall_score"] * 100
            console.print(f"  {status} (Score: {score:.1f}%)\n")
            
        except Exception as e:
            console.print(f"  [red]ERROR: {e}[/red]\n")
            results.append({
                "query": golden.query,
                "passed": False,
                "overall_score": 0.0,
                "error": str(e),
            })
    
    # Calculate summary statistics
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r["passed"])
    failed_tests = total_tests - passed_tests
    pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    avg_score = sum(r["overall_score"] for r in results) / total_tests if total_tests > 0 else 0
    
    # Display summary
    console.print("\n[bold cyan]📊 Evaluation Summary[/bold cyan]\n")
    
    summary_table = Table(show_header=True, header_style="bold magenta")
    summary_table.add_column("Metric", style="cyan")
    summary_table.add_column("Value", justify="right", style="green")
    
    summary_table.add_row("Total Tests", str(total_tests))
    summary_table.add_row("Passed", str(passed_tests))
    summary_table.add_row("Failed", str(failed_tests))
    summary_table.add_row("Pass Rate", f"{pass_rate:.1f}%")
    summary_table.add_row("Average Score", f"{avg_score * 100:.1f}%")
    
    console.print(summary_table)
    console.print()
    
    # Display failed tests details
    failed_results = [r for r in results if not r["passed"]]
    if failed_results:
        console.print("\n[bold red]❌ Failed Tests Details[/bold red]\n")
        
        for result in failed_results:
            console.print(Panel(
                f"[bold]Query:[/bold] {result['query']}\n\n"
                f"[bold]Score:[/bold] {result['overall_score'] * 100:.1f}%\n"
                f"[bold]Expected:[/bold] {result.get('expected_behavior', 'N/A')}\n\n"
                f"[yellow]Required Missing:[/yellow] {', '.join(result.get('required_missing', []))}\n"
                f"[red]Prohibited Found:[/red] {', '.join(result.get('prohibited_found', []))}",
                title=f"Failed Test",
                border_style="red",
            ))
    
    # Check critical risk areas
    risk_failures = {}
    for result in failed_results:
        for risk in result.get("risk_areas", []):
            risk_failures[risk] = risk_failures.get(risk, 0) + 1
    
    if risk_failures:
        console.print("\n[bold yellow]⚠️  Risk Areas with Failures[/bold yellow]\n")
        risk_table = Table(show_header=True, header_style="bold magenta")
        risk_table.add_column("Risk Area", style="yellow")
        risk_table.add_column("Failures", justify="right", style="red")
        
        for risk, count in sorted(risk_failures.items(), key=lambda x: x[1], reverse=True):
            risk_table.add_row(risk, str(count))
        
        console.print(risk_table)
        console.print()
    
    return {
        "total_tests": total_tests,
        "passed_tests": passed_tests,
        "failed_tests": failed_tests,
        "pass_rate": pass_rate,
        "average_score": avg_score,
        "results": results,
        "risk_failures": risk_failures,
    }


if __name__ == "__main__":
    summary = run_evaluation()
    
    if summary["pass_rate"] >= 80:
        console.print("[bold green]✅ Evaluation PASSED (≥80% pass rate)[/bold green]\n")
        exit(0)
    else:
        console.print("[bold red]❌ Evaluation FAILED (<80% pass rate)[/bold red]\n")
        exit(1)
