##### This code was developed through multiple iterative refinements using Claude 3.5 Sonnet. 
##### It facilitates querying advanced language models like Claude 3.5 Sonnet and Grok via OpenRouter, which currently represent the most sophisticated large language models (LLMs) for code generation and real-time information retrieval. 
##### The implementation provides flexible options for incorporating files and directories into the prompt.
##### Install:
```bash
pip install -r requirements.txt
or
pip install click rich aiohttp orjson pyyaml keyboard
```

##### Usage:
```
Usage: orclient.py [OPTIONS] COMMAND [ARGS]...

  AI Code Assistant CLI - A command-line interface for coding-related queries
  using Claude or Grok.

  Model Parameters:

  Claude defaults (p10 - p50 - p90):   temperature: 0.0 - 0.50 - 1.0   top_p:
  0.90 - 1.0 - 1.0   frequency_penalty: 0 - 0 - 0.35   presence_penalty: 0 - 0
  - 0.35

  Grok defaults (p10 - p50 - p90):   temperature: 0.50 - 0.80 - 1.0   top_p:
  1.0 - 1.0 - 1.0   presence_penalty: 0 - 0 - 0.10

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
  --json                      Output raw JSON response
  --temperature FLOAT         Temperature (0-1)
  --top-p FLOAT               Top P (0-1)
  --top-k INTEGER             Top K
  --frequency-penalty FLOAT   Frequency penalty (0-2)
  --presence-penalty FLOAT    Presence penalty (0-2)
  --repetition-penalty FLOAT  Repetition penalty
  --min-p FLOAT               Min P (0-1)
  --top-a FLOAT               Top A
  --help                      Show this message and exit.

Commands:
  explain     Explain how the code works with detailed examples.
  parameters  Show information about model parameters and their defaults.
  query       Send a custom query to the AI model.
  review      Review code from a file for quality, bugs, and improvements.
  templates   List available templates and their descriptions
```

##### Here are example usages for `orclient.py`, leveraging Claude for code-related tasks and Grok for current events/discussions:

```bash
# Set your API key first
export OPENROUTER_API_KEY='your_api_key_here'

# Code Review with Claude
python orclient.py review path/to/your/code.py
python orclient.py --temperature 0.7 review complex_algorithm.py
python orclient.py review app.py --context "src/*.py" --context "tests/*.py"

# Code Explanation with Claude
python orclient.py explain database_connection.py
python orclient.py explain complex_class.py --context "utils/*.py"
python orclient.py --temperature 0.4 explain authentication.py

# Custom Code Queries with Claude
python orclient.py query "How can I optimize this database query?" --code-file query.sql
python orclient.py query "Convert this function to TypeScript" --code-file function.js
python orclient.py query "Suggest unit tests for this code" --code-file app.py

# Current Events/News with Grok
python orclient.py --grok query "What are the most significant tech industry developments in the past week?"
python orclient.py --grok query "Explain the current state of AI regulation globally"
python orclient.py --grok --temperature 0.9 query "What are the trending discussions in the open source community?"

# Tech Analysis with Grok
python orclient.py --grok query "Compare recent developments in LLMs"
python orclient.py --grok query "What are the emerging trends in cloud computing?"
python orclient.py --grok query "Analysis of recent cybersecurity incidents"

# Get JSON output for parsing
python orclient.py --json query "Security review" --code-file auth.py
python orclient.py --grok --json query "Latest developments in quantum computing"

# List available templates
python orclient.py templates

# Show parameter information
python orclient.py parameters

# Using multiple context files
python orclient.py review main.py --context "src/**/*.py" --context "docs/*.md"

# Complex examples with parameters
python orclient.py --temperature 0.7 --top-p 0.95 explain complex_algorithm.py
python orclient.py --grok --temperature 0.9 --presence-penalty 0.1 query "Analysis of current tech startup trends"

# Using different templates
python orclient.py query "Improve this code" --template refactor --code-file app.py
python orclient.py query "Fix this bug" --template debug --code-file buggy.py --context "logs/*.txt"
```

##### Example workflow scenarios:

```bash
# Code Review Workflow
# First review the code
python orclient.py review app.py
# Then get detailed explanation of complex parts
python orclient.py explain app.py
# Finally get optimization suggestions
python orclient.py query "How can this code be optimized?" --code-file app.py

# Tech Research Workflow with Grok
# Get overview of a topic
python orclient.py --grok query "What's happening with AI regulation?"
# Get deeper analysis
python orclient.py --grok --temperature 0.7 query "Analyze the implications of recent AI regulation for developers"
# Get specific recommendations
python orclient.py --grok query "What should developers consider regarding AI compliance?"

# Debug Workflow
# Get error analysis
python orclient.py query "Debug this error" --template debug --code-file broken.py
# Get fix suggestions
python orclient.py query "How to fix this error?" --code-file broken.py --context "error_logs.txt"
# Get prevention tips
python orclient.py query "How to prevent similar errors?" --code-file broken.py

# Project Analysis
# Review entire project
python orclient.py review main.py --context "src/**/*.py"
# Get architecture suggestions
python orclient.py query "Suggest architectural improvements" --context "src/**/*.py"
# Get testing recommendations
python orclient.py query "Suggest testing strategy" --context "src/**/*.py"
```

