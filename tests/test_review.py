from __future__ import annotations

from pathlib import Path

from conftest import git

from controller.review import passes, review_repository

GOOD_README = """# demo
[![CI](https://example.com/badge.svg)](x)
## Architecture
## Usage
## Evaluation results
"""


def make_repo(tmp_path: Path, files: dict[str, str], messages: list[str]) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    git(repo, "init", "-q")
    for i, message in enumerate(messages):
        if i == 0:
            for name, content in files.items():
                path = repo / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content)
        else:
            (repo / f"change{i}.txt").write_text(str(i))
        git(repo, "add", "-A")
        git(repo, "commit", "-q", "-m", message)
    return repo


COMPLETE = {
    "README.md": GOOD_README,
    "PROJECT_SPEC.md": "spec",
    "PLAN.md": "plan",
    "CHANGELOG.md": "log",
    "LICENSE": "MIT",
    ".env.example": "API_KEY=<placeholder>",
    ".gitignore": ".env",
    "pyproject.toml": "[project]",
    "Dockerfile": "FROM python:3.12-slim",
    "TODO.md": "- [ ] x",
    "tests/test_core.py": "def test_x():\n    assert True\n",
    ".github/workflows/ci.yml": "name: CI",
    "evals/results/run.json": "{}",
}


def test_complete_repository_passes(tmp_path: Path) -> None:
    repo = make_repo(tmp_path, COMPLETE, ["feat: initial implementation", "docs: add results"])
    findings = review_repository(repo)
    assert findings == []
    assert passes(findings)


def test_missing_artifacts_and_leaked_secrets_fail(tmp_path: Path) -> None:
    files = dict(COMPLETE)
    for name in ("Dockerfile", "evals/results/run.json", "tests/test_core.py"):
        del files[name]
    files[".gitignore"] = "*.pyc\n"  # .env not ignored, so it gets committed
    files[".env"] = "TOKEN=abc"
    fake_token = "ghp_" + "A" * 36
    files["src/config.py"] = f'TOKEN = "{fake_token}"\n'
    files["README.md"] = "# demo\n\nNo sections here.\n"
    repo = make_repo(tmp_path, files, ["initial", "update", "feat: real change"])
    findings = review_repository(repo)
    by_severity = {(f.severity, f.check) for f in findings}

    assert ("CRITICAL", "secrets") in by_severity
    assert ("CRITICAL", "tests") in by_severity
    assert ("MAJOR", "required-file") in by_severity
    assert ("MAJOR", "evaluation") in by_severity
    assert ("MAJOR", "readme") in by_severity
    assert ("MINOR", "commits") in by_severity
    assert not passes(findings)
    assert findings[0].severity == "CRITICAL"  # sorted by severity
    messages = " ".join(f.message for f in findings)
    assert "environment file tracked: .env" in messages
    assert fake_token not in messages  # findings never echo the secret itself


def test_quality_commands_are_executed(tmp_path: Path) -> None:
    repo = make_repo(tmp_path, COMPLETE, ["feat: initial"])
    findings = review_repository(repo, quality_commands=["true", "false", "no-such-binary-xyz"])
    quality = [f for f in findings if f.check == "quality"]
    assert len(quality) == 2
    assert any("`false` failed" in f.message for f in quality)
    assert any("could not run" in f.message for f in quality)


def test_eval_requirement_can_be_disabled(tmp_path: Path) -> None:
    files = {k: v for k, v in COMPLETE.items() if not k.startswith("evals/")}
    repo = make_repo(tmp_path, files, ["feat: initial"])
    assert passes(review_repository(repo, requires_eval=False))
    assert not passes(review_repository(repo, requires_eval=True))


def test_repository_without_commits_is_a_finding_not_a_crash(tmp_path: Path) -> None:
    repo = tmp_path / "fresh"
    repo.mkdir()
    git(repo, "init", "-q")
    findings = review_repository(repo, requires_eval=False)
    assert any(f.check == "commits" and f.severity == "MAJOR" for f in findings)
