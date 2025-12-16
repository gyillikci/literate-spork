#!/bin/bash
# Example usage scripts for retrieve_commits.py

echo "=================================="
echo "Example 1: Basic search"
echo "=================================="
python3 retrieve_commits.py "commit"

echo ""
echo "=================================="
echo "Example 2: Search with file list"
echo "=================================="
python3 retrieve_commits.py "retrieval" --files

echo ""
echo "=================================="
echo "Example 3: Show all commits"
echo "=================================="
python3 retrieve_commits.py "" --all

echo ""
echo "=================================="
echo "Example 4: Search by author"
echo "=================================="
python3 retrieve_commits.py "copilot"

echo ""
echo "=================================="
echo "Example 5: Limited search scope"
echo "=================================="
python3 retrieve_commits.py "initial" -n 5

echo ""
echo "All examples completed!"
