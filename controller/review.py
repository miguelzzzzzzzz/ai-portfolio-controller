"""Static completion-gate review of a project repository.

This automates the mechanical part of an independent review (files, secrets,
CI, evaluation artifacts, commit hygiene, optional quality commands). The
judgement part (architecture, code quality, honesty of claims) is done by the
reviewer role using ``prompts/reviewer.md``, which records its findings with
the same severity scale.
"""

from __future__ import annotations

import re
import shlex
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

CONVENTIONAL = re.compile(
    r"^(feat|fix|docs|test|eval|perf|refactor|ci|chore|build|style|revert)(\([\w./-]+\))?!?: \S"
)
SECRET_PATTERNS = {
    "GitHub fine-grained token": re.compile(r"github_pat_[A-Za-z0-9_]{22,}"),
    "GitHub classic token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,}\b"),
    "OpenAI-style API key": re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{32,}\b"),
    "AWS access key id": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "Hugging Face token": re.compile(r"\bhf_[A-Za-z0-9]{34,}\b"),
    "Private key block": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"),
}
REQUIRED_FILES = {
    "README.md": "MAJOR",
    "PROJECT_SPEC.md": "MAJOR",
    "PLAN.md": "MAJOR",
    "CHANGELOG.md": "MAJOR",
    "LICENSE": "MAJOR",
    ".env.example": "MAJOR",
    ".gitignore": "MAJOR",
    "pyproject.toml": "MAJOR",
    "Dockerfile": "MAJOR",
    "TODO.md": "MINOR",
}
README_SECTIONS = {
    "architecture": r"^#+ .*architecture",
    "usage or quickstart": r"^#+ .*(usage|quickstart|getting started)",
    "evaluation or results": r"^#+ .*(evaluation|results|benchmark)",
}


@dataclass(frozen=True)
class Finding:
    severity: str  # CRITICAL | MAJOR | MINOR
    check: str
    message: str

    def to_dict(self) -> dict[str, Any]:
        return {**asdict(self), "resolved": False}


def _git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True, check=False
    )
    if result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout


def tracked_files(repo: Path) -> list[str]:
    return [line for line in _git(repo, "ls-files").splitlines() if line]


def check_required_files(repo: Path, files: list[str]) -> list[Finding]:
    present = set(files)
    return [
        Finding(severity, "required-file", f"missing {name}")
        for name, severity in REQUIRED_FILES.items()
        if name not in present
    ]


def check_secrets(repo: Path, files: list[str]) -> list[Finding]:
    findings: list[Finding] = []
    for name in files:
        if Path(name).name == ".env" or (
            Path(name).name.startswith(".env.") and name != ".env.example"
        ):
            findings.append(Finding("CRITICAL", "secrets", f"environment file tracked: {name}"))
        path = repo / name
        if not path.is_file() or path.stat().st_size > 2_000_000:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for label, pattern in SECRET_PATTERNS.items():
            if pattern.search(text):
                findings.append(Finding("CRITICAL", "secrets", f"{label} pattern in {name}"))
    return findings


def check_tests_and_ci(files: list[str]) -> list[Finding]:
    findings: list[Finding] = []
    test_files = [f for f in files if re.search(r"(^|/)test_[^/]+\.py$|_test\.py$", f)]
    if not test_files:
        findings.append(Finding("CRITICAL", "tests", "no test files (test_*.py) found"))
    workflows = [f for f in files if f.startswith(".github/workflows/") and f.endswith(".yml")]
    if not workflows:
        findings.append(Finding("CRITICAL", "ci", "no GitHub Actions workflow"))
    return findings


def check_evaluation(files: list[str], requires_eval: bool) -> list[Finding]:
    if not requires_eval:
        return []
    reports = [f for f in files if f.startswith("evals/results/") and f.endswith(".json")]
    if not reports:
        return [Finding("MAJOR", "evaluation", "no committed evaluation report in evals/results/")]
    return []


def check_readme(repo: Path) -> list[Finding]:
    readme = repo / "README.md"
    if not readme.exists():
        return []
    text = readme.read_text(encoding="utf-8")
    findings = [
        Finding("MAJOR", "readme", f"README has no {label} section")
        for label, pattern in README_SECTIONS.items()
        if not re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE)
    ]
    if "badge.svg" not in text:
        findings.append(Finding("MINOR", "readme", "README has no CI status badge"))
    return findings


def check_commits(repo: Path, min_ratio: float = 0.9) -> list[Finding]:
    try:
        subjects = [s for s in _git(repo, "log", "--format=%s").splitlines() if s]
    except RuntimeError:
        subjects = []  # unborn branch: `git log` fails before the first commit
    if not subjects:
        return [Finding("MAJOR", "commits", "repository has no commits")]
    bad = [s for s in subjects if not CONVENTIONAL.match(s)]
    if len(subjects) - len(bad) < min_ratio * len(subjects):
        sample = "; ".join(bad[:3])
        return [
            Finding(
                "MINOR",
                "commits",
                f"{len(bad)}/{len(subjects)} commit subjects are not conventional: {sample}",
            )
        ]
    return []


def run_quality_commands(repo: Path, commands: list[str], timeout: int = 900) -> list[Finding]:
    findings: list[Finding] = []
    for command in commands:
        try:
            result = subprocess.run(
                shlex.split(command),
                cwd=repo,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            findings.append(Finding("MAJOR", "quality", f"`{command}` could not run: {exc}"))
            continue
        if result.returncode != 0:
            tail = (result.stdout + result.stderr).strip().splitlines()[-3:]
            findings.append(Finding("MAJOR", "quality", f"`{command}` failed: {' | '.join(tail)}"))
    return findings


def review_repository(
    repo: Path,
    *,
    requires_eval: bool = True,
    quality_commands: list[str] | None = None,
) -> list[Finding]:
    files = tracked_files(repo)
    findings = [
        *check_required_files(repo, files),
        *check_secrets(repo, files),
        *check_tests_and_ci(files),
        *check_evaluation(files, requires_eval),
        *check_readme(repo),
        *check_commits(repo),
    ]
    if quality_commands:
        findings += run_quality_commands(repo, quality_commands)
    order = {"CRITICAL": 0, "MAJOR": 1, "MINOR": 2}
    return sorted(findings, key=lambda f: (order[f.severity], f.check, f.message))


def passes(findings: list[Finding]) -> bool:
    return not any(f.severity in ("CRITICAL", "MAJOR") for f in findings)
