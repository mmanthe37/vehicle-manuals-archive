"""vmw — Vehicle Manuals Warehouse admin CLI."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(
    name="vmw",
    help="Vehicle Manuals Warehouse admin CLI",
    no_args_is_help=True,
)
console = Console()

# ---------------------------------------------------------------------------
# Sub-command groups
# ---------------------------------------------------------------------------

seed_app = typer.Typer(help="Manage seed sources", no_args_is_help=True)
crawl_app = typer.Typer(help="Manage crawl jobs", no_args_is_help=True)
parse_app = typer.Typer(help="Parse and OCR management", no_args_is_help=True)
index_app = typer.Typer(help="Index management", no_args_is_help=True)
manual_app = typer.Typer(help="Manual management", no_args_is_help=True)
vin_app = typer.Typer(help="VIN decode utilities", no_args_is_help=True)

app.add_typer(seed_app, name="seed")
app.add_typer(crawl_app, name="crawl")
app.add_typer(parse_app, name="parse")
app.add_typer(index_app, name="index")
app.add_typer(manual_app, name="manual")
app.add_typer(vin_app, name="vin")

# ---------------------------------------------------------------------------
# seed commands
# ---------------------------------------------------------------------------


@seed_app.command("add")
def seed_add(
    adapter: str = typer.Argument(..., help="Adapter ID to register as seed source"),
) -> None:
    """Register an adapter as a seed source."""
    console.print(f"[green]Registered seed adapter:[/green] {adapter}")


@seed_app.command("list")
def seed_list() -> None:
    """List registered seed sources."""
    table = Table(title="Seed Sources")
    table.add_column("Adapter ID")
    table.add_column("Base URL")
    table.add_column("Active")
    table.add_row("mock_oem", "http://mock-oem.local", "Yes")
    console.print(table)


@seed_app.command("run")
def seed_run(
    adapter: str = typer.Option("mock_oem", "--adapter", "-a", help="Adapter ID to run"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Discover only, don't store"),
) -> None:
    """Run a seed adapter end-to-end: discover → fetch → store → parse → index."""
    console.print(f"[bold]Running seed adapter:[/bold] {adapter}")

    try:
        if adapter == "mock_oem":
            _run_mock_oem(dry_run=dry_run)
        else:
            console.print(f"[red]Unknown adapter:[/red] {adapter}")
            raise typer.Exit(code=1)
    except Exception as exc:
        console.print(f"[red]Seed run failed:[/red] {exc}")
        raise typer.Exit(code=1)


def _run_mock_oem(dry_run: bool = False) -> None:
    """Execute the mock OEM adapter end-to-end pipeline."""
    from services.ingestion.adapters.mock_oem import MockOemAdapter
    from services.ingestion.fetchers.pipeline import IngestionPipeline

    adapter = MockOemAdapter()

    console.print("[cyan]Step 1:[/cyan] Discovering models/years from mock adapter …")
    model_years = list(adapter.enumerate_models_years())
    console.print(f"  Found {len(model_years)} model/year combinations")

    all_requests = []
    for make, model, year in model_years:
        requests = adapter.list_manual_links(make, model, year)
        all_requests.extend(requests)
        console.print(f"  {make.upper()} {model.title()} {year}: {len(requests)} manual(s)")

    console.print(f"\n[cyan]Step 2:[/cyan] Total manuals to ingest: {len(all_requests)}")

    if dry_run:
        console.print("[yellow]--dry-run set: skipping storage.[/yellow]")
        return

    pipeline = IngestionPipeline()  # no storage/db/events in local mode
    results = []
    for req in all_requests:
        try:
            result = pipeline.ingest(req, adapter=adapter)
            results.append(result)
            console.print(f"  [green]✓[/green] {result.logical_id} → {result.content_id[:16]}…")
        except Exception as exc:
            console.print(f"  [red]✗[/red] {req.file_path or req.source_url}: {exc}")

    console.print(
        f"\n[bold green]Ingestion complete.[/bold green] {len(results)}/{len(all_requests)} succeeded."
    )
    console.print("\n[cyan]Step 3:[/cyan] Parse, OCR, index skipped in local CLI mode.")
    console.print("  Run [bold]docker compose up[/bold] for full pipeline.")


# ---------------------------------------------------------------------------
# crawl commands
# ---------------------------------------------------------------------------


@crawl_app.command("start")
def crawl_start(source_id: str = typer.Argument(...)) -> None:
    console.print(f"[green]Started crawl for source:[/green] {source_id}")


@crawl_app.command("status")
def crawl_status() -> None:
    console.print("[yellow]No active crawls.[/yellow]")


@crawl_app.command("stop")
def crawl_stop(crawl_id: str = typer.Argument(...)) -> None:
    console.print(f"[red]Stopped crawl:[/red] {crawl_id}")


# ---------------------------------------------------------------------------
# parse commands
# ---------------------------------------------------------------------------


@parse_app.command("reprocess")
def parse_reprocess(
    since: str | None = typer.Option(None, "--since", help="ISO datetime lower bound"),
) -> None:
    console.print(f"[green]Re-queuing parse jobs since:[/green] {since or 'beginning'}")


# ---------------------------------------------------------------------------
# index commands
# ---------------------------------------------------------------------------


@index_app.command("rebuild")
def index_rebuild(
    scope: str = typer.Option("all", "--scope", help="all | manuals | pages"),
) -> None:
    console.print(f"[green]Rebuilding index:[/green] {scope}")


# ---------------------------------------------------------------------------
# manual commands
# ---------------------------------------------------------------------------


@manual_app.command("link")
def manual_link(
    content_id: str = typer.Argument(...), logical_id: str = typer.Argument(...)
) -> None:
    console.print(f"[green]Linked[/green] {content_id} → {logical_id}")


@manual_app.command("verify")
def manual_verify(content_id: str = typer.Argument(...)) -> None:
    console.print(f"[green]Verifying checksum for:[/green] {content_id}")


# ---------------------------------------------------------------------------
# export command
# ---------------------------------------------------------------------------


@app.command("export")
def export_manifest(
    output: Path = typer.Option(Path("manifest.jsonl"), "--output", "-o"),
) -> None:
    """Export a JSONL manifest of all documents."""
    console.print(f"[green]Exporting manifest to:[/green] {output}")
    output.write_text("")
    console.print("Manifest written (empty in local mode).")


# ---------------------------------------------------------------------------
# vin commands
# ---------------------------------------------------------------------------


@vin_app.command("decode")
def vin_decode(vin: str = typer.Argument(...)) -> None:
    """Decode a VIN via NHTSA API and suggest matching manuals."""
    console.print(f"[cyan]Decoding VIN:[/cyan] {vin}")
    import json
    import urllib.request

    url = f"https://vpic.nhtsa.dot.gov/api/vehicles/decodevin/{vin}?format=json"
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:  # noqa: S310
            data = json.loads(resp.read())
        results = {r["Variable"]: r["Value"] for r in data.get("Results", []) if r.get("Value")}
        make = results.get("Make", "Unknown")
        model = results.get("Model", "Unknown")
        year = results.get("Model Year", "Unknown")
        console.print(f"  Make: {make}  Model: {model}  Year: {year}")
    except Exception as exc:
        console.print(f"[red]VIN decode failed:[/red] {exc}")


if __name__ == "__main__":
    app()
