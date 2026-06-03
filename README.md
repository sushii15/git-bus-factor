# git-bus-factor

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![No Dependencies](https://img.shields.io/badge/dependencies-none-brightgreen.svg)]()

**Identify knowledge concentration risk in your git repository.**

`git-bus-factor` analyzes `git blame` across every tracked file to compute the *bus factor* — the minimum number of contributors whose loss would leave a file with no active knowledge holders. It also computes a normalized **HHI-based concentration score** (0–1) per file, so you can prioritize documentation efforts and code reviews where they matter most.

## Why This Matters

A bus factor of 1 means a single developer owns the majority of a file. If they leave, get sick, or go on vacation, that code becomes a black box. Teams use this to:
- Identify critical files that need better docs or second-owner pairing
- Guide onboarding — who should shadow whom
- Inform rotation and review policies

## Installation

```bash
git clone https://github.com/sushii15/git-bus-factor.git
cd git-bus-factor
# No dependencies — pure Python stdlib + git CLI
```

## Usage

```bash
# Analyze current repo (top 20 riskiest files)
python bus_factor.py .

# Filter to Python files only
python bus_factor.py /path/to/repo --ext .py

# Show top 50, export as JSON
python bus_factor.py . --top 50 --format json > report.json

# Adjust coverage threshold (default 0.5 = 50%)
python bus_factor.py . --threshold 0.75
```

## Example Output

```
========================================================================
  git-bus-factor — Top 20 Riskiest Files
========================================================================

BusFactor  RiskScore  Authors  TopAuthor%  File
------------------------------------------------------------------------
        1      1.000        1      100.0%  src/auth/tokens.py  [████████]
        1      0.891        2       92.0%  core/scheduler.py   [███████░]
        1      0.640        3       78.5%  api/handlers.py     [█████░░░]
        2      0.320        4       55.0%  utils/parser.py     [██░░░░░░]

Files with bus_factor=1 (critical risk): 3
  * src/auth/tokens.py (100% owned by Alice)
  * core/scheduler.py (92% owned by Bob)
  * api/handlers.py (79% owned by Alice)
```

**Columns:**
- `BusFactor` — minimum authors to cover ≥50% of lines (lower = riskier)
- `RiskScore` — normalized HHI concentration (1.0 = one person owns everything)
- `TopAuthor%` — percentage of lines by the dominant contributor
- `[████░░░░]` — visual risk bar

## How It Works

1. Runs `git ls-files` to enumerate tracked files
2. Runs `git blame --line-porcelain` per file to attribute each line to an author
3. Computes **bus factor**: greedily accumulates top authors until their combined line ownership crosses a threshold (default 50%)
4. Computes **concentration score**: normalized [Herfindahl-Hirschman Index](https://en.wikipedia.org/wiki/Herfindahl%E2%80%93Hirschman_index) — a classic market-concentration metric repurposed for code ownership

## Running Tests

```bash
python test_bus_factor.py
# 8/8 tests passed
```

## Contributing

Contributions welcome! Ideas:
- `--since` flag to weight recent commits more heavily
- Team aliases (merge multiple git identities)
- HTML report output
- GitHub Actions integration

Please open an issue before submitting large PRs.

## License

MIT © 2026 sushii15
