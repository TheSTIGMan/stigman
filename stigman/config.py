import json
import os
import click

CONFIG_DIR = os.path.expanduser("~/.stigman")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

def load_config(cli_api_key=None):
    """
    Loads configuration. Priority:
    1. CLI Flag (--api-key)
    2. Env Var (STIGMAN_API_KEY)
    3. Config File (~/.stigman/config.json)
    """
    config = {}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
        except json.JSONDecodeError:
            pass

    # API key resolution
    api_key = cli_api_key or os.environ.get("STIGMAN_API_KEY") or config.get("api_key")
    provider = config.get("provider")

    if not api_key or not provider:
        return None  # Needs setup

    return {
        "provider": provider,
        "api_key": api_key
    }

def setup_config():
    """Interactive first-time or --setup prompt."""
    click.echo("\nFirst-time setup detected or reconfiguration requested.")
    click.echo("Select your LLM provider:")
    click.echo("  [1] Anthropic (Claude)")
    click.echo("  [2] OpenAI (GPT)")
    
    choice = click.prompt("Choice", type=click.Choice(['1', '2']))
    provider = "anthropic" if choice == '1' else "openai"
    
    api_key = click.prompt(f"Enter your {provider.capitalize()} API key", hide_input=True)
    
    config = {
        "provider": provider,
        "api_key": api_key
    }
    
    os.makedirs(CONFIG_DIR, exist_ok=True)
    
    # Store with restricted permissions since it contains an API key
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)
    
    # Restrict permissions to user
    try:
        os.chmod(CONFIG_FILE, 0o600)
    except Exception:
        pass
        
    click.echo(f"Config saved to {CONFIG_FILE}\n")
    return config
