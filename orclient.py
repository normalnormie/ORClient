import asyncio
import aiohttp
import orjson
import click
import yaml
import glob
from typing import Optional, Dict, Any, List, Union, Set
from pathlib import Path
from rich import print as rprint
from rich.console import Console
from rich.syntax import Syntax
from itertools import chain

console = Console()

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
        """
        Load and read context from files and directories.
        Supports glob patterns and directory traversal.
        """
        if isinstance(paths, (str, Path)):
            paths = [paths]

        # Set of supported file extensions
        supported_extensions = {'.py', '.txt', '.md', '.yml', '.yaml', '.json', 
                              '.js', '.css', '.html', '.cpp', '.h', '.java', 
                              '.rs', '.go', '.ts', '.jsx', '.tsx'}
        
        # Collect all file paths
        all_files: Set[Path] = set()
        for path in paths:
            path_obj = Path(path)
            
            if path_obj.is_dir():
                # Recursively get all files in directory
                for ext in supported_extensions:
                    all_files.update(path_obj.rglob(f"*{ext}"))
            elif '*' in str(path):
                # Handle glob patterns
                all_files.update(Path(p) for p in glob.glob(str(path), recursive=True))
            else:
                all_files.add(path_obj)

        # Filter out unsupported files and load contents
        contexts = []
        async with aiohttp.ClientSession() as session:
            tasks = []
            for file_path in sorted(all_files):  # Sort for consistent ordering
                if file_path.suffix in supported_extensions and file_path.exists():
                    tasks.append(self._load_file(session, file_path))

            contexts = await asyncio.gather(*tasks, return_exceptions=True)
        
        return [ctx for ctx in contexts if isinstance(ctx, str)]

    async def _load_file(self, session: aiohttp.ClientSession, file_path: Path) -> str:
        """Load a single file with metadata."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Add file metadata
            file_info = f"""
            File: {file_path.name}
            Type: {file_path.suffix[1:]}
            Path: {file_path}
            ---
            {content}
            ---
            """
                
            if file_path.suffix in {'.yml', '.yaml'}:
                return yaml.safe_load(content)
            return file_info
        except Exception as e:
            console.print(f"[yellow]Warning:[/yellow] Error loading {file_path}: {e}")
            return ""

    async def query_claude(
        self,
        query: str,
        contexts: Optional[Union[str, List[str]]] = None,
        template_name: Optional[str] = None,
        template_vars: Optional[Dict[str, str]] = None,
        temperature: float = 0.7
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

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_url,
                    headers=self.headers,
                    json=payload
                ) as response:
                    return await response.json(loads=orjson.loads)
        except Exception as e:
            return {"error": f"Query failed: {str(e)}"}

@click.group()
@click.option('--api-key', envvar='OPENROUTER_API_KEY', 
              help='OpenRouter API key (can also be set via OPENROUTER_API_KEY env variable)')
@click.option('--grok', is_flag=True, help='Use Grok model instead of Claude')
@click.pass_context
def cli(ctx, api_key, grok):
    """
    AI Code Assistant CLI - A command-line interface for coding-related queries using Claude or Grok.

    Context can be provided in multiple ways:
    - Single file: --context file.py
    - Multiple files: --context "*.py"
    - Directories: --context src/
    - Multiple patterns: --context "src/**/*.py" --context "docs/*.md"

    Examples:
        # Review code using Claude:
        ai-assist review code.py

        # Review code using Grok:
        ai-assist --grok review code.py

        # Explain code with multiple context files:
        ai-assist explain main.py --context "src/**/*.py" --context "docs/"

        # Generate documentation:
        ai-assist document api.py --output docs.md

        # Custom query with template:
        ai-assist query "How to optimize this code?" --template performance --code-file slow.py
    """
    if not api_key:
        raise click.UsageError("API key is required. Set it via --api-key or OPENROUTER_API_KEY environment variable.")
    ctx.obj = AIClient(api_key, use_grok=grok)

@cli.command()
@click.argument('file', type=click.Path(exists=True))
@click.option('--context', '-c', multiple=True, help='Context files/directories (supports glob patterns)')
@click.option('--temperature', '-t', default=0.7, help='Temperature for response generation (0.0-1.0)')
@click.pass_obj
def review(client, file, context, temperature):
    """Review code from a file for quality, bugs, and improvements."""
    async def run():
        with open(file, 'r') as f:
            code = f.read()

        contexts = await client.load_context_files(list(context)) if context else None
        
        model_name = "Grok" if isinstance(client.model, str) and "grok" in client.model.lower() else "Claude"
        with console.status(f"[bold green]Analyzing code with {model_name}...[/bold green]"):
            response = await client.query_claude(
                query="",
                contexts=contexts,
                template_name="code_review",
                template_vars={"code": code},
                temperature=temperature
            )

        if "error" in response:
            console.print(f"[red]Error:[/red] {response['error']}")
            return

        console.print(f"\n[bold green]{model_name} Code Review Results:[/bold green]")
        console.print(response["choices"][0]["message"]["content"])

    asyncio.run(run())

@cli.command()
@click.argument('file', type=click.Path(exists=True))
@click.option('--context', '-c', multiple=True, help='Context files/directories (supports glob patterns)')
@click.option('--temperature', '-t', default=0.7, help='Temperature for response generation (0.0-1.0)')
@click.pass_obj
def explain(client, file, context, temperature):
    """Explain how the code works with detailed examples."""
    async def run():
        with open(file, 'r') as f:
            code = f.read()

        contexts = await client.load_context_files(list(context)) if context else None
        
        model_name = "Grok" if isinstance(client.model, str) and "grok" in client.model.lower() else "Claude"
        with console.status(f"[bold green]Generating explanation with {model_name}...[/bold green]"):
            response = await client.query_claude(
                query="",
                contexts=contexts,
                template_name="explain_code",
                template_vars={"code": code},
                temperature=temperature
            )

        if "error" in response:
            console.print(f"[red]Error:[/red] {response['error']}")
            return

        console.print(f"\n[bold green]{model_name} Explanation:[/bold green]")
        console.print(response["choices"][0]["message"]["content"])

    asyncio.run(run())

@cli.command()
@click.argument('file', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(), help='Output file for documentation')
@click.option('--format', '-f', default='markdown', 
              type=click.Choice(['markdown', 'rst', 'html', 'docstring']), 
              help='Documentation format')
@click.option('--context', '-c', multiple=True, help='Context files/directories (supports glob patterns)')
@click.pass_obj
def document(client, file, output, format, context):
    """Generate documentation for the given code."""
    async def run():
        with open(file, 'r') as f:
            code = f.read()

        contexts = await client.load_context_files(list(context)) if context else None

        template = f"""Generate comprehensive documentation for this code in {format} format:
        {code}
        Include:
        1. Overview
        2. Function/class descriptions
        3. Parameters
        4. Return values
        5. Usage examples
        6. Dependencies
        7. Installation instructions (if applicable)
        """

        model_name = "Grok" if isinstance(client.model, str) and "grok" in client.model.lower() else "Claude"
        with console.status(f"[bold green]Generating documentation with {model_name}...[/bold green]"):
            response = await client.query_claude(
                query=template,
                contexts=contexts
            )

        if "error" in response:
            console.print(f"[red]Error:[/red] {response['error']}")
            return

        documentation = response["choices"][0]["message"]["content"]
        
        if output:
            with open(output, 'w') as f:
                f.write(documentation)
            console.print(f"[green]Documentation saved to {output}[/green]")
        else:
            console.print(f"\n[bold green]{model_name} Documentation:[/bold green]")
            console.print(documentation)

    asyncio.run(run())

@cli.command()
@click.argument('query')
@click.option('--template', '-t', help='Name of the template to use')
@click.option('--code-file', '-f', type=click.Path(exists=True), help='File containing code to include in the query')
@click.option('--context', '-c', multiple=True, help='Context files/directories (supports glob patterns)')
@click.option('--temperature', default=0.7, help='Temperature for response generation (0.0-1.0)')
@click.pass_obj
def query(client, query, template, code_file, context, temperature):
    """Send a custom query to the AI model."""
    async def run():
        template_vars = {}
        if code_file:
            with open(code_file, 'r') as f:
                template_vars["code"] = f.read()

        contexts = await client.load_context_files(list(context)) if context else None

        model_name = "Grok" if isinstance(client.model, str) and "grok" in client.model.lower() else "Claude"
        with console.status(f"[bold green]Processing query with {model_name}...[/bold green]"):
            response = await client.query_claude(
                query=query,
                contexts=contexts,
                template_name=template if template else None,
                template_vars=template_vars,
                temperature=temperature
            )

        if "error" in response:
            console.print(f"[red]Error:[/red] {response['error']}")
            return

        console.print(f"\n[bold green]{model_name} Response:[/bold green]")
        console.print(response["choices"][0]["message"]["content"])

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
def info():
    """Show information about supported file types and context handling."""
    console.print("\n[bold green]Supported File Types:[/bold green]")
    supported_files = [
        ".py (Python)",
        ".txt (Text)",
        ".md (Markdown)",
        ".yml/.yaml (YAML)",
        ".json (JSON)",
        ".js (JavaScript)",
        ".css (CSS)",
        ".html (HTML)",
        ".cpp (C++)",
        ".h (C/C++ Headers)",
        ".java (Java)",
        ".rs (Rust)",
        ".go (Go)",
        ".ts (TypeScript)",
        ".jsx (React JSX)",
        ".tsx (React TSX)"
    ]
    for file_type in supported_files:
        console.print(f"• {file_type}")

    console.print("\n[bold green]Context Patterns Examples:[/bold green]")
    examples = [
        ("Single file", "ai-assist review code.py --context utils.py"),
        ("Multiple files", 'ai-assist review code.py --context "*.py"'),
        ("Directory", "ai-assist review code.py --context src/"),
        ("Recursive", 'ai-assist review code.py --context "src/**/*.py"'),
        ("Multiple patterns", 'ai-assist review code.py --context "src/**/*.py" --context "docs/*.md"'),
        ("Mixed", 'ai-assist review code.py --context "src/" --context "tests/**/*.py" --context "config.yml"')
    ]
    for label, example in examples:
        console.print(f"• [bold]{label}[/bold]")
        console.print(f"  {example}")

if __name__ == "__main__":
    cli()

