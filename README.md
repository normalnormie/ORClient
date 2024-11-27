##### This code was developed through multiple iterative refinements using Claude 3.5 Sonnet. 
##### It facilitates querying advanced language models like Claude 3.5 Sonnet and Grok via OpenRouter, which currently represent the most sophisticated large language models (LLMs) for code generation and real-time information retrieval. 
##### The implementation provides flexible options for incorporating files and directories into the prompt.
##### Install:
```bash
pip install -r requirements.txt
```

##### Usage:
```
Usage: orclient.py [OPTIONS] COMMAND [ARGS]...

  AI Code Assistant CLI - A command-line interface for coding-related queries
  using Claude or Grok.

  Context can be provided in multiple ways: - Single file: --context file.py -
  Multiple files: --context "*.py" - Directories: --context src/ - Multiple
  patterns: --context "src/**/*.py" --context "docs/*.md"

  Examples:     # Review code using Claude:     ai-assist review code.py

      # Review code using Grok:     ai-assist --grok review code.py

      # Explain code with multiple context files:     ai-assist explain
      main.py --context "src/**/*.py" --context "docs/"

      # Generate documentation:     ai-assist document api.py --output docs.md

      # Custom query with template:     ai-assist query "How to optimize this
      code?" --template performance --code-file slow.py

Options:
  --api-key TEXT  OpenRouter API key (can also be set via OPENROUTER_API_KEY
                  env variable)
  --grok          Use Grok model instead of Claude
  --help          Show this message and exit.

Commands:
  document   Generate documentation for the given code.
  explain    Explain how the code works with detailed examples.
  info       Show information about supported file types and context...
  query      Send a custom query to the AI model.
  review     Review code from a file for quality, bugs, and improvements.
  templates  List available templates and their descriptions.
```

```bash
# Show help
python ai_code_assistant.py --help

# Show available templates
python ai_code_assistant.py templates

# Show supported file types and context patterns
python ai_code_assistant.py info

# Review code using Claude
python ai_code_assistant.py review your_code.py --context "src/**/*.py"

# Review code using Grok
python ai_code_assistant.py --grok review your_code.py --context "src/"

# Generate documentation
python ai_code_assistant.py document api.py --output docs.md --format markdown
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

