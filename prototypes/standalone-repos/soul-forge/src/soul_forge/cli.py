"""Command line interface for Soul Forge."""

import argparse
import json
import sys
from pathlib import Path

from rich.console import Console
from rich.table import Table

from .soul_forge import SoulForge
from .activator import SoulActivator
from .vector import SoulVector

console = Console()


def cmd_digest(args):
    """Digest a repository into a soul vector."""
    forge = SoulForge()
    
    console.print(f"[bold blue]Digesting {args.repo}...[/]")
    
    soul = forge.digest_repo(args.repo, agent_name=args.name)
    soul.save(args.output)
    
    console.print(f"[bold green]✓ Soul saved to {args.output}[/]")
    console.print(f"  Agent: {soul.metadata.agent_name}")
    console.print(f"  Repo hash: {soul.metadata.repo_hash}")
    console.print(f"  Compression: {soul.metadata.compression_ratio:.1f}:1")
    console.print(f"  Activation tokens: {', '.join(soul.activation_tokens)}")


def cmd_activate(args):
    """Activate a soul vector."""
    activator = SoulActivator(lora_r=args.lora_r)
    
    console.print(f"[bold blue]Activating {args.soul}...[/]")
    
    adapter = activator.activate(args.soul)
    
    if args.output:
        adapter.save(args.output)
        console.print(f"[bold green]✓ LoRA adapter saved to {args.output}[/]")
    
    console.print(f"  Soul: {adapter.soul_name}")
    console.print(f"  LoRA rank: {adapter.config.r}")
    console.print(f"  Target modules: {', '.join(adapter.config.target_modules)}")
    
    # Show active souls
    active = activator.list_active()
    if active:
        console.print(f"  Active souls: {', '.join(active)}")


def cmd_compare(args):
    """Compare two soul vectors."""
    soul_a = SoulVector.load(args.soul_a)
    soul_b = SoulVector.load(args.soul_b)
    
    similarity = soul_a.cosine_similarity(soul_b)
    
    console.print(f"[bold blue]Comparing souls...[/]")
    console.print(f"  {soul_a.metadata.agent_name} vs {soul_b.metadata.agent_name}")
    console.print(f"  Similarity: {similarity:.3f}")
    
    if similarity > 0.9:
        console.print("  [green]Nearly identical personas[/]")
    elif similarity > 0.7:
        console.print("  [yellow]Similar style, different focus[/]")
    elif similarity > 0.5:
        console.print("  [orange]Distant cousins[/]")
    else:
        console.print("  [red]Different species[/]")


def cmd_stack(args):
    """Stack multiple souls."""
    activator = SoulActivator()
    
    console.print(f"[bold blue]Stacking {len(args.souls)} souls...[/]")
    
    hybrid = activator.stack(args.souls)
    
    if args.output:
        hybrid.save(args.output)
        console.print(f"[bold green]✓ Hybrid saved to {args.output}[/]")
    
    console.print(f"  Hybrid name: {hybrid.soul_name}")
    console.print(f"  Components: {', '.join(args.souls)}")


def cmd_fleet(args):
    """List fleet soul registry."""
    registry = Path(args.registry)
    
    if not registry.exists():
        console.print(f"[red]Registry not found: {registry}[/]")
        return
    
    table = Table(title="Fleet Soul Registry")
    table.add_column("Agent", style="cyan")
    table.add_column("Repo Hash", style="magenta")
    table.add_column("Created", style="green")
    table.add_column("Compression", justify="right")
    
    for soul_file in sorted(registry.glob("*.soul")):
        try:
            soul = SoulVector.load(str(soul_file))
            table.add_row(
                soul.metadata.agent_name,
                soul.metadata.repo_hash,
                soul.metadata.created[:10],
                f"{soul.metadata.compression_ratio:.0f}:1",
            )
        except Exception as e:
            console.print(f"[red]Error loading {soul_file}: {e}[/]")
    
    console.print(table)


def cmd_info(args):
    """Show soul vector info."""
    soul = SoulVector.load(args.soul)
    
    console.print(f"[bold blue]{soul.metadata.agent_name}[/]")
    console.print(f"  Repo hash: {soul.metadata.repo_hash}")
    console.print(f"  Created: {soul.metadata.created}")
    console.print(f"  Digest model: {soul.metadata.digest_model}")
    console.print(f"  Compression: {soul.metadata.compression_ratio:.1f}:1")
    console.print(f"  Source: {soul.metadata.source_repo or 'unknown'}")
    console.print(f"  Activation tokens: {', '.join(soul.activation_tokens)}")
    console.print(f"  Vector norm: {float(soul.vector @ soul.vector):.3f}")
    
    # Dimension breakdown
    dims = soul.dimensions
    console.print("\n[bold]Dimensions:[/]")
    console.print(f"  Temporal:      {float(dims.temporal @ dims.temporal):.3f}")
    console.print(f"  Stylistic:     {float(dims.stylistic @ dims.stylistic):.3f}")
    console.print(f"  Social:        {float(dims.social @ dims.social):.3f}")
    console.print(f"  Philosophical: {float(dims.philosophical @ dims.philosophical):.3f}")


def main():
    parser = argparse.ArgumentParser(
        description="Soul Forge — Git-native soul vector extraction",
        prog="soul-forge",
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Digest
    digest_parser = subparsers.add_parser("digest", help="Digest a repo")
    digest_parser.add_argument("repo", help="Path to git repository")
    digest_parser.add_argument("--name", help="Agent name (default: repo name)")
    digest_parser.add_argument("-o", "--output", required=True, help="Output soul file")
    digest_parser.set_defaults(func=cmd_digest)
    
    # Activate
    activate_parser = subparsers.add_parser("activate", help="Activate a soul")
    activate_parser.add_argument("soul", help="Path to soul file")
    activate_parser.add_argument("-o", "--output", help="Output LoRA file")
    activate_parser.add_argument("--lora-r", type=int, default=16, help="LoRA rank")
    activate_parser.set_defaults(func=cmd_activate)
    
    # Compare
    compare_parser = subparsers.add_parser("compare", help="Compare two souls")
    compare_parser.add_argument("soul_a", help="First soul file")
    compare_parser.add_argument("soul_b", help="Second soul file")
    compare_parser.set_defaults(func=cmd_compare)
    
    # Stack
    stack_parser = subparsers.add_parser("stack", help="Stack multiple souls")
    stack_parser.add_argument("souls", nargs="+", help="Soul files to stack")
    stack_parser.add_argument("-o", "--output", required=True, help="Output hybrid soul")
    stack_parser.set_defaults(func=cmd_stack)
    
    # Fleet
    fleet_parser = subparsers.add_parser("fleet", help="List fleet registry")
    fleet_parser.add_argument("--registry", default=".soul", help="Registry directory")
    fleet_parser.set_defaults(func=cmd_fleet)
    
    # Info
    info_parser = subparsers.add_parser("info", help="Show soul info")
    info_parser.add_argument("soul", help="Path to soul file")
    info_parser.set_defaults(func=cmd_info)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    args.func(args)


if __name__ == "__main__":
    main()
