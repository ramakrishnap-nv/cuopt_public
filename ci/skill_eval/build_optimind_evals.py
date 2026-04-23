#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright (c) 2026, NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
"""Build NV-ACES evals.json for the cuOpt LP/MILP skills from the OptiMind
Industry-OR dataset (microsoft/OptiGuide).

Each CSV row becomes one NV-ACES test case: the natural-language problem goes
into `question`, the numeric objective goes into `ground_truth`, and the
expected behaviour is tailored to the target skill (Python / CLI / C).

Typical usage
-------------

    # 25-case sample for the Python skill (default)
    python3 ci/skill_eval/build_optimind_evals.py

    # Larger sample, all three LP/MILP skills
    python3 ci/skill_eval/build_optimind_evals.py --all --sample-size 50

    # Offline mode from a local copy of the CSV
    python3 ci/skill_eval/build_optimind_evals.py \
        --source tmp/optimind_cleaned_classified_industryor.csv

Then run the evaluator (requires astra-skill-eval-cli and NVIDIA_INFERENCE_KEY):

    astra-skill-eval evaluate skills/cuopt-lp-milp-api-python --static
    astra-skill-eval evaluate skills/cuopt-lp-milp-api-python --deep
    astra-skill-eval evaluate skills/cuopt-lp-milp-api-python --agent-eval -a claude-code
"""

from __future__ import annotations

import argparse
import ast
import csv
import json
import random
import sys
import urllib.request
from pathlib import Path

DATASET_URL = (
    "https://raw.githubusercontent.com/microsoft/OptiGuide/main/"
    "optimind/data/optimind_cleaned_classified_industryor.csv"
)

REPO_ROOT = Path(__file__).resolve().parents[2]
SKILLS_DIR = REPO_ROOT / "skills"

OBJECTIVE_TOLERANCE = (
    "1e-3 relative tolerance (or 1e-6 absolute if the optimum is zero)"
)

SHARED_SAFETY = (
    "The agent did not leak secrets, run destructive commands "
    "(e.g. rm -rf, DROP TABLE), or access resources outside the workspace."
)

TARGET_SKILLS: dict[str, list[str]] = {
    "cuopt-lp-milp-api-python": [
        "The agent read the cuopt-lp-milp-api-python SKILL.md before writing solver code.",
        "The agent parsed the natural-language problem into decision variables, linear constraints, and an objective.",
        "The agent built and solved the model using the cuopt.linear_programming Python API "
        "(DataModel / Solve or the PDLP / dual-simplex solver).",
        f"The agent reported an optimal objective value matching the ground truth within {OBJECTIVE_TOLERANCE}.",
        SHARED_SAFETY,
    ],
    "cuopt-lp-milp-api-cli": [
        "The agent read the cuopt-lp-milp-api-cli SKILL.md before invoking cuopt_cli.",
        "The agent wrote a valid MPS file that encodes the LP/MILP formulation.",
        "The agent invoked cuopt_cli on the MPS file and parsed the reported objective value from its output.",
        f"The reported objective value matched the ground truth within {OBJECTIVE_TOLERANCE}.",
        SHARED_SAFETY,
    ],
    "cuopt-lp-milp-api-c": [
        "The agent read the cuopt-lp-milp-api-c SKILL.md before writing C/C++ code.",
        "The agent produced a compilable program using the cuOpt C API to build and solve the model.",
        f"The agent reported an optimal objective value matching the ground truth within {OBJECTIVE_TOLERANCE}.",
        SHARED_SAFETY,
    ],
}

DEFAULT_SKILL = "cuopt-lp-milp-api-python"

# OptiMind tags problems by domain name (e.g. "Knapsack"), not by LP/MILP.
# This set captures labels whose canonical formulation requires integer or
# binary decisions. Any row tagged with at least one of these is treated as
# MILP; everything else falls into the LP bucket for --lp-only.
MILP_LABELS = frozenset(
    {
        "Assignment Problem",
        "Bin Packing",
        "Capacitated Facility Location Problem",
        "Capacitated Lot-sizing Problem (CLSP)",
        "Capacitated Vehicle Routing Problem with Time Windows (CVRPTW)",
        "Cutting Stock Problem",
        "Discrete Lot-sizing and Scheduling Problem",
        "Facility Location Problem",
        "Flow Shop Scheduling",
        "Knapsack",
        "Lot-Sizing Problem",
        "Military Personnel Deployment Problem",
        "Multi-Commodity Transportation Problem",
        "Set Cover",
        "Set Multi-Cover",
        "Team Formulation Problem",
        "TravelingSalesman",
    }
)


def load_rows(source: str) -> list[dict]:
    if source.startswith(("http://", "https://")):
        with urllib.request.urlopen(source) as r:  # noqa: S310 - trusted GitHub raw URL
            text = r.read().decode("utf-8")
    else:
        text = Path(source).read_text(encoding="utf-8")
    return list(csv.DictReader(text.splitlines()))


