#!/usr/bin/env python3
"""
git-bus-factor: Analyze a git repository for knowledge concentration risk.
"""

import subprocess
import sys
import os
import json
import argparse
from collections import defaultdict
from typing import Dict, List


def run_git(args: List[str], cwd: str) -> str:
    result = subprocess.run(["git"] + args, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout


def get_tracked_files(repo_path: str) -> List[str]:
    output = run_git(["ls-files"], repo_path)
    return [f.strip() for f in output.splitlines() if f.strip()]


def get_file_authors(repo_path: str, filepath: str) -> Dict[str, int]:
    """Return {author: line_count} for a file using git blame."""
    try:
        output = run_git(["blame", "--line-porcelain", "HEAD", "--", filepath], repo_path)
    except RuntimeError:
        return {}
    author_lines: Dict[str, int] = defaultdict(int)
    for line in output.splitlines():
        if line.startswith("author "):
            author = line[7:].strip()
            author_lines[author] += 1
    return dict(author_lines)


def compute_bus_factor(author_lines: Dict[str, int], threshold: float = 0.5) -> int:
    """Min authors whose removal drops coverage below threshold."""
    if not author_lines:
        return 0
    total = sum(author_lines.values())
    sorted_authors = sorted(author_lines.items(), key=lambda x: x[1], reverse=True)
    cumulative = 0
    for i, (_, lines) in enumerate(sorted_authors):
        cumulative += lines
        if cumulative / total >= threshold:
            return i + 1
    return len(sorted_authors)


def compute_concentration_score(author_lines: Dict[str, int]) -> float:
    """0-1 score via normalized HHI. 1.0 = single author owns everything."""
    if not author_lines:
        return 0.0
    total = sum(author_lines.values())
    n = len(author_lines)
    if n == 1:
        return 1.0
    shares = [v / total for v in author_lines.values()]
    hhi = sum(s ** 2 for s in shares)
    hhi_min = 1.0 / n
    if hhi_min >= 1.0:
        return 1.0
    return (hhi - hhi_min) / (1.0 - hhi_min)


def analyze_repo(repo_path: str, extensions: List[str] = None, top_n: int = 20, threshold: float = 0.5) -> List[dict]:
    repo_path = os.path.abspath(repo_path)
    files = get_tracked_files(repo_path)
    if extensions:
        files = [f for f in files if any(f.endswith(ext) for ext in extensions)]

    results = []
    total = len(files)
    for i, filepath in enumerate(files, 1):
        if total > 5:
            print(f"  Analyzing [{i}/{total}] {filepath}                ", end="\r", file=sys.stderr)
        author_lines = get_file_authors(repo_path, filepath)
        if not author_lines:
            continue
        bf = compute_bus_factor(author_lines, threshold)
        concentration = compute_concentration_score(author_lines)
        total_lines = sum(author_lines.values())
        top_author = max(author_lines, key=author_lines.get)
        top_pct = author_lines[top_author] / total_lines * 100
        results.append({
            "file": filepath,
            "bus_factor": bf,
            "concentration": round(concentration, 3),
            "total_lines": total_lines,
            "authors": len(author_lines),
            "top_author": top_author,
            "top_author_pct": round(top_pct, 1),
        })

    if total > 5:
        print(" " * 70, end="\r", file=sys.stderr)

    results.sort(key=lambda r: (r["bus_factor"], -r["concentration"]))
    return results[:top_n]


def print_table(results: List[dict]) -> None:
    if not results:
        print("No results.")
        return
    print(f"{'BusFactor':>9}  {'RiskScore':>9}  {'Authors':>7}  {'TopAuthor%':>10}  File")
    print("-" * 72)
    for r in results:
        bar = "█" * int(r["concentration"] * 8) + "░" * (8 - int(r["concentration"] * 8))
        print(f"{r['bus_factor']:>9}  {r['concentration']:>9.3f}  {r['authors']:>7}  {r['top_author_pct']:>9.1f}%  {r['file']}  [{bar}]")


def main():
    parser = argparse.ArgumentParser(description="Analyze a git repo for bus factor risk.")
    parser.add_argument("repo", nargs="?", default=".", help="Path to git repository")
    parser.add_argument("--ext", nargs="+", metavar="EXT", help="Filter by file extensions e.g. .py .js")
    parser.add_argument("--top", type=int, default=20, help="Show top N riskiest files")
    parser.add_argument("--threshold", type=float, default=0.5, help="Coverage threshold (default 0.5)")
    parser.add_argument("--format", choices=["table", "json"], default="table")
    args = parser.parse_args()

    print(f"Analyzing: {os.path.abspath(args.repo)}", file=sys.stderr)
    results = analyze_repo(args.repo, args.ext, args.top, args.threshold)

    if args.format == "json":
        print(json.dumps(results, indent=2))
    else:
        print(f"\n{'='*72}")
        print(f"  git-bus-factor — Top {args.top} Riskiest Files")
        print(f"{'='*72}\n")
        print_table(results)
        bf1 = [r for r in results if r["bus_factor"] == 1]
        print(f"\nFiles with bus_factor=1 (critical risk): {len(bf1)}")
        for r in bf1[:5]:
            print(f"  * {r['file']} ({r['top_author_pct']:.0f}% owned by {r['top_author']})")
        print()


if __name__ == "__main__":
    main()