##### Project-specific examples:

```bash
# Web Application
python orclient.py review app.py --context "routes/*.py" --context "models/*.py"
python orclient.py query "Security audit" --context "auth/*.py"

# Data Science Project
python orclient.py review data_pipeline.py --context "preprocessing/*.py"
python orclient.py query "Optimize this data processing" --code-file process.py

# API Development
python orclient.py review api.py --context "endpoints/*.py"
python orclient.py query "API documentation" --context "api/*.py"

# DevOps
python orclient.py review deployment.yaml --context "kubernetes/*.yaml"
python orclient.py --grok query "Current best practices for Kubernetes deployments"
```

##### To further enhance this codebase, we recommend leveraging Claude 3.5 Sonnet's capabilities by incorporating the following contextual details:
```
<CleanCode>
Don't Repeat Yourself (DRY)
Duplication of code can make code very difficult to maintain. Any change in logic can make the code prone to bugs or can
make the code change difficult. This can be fixed by doing code reuse (DRY Principle).

The DRY principle is stated as "Every piece of knowledge must have a single, unambiguous, authoritative representation
within a system".

The way to achieve DRY is by creating functions and classes to make sure that any logic should be written in only one
place.

Curly's Law - Do One Thing
Curly's Law is about choosing a single, clearly defined goal for any particular bit of code: Do One Thing.

Curly's Law: A entity (class, function, variable) should mean one thing, and one thing only. It should not mean one
thing in one circumstance and carry a different value from a different domain some other time. It should not mean two
things at once. It should mean One Thing and should mean it all of the time.

Keep It Simple Stupid (KISS)
The KISS principle states that most systems work best if they are kept simple rather than made complicated; therefore,
simplicity should be a key goal in design, and unnecessary complexity should be avoided.

Simple code has the following benefits:

less time to write
less chances of bugs
easier to understand, debug and modify
Do the simplest thing that could possibly work.

Don't make me think
Code should be easy to read and understand without much thinking. If it isn't then there is a prospect of
simplification.

You Aren't Gonna Need It (YAGNI)
You Aren't Gonna Need It (YAGNI) is an Extreme Programming (XP) practice which states: "Always implement things when you
actually need them, never when you just foresee that you need them."

Even if you're totally, totally, totally sure that you'll need a feature, later on, don't implement it now. Usually,
it'll turn out either:

you don't need it after all, or
what you actually need is quite different from what you foresaw needing earlier.
This doesn't mean you should avoid building flexibility into your code. It means you shouldn't overengineer something
based on what you think you might need later on.

There are two main reasons to practice YAGNI:

You save time because you avoid writing code that you turn out not to need.
Your code is better because you avoid polluting it with 'guesses' that turn out to be more or less wrong but stick
around anyway.
Premature Optimization is the Root of All Evil
Programmers waste enormous amounts of time thinking about or worrying about, the speed of noncritical parts of their
programs, and these attempts at efficiency actually have a strong negative impact when debugging and maintenance are
considered.

We should forget about small efficiencies, say about 97% of the time: premature optimization is the root of all evil.
Yet we should not pass up our opportunities in that critical 3%.

- Donald Knuth

Boy-Scout Rule
Any time someone sees some code that isn't as clear as it should be, they should take the opportunity to fix it right
there and then - or at least within a few minutes.

This opportunistic refactoring is referred to by Uncle Bob as following the boy-scout rule - always leave the code
behind in a better state than you found it.

The code quality tends to degrade with each change. This results in technical debt. The Boy-Scout Principle saves us
from that.

Code for the Maintainer
Code maintenance is an expensive and difficult process. Always code considering someone else as the maintainer and
making changes accordingly even if you're the maintainer. After a while, you'll remember the code as much as a stranger.

Always code as if the person who ends up maintaining your code is a violent psychopath who knows where you live.

Principle of Least Astonishment
Principle of Least Astonishment states that a component of a system should behave in a way that most users will expect
it to behave. The behavior should not astonish or surprise users.

Code should do what the name and comments suggest. Conventions should be followed. Surprising side effects should be
avoided as much as possible.
</CleanCode>
```

