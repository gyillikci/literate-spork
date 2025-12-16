#!/usr/bin/env python3
"""
Tool to retrieve commit changes from a git repository based on a search prompt.

This script searches through git commit history and retrieves commits
that match the given search query, showing the changes made in those commits.
"""

import subprocess
import sys
import argparse
import re
import json
from typing import List, Dict, Optional


class CommitRetriever:
    """Class to retrieve and filter git commits based on search criteria."""
    
    # Constants for issue/solution finding
    MIN_KEYWORD_LENGTH = 3
    FIX_KEYWORDS = ['fix', 'fixed', 'fixes', 'resolve', 'resolved', 'resolves', 
                    'close', 'closed', 'closes', 'address', 'addressed', 'addresses']
    ISSUE_PATTERN = re.compile(
        r'\b(?:fix(?:es|ed)?|close(?:s|d)?|resolve(?:s|d)?|address(?:es|ed)?|issue|bug)\b\s*[:#]?\s*(\d+)',
        re.IGNORECASE
    )
    WORD_PATTERN = re.compile(r'\b\w+\b')

    def __init__(self, repo_path: str = "."):
        """
        Initialize the CommitRetriever.
        
        Args:
            repo_path: Path to the git repository (default: current directory)
        """
        self.repo_path = repo_path

    def _run_git_command(self, args: List[str]) -> str:
        """
        Run a git command and return its output.
        
        Args:
            args: List of git command arguments
            
        Returns:
            Command output as string
            
        Raises:
            subprocess.CalledProcessError: If git command fails
        """
        cmd = ["git", "-C", self.repo_path] + args
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout

    def get_commits(self, max_count: Optional[int] = None) -> List[Dict[str, str]]:
        """
        Get all commits from the repository.
        
        Args:
            max_count: Maximum number of commits to retrieve (None for all)
            
        Returns:
            List of commit dictionaries with hash, author, date, and message
        """
        args = ["log", "--format=%H%x00%an%x00%ad%x00%s", "--date=iso"]
        if max_count:
            args.append(f"-n{max_count}")
        
        try:
            output = self._run_git_command(args)
        except subprocess.CalledProcessError as e:
            print(f"Error retrieving commits: {e}", file=sys.stderr)
            return []
        
        # Handle empty repository
        if not output or not output.strip():
            return []
        
        commits = []
        for line in output.strip().split("\n"):
            if line:
                parts = line.split("\x00", 3)
                if len(parts) == 4:
                    commits.append({
                        "hash": parts[0],
                        "author": parts[1],
                        "date": parts[2],
                        "message": parts[3]
                    })
        
        return commits

    def search_commits(self, prompt: str, max_count: Optional[int] = None) -> List[Dict[str, str]]:
        """
        Search for commits matching the given prompt.
        
        The search looks in commit messages, author names, and commit hashes.
        
        Args:
            prompt: Search query string
            max_count: Maximum number of commits to search through
            
        Returns:
            List of matching commit dictionaries
        """
        commits = self.get_commits(max_count)
        prompt_lower = prompt.lower()
        
        matching_commits = []
        for commit in commits:
            if (prompt_lower in commit["message"].lower() or
                prompt_lower in commit["author"].lower() or
                prompt_lower in commit["hash"].lower()):
                matching_commits.append(commit)
        
        return matching_commits

    def get_commit_diff(self, commit_hash: str) -> str:
        """
        Get the diff for a specific commit.
        
        Args:
            commit_hash: Git commit hash
            
        Returns:
            Commit diff as string
        """
        try:
            return self._run_git_command(["show", commit_hash])
        except subprocess.CalledProcessError as e:
            print(f"Error retrieving diff for commit {commit_hash}: {e}", file=sys.stderr)
            return ""

    def get_commit_files(self, commit_hash: str) -> List[str]:
        """
        Get the list of files changed in a commit.
        
        Args:
            commit_hash: Git commit hash
            
        Returns:
            List of file paths
        """
        try:
            output = self._run_git_command(["show", "--name-only", "--format=", commit_hash])
            # Handle empty output or commits with no files (e.g., merge commits)
            if not output or not output.strip():
                return []
            return [f for f in output.strip().split("\n") if f]
        except subprocess.CalledProcessError as e:
            print(f"Error retrieving files for commit {commit_hash}: {e}", file=sys.stderr)
            return []

    def get_commits_by_file(self, file_path: str, max_count: Optional[int] = None) -> List[Dict[str, str]]:
        """
        Get commits that modified a specific file.
        
        Args:
            file_path: Path to the file
            max_count: Maximum number of commits to retrieve
            
        Returns:
            List of commit dictionaries
        """
        args = ["log", "--format=%H%x00%an%x00%ad%x00%s", "--date=iso", "--", file_path]
        if max_count:
            args.insert(1, f"-n{max_count}")
        
        try:
            output = self._run_git_command(args)
        except subprocess.CalledProcessError as e:
            print(f"Error retrieving commits for file {file_path}: {e}", file=sys.stderr)
            return []
        
        if not output or not output.strip():
            return []
        
        commits = []
        for line in output.strip().split("\n"):
            if line:
                parts = line.split("\x00", 3)
                if len(parts) == 4:
                    commits.append({
                        "hash": parts[0],
                        "author": parts[1],
                        "date": parts[2],
                        "message": parts[3]
                    })
        
        return commits

    def get_related_commits(self, file_patterns: List[str], max_count: Optional[int] = None) -> List[Dict[str, str]]:
        """
        Get commits related to specific file patterns (e.g., for learning context).
        
        Args:
            file_patterns: List of file patterns (e.g., ["*.py", "src/auth/*"])
            max_count: Maximum number of commits to retrieve
            
        Returns:
            List of unique commit dictionaries
        """
        all_commits = {}
        
        for pattern in file_patterns:
            args = ["log", "--format=%H%x00%an%x00%ad%x00%s", "--date=iso", "--all", "--", pattern]
            if max_count:
                args.insert(1, f"-n{max_count}")
            
            try:
                output = self._run_git_command(args)
                if not output or not output.strip():
                    continue
                
                for line in output.strip().split("\n"):
                    if line:
                        parts = line.split("\x00", 3)
                        if len(parts) == 4:
                            commit_hash = parts[0]
                            if commit_hash not in all_commits:
                                all_commits[commit_hash] = {
                                    "hash": commit_hash,
                                    "author": parts[1],
                                    "date": parts[2],
                                    "message": parts[3]
                                }
            except subprocess.CalledProcessError:
                continue
        
        return list(all_commits.values())

    def analyze_commit_patterns(self, commits: List[Dict[str, str]]) -> Dict:
        """
        Analyze patterns in a list of commits to learn coding style and conventions.
        
        Args:
            commits: List of commit dictionaries
            
        Returns:
            Dictionary with pattern analysis
        """
        if not commits:
            return {}
        
        analysis = {
            "total_commits": len(commits),
            "authors": {},
            "common_keywords": {},
            "commit_types": {}
        }
        
        # Analyze authors
        for commit in commits:
            author = commit["author"]
            analysis["authors"][author] = analysis["authors"].get(author, 0) + 1
        
        # Analyze commit messages for patterns
        message_words = []
        for commit in commits:
            message = commit["message"].lower()
            
            # Detect commit type prefixes (conventional commits)
            if message.startswith("fix"):
                analysis["commit_types"]["fix"] = analysis["commit_types"].get("fix", 0) + 1
            elif message.startswith("feat"):
                analysis["commit_types"]["feat"] = analysis["commit_types"].get("feat", 0) + 1
            elif message.startswith("refactor"):
                analysis["commit_types"]["refactor"] = analysis["commit_types"].get("refactor", 0) + 1
            elif message.startswith("test"):
                analysis["commit_types"]["test"] = analysis["commit_types"].get("test", 0) + 1
            elif message.startswith("docs"):
                analysis["commit_types"]["docs"] = analysis["commit_types"].get("docs", 0) + 1
            
            # Extract keywords
            words = re.findall(r'\b\w+\b', message)
            message_words.extend(words)
        
        # Count common keywords (excluding common words)
        common_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "from"}
        for word in message_words:
            if len(word) > 3 and word not in common_words:
                analysis["common_keywords"][word] = analysis["common_keywords"].get(word, 0) + 1
        
        # Sort and limit keywords
        analysis["common_keywords"] = dict(sorted(
            analysis["common_keywords"].items(),
            key=lambda x: x[1],
            reverse=True
        )[:10])
        
        return analysis

    def get_file_history_summary(self, file_path: str) -> str:
        """
        Get a summary of changes to a specific file over time.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Summary string
        """
        commits = self.get_commits_by_file(file_path, max_count=10)
        if not commits:
            return f"No history found for {file_path}"
        
        summary = f"Recent changes to {file_path}:\n"
        summary += f"Total commits: {len(commits)}\n\n"
        
        for i, commit in enumerate(commits[:5], 1):
            summary += f"{i}. [{commit['hash'][:8]}] {commit['date'][:10]} - {commit['message'][:60]}\n"
            summary += f"   By: {commit['author']}\n"
        
        return summary

    def extract_issue_references(self, commits: List[Dict[str, str]]) -> Dict[str, List[Dict[str, str]]]:
        """
        Extract issue/bug references from commit messages and link them to commits.
        
        Recognizes patterns like:
        - fixes #123, fix #123, fixed #123
        - closes #123, close #123, closed #123
        - resolves #123, resolve #123, resolved #123
        - addresses #123, address #123, addressed #123
        - issue #123, bug #123
        
        Args:
            commits: List of commit dictionaries
            
        Returns:
            Dictionary mapping issue numbers to lists of commits that reference them
        """
        issue_to_commits = {}
        
        for commit in commits:
            message = commit["message"]
            matches = self.ISSUE_PATTERN.findall(message)
            
            for issue_num in matches:
                issue_key = f"#{issue_num}"
                if issue_key not in issue_to_commits:
                    issue_to_commits[issue_key] = []
                
                issue_to_commits[issue_key].append({
                    "hash": commit["hash"],
                    "hash_short": commit["hash"][:8],
                    "author": commit["author"],
                    "date": commit["date"],
                    "message": commit["message"]
                })
        
        return issue_to_commits

    def find_solution_for_problem(self, problem_description: str, max_count: Optional[int] = None) -> Dict:
        """
        Find commits that solved similar problems based on a problem description.
        
        This method searches for commits that:
        1. Mention fix/resolve/close keywords
        2. Have similar keywords to the problem description
        3. Show the implementation solution
        
        Args:
            problem_description: Description of the problem/bug/feature request
            max_count: Maximum number of commits to analyze
            
        Returns:
            Dictionary with matching commits and analysis
        """
        # Get all commits
        all_commits = self.get_commits(max_count)
        
        # Extract keywords from problem description
        problem_keywords = set(self.WORD_PATTERN.findall(problem_description.lower()))
        problem_keywords = {w for w in problem_keywords if len(w) > self.MIN_KEYWORD_LENGTH}
        
        # Find commits that are fixes/solutions
        solution_commits = []
        
        for commit in all_commits:
            message_lower = commit["message"].lower()
            
            # Check if it's a fix/solution commit
            is_fix = any(keyword in message_lower for keyword in self.FIX_KEYWORDS)
            
            if is_fix:
                # Calculate relevance based on keyword overlap
                commit_words = set(self.WORD_PATTERN.findall(message_lower))
                overlap = problem_keywords.intersection(commit_words)
                
                if overlap:
                    solution_commits.append({
                        "commit": commit,
                        "relevance_score": len(overlap),
                        "matching_keywords": list(overlap)
                    })
        
        # Sort by relevance
        solution_commits.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        return {
            "problem_description": problem_description,
            "total_solutions_found": len(solution_commits),
            "solutions": solution_commits
        }


