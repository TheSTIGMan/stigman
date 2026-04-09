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
        "api_key": api_key,
        "model": config.get("model"),  # only set for openrouter
    }

# Free OpenRouter models (Llama + Gemma, $0 prompt & completion)
OPENROUTER_FREE_MODELS = [
    ("meta-llama/llama-3.3-70b-instruct:free",  "Meta: Llama 3.3 70B Instruct"),
    ("meta-llama/llama-3.2-3b-instruct:free",   "Meta: Llama 3.2 3B Instruct"),
    ("nousresearch/hermes-3-llama-3.1-405b:free", "Nous: Hermes 3 405B (Llama)"),
    ("google/gemma-4-31b-it:free",              "Google: Gemma 4 31B"),
    ("google/gemma-4-26b-a4b-it:free",          "Google: Gemma 4 26B A4B"),
    ("google/gemma-3-27b-it:free",              "Google: Gemma 3 27B"),
    ("google/gemma-3-12b-it:free",              "Google: Gemma 3 12B"),
    ("google/gemma-3-4b-it:free",               "Google: Gemma 3 4B"),
    ("google/gemma-3n-e4b-it:free",             "Google: Gemma 3n 4B"),
    ("google/gemma-3n-e2b-it:free",             "Google: Gemma 3n 2B"),
]

def setup_config():
    """Interactive first-time or --setup prompt."""
    click.echo("\nFirst-time setup detected or reconfiguration requested.")
    click.echo("Select your LLM provider:")
    click.echo("  [1] Anthropic (Claude)")
    click.echo("  [2] OpenAI (GPT)")
    click.echo("  [3] OpenRouter (free Llama / Gemma models)")

    choice = click.prompt("Choice", type=click.Choice(['1', '2', '3']))

    model = None
    if choice == '1':
        provider = "anthropic"
    elif choice == '2':
        provider = "openai"
    else:
        provider = "openrouter"
        click.echo("\nSelect a free model:")
        for i, (mid, name) in enumerate(OPENROUTER_FREE_MODELS, 1):
            click.echo(f"  [{i:2}] {name}")
        model_choice = click.prompt(
            "Model",
            type=click.IntRange(1, len(OPENROUTER_FREE_MODELS))
        )
        model = OPENROUTER_FREE_MODELS[model_choice - 1][0]
        click.echo(f"Selected: {model}")

    api_key = click.prompt(f"Enter your {provider.capitalize()} API key", hide_input=True)

    config = {
        "provider": provider,
        "api_key": api_key,
    }
    if model:
        config["model"] = model

    os.makedirs(CONFIG_DIR, exist_ok=True)

    # Store with restricted permissions since it contains an API key
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)

    # Restrict permissions to owner only
    try:
        os.chmod(CONFIG_FILE, 0o600)
    except Exception:
        pass

    click.echo(f"Config saved to {CONFIG_FILE}\n")
    return config
