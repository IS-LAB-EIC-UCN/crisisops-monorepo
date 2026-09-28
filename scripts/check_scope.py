from __future__ import annotations

import subprocess
import sys
from pathlib import PurePosixPath

SCOPES = {
    "gA": (
        "src/crisisops/modules/emergencies/",
        "tests/emergencies/",
    ),
    "gB": (
        "src/crisisops/modules/resources/",
        "tests/resources/",
    ),
    "gC": (
        "src/crisisops/modules/personnel/",
        "tests/personnel/",
    ),
    "gD": (
        "src/crisisops/modules/operations/",
        "tests/operations/",
    ),
    "gE": (
        "src/crisisops/modules/evacuation/",
        "tests/evacuation/",
    ),
    "common": (
        "src/crisisops/core/",
        "src/crisisops/shared/",
        "migrations/",
        "docs/adr/",
        "docs/governance/",
        "ARCHITECTURE.md",
        "alembic.ini",
        "pyproject.toml",
        "Dockerfile",
        "docker-compose.yml",
    ),
}


def changed_files(base_sha: str, head_sha: str) -> list[str]:
    """Return files changed in the PR branch since its common ancestor with base."""
    output = subprocess.check_output(
        ["git", "diff", "--name-only", f"{base_sha}...{head_sha}"],
        text=True,
    )
    return [line.strip() for line in output.splitlines() if line.strip()]


def is_allowed(path: str, allowed: tuple[str, ...]) -> bool:
    """Check whether a changed path belongs to an allowed directory or file."""
    normalized = PurePosixPath(path).as_posix()

    for root in allowed:
        if root.endswith("/"):
            if normalized.startswith(root):
                return True
        elif normalized == root:
            return True

    return False


def main() -> int:
    if len(sys.argv) != 4:
        print("usage: check_scope.py <head-branch> <base-sha> <head-sha>")
        return 2

    branch, base_sha, head_sha = sys.argv[1:]

    # Dependabot may update dependencies outside the group scopes.
    if branch.startswith("dependabot/"):
        return 0

    # Enforce branch naming convention:
    # gA/..., gB/..., gC/..., gD/..., gE/... or common/...
    if "/" not in branch:
        print(
            f"Rama '{branch}' no cumple convención. "
            "Use gA/..., gB/..., gC/..., gD/..., gE/... o common/..."
        )
        return 1

    prefix, suffix = branch.split("/", 1)

    if not suffix.strip():
        print(
            f"Rama '{branch}' no cumple convención. "
            "Debe incluir una descripción después del prefijo, por ejemplo "
            "gA/23-register-emergency."
        )
        return 1

    allowed = SCOPES.get(prefix)
    if allowed is None:
        print(
            f"Rama '{branch}' no cumple convención. "
            "Use gA/..., gB/..., gC/..., gD/..., gE/... o common/..."
        )
        return 1

    files = changed_files(base_sha, head_sha)

    forbidden = [
        path
        for path in files
        if not is_allowed(path, allowed)
    ]

    if forbidden:
        print(f"La rama {branch} solo puede modificar:")
        for root in allowed:
            print(f"  - {root}")

        print("Archivos fuera de alcance:")
        for path in forbidden:
            print(f"  - {path}")

        return 1

    print(f"Scope válido para {branch}: {len(files)} archivo(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