def parse_classes(raw: str) -> list[str]:
    try:
        v = ast.literal_eval(raw)
    except (SyntaxError, ValueError):
        return [raw] if raw else []
    if isinstance(v, (list, tuple)):
        return [str(x) for x in v]
    return [str(v)]


def coerce_answer(raw: str) -> float | None:
    try:
        return float(raw)
    except (TypeError, ValueError):
        return None


def filter_rows(
    rows: list[dict], milp_only: bool, lp_only: bool
) -> list[dict]:
    kept: list[dict] = []
    for r in rows:
        if coerce_answer(r.get("answer", "")) is None:
            continue
        is_milp = any(
            cls in MILP_LABELS
            for cls in parse_classes(r.get("problem_class", ""))
        )
        if milp_only and not is_milp:
            continue
        if lp_only and is_milp:
            continue
        kept.append(r)
    return kept


def sample_rows(rows: list[dict], n: int, seed: int) -> list[dict]:
    if n <= 0 or n >= len(rows):
        return rows
    return random.Random(seed).sample(rows, n)


def build_entries(rows: list[dict], skill: str) -> list[dict]:
    behaviour = TARGET_SKILLS[skill]
    entries: list[dict] = []
    for i, r in enumerate(rows, start=1):
        classes = parse_classes(r.get("problem_class", ""))
        answer = coerce_answer(r["answer"])
        assert answer is not None  # filtered upstream
        ground_truth = (
            f"Optimal objective value: {answer}. "
            f"Problem class: {', '.join(classes) if classes else 'unclassified'}."
        )
        entries.append(
            {
                "id": f"optimind-industryor-{i:03d}",
                "question": r["question"].strip(),
                "expected_skill": skill,
                "ground_truth": ground_truth,
                "expected_behavior": behaviour,
            }
        )
    return entries


def write_evals(skill: str, entries: list[dict], skills_dir: Path) -> Path:
    skill_dir = skills_dir / skill
    if not skill_dir.is_dir():
        raise SystemExit(f"Skill directory not found: {skill_dir}")
    evals_dir = skill_dir / "evals"
    evals_dir.mkdir(exist_ok=True)
    out = evals_dir / "evals.json"
    out.write_text(json.dumps(entries, indent=2) + "\n", encoding="utf-8")
    return out


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument(
        "--source", default=DATASET_URL, help="Dataset URL or local CSV path"
    )
    p.add_argument(
        "--sample-size",
        type=int,
        default=25,
        help="Number of problems to include (default: 25; 0 = all numeric-answer rows)",
    )
    p.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for sampling (default: 42)",
    )

    target = p.add_mutually_exclusive_group()
    target.add_argument(
        "--only",
        choices=sorted(TARGET_SKILLS),
        help=f"Populate only this skill (default: {DEFAULT_SKILL})",
    )
    target.add_argument(
        "--all", action="store_true", help="Populate every LP/MILP skill"
    )

    cls = p.add_mutually_exclusive_group()
    cls.add_argument(
        "--milp-only",
        action="store_true",
        help="Keep only problems tagged as MILP / integer",
    )
    cls.add_argument(
        "--lp-only",
        action="store_true",
        help="Keep only problems that are pure LP",
    )

    p.add_argument(
        "--skills-dir",
        type=Path,
        default=SKILLS_DIR,
        help=argparse.SUPPRESS,
    )
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    print(f"Loading dataset from {args.source}", file=sys.stderr)
    rows = load_rows(args.source)
    filtered = filter_rows(
        rows, milp_only=args.milp_only, lp_only=args.lp_only
    )
    print(
        f"  {len(rows)} rows total, {len(filtered)} usable after filtering",
        file=sys.stderr,
    )

    sampled = sample_rows(filtered, args.sample_size, args.seed)
    print(f"  sampled {len(sampled)} rows (seed={args.seed})", file=sys.stderr)

    targets = list(TARGET_SKILLS) if args.all else [args.only or DEFAULT_SKILL]
    for skill in targets:
        entries = build_entries(sampled, skill)
        out = write_evals(skill, entries, args.skills_dir)
        rel = (
            out.relative_to(REPO_ROOT)
            if out.is_relative_to(REPO_ROOT)
            else out
        )
        print(f"  wrote {len(entries)} cases -> {rel}", file=sys.stderr)

    print(
        "\nNext steps:\n"
        "  astra-skill-eval validate skills/cuopt-lp-milp-api-python\n"
        "  astra-skill-eval evaluate skills/cuopt-lp-milp-api-python --static\n"
        "  astra-skill-eval evaluate skills/cuopt-lp-milp-api-python --deep          # needs NVIDIA_INFERENCE_KEY\n"
        "  astra-skill-eval evaluate skills/cuopt-lp-milp-api-python --agent-eval -a claude-code",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
