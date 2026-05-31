"""One-shot project-template initializer.

Run **once** after `degit fmonfasani/project-template <dir>` to rename the
sample package and stamp your name/description into the placeholder files:

    python scripts/init.py

What it does, in order:

  1. Prompt for the project's name / slug / description / author / email / license.
  2. Walk every text file under the repo, replacing ``{{ placeholder }}`` tokens
     with the answers.
  3. Rename ``src/sample/`` to ``src/<slug>/`` so the package import path
     matches the slug.
  4. Initialize a fresh git history (you cloned a snapshot — your new repo
     should not inherit the template's commits).
  5. Delete itself so the placeholder runner doesn't ship in your new repo.

The script has no third-party dependencies — stdlib only — so it works the
moment you have Python 3.11+ on PATH, before you've even created the venv.
"""

from __future__ import annotations

import contextlib
from pathlib import Path
import re
import shutil
import subprocess
import sys

# Files that contain ``{{ ... }}`` placeholders. Walking *everything* would
# accidentally rewrite content in binary files or someone's lock file later
# down the line; keep the rewrite set deliberate and small.
_TEXT_GLOBS = (
    "pyproject.toml",
    "README.md",
    "CHARTER.md",
    "LICENSE",
    "Makefile",
    ".env.example",
    "src/**/*.py",
    "services/**/*.py",
    "tests/**/*.py",
    "scripts/**/*.py",
    "docs/**/*.md",
    ".github/**/*.yml",
    "config/**/*.md",
    "config/**/*.yaml",
    "services/**/*.md",
    "infra/**/*.md",
    "infra/**/*.yml",
    "infra/**/*.yaml",
)

_SLUG_RE = re.compile(r"^[a-z][a-z0-9_]*$")
_REPO_ROOT = Path(__file__).resolve().parent.parent


def _ask(prompt: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    answer = input(f"{prompt}{suffix}: ").strip()
    return answer or default


def _ask_slug(prompt: str, default: str) -> str:
    while True:
        value = _ask(prompt, default)
        if _SLUG_RE.match(value):
            return value
        print(f"  ! slug must match {_SLUG_RE.pattern} (got {value!r})", file=sys.stderr)


def gather_answers() -> dict[str, str]:
    print("Project template — initialization\n")
    name = _ask("Project name (display)", "My Project")
    default_slug = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_") or "my_project"
    slug = _ask_slug("Package slug (a-z, 0-9, _)", default_slug)
    description = _ask("One-line description", f"{name} — TODO")
    author = _ask("Author name", "")
    email = _ask("Author email", "")
    license_id = _ask("License (SPDX)", "MIT")
    homepage = _ask("Homepage URL (GitHub repo)", "")
    return {
        "project_name": name,
        "project_slug": slug,
        "project_description": description,
        "project_author": author,
        "project_email": email,
        "project_license": license_id,
        "project_homepage": homepage,
    }


def _candidate_files(root: Path) -> list[Path]:
    seen: set[Path] = set()
    for pattern in _TEXT_GLOBS:
        for path in root.glob(pattern):
            if path.is_file() and path not in seen:
                seen.add(path)
    return sorted(seen)


def substitute(root: Path, answers: dict[str, str]) -> None:
    placeholder_re = re.compile(r"\{\{\s*([a-z_]+)\s*\}\}")
    for path in _candidate_files(root):
        text = path.read_text(encoding="utf-8")
        new_text = placeholder_re.sub(lambda m: answers.get(m.group(1), m.group(0)), text)
        if new_text != text:
            path.write_text(new_text, encoding="utf-8")
            print(f"  rewrote {path.relative_to(root)}")


def rename_package(root: Path, slug: str) -> None:
    old = root / "src" / "sample"
    new = root / "src" / slug
    if not old.exists():
        return  # already initialized
    if slug != "sample":
        if new.exists():
            raise SystemExit(f"refusing to overwrite {new} -- pick another slug or remove it")
        old.rename(new)
        print(f"  renamed src/sample -> src/{slug}")
        _rewrite_sample_imports(root, slug)


def _rewrite_sample_imports(root: Path, slug: str) -> None:
    """Rewrite literal ``sample`` references that survived placeholder substitution.

    The test file imports via ``from sample.core import greet`` so the template
    stays parseable Python (a ``{{ project_slug }}.core`` placeholder would be
    a syntax error before init runs). After the package is renamed, walk the
    Python files and patch the import target to match.
    """
    patterns = (
        # Handles `from sample import x`, `from sample.a import x`, and
        # `from sample.a.b.c import x` — earlier templates only caught one level.
        (re.compile(r"\bfrom sample((?:\.\w+)*) import\b"), rf"from {slug}\1 import"),
        (re.compile(r"\bimport sample\b"), f"import {slug}"),
    )
    for path in (
        *root.glob("src/**/*.py"),
        *root.glob("services/**/*.py"),
        *root.glob("tests/**/*.py"),
        *root.glob("scripts/**/*.py"),
    ):
        text = path.read_text(encoding="utf-8")
        new_text = text
        for pat, repl in patterns:
            new_text = pat.sub(repl, new_text)
        if new_text != text:
            path.write_text(new_text, encoding="utf-8")
            print(f"  rewrote imports in {path.relative_to(root)}")


def reset_git_history(root: Path) -> None:
    git_dir = root / ".git"
    if git_dir.exists():
        shutil.rmtree(git_dir)
    subprocess.run(["git", "init", "-b", "main"], cwd=root, check=True)  # noqa: S607 — git is universal on dev machines
    print("  reset git history (run `git add -A && git commit` when ready)")


def self_destruct(script: Path) -> None:
    # The script has done its job; future contributors shouldn't see it.
    script.unlink()
    # Best-effort cleanup of the (now likely empty) scripts/ dir.
    with contextlib.suppress(OSError):
        script.parent.rmdir()
    print("  removed scripts/init.py")


def main() -> int:
    answers = gather_answers()
    print("\nApplying...")
    substitute(_REPO_ROOT, answers)
    rename_package(_REPO_ROOT, answers["project_slug"])
    reset_git_history(_REPO_ROOT)
    self_destruct(Path(__file__).resolve())
    print("\nDone. Next: `make dev && make check`.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