def print_commit_summary(commit: Dict[str, str], show_index: bool = True, index: int = 0):
    """Print a formatted summary of a commit."""
    prefix = f"{index}. " if show_index else ""
    print(f"{prefix}Commit: {commit['hash'][:8]}")
    print(f"   Author: {commit['author']}")
    print(f"   Date: {commit['date']}")
    print(f"   Message: {commit['message']}")
    print()


def format_for_ai(commits: List[Dict[str, str]], retriever: 'CommitRetriever', include_diffs: bool = True, 
                  include_analysis: bool = True) -> str:
    """
    Format commit information optimized for AI coding agents.
    
    Args:
        commits: List of commit dictionaries
        retriever: CommitRetriever instance
        include_diffs: Whether to include diffs
        include_analysis: Whether to include pattern analysis
        
    Returns:
        Formatted string optimized for AI consumption
    """
    output = []
    output.append("# COMMIT CONTEXT FOR AI IMPLEMENTATION")
    output.append("=" * 80)
    output.append("")
    
    if include_analysis and commits:
        analysis = retriever.analyze_commit_patterns(commits)
        output.append("## PROJECT CONVENTIONS AND PATTERNS")
        output.append("")
        
        if analysis.get('commit_types'):
            output.append("### Commit Message Style:")
            for ctype, count in sorted(analysis['commit_types'].items(), key=lambda x: x[1], reverse=True):
                output.append(f"  - Use '{ctype}:' prefix ({count} examples found)")
        
        if analysis.get('common_keywords'):
            output.append("\n### Common Implementation Keywords:")
            keywords = list(analysis['common_keywords'].keys())[:5]
            output.append(f"  - Focus areas: {', '.join(keywords)}")
        
        output.append("\n### Active Contributors:")
        if analysis.get('authors'):
            for author, count in sorted(analysis['authors'].items(), key=lambda x: x[1], reverse=True)[:3]:
                output.append(f"  - {author} ({count} commits)")
        
        output.append("")
        output.append("-" * 80)
        output.append("")
    
    output.append("## REFERENCE IMPLEMENTATIONS")
    output.append("")
    output.append(f"Total commits analyzed: {len(commits)}")
    output.append("")
    
    for i, commit in enumerate(commits, 1):
        output.append(f"### Commit {i}: {commit['message']}")
        output.append(f"**Hash**: {commit['hash'][:8]}  |  **Author**: {commit['author']}  |  **Date**: {commit['date'][:10]}")
        output.append("")
        
        files = retriever.get_commit_files(commit['hash'])
        if files:
            output.append("**Files Modified:**")
            for file in files:
                output.append(f"  - `{file}`")
            output.append("")
        
        if include_diffs:
            diff = retriever.get_commit_diff(commit['hash'])
            output.append("**Implementation Details:**")
            output.append("```diff")
            output.append(diff.strip())
            output.append("```")
            output.append("")
        
        output.append("-" * 80)
        output.append("")
    
    output.append("## GUIDANCE FOR AI IMPLEMENTATION")
    output.append("")
    output.append("When implementing new features or fixes, follow these patterns from the commits above:")
    output.append("")
    output.append("1. **Code Style**: Observe naming conventions, indentation, and code organization")
    output.append("2. **Commit Messages**: Follow the commit message format shown above")
    output.append("3. **File Structure**: Maintain the file organization patterns")
    output.append("4. **Error Handling**: Use similar error handling approaches")
    output.append("5. **Documentation**: Match the documentation style in code and docstrings")
    output.append("6. **Testing**: Follow the testing patterns if present")
    output.append("")
    output.append("=" * 80)
    
    return "\n".join(output)


