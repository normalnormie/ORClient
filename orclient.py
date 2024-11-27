#Monitor for updating defaults:
# https://openrouter.ai/x-ai/grok-beta?tab=parameters
# https://openrouter.ai/anthropic/claude-3.5-sonnet:beta
#Todo:
#add preserve context -chat history with duckdb?-: https://community.openai.com/t/how-to-preserve-the-context-session-of-a-conversation-with-the-api/324986/3

import asyncio
import aiohttp
import orjson
import click
import yaml
import signal
import sys
import json
from typing import Optional, Dict, Any, List, Union, Set
from pathlib import Path
from rich import print as rprint
from rich.console import Console
from rich.syntax import Syntax
from itertools import chain

console = Console()


# Signal handling
def handle_sigint(signum, frame):
    console.print("\n[yellow]Cancelling request...[/yellow]")
    sys.exit(0)


signal.signal(signal.SIGINT, handle_sigint)
signal.signal(signal.SIGTERM, handle_sigint)
signal.signal(signal.SIGHUP, handle_sigint)


class ModelConfig:
    def __init__(self):
        self.temperature = 0.50
        self.top_p = 1.0
        self.top_k = 0
        self.frequency_penalty = 0
        self.presence_penalty = 0
        self.repetition_penalty = 1.0
        self.min_p = 0
        self.top_a = 0


class ClaudeConfig(ModelConfig):
    def __init__(self):
        super().__init__()
        self.temperature = 0.50  # p50 value
        self.top_p = 1.0
        self.frequency_penalty = 0
        self.presence_penalty = 0


class GrokConfig(ModelConfig):
    def __init__(self):
        super().__init__()
        self.temperature = 0.80  # p50 value
        self.top_p = 1.0
        self.presence_penalty = 0.0


class PromptTemplate:
    def __init__(self, template: str):
        self.template = template

    def format(self, **kwargs) -> str:
        try:
            return self.template.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"Missing required variable in template: {e}")


class AIClient:
    def __init__(self, api_key: str, use_grok: bool = False):
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": "https://localhost",
            "Content-Type": "application/json"
        }
        self.model = "x-ai/grok-beta" if use_grok else "anthropic/claude-3.5-sonnet:beta"
        self.config = GrokConfig() if use_grok else ClaudeConfig()
        self.templates = self._load_default_templates()

    def _load_default_templates(self) -> Dict[str, PromptTemplate]:
        """Load default prompt templates."""
        return {
            "code_review": PromptTemplate(
                "Please review the following code:\n{code}\n"
                "Focus on:\n"
                "1. Code quality\n"
                "2. Potential bugs\n"
                "3. Performance improvements\n"
                "4. Security considerations\n"
                "5. Best practices"
            ),
            "explain_code": PromptTemplate(
                "Please explain how this code works:\n{code}\n"
                "Provide:\n"
                "1. High-level overview\n"
                "2. Detailed explanation of key components\n"
                "3. Flow of execution\n"
                "4. Practical examples\n"
                "5. Potential edge cases"
            ),
            "refactor": PromptTemplate(
                "Please suggest refactoring improvements for this code:\n{code}\n"
                "Consider:\n"
                "1. Clean code principles\n"
                "2. Design patterns\n"
                "3. Performance optimization\n"
                "4. Code maintainability\n"
                "5. Modern best practices"
            ),
            "debug": PromptTemplate(
                "Help debug this code:\n{code}\n"
                "Error message:\n{error}\n"
                "Please provide:\n"
                "1. Error analysis\n"
                "2. Potential causes\n"
                "3. Solution suggestions\n"
                "4. Prevention tips"
            ),
            "optimize": PromptTemplate(
                "Optimize this code for better performance:\n{code}\n"
                "Consider:\n"
                "1. Time complexity\n"
                "2. Space complexity\n"
                "3. Resource usage\n"
                "4. Algorithm improvements\n"
                "5. Language-specific optimizations"
            )
        }

    def add_template(self, name: str, template: str) -> None:
        """Add a new prompt template."""
        self.templates[name] = PromptTemplate(template)

    def get_template(self, name: str) -> PromptTemplate:
        """Get a prompt template by name."""
        if name not in self.templates:
            raise KeyError(f"Template '{name}' not found")
        return self.templates[name]

    async def load_context_files(self, paths: Union[str, List[str], Path, List[Path]]) -> List[str]:
        """Load and read context from files and directories."""
        if isinstance(paths, (str, Path)):
            paths = [paths]

        supported_extensions = {'.py', '.txt', '.md', '.yml', '.yaml', '.json',
                                '.js', '.css', '.html', '.cpp', '.h', '.java',
                                '.rs', '.go', '.ts', '.jsx', '.tsx'}

        all_files: Set[Path] = set()
        for path in paths:
            path_obj = Path(path)

            if path_obj.is_dir():
                for ext in supported_extensions:
                    all_files.update(path_obj.rglob(f"*{ext}"))
            elif '*' in str(path):
                all_files.update(Path(p) for p in glob.glob(str(path), recursive=True))
            else:
                all_files.add(path_obj)

        contexts = []
        for file_path in sorted(all_files):
            if file_path.suffix in supported_extensions and file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        file_info = f"""
                        File: {file_path.name}
                        Type: {file_path.suffix[1:]}
                        Path: {file_path}
                        ---
                        {content}
                        ---
                        """
                        contexts.append(file_info)
                except Exception as e:
                    console.print(f"[yellow]Warning:[/yellow] Error loading {file_path}: {e}")

        return contexts

    async def query_claude(
            self,
            query: str,
            contexts: Optional[Union[str, List[str]]] = None,
            template_name: Optional[str] = None,
            template_vars: Optional[Dict[str, str]] = None,
            **kwargs
    ) -> Dict[Any, Any]:
        """Send a query to the AI model with optional contexts and template."""
        messages = []

        if contexts:
            if isinstance(contexts, str):
                contexts = [contexts]

            context_message = "Using the following contexts for reference:\n\n"
            for idx, context in enumerate(contexts, 1):
                context_message += f"Context {idx}:\n{context}\n\n"

            messages.append({
                "role": "system",
                "content": context_message
            })

        final_query = query
        if template_name:
            try:
                template = self.get_template(template_name)
                template_vars = template_vars or {}
                final_query = template.format(**template_vars)
            except (KeyError, ValueError) as e:
                return {"error": f"Template error: {str(e)}"}

        messages.append({
            "role": "user",
            "content": final_query
        })

        # Update config with any provided kwargs
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": self.config.temperature,
            "top_p": self.config.top_p,
            "top_k": self.config.top_k,
            "frequency_penalty": self.config.frequency_penalty,
            "presence_penalty": self.config.presence_penalty,
            "repetition_penalty": self.config.repetition_penalty,
            "min_p": self.config.min_p,
            "top_a": self.config.top_a
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                        self.api_url,
                        headers=self.headers,
                        json=payload
                ) as response:
                    if not response.ok:
                        error_data = await response.text()
                        return {"error": f"API request failed: {error_data}"}

                    return await response.json(loads=orjson.loads)
        except Exception as e:
            return {"error": f"Query failed: {str(e)}"}


