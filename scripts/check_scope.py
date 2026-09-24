from __future__ import annotations

import subprocess
import sys
from pathlib import PurePosixPath

SCOPES = {
    "gA": ("src/crisisops/modules/emergencies/", "tests/emergencies/"),
    "gB": ("src/crisisops/modules/resources/", "tests/resources/"),
    "gC": ("src/crisisops/modules/personnel/", "tests/personnel/"),
    "gD": ("src/crisisops/modules/operations/", "tests/operations/"),
    "gE": ("src/crisisops/modules/evacuation/", "tests/evacuation/"),
}


def changed_files(base_sha: str, head_sha: str) -> list[str]:
    output = subprocess.check_output(
        ["git", "diff", "--name-only", base_sha, head_sha], text=True
    )
    return [line.strip() for line in output.splitlines() if line.strip()]


def main() -> int:
    if len(sys.argv) != 4:
        print("usage: check_scope.py <head-branch> <base-sha> <head-sha>")
        return 2

    branch, base_sha, head_sha = sys.argv[1:]
    prefix = branch.split("/", 1)[0]

    # common/* se reserva para cambios transversales; CODEOWNERS debe exigir
    # revisión del Comité de Arquitectura.
    if prefix == "common":
        print("common/*: scope transversal; se delega autorización a CODEOWNERS/rulesets.")
        return 0

    if branch.startswith("dependabot/"):
        return 0

    allowed = SCOPES.get(prefix)
    if allowed is None:
        print(
            f"Rama '{branch}' no cumple convención. Use gA/, gB/, gC/, gD/, gE/ o common/."
        )
        return 1

    files = changed_files(base_sha, head_sha)
    forbidden = [
        path
        for path in files
        if not any(PurePosixPath(path).as_posix().startswith(root) for root in allowed)
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
