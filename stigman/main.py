import os
import sys
import click

from .config import load_config, setup_config
from .agent import AgentSession

def check_root():
    if os.geteuid() != 0:
        click.secho("Error: stigman must be run as root to execute OpenSCAP scans and remediations.", fg="red", err=True)
        click.secho("Please run again with sudo: sudo stigman", fg="yellow", err=True)
        sys.exit(1)

@click.command()
@click.option("--setup", is_flag=True, help="Run first-time setup to configure an LLM provider.")
@click.option("--api-key", help="Provide the API key directly (overrides env and config file).")
def cli(setup, api_key):
    """AI-powered DISA STIG compliance scanner for Ubuntu Server 22.04 LTS."""
    
    # Must be root
    check_root()
    
    if setup:
        config = setup_config()
    else:
        config = load_config(cli_api_key=api_key)
        if not config:
            click.echo("\nWelcome to stigman! AI-powered DISA STIG compliance scanner.")
            config = setup_config()
            
    # Initialize the Agent
    provider = config.get("provider")
    key = config.get("api_key")
    
    if not provider or not key:
        click.secho("Configuration incomplete. Please run 'stigman --setup'.", fg="red", err=True)
        sys.exit(1)
        
    try:
        agent = AgentSession(provider=provider, api_key=key)
    except Exception as e:
        click.secho(f"Error initializing agent: {str(e)}", fg="red", err=True)
        click.secho("Ensure you have the required SDKs installed (anthropic or openai).", fg="yellow")
        sys.exit(1)
        
    click.echo("\nYou're all set! Type a command or ask a question.")
    click.echo("(Type 'exit' or 'quit' to close, or hit Ctrl+C)\n")
    
    while True:
        try:
            user_input = input("> ").strip()
            if user_input.lower() in ["exit", "quit"]:
                break
            if not user_input:
                continue
                
            response = agent.run_conversation(user_input)
            click.echo(f"\n{response}\n")
            
        except KeyboardInterrupt:
            click.echo("\nExiting stigman. Goodbye!")
            break
        except Exception as e:
            click.secho(f"\nAn error occurred: {str(e)}\n", fg="red")

if __name__ == "__main__":
    cli()
