async def example_usage():
    client = ClaudeClient("your_api_key")

    # Load multiple contexts
    contexts = await client.load_context_files([
        "project_specs.md",
        "coding_standards.yml",
        "example_code.py"
    ])

    # Use built-in template
    response1 = await client.query_claude(
        query="",
        contexts=contexts,
        template_name="code_review",
        template_vars={"code": "your_code_here"}
    )

    # Add and use custom template
    client.add_template(
        "api_docs",
        "Generate API documentation for:\n{code}\n"
        "Format: {format}"
    )

    response2 = await client.query_claude(
        query="",
        contexts=contexts,
        template_name="api_docs",
        template_vars={
            "code": "your_api_code",
            "format": "OpenAPI 3.0"
        }
    )