@click.group()
@click.option('--api-key', envvar='OPENROUTER_API_KEY',
              help='OpenRouter API key (can also be set via OPENROUTER_API_KEY env variable)')
@click.option('--grok', is_flag=True, help='Use Grok model instead of Claude')
@click.option('--json', 'json_output', is_flag=True, help='Output raw JSON response')
@click.option('--temperature', type=float, help='Temperature (0-1)')
@click.option('--top-p', type=float, help='Top P (0-1)')
@click.option('--top-k', type=int, help='Top K')
@click.option('--frequency-penalty', type=float, help='Frequency penalty (0-2)')
@click.option('--presence-penalty', type=float, help='Presence penalty (0-2)')
@click.option('--repetition-penalty', type=float, help='Repetition penalty')
@click.option('--min-p', type=float, help='Min P (0-1)')
@click.option('--top-a', type=float, help='Top A')
@click.pass_context
def cli(ctx, api_key, grok, json_output, **kwargs):
    """
    AI Code Assistant CLI - A command-line interface for coding-related queries using Claude or Grok.

    \b
    Model Parameters:

    Claude defaults (p10 - p50 - p90):
      temperature: 0.0 - 0.50 - 1.0
      top_p: 0.90 - 1.0 - 1.0
      frequency_penalty: 0 - 0 - 0.35
      presence_penalty: 0 - 0 - 0.35

    Grok defaults (p10 - p50 - p90):
      temperature: 0.50 - 0.80 - 1.0
      top_p: 1.0 - 1.0 - 1.0
      presence_penalty: 0 - 0 - 0.10

    \b
    Request Cancellation:
      - Press Ctrl+C to cancel request
      - Send SIGINT, SIGTERM, or SIGHUP signals

    \b
    Context can be provided in multiple ways:
      - Single file: --context file.py
      - Multiple files: --context "*.py"
      - Directories: --context src/
      - Multiple patterns: --context "src/**/*.py" --context "docs/*.md"
    """
    if not api_key:
        raise click.UsageError(
            "API key is required. Set it via --api-key or OPENROUTER_API_KEY environment variable.")

    ctx.obj = {
        'client': AIClient(api_key, use_grok=grok),
        'json_output': json_output,
        'model_params': {k: v for k, v in kwargs.items() if v is not None}
    }


