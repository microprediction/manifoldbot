"""
Command-line interface for ManifoldBot.

Provides CLI commands for managing and running bots.
"""

import logging
from pathlib import Path


import click

from .config.settings import create_example_config, load_config
from .core.bot import Bot


@click.group()
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
@click.option("--log-level", default="INFO", help="Set logging level")
def cli(verbose: bool, log_level: str):
    """ManifoldBot - Intelligent trading bots for Manifold Markets."""
    # Set up logging
    level = logging.DEBUG if verbose else getattr(logging, log_level.upper())
    logging.basicConfig(level=level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")


@cli.command()
@click.option("--config", "-c", required=True, help="Path to configuration file")
def start(config: str):
    """Start a bot with the given configuration."""
    try:
        bot = Bot.from_config_file(config)
        click.echo(f"Starting bot: {bot.config.name}")
        bot.run()
    except Exception as e:
        click.echo(f"Error starting bot: {e}", err=True)
        raise click.Abort()


@cli.command()
@click.option("--output", "-o", default="bot_config.yaml", help="Output file path")
def init(output: str):
    """Create an example configuration file."""
    config_content = create_example_config()

    output_path = Path(output)
    if output_path.exists():
        if not click.confirm(f"File {output} already exists. Overwrite?"):
            click.echo("Aborted.")
            return

    with open(output_path, "w") as f:
        f.write(config_content)

    click.echo(f"Created example configuration: {output}")
    click.echo("Edit the file and run: manifoldbot start --config bot_config.yaml")


@cli.command()
@click.option("--config", "-c", required=True, help="Path to configuration file")
def validate(config: str):
    """Validate a configuration file."""
    try:
        bot_config = load_config(config)
        click.echo("✅ Configuration is valid!")
        click.echo(f"Bot name: {bot_config.name}")
        click.echo(f"Data sources: {len(bot_config.data_sources)}")
        click.echo(f"Market: {bot_config.manifold.market_slug}")
    except Exception as e:
        click.echo(f"❌ Configuration error: {e}", err=True)
        raise click.Abort()


@cli.command()
def version():
    """Show version information."""
    from . import __version__

    click.echo(f"ManifoldBot version {__version__}")


# Main entry point for the package
def main():
    """Main entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
