# literate-spork

A tool to retrieve commit changes from a git repository based on a search prompt, with learning capabilities to guide AI coding agents in understanding project coding style and conventions.

## Features

### Core Features
- Search through git commit history using keywords
- Filter commits by message, author, or commit hash
- Display commit summaries with author and date information
- Show full diffs for matching commits
- List files changed in commits
- Support for limiting search to recent commits

### AI Coding Agent Features
- **AI-Optimized Format**: Structured output specifically designed for AI coding agents
- **Learning Mode**: Retrieve related commits to understand coding style and project conventions
- **Context Guidance**: Extract implementation patterns and provide AI-specific guidance
- **File-based Search**: Find commits that modified specific files
- **Pattern Analysis**: Analyze commit patterns to learn project conventions
- **JSON Export**: Machine-readable format for programmatic processing
- **Multi-format Output**: Human, AI-optimized, or JSON formats
- **Issue/Bug Linking**: Link commits to issues/bugs they fixed (extracts references from commit messages)
- **Solution Finder**: Find commits that solved similar problems based on problem descriptions

## Installation

No external dependencies are required. The tool uses only Python standard library modules.

Requirements:
- Python 3.6 or higher
- Git installed and accessible in PATH

## Usage

### Basic Search

Search for commits containing a keyword:

```bash
python retrieve_commits.py "fix bug"
```

### Show Full Diffs

Display the complete diff for matching commits:

```bash
python retrieve_commits.py "feature" --diff
```

### Show Changed Files

List files modified in matching commits:

```bash
python retrieve_commits.py "refactor" --files
```

### Limit Search Scope

Search only the last N commits:

```bash
python retrieve_commits.py "update" -n 50
```

### Search in Specific Repository

Specify a different repository path:

```bash
python retrieve_commits.py "initial" --repo /path/to/repo
```

### Show All Commits

Display all commits without filtering:

```bash
python retrieve_commits.py "" --all
```

### Learning Mode - Find Related Commits

Retrieve commits related to specific files or patterns to learn coding style and conventions:

```bash
# Find commits that modified a specific file
python retrieve_commits.py --file src/auth.py

# Find commits related to file patterns (for learning context)
python retrieve_commits.py --related "*.py" "tests/*"

# Learning mode: show detailed context for implementing similar features
python retrieve_commits.py "authentication" --learn

# Analyze patterns in commits to understand project conventions
python retrieve_commits.py --related "src/api/*" --analyze
```

### AI Coding Agent Mode

Optimized output formats for AI coding agents to guide their implementation:

```bash
# AI-optimized format with structured guidance
python retrieve_commits.py --related "*.py" --format ai

# Get contextual guidance for AI implementation
python retrieve_commits.py "bug fix" --context --format ai

# JSON output for programmatic processing
python retrieve_commits.py --file app.py --format json

# Full context for AI: related commits + analysis + guidance
python retrieve_commits.py --related "src/auth/*" --learn --format ai
```

### Issue/Bug Linking and Solution Finding

Link commits to issues and find solutions to problems:

```bash
# Link commits to issues/bugs they fixed
python retrieve_commits.py "fix" --link-issues

# Find commits that solved similar problems
python retrieve_commits.py --find-solution "authentication timeout error"

# Combine with other features
python retrieve_commits.py --find-solution "memory leak" --diff
```

## Examples

### Basic Search Examples

1. Find commits related to bug fixes:
   ```bash
   python retrieve_commits.py "bug"
   ```

2. Search for commits by a specific author:
   ```bash
   python retrieve_commits.py "john" -n 100
   ```

3. Find commits with specific keywords and show their diffs:
   ```bash
   python retrieve_commits.py "authentication" --diff
   ```

4. List all files changed in commits mentioning "database":
   ```bash
   python retrieve_commits.py "database" --files
   ```

### Learning and Context Examples

5. Learn from commits that modified authentication code:
   ```bash
   python retrieve_commits.py --file src/auth.py --learn
   ```

6. Find related commits for implementing a new API feature:
   ```bash
   python retrieve_commits.py --related "src/api/*" --learn
   ```

7. Analyze coding patterns in all Python files:
   ```bash
   python retrieve_commits.py --related "*.py" --analyze
   ```

