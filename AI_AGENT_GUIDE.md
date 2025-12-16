# Guide for AI Coding Agents

This guide explains how AI coding agents can use `retrieve_commits.py` to learn from previous commits and implement new features with consistent style and conventions.

## Overview

The tool retrieves and analyzes commit history to provide context about:
- Coding style and conventions used in the project
- Implementation patterns for similar features
- Common approaches to error handling, testing, and documentation
- File structure and organization patterns

## Usage Patterns for AI Agents

### 1. Before Implementing a New Feature

**Scenario**: You need to implement authentication functionality.

```bash
# Find all commits related to authentication
python3 retrieve_commits.py "authentication" --learn --format ai

# Or search commits that modified auth-related files
python3 retrieve_commits.py --related "src/auth/*" "*/auth.py" --format ai --context
```

**What you get**:
- Analysis of commit patterns and conventions
- Full diffs showing how similar features were implemented
- Guidance on coding style, naming conventions, and structure
- List of files typically involved in similar implementations

### 2. When Fixing a Bug

**Scenario**: You need to fix a bug similar to previous fixes.

```bash
# Find how previous bugs were fixed
python3 retrieve_commits.py "fix bug" --learn --format ai

# Find fixes in specific files
python3 retrieve_commits.py --file src/utils.py --format ai --context
```

**What you learn**:
- Common bug patterns and their fixes
- Error handling approaches
- Testing patterns for bug fixes
- Commit message conventions for bug fixes

### 3. Understanding Project Conventions

**Scenario**: You need to understand the overall project coding style.

```bash
# Analyze patterns in Python files
python3 retrieve_commits.py --related "*.py" --analyze --format ai

# Get comprehensive context
python3 retrieve_commits.py --related "src/*" --learn --context --format ai
```

**What you discover**:
- Naming conventions for variables, functions, and classes
- Code organization patterns
- Documentation style (docstrings, comments)
- Import organization
- Error handling strategies

### 4. Machine-Readable Output

**Scenario**: You need structured data for programmatic processing.

```bash
# Export as JSON
python3 retrieve_commits.py --related "*.py" --format json > context.json

# With analysis included
python3 retrieve_commits.py "feature" --analyze --format json > analysis.json
```

**Use cases**:
- Feed into AI model context
- Parse and extract specific patterns
- Build automated learning pipelines
- Integration with other tools

## Example Workflow

### Step 1: Gather Context

```bash
# Get context for implementing a new API endpoint
python3 retrieve_commits.py --related "src/api/*" --format ai --context > api_context.txt
```

### Step 2: Analyze the Output

The AI-optimized output includes:

```
# COMMIT CONTEXT FOR AI IMPLEMENTATION
================================================================================

## PROJECT CONVENTIONS AND PATTERNS
- Commit message style
- Common keywords and focus areas
- Active contributors

## REFERENCE IMPLEMENTATIONS
- Full diffs of related commits
- Files modified in each commit
- Implementation details

## GUIDANCE FOR AI IMPLEMENTATION
- Code style observations
- Naming conventions
- Error handling patterns
- Documentation requirements
```

### Step 3: Apply the Patterns

Use the extracted information to:
1. Match the coding style (indentation, spacing, naming)
2. Follow the same file structure patterns
3. Use similar error handling approaches
4. Match documentation and comment styles
5. Follow commit message conventions

## Output Formats

### AI Format (`--format ai`)

Optimized for AI consumption with:
- Structured markdown sections
- Clear pattern analysis
- Implementation guidance
- Code examples in diff format

### JSON Format (`--format json`)

Machine-readable with:
- Structured data fields
- Optional analysis section
- Optional diffs
- Easy to parse and process

### Human Format (default)

Traditional git log style with:
- Readable commit summaries
- Optional diffs and file lists
- Analysis summaries

## Best Practices for AI Agents

1. **Always check related commits** before implementing new features
2. **Use --context flag** to get AI-specific guidance
3. **Combine --analyze with --learn** for comprehensive understanding
4. **Use file patterns** (--related) to focus on relevant code areas
5. **Export to JSON** for structured processing
6. **Review diffs carefully** to understand implementation details
7. **Match the patterns** found in commits for consistency

## Integration Examples

### Python Integration

```python
import subprocess
import json

# Get commit context as JSON
result = subprocess.run(
    ["python3", "retrieve_commits.py", "--related", "*.py", "--format", "json"],
    capture_output=True,
    text=True
)

commits = json.loads(result.stdout)

# Extract patterns
for commit in commits["commits"]:
    print(f"Commit: {commit['message']}")
    print(f"Files: {', '.join(commit['files'])}")
```

### Command Line Pipeline

```bash
# Get context and feed to an AI model
python3 retrieve_commits.py --related "src/*" --format ai | \
    ai-model-cli --instruction "Implement similar feature" --context -
```

## Tips for Maximum Effectiveness

1. **Be Specific**: Use targeted file patterns instead of searching all files
2. **Combine Flags**: Use `--learn --context --format ai` together for best results
3. **Limit Scope**: Use `-n` to focus on recent commits if the project is large
4. **Iterate**: Start broad, then narrow down to specific areas
5. **Version Control**: Different time periods may have different conventions

## Common Use Cases

| Task | Command |
|------|---------|
| Learn auth patterns | `--related "*/auth*" --learn --format ai` |
| Fix bug style | `"bug fix" --context --format ai` |
| API implementation | `--related "src/api/*" --learn --format ai` |
| Project conventions | `--related "*.py" --analyze --format ai` |
| Export for processing | `--file app.py --format json` |
| Full context | `--related "src/*" --learn --context --format ai` |

## Conclusion

This tool enables AI coding agents to:
- Learn from project history
- Maintain consistency with existing code
- Follow established patterns and conventions
- Generate code that fits naturally into the project

Always use the retrieved context to guide your implementation and ensure your generated code matches the project's style and conventions.
