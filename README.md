# literate-spork

A tool to retrieve commit changes from a git repository based on a search prompt.

## Features

- Search through git commit history using keywords
- Filter commits by message, author, or commit hash
- Display commit summaries with author and date information
- Show full diffs for matching commits
- List files changed in commits
- Support for limiting search to recent commits

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

## Examples

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

## Command-line Options

```
usage: retrieve_commits.py [-h] [-r REPO] [-n MAX_COUNT] [-d] [-f] [--all] prompt

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
```

## How It Works

The tool performs the following steps:

1. **Retrieves Commits**: Uses `git log` to get commit history from the repository
2. **Filters Results**: Searches commit messages, author names, and hashes for the given prompt (case-insensitive)
3. **Displays Information**: Shows matching commits with their metadata
4. **Optional Details**: Can show full diffs or file lists for each matching commit

## Use Cases

- **Code Archaeology**: Find when specific features were added or bugs were fixed
- **Author Tracking**: Identify commits by a particular developer
- **Change Review**: Review changes related to specific functionality
- **Documentation**: Generate reports of changes for release notes
- **Debugging**: Trace the history of code changes related to an issue