8. Learn implementation patterns for a specific feature:
   ```bash
   python retrieve_commits.py "user authentication" --learn --diff
   ```

### AI Coding Agent Examples

9. Get AI-optimized guidance for implementing authentication:
   ```bash
   python retrieve_commits.py --related "src/auth/*" --format ai --context
   ```

10. Export commit data as JSON for AI processing:
    ```bash
    python retrieve_commits.py "feature" --format json > commits.json
    ```

11. Guide AI agent with full context (analysis + diffs + guidance):
    ```bash
    python retrieve_commits.py --related "*.py" --learn --format ai
    ```

### Issue Linking and Solution Finding Examples

12. Link commits to the issues they fixed:
    ```bash
    python retrieve_commits.py "fix" --link-issues
    ```

13. Find how similar problems were solved:
    ```bash
    python retrieve_commits.py --find-solution "database connection timeout"
    ```

14. Find solutions with full implementation details:
    ```bash
    python retrieve_commits.py --find-solution "memory leak in cache" --diff
    ```

## Command-line Options

```
usage: retrieve_commits.py [-h] [-r REPO] [-n MAX_COUNT] [-d] [-f] [--all] 
                           [--file FILE] [--related RELATED [RELATED ...]]
                           [--analyze] [--learn] [--format {human,ai,json}]
                           [--context] [--link-issues]
                           [--find-solution PROBLEM]
                           [prompt]

Retrieve commit changes from git repository based on a search prompt

positional arguments:
  prompt                Search query to filter commits (searches in message, author, and hash)

optional arguments:
  -h, --help            show this help message and exit
  -r REPO, --repo REPO  Path to git repository (default: current directory)
  -n MAX_COUNT, --max-count MAX_COUNT
                        Maximum number of commits to search through
  -d, --diff            Show full diff for matching commits
  -f, --files           Show files changed in matching commits
  --all                 Show all commits without filtering (ignores prompt)
  --file FILE           Search commits that modified a specific file
  --related RELATED [RELATED ...]
                        Find commits related to file patterns for learning context
  --analyze             Analyze commit patterns to learn coding style and conventions
  --learn               Learning mode: show detailed context from related commits
  --format {human,ai,json}
                        Output format: 'human' (default), 'ai' (optimized for AI agents),
                        or 'json' (machine-readable)
  --context             Include contextual guidance for AI coding agents
  --link-issues         Link commits to issues/bugs they fixed (extracts issue references)
  --find-solution PROBLEM
                        Find commits that solved similar problems (provide problem description)
```

## How It Works

The tool performs the following steps:

1. **Retrieves Commits**: Uses `git log` to get commit history from the repository
2. **Filters Results**: Searches commit messages, author names, and hashes for the given prompt (case-insensitive)
3. **Displays Information**: Shows matching commits with their metadata
4. **Optional Details**: Can show full diffs or file lists for each matching commit
5. **AI Guidance**: Analyzes patterns and provides structured output for AI coding agents
6. **Context Extraction**: Identifies coding conventions, style patterns, and implementation approaches

## Use Cases

### For Developers
- **Code Archaeology**: Find when specific features were added or bugs were fixed
- **Author Tracking**: Identify commits by a particular developer
- **Change Review**: Review changes related to specific functionality
- **Documentation**: Generate reports of changes for release notes
- **Debugging**: Trace the history of code changes related to an issue
- **Onboarding**: Help new developers understand the project's development patterns

### For AI Coding Agents
- **Context Learning**: Retrieve related commits to understand how similar features were implemented
- **Style Analysis**: Analyze commit patterns to learn project coding conventions and style
- **Pattern Recognition**: Extract implementation patterns from historical commits
- **Consistency Enforcement**: Ensure AI-generated code follows existing patterns and conventions
- **Feature Planning**: Review how similar features were implemented before generating new code
- **Guided Implementation**: Use structured output to guide AI agents in maintaining code quality
- **Convention Detection**: Automatically detect and apply project-specific conventions
- **Error Pattern Learning**: Learn from bug fixes to avoid similar issues
- **Issue Tracking**: Link issues/bugs with the commits that fixed them
- **Solution Discovery**: Find how similar problems were solved in the past