def format_as_json(commits: List[Dict[str, str]], retriever: 'CommitRetriever', include_diffs: bool = False,
                   include_analysis: bool = False) -> str:
    """
    Format commit information as JSON for machine processing.
    
    Args:
        commits: List of commit dictionaries
        retriever: CommitRetriever instance
        include_diffs: Whether to include diffs
        include_analysis: Whether to include pattern analysis
        
    Returns:
        JSON formatted string
    """
    output = {
        "total_commits": len(commits),
        "commits": []
    }
    
    if include_analysis and commits:
        output["analysis"] = retriever.analyze_commit_patterns(commits)
    
    for commit in commits:
        commit_data = {
            "hash": commit["hash"],
            "hash_short": commit["hash"][:8],
            "author": commit["author"],
            "date": commit["date"],
            "message": commit["message"],
            "files": retriever.get_commit_files(commit["hash"])
        }
        
        if include_diffs:
            commit_data["diff"] = retriever.get_commit_diff(commit["hash"])
        
        output["commits"].append(commit_data)
    
    return json.dumps(output, indent=2)


def main():
    """Main function to handle command-line interface."""
    parser = argparse.ArgumentParser(
        description="Retrieve commit changes from git repository based on a search prompt",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "fix bug"                      # Search for commits containing "fix bug"
  %(prog)s "feature" --diff               # Search and show full diffs
  %(prog)s "john" -n 50                   # Search last 50 commits for "john"
  %(prog)s "initial" --files              # Show files changed in matching commits
  %(prog)s --file src/auth.py             # Find commits that modified a specific file
  %(prog)s --related "*.py" "tests/*"     # Find commits related to Python files and tests
  %(prog)s "authentication" --learn       # Learning mode: show context for implementing auth features
  %(prog)s --related "src/api/*" --analyze # Analyze patterns in API-related commits
  %(prog)s --related "*.py" --format ai   # AI-optimized format for coding agents
  %(prog)s "bug fix" --context --format ai # Get AI guidance with implementation context
  %(prog)s --file app.py --format json    # Machine-readable JSON output
  %(prog)s "fix" --link-issues            # Link commits to issues/bugs they fixed
  %(prog)s --find-solution "auth timeout" # Find commits that solved similar problems
        """
    )
    
    parser.add_argument(
        "prompt",
        nargs="?",
        default="",
        help="Search query to filter commits (searches in message, author, and hash). Not required with --all flag."
    )
    
    parser.add_argument(
        "-r", "--repo",
        default=".",
        help="Path to git repository (default: current directory)"
    )
    
    parser.add_argument(
        "-n", "--max-count",
        type=int,
        help="Maximum number of commits to search through"
    )
    
    parser.add_argument(
        "-d", "--diff",
        action="store_true",
        help="Show full diff for matching commits"
    )
    
    parser.add_argument(
        "-f", "--files",
        action="store_true",
        help="Show files changed in matching commits"
    )
    
    parser.add_argument(
        "--all",
        action="store_true",
        help="Show all commits without filtering (ignores prompt)"
    )
    
    parser.add_argument(
        "--file",
        help="Search commits that modified a specific file"
    )
    
    parser.add_argument(
        "--related",
        nargs="+",
        help="Find commits related to file patterns (e.g., '*.py' 'src/auth/*') for learning context"
    )
    
    parser.add_argument(
        "--analyze",
        action="store_true",
        help="Analyze commit patterns to learn coding style and conventions"
    )
    
    parser.add_argument(
        "--learn",
        action="store_true",
        help="Learning mode: show detailed context from related commits for implementing similar features"
    )
    
    parser.add_argument(
        "--format",
        choices=["human", "ai", "json"],
        default="human",
        help="Output format: 'human' (default), 'ai' (optimized for AI agents), or 'json' (machine-readable)"
    )
    
    parser.add_argument(
        "--context",
        action="store_true",
        help="Include contextual guidance for AI coding agents based on commit patterns"
    )
    
    parser.add_argument(
        "--link-issues",
        action="store_true",
        help="Link commits to issues/bugs they fixed (extracts issue references from commit messages)"
    )
    
    parser.add_argument(
        "--find-solution",
        metavar="PROBLEM",
        help="Find commits that solved similar problems (provide problem description)"
    )
    
    args = parser.parse_args()
    
    # Initialize retriever
    retriever = CommitRetriever(args.repo)
    
    # Handle find-solution mode
    if args.find_solution:
        solution_results = retriever.find_solution_for_problem(args.find_solution, args.max_count)
        print(f"Problem: {solution_results['problem_description']}")
        print(f"Found {solution_results['total_solutions_found']} potential solutions:\n")
        
        for i, solution in enumerate(solution_results['solutions'][:10], 1):
            commit = solution['commit']
            print(f"{i}. Commit: {commit['hash'][:8]}")
            print(f"   Author: {commit['author']}")
            print(f"   Date: {commit['date']}")
            print(f"   Message: {commit['message']}")
            print(f"   Relevance: {solution['relevance_score']} matching keywords: {', '.join(solution['matching_keywords'])}")
            print()
        
        return 0
    
    # Handle file-specific search
    if args.file:
        commits = retriever.get_commits_by_file(args.file, args.max_count)
        print(f"Found {len(commits)} commits that modified '{args.file}':\n")
    # Handle related commits search
    elif args.related:
        commits = retriever.get_related_commits(args.related, args.max_count)
        print(f"Found {len(commits)} commits related to patterns: {', '.join(args.related)}\n")
    # Get matching commits
    elif args.all:
        commits = retriever.get_commits(args.max_count)
        print(f"Retrieved {len(commits)} commits:\n")
    else:
        if not args.prompt:
            print("Error: prompt is required when no exclusive flags are used (--all, --file, --related, --find-solution).", file=sys.stderr)
            return 1
        commits = retriever.search_commits(args.prompt, args.max_count)
        print(f"Found {len(commits)} commits matching '{args.prompt}':\n")
    
    if not commits:
        print("No matching commits found.")
        return 0
    
    # Handle issue linking if requested
    if args.link_issues:
        issue_links = retriever.extract_issue_references(commits)
        if issue_links:
            print("=" * 80)
            print("ISSUE/BUG TO COMMIT MAPPING")
            print("=" * 80)
            print(f"\nFound {len(issue_links)} issues/bugs referenced in commits:\n")
            
            for issue, linked_commits in sorted(issue_links.items()):
                print(f"{issue}:")
                for commit in linked_commits:
                    print(f"  - [{commit['hash_short']}] {commit['message'][:70]}")
                    print(f"    By {commit['author']} on {commit['date'][:10]}")
                print()
            
            print("=" * 80)
            print()
    
    # Handle different output formats
    if args.format == "json":
        # JSON output for machine processing
        include_diffs = args.diff or args.learn
        include_analysis = args.analyze or args.context
        output = format_as_json(commits, retriever, include_diffs, include_analysis)
        print(output)
        return 0
    
    elif args.format == "ai":
        # AI-optimized format with structured guidance
        include_diffs = args.diff or args.learn or args.context
        include_analysis = args.analyze or args.context or args.learn
        output = format_for_ai(commits, retriever, include_diffs, include_analysis)
        print(output)
        return 0
    
    # Default human-readable format
    # Analyze patterns if requested
    if args.analyze:
        analysis = retriever.analyze_commit_patterns(commits)
        print("=" * 80)
        print("COMMIT PATTERN ANALYSIS")
        print("=" * 80)
        print(f"\nTotal commits analyzed: {analysis.get('total_commits', 0)}")
        
        if analysis.get('authors'):
            print("\nTop contributors:")
            for author, count in sorted(analysis['authors'].items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"  - {author}: {count} commits")
        
        if analysis.get('commit_types'):
            print("\nCommit types (conventional commits):")
            for ctype, count in sorted(analysis['commit_types'].items(), key=lambda x: x[1], reverse=True):
                print(f"  - {ctype}: {count} commits")
        
        if analysis.get('common_keywords'):
            print("\nCommon keywords in commit messages:")
            for keyword, count in list(analysis['common_keywords'].items())[:10]:
                print(f"  - {keyword}: {count} occurrences")
        
        print("\n" + "=" * 80)
        print()
    
    # Display commits
    for i, commit in enumerate(commits, 1):
        print_commit_summary(commit, show_index=True, index=i)
        
        if args.files or args.learn:
            files = retriever.get_commit_files(commit["hash"])
            if files:
                print("   Files changed:")
                for file in files:
                    print(f"     - {file}")
                print()
        
        if args.diff or args.learn:
            print("   Diff:")
            print("-" * 80)
            diff = retriever.get_commit_diff(commit["hash"])
            print(diff)
            print("-" * 80)
            print()
    
    # Learning mode summary or context guidance
    if args.learn or args.context:
        print("\n" + "=" * 80)
        print("GUIDANCE FOR AI CODING AGENTS" if args.context else "LEARNING SUMMARY")
        print("=" * 80)
        print("\nUse these commits as reference for:")
        print("  • Understanding the project's coding style and conventions")
        print("  • Identifying common patterns in similar implementations")
        print("  • Learning how previous bugs were fixed or features were added")
        print("  • Maintaining consistency with existing code")
        print("\nWhen implementing new features, pay attention to:")
        print("  • Code structure and organization patterns")
        print("  • Naming conventions for variables, functions, and classes")
        print("  • Comment style and documentation patterns")
        print("  • Testing approaches and patterns")
        print("  • Error handling strategies")
        print("  • Import organization and dependencies")
        if args.context:
            print("\nFor AI implementation:")
            print("  • Extract coding patterns from the diffs above")
            print("  • Follow the same file structure and naming conventions")
            print("  • Maintain consistent code style (indentation, spacing, etc.)")
            print("  • Use similar error handling and validation approaches")
            print("  • Match the documentation and comment style")
        print("=" * 80)
        print()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
