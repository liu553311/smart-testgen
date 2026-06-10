"""CLI entry point using Click."""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from smart_testgen import __version__

console = Console()


@click.group()
@click.version_option(version=__version__, prog_name="smart-testgen")
def cli() -> None:
    """smart-testgen: AI-powered test case generator for software testers."""
    pass


@cli.command()
@click.argument("input_source", required=False, type=click.Path())
@click.option("--text", "-t", type=str, help="Requirements text as inline string")
@click.option(
    "--provider", "-p",
    type=click.Choice(["anthropic", "openai"], case_sensitive=False),
    default=None,
    help="LLM provider to use",
)
@click.option("--model", "-m", type=str, default=None, help="Model name override")
@click.option("--num-cases", "-n", type=int, default=None, help="Number of test cases to generate")
@click.option(
    "--format", "-f", "export_format",
    type=click.Choice(["markdown", "excel", "json"], case_sensitive=False),
    default=None,
    help="Export format",
)
@click.option("--output", "-o", type=click.Path(), default=None, help="Output file path")
@click.option(
    "--categories", "-c", type=str, default=None,
    help="Comma-separated categories (e.g., functional,boundary,negative)",
)
def generate(
    input_source: Optional[str],
    text: Optional[str],
    provider: Optional[str],
    model: Optional[str],
    num_cases: Optional[int],
    export_format: Optional[str],
    output: Optional[str],
    categories: Optional[str],
) -> None:
    """Generate test cases from requirements.

    Provide either a file path (INPUT_SOURCE) or --text for inline requirements.
    """
    from smart_testgen.config import Settings
    from smart_testgen.core.generator import TestGenerator
    from smart_testgen.core.parser import read_requirements
    from smart_testgen.exporters.excel import ExcelExporter
    from smart_testgen.exporters.json_exporter import JsonExporter
    from smart_testgen.exporters.markdown import MarkdownExporter
    from smart_testgen.llm import LLMProviderFactory

    # Validate input
    if not input_source and not text:
        console.print("[red]Error:[/red] Provide a file path or use --text for inline requirements.")
        sys.exit(1)
    if input_source and text:
        console.print("[red]Error:[/red] Use either a file path or --text, not both.")
        sys.exit(1)

    try:
        settings = Settings.load()
    except Exception as e:
        console.print(f"[red]Config error:[/red] {e}")
        sys.exit(1)

    # Resolve options (CLI overrides config)
    resolved_provider = (provider or settings.llm_provider).lower()
    resolved_model = model or settings.get_model(resolved_provider)
    resolved_num = num_cases or settings.default_num_cases
    resolved_format = (export_format or settings.default_export_format).lower()
    focus = categories.split(",") if categories else None

    # Read input
    try:
        if text:
            requirements = text
        else:
            requirements = read_requirements(input_source)
    except Exception as e:
        console.print(f"[red]Input error:[/red] {e}")
        sys.exit(1)

    # Get API key
    try:
        api_key = settings.get_api_key(resolved_provider)
    except ValueError as e:
        console.print(f"[red]{e}[/red]")
        sys.exit(1)

    # Show info panel
    source_display = input_source or "inline text"
    console.print(Panel(
        f"[bold]Provider:[/bold] {resolved_provider} ({resolved_model})\n"
        f"[bold]Input:[/bold] {source_display} ({len(requirements)} chars)\n"
        f"[bold]Cases:[/bold] {resolved_num} | [bold]Format:[/bold] {resolved_format}"
        + (f"\n[bold]Categories:[/bold] {categories}" if categories else ""),
        title="[bold blue]smart-testgen[/bold blue]",
        border_style="blue",
    ))

    # Generate
    try:
        provider_instance = LLMProviderFactory.create(
            provider=resolved_provider,
            api_key=api_key,
            model=resolved_model,
            max_tokens=settings.max_tokens,
        )
        generator = TestGenerator(provider_instance)

        with console.status("[bold green]Generating test cases..."):
            suite = generator.generate(
                requirements=requirements,
                num_cases=resolved_num,
                focus_categories=focus,
            )
    except Exception as e:
        console.print(f"[red]Generation error:[/red] {e}")
        sys.exit(1)

    # Display summary
    summary_table = Table(title="Generation Summary")
    summary_table.add_column("Category", style="cyan")
    summary_table.add_column("Count", justify="right", style="green")
    for cat, count in sorted(suite.summary.items()):
        summary_table.add_row(cat, str(count))
    console.print(summary_table)

    # Export
    exporters = {
        "markdown": (MarkdownExporter, ".md"),
        "excel": (ExcelExporter, ".xlsx"),
        "json": (JsonExporter, ".json"),
    }

    exporter_cls, ext = exporters[resolved_format]
    if output:
        output_path = Path(output)
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path(settings.output_directory)
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"testcases_{timestamp}{ext}"

    try:
        exporter = exporter_cls()
        result_path = exporter.export(suite, output_path)
        console.print(f"\n[green]✓[/green] Exported {len(suite.test_cases)} test cases to: [bold]{result_path}[/bold]")
    except Exception as e:
        console.print(f"[red]Export error:[/red] {e}")
        sys.exit(1)


@cli.command()
@click.option(
    "--provider", "-p",
    type=click.Choice(["anthropic", "openai"], case_sensitive=False),
    required=True,
    help="Provider to configure",
)
def configure(provider: str) -> None:
    """Interactive setup for API keys (writes to .env file)."""
    provider = provider.lower()
    env_var = "ANTHROPIC_API_KEY" if provider == "anthropic" else "OPENAI_API_KEY"

    console.print(f"\n[bold]Configure {provider} API key[/bold]\n")
    console.print(f"The key will be saved as [cyan]{env_var}[/cyan] in .env\n")

    api_key = click.prompt("Enter your API key", hide_input=True)

    env_file = Path(".env")
    lines: list[str] = []
    if env_file.exists():
        lines = env_file.read_text(encoding="utf-8").splitlines()

    # Update or add the key
    updated = False
    for i, line in enumerate(lines):
        if line.startswith(f"{env_var}=") or line.startswith(f"SMARTTESTGEN_{env_var}="):
            lines[i] = f"{env_var}={api_key}"
            updated = True
            break

    if not updated:
        lines.append(f"{env_var}={api_key}")

    env_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    console.print(f"\n[green]✓[/green] API key saved to {env_file}")
    console.print(f"[dim]Set SMARTTESTGEN_PROVIDER={provider} to use this provider by default[/dim]")


@cli.command()
def version() -> None:
    """Show version and environment info."""
    import platform

    console.print(f"[bold]smart-testgen[/bold] v{__version__}")
    console.print(f"Python {platform.python_version()}")
    console.print(f"Platform {platform.platform()}")

    from smart_testgen.llm import LLMProviderFactory

    providers = LLMProviderFactory.available_providers()
    console.print(f"Available providers: {', '.join(providers)}")
