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
from typing import List, Dict, Optional


class CommitRetriever:
    """Class to retrieve and filter git commits based on search criteria."""

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
        args = ["log", "--format=%H|%an|%ad|%s", "--date=iso"]
        if max_count:
            args.append(f"-n{max_count}")
        
        try:
            output = self._run_git_command(args)
        except subprocess.CalledProcessError as e:
            print(f"Error retrieving commits: {e}", file=sys.stderr)
            return []
        
        commits = []
        for line in output.strip().split("\n"):
            if line:
                parts = line.split("|", 3)
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
            return [f for f in output.strip().split("\n") if f]
        except subprocess.CalledProcessError as e:
            print(f"Error retrieving files for commit {commit_hash}: {e}", file=sys.stderr)
            return []


def print_commit_summary(commit: Dict[str, str], show_index: bool = True, index: int = 0):
    """Print a formatted summary of a commit."""
    prefix = f"{index}. " if show_index else ""
    print(f"{prefix}Commit: {commit['hash'][:8]}")
    print(f"   Author: {commit['author']}")
    print(f"   Date: {commit['date']}")
    print(f"   Message: {commit['message']}")
    print()


def main():
    """Main function to handle command-line interface."""
    parser = argparse.ArgumentParser(
        description="Retrieve commit changes from git repository based on a search prompt",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "fix bug"           # Search for commits containing "fix bug"
  %(prog)s "feature" --diff    # Search and show full diffs
  %(prog)s "john" -n 50        # Search last 50 commits for "john"
  %(prog)s "initial" --files   # Show files changed in matching commits
        """
    )
    
    parser.add_argument(
        "prompt",
        help="Search query to filter commits (searches in message, author, and hash)"
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
    
    args = parser.parse_args()
    
    # Initialize retriever
    retriever = CommitRetriever(args.repo)
    
    # Get matching commits
    if args.all:
        commits = retriever.get_commits(args.max_count)
        print(f"Retrieved {len(commits)} commits:\n")
    else:
        commits = retriever.search_commits(args.prompt, args.max_count)
        print(f"Found {len(commits)} commits matching '{args.prompt}':\n")
    
    if not commits:
        print("No matching commits found.")
        return 0
    
    # Display commits
    for i, commit in enumerate(commits, 1):
        print_commit_summary(commit, show_index=True, index=i)
        
        if args.files:
            files = retriever.get_commit_files(commit["hash"])
            if files:
                print("   Files changed:")
                for file in files:
                    print(f"     - {file}")
                print()
        
        if args.diff:
            print("   Diff:")
            print("-" * 80)
            diff = retriever.get_commit_diff(commit["hash"])
            print(diff)
            print("-" * 80)
            print()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