@cli.command()
@click.argument('file', type=click.Path(exists=True))
@click.option('--context', '-c', multiple=True, help='Context files/directories (supports glob patterns)')
@click.pass_obj
def review(obj, file, context):
    """Review code from a file for quality, bugs, and improvements."""

    async def run():
        with open(file, 'r') as f:
            code = f.read()

        client = obj['client']
        contexts = await client.load_context_files(list(context)) if context else None

        model_name = "Grok" if "grok" in client.model else "Claude"
        with console.status(f"[bold green]Analyzing code with {model_name}...[/bold green]"):
            response = await client.query_claude(
                query="",
                contexts=contexts,
                template_name="code_review",
                template_vars={"code": code},
                **obj['model_params']
            )

            if obj['json_output']:
                console.print(json.dumps(response, indent=2))
            else:
                if 'choices' in response and response['choices']:
                    content = response['choices'][0].get('message', {}).get('content', '')
                    if content:
                        console.print(content)
                elif 'error' in response:
                    console.print(f"[red]Error:[/red] {response['error']}")

    asyncio.run(run())


@cli.command()
@click.argument('file', type=click.Path(exists=True))
@click.option('--context', '-c', multiple=True, help='Context files/directories (supports glob patterns)')
@click.pass_obj
def explain(obj, file, context):
    """Explain how the code works with detailed examples."""

    async def run():
        with open(file, 'r') as f:
            code = f.read()

        client = obj['client']
        contexts = await client.load_context_files(list(context)) if context else None

        model_name = "Grok" if "grok" in client.model else "Claude"
        with console.status(f"[bold green]Analyzing code with {model_name}...[/bold green]"):
            response = await client.query_claude(
                query="",
                contexts=contexts,
                template_name="explain_code",
                template_vars={"code": code},
                **obj['model_params']
            )

            if obj['json_output']:
                console.print(json.dumps(response, indent=2))
            else:
                if 'choices' in response and response['choices']:
                    content = response['choices'][0].get('message', {}).get('content', '')
                    if content:
                        console.print(content)
                elif 'error' in response:
                    console.print(f"[red]Error:[/red] {response['error']}")

    asyncio.run(run())


@cli.command()
@click.argument('query')
@click.option('--template', '-t', help='Name of the template to use')
@click.option('--code-file', '-f', type=click.Path(exists=True),
              help='File containing code to include in the query')
@click.option('--context', '-c', multiple=True, help='Context files/directories (supports glob patterns)')
@click.pass_obj
def query(obj, query, template, code_file, context):
    """Send a custom query to the AI model."""

    async def run():
        template_vars = {}
        if code_file:
            with open(code_file, 'r') as f:
                template_vars["code"] = f.read()

        client = obj['client']
        contexts = await client.load_context_files(list(context)) if context else None

        model_name = "Grok" if "grok" in client.model else "Claude"
        with console.status(f"[bold green]Processing query with {model_name}...[/bold green]"):
            response = await client.query_claude(
                query=query,
                contexts=contexts,
                template_name=template if template else None,
                template_vars=template_vars,
                **obj['model_params']
            )

            if obj['json_output']:
                console.print(json.dumps(response, indent=2))
            else:
                if 'choices' in response and response['choices']:
                    content = response['choices'][0].get('message', {}).get('content', '')
                    if content:
                        console.print(content)
                elif 'error' in response:
                    console.print(f"[red]Error:[/red] {response['error']}")

    asyncio.run(run())


@cli.command()
def templates():
    """List available templates and their descriptions."""
    client = AIClient("dummy")  # API key not needed for listing templates
    console.print("\n[bold green]Available Templates:[/bold green]")
    for name, template in client.templates.items():
        console.print(f"\n[bold]{name}[/bold]")
        console.print(template.template)


@cli.command()
def parameters():
    """Show information about model parameters and their defaults."""
    console.print("\n[bold green]Claude Parameters (p10 - p50 - p90):[/bold green]")
    claude_params = {
        "temperature": "0.0 - 0.50 - 1.0",
        "top_p": "0.90 - 1.0 - 1.0",
        "top_k": "0 - 0 - 0",
        "frequency_penalty": "0 - 0 - 0.35",
        "presence_penalty": "0 - 0 - 0.35",
        "repetition_penalty": "1.0 - 1.0 - 1.0",
        "min_p": "0 - 0 - 0",
        "top_a": "0 - 0 - 0"
    }
    for param, values in claude_params.items():
        console.print(f"• [bold]{param}:[/bold] {values}")

    console.print("\n[bold green]Grok Parameters (p10 - p50 - p90):[/bold green]")
    grok_params = {
        "temperature": "0.50 - 0.80 - 1.0",
        "top_p": "1.0 - 1.0 - 1.0",
        "top_k": "0 - 0 - 0",
        "frequency_penalty": "0 - 0 - 0",
        "presence_penalty": "0 - 0 - 0.10",
        "repetition_penalty": "1.0 - 1.0 - 1.0",
        "min_p": "0 - 0 - 0",
        "top_a": "0 - 0 - 0"
    }
    for param, values in grok_params.items():
        console.print(f"• [bold]{param}:[/bold] {values}")


if __name__ == "__main__":
    cli()

