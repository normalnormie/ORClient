##### This code was developed through multiple iterative refinements using Claude 3.5 Sonnet. 
##### It facilitates querying advanced language models like Claude 3.5 Sonnet, Grok, and Gemini 2.0(Free) via OpenRouter, which currently represent the most sophisticated large language models (LLMs) for code generation and in future when Grok is ready, real-time information retrieval. 
##### The implementation provides flexible options for incorporating files and directories into the prompt.

##### Install:
```
pip install -r requirements.txt
or
pip install click rich aiohttp orjson pyyaml
```

##### Usage:
```
Usage: orclient.py [OPTIONS] COMMAND [ARGS]...

  AI Code Assistant CLI - A command-line interface for coding-related queries
  using Claude, Grok, or Gemini.

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

  Gemini defaults:
    temperature: 0.70
    top_p: 1.0
    presence_penalty: 0.0

  Request Cancellation:
    - Press Ctrl+C to cancel request
    - Send SIGINT, SIGTERM, or SIGHUP signals

  Context can be provided in multiple ways:
    - Single file: --context file.py
    - Multiple files: --context "*.py"
    - Directories: --context src/
    - Multiple patterns: --context "src/**/*.py" --context "docs/*.md"

Options:
  --api-key TEXT              OpenRouter API key (can also be set via
                              OPENROUTER_API_KEY env variable)
  --grok                      Use Grok model instead of Claude
  --gemini                    Use Gemini model instead of Claude
  --json                      Output raw JSON response
  --temperature FLOAT         Temperature (0-1)
  --top-p FLOAT              Top P (0-1)
  --top-k INTEGER            Top K
  --frequency-penalty FLOAT   Frequency penalty (0-2)
  --presence-penalty FLOAT    Presence penalty (0-2)
  --repetition-penalty FLOAT  Repetition penalty
  --min-p FLOAT              Min P (0-1)
  --top-a FLOAT              Top A
  --help                      Show this message and exit.

Note: --grok and --gemini flags cannot be used simultaneously.

Commands:
  explain     Explain how the code works with detailed examples.
  parameters  Show information about model parameters and their defaults.
  query       Send a custom query to the AI model.
  review      Review code from a file for quality, bugs, and improvements.
  templates   List available templates and their descriptions
```

##### Here are example usages for `orclient.py`, leveraging different models for various tasks:

```bash
# Set your API key first
export OPENROUTER_API_KEY='your_api_key_here'

# Code Review with Claude (Default)
python orclient.py review path/to/your/code.py
python orclient.py --temperature 0.7 review complex_algorithm.py
python orclient.py review app.py --context "src/*.py" --context "tests/*.py"

# Code Explanation with Gemini
python orclient.py --gemini explain database_connection.py
python orclient.py --gemini explain complex_class.py --context "utils/*.py"
python orclient.py --gemini --temperature 0.4 explain authentication.py

# Custom Code Queries with Different Models
python orclient.py query "How can I optimize this database query?" --code-file query.sql
python orclient.py --gemini query "Convert this function to TypeScript" --code-file function.js
python orclient.py --grok query "Suggest unit tests for this code" --code-file app.py

# Current Events/News with Grok
python orclient.py --grok query "What are the most significant tech industry developments in the past week?"
python orclient.py --grok query "Explain the current state of AI regulation globally"
python orclient.py --grok --temperature 0.9 query "What are the trending discussions in the open source community?"

# Technical Analysis with Gemini
python orclient.py --gemini query "Analyze performance implications of this code"
python orclient.py --gemini query "Suggest architectural improvements"
python orclient.py --gemini --temperature 0.8 query "Review this API design"

# Get JSON output for parsing
python orclient.py --json query "Security review" --code-file auth.py
python orclient.py --gemini --json query "Code optimization suggestions"
# For clean JSON output
python orclient.py --json review code.py | jq .content
# For different models with JSON
python orclient.py --grok --json query "Latest tech news" | jq .content
python orclient.py --gemini --json query "Code analysis" | jq .content
# List templates in JSON format
python orclient.py --json templates
# Show parameters in JSON format
python orclient.py --json parameters

# List available templates
python orclient.py templates

# Show parameter information
python orclient.py parameters

# Using multiple context files
python orclient.py review main.py --context "src/**/*.py" --context "docs/*.md"

# Complex examples with parameters
python orclient.py --temperature 0.7 --top-p 0.95 explain complex_algorithm.py
python orclient.py --gemini --temperature 0.8 --presence-penalty 0.1 query "Analyze code complexity"
python orclient.py --grok --temperature 0.9 --presence-penalty 0.1 query "Analysis of current tech startup trends"

# Using different templates
python orclient.py query "Improve this code" --template refactor --code-file app.py
python orclient.py query "Fix this bug" --template debug --code-file buggy.py --context "logs/*.txt"
```

##### Example workflow scenarios:

```bash
# Code Review Workflow with Multiple Models
# First review with Claude
python orclient.py review app.py
# Get Gemini's perspective
python orclient.py --gemini review app.py
# Get optimization suggestions from Grok
python orclient.py --grok query "How can this code be optimized?" --code-file app.py

# Tech Research Workflow
# Get overview with Gemini
python orclient.py --gemini query "What's new in software architecture?"
# Get deeper analysis with Grok
python orclient.py --grok --temperature 0.7 query "Analyze current software architecture trends"
# Get specific recommendations with Claude
python orclient.py query "Recommend architecture improvements for this codebase" --context "src/**/*.py"

# Debug Workflow
# Get error analysis from Claude
python orclient.py query "Debug this error" --template debug --code-file broken.py
# Get Gemini's perspective
python orclient.py --gemini query "Analyze this error" --code-file broken.py --context "error_logs.txt"
# Get prevention tips from Grok
python orclient.py --grok query "How to prevent similar errors?" --code-file broken.py

# Project Analysis with Different Models
# Review with Claude
python orclient.py review main.py --context "src/**/*.py"
# Get architecture suggestions from Gemini
python orclient.py --gemini query "Suggest architectural improvements" --context "src/**/*.py"
# Get testing recommendations from Grok
python orclient.py --grok query "Suggest testing strategy" --context "src/**/*.py"
```

##### Project-specific examples:

```bash
# Web Application
python orclient.py review app.py --context "routes/*.py" --context "models/*.py"
python orclient.py --gemini query "Security audit" --context "auth/*.py"

# Data Science Project
python orclient.py --gemini review data_pipeline.py --context "preprocessing/*.py"
python orclient.py query "Optimize this data processing" --code-file process.py

# API Development
python orclient.py --gemini review api.py --context "endpoints/*.py"
python orclient.py query "API documentation" --context "api/*.py"

# DevOps
python orclient.py review deployment.yaml --context "kubernetes/*.yaml"
python orclient.py --grok query "Current best practices for Kubernetes deployments"
```
