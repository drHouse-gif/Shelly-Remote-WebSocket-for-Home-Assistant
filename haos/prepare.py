"""Prepare the pinned source checkouts for the HAOS development image."""

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

import tomllib

CORE_COMMIT = "b2e5fb3eba8645cce0453829c12f02a9c4b2135f"
AIOSHELLY_COMMIT = "74751fcb876cc5fbd993721da765d40cd5b5b750"
CORE_VERSION = "2026.11.0.dev0"


def main() -> None:
    """Collect runtime requirements and record source provenance."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--core", type=Path, required=True)
    parser.add_argument("--aioshelly", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--base-image", required=True)
    parser.add_argument("--image-version", required=True)
    args = parser.parse_args()

    sources = {"core": args.core, "aioshelly": args.aioshelly}
    commits = {"core": CORE_COMMIT, "aioshelly": AIOSHELLY_COMMIT}
    for name, source in sources.items():
        actual = subprocess.check_output(
            ["git", "-C", str(source), "rev-parse", "HEAD"], text=True
        ).strip()
        if actual != commits[name]:
            raise SystemExit(f"Unexpected {name} commit: {actual}")

    core_project = tomllib.loads((args.core / "pyproject.toml").read_text())
    library_project = tomllib.loads((args.aioshelly / "pyproject.toml").read_text())
    if core_project["project"]["version"] != CORE_VERSION:
        raise SystemExit("Core version differs from the tested source")

    pending = ["default_config", "shelly", "hassio", "frontend", "cloud"]
    domains: set[str] = set()
    requirements: set[str] = set(library_project["project"]["dependencies"])
    while pending:
        domain = pending.pop()
        if domain in domains:
            continue
        domains.add(domain)
        manifest = json.loads(
            (
                args.core / "homeassistant/components" / domain / "manifest.json"
            ).read_text()
        )
        requirements.update(manifest.get("requirements", []))
        pending.extend(manifest.get("dependencies", []))
        pending.extend(manifest.get("after_dependencies", []))
    requirements = {
        requirement
        for requirement in requirements
        if not re.match(r"^aioshelly(?:[<>=!~;\s\[]|$)", requirement)
    }

    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "requirements-runtime.txt").write_text(
        "-c homeassistant/package_constraints.txt\n\n"
        + "\n".join(sorted(requirements))
        + "\n"
    )

    fingerprints = []
    for name, directory in (
        ("core", args.core / "homeassistant/components/shelly"),
        ("aioshelly", args.aioshelly / "aioshelly"),
    ):
        for path in sorted(directory.rglob("*")):
            if path.is_file() and (
                path.suffix in {".py", ".json"} or path.name == "py.typed"
            ):
                fingerprints.append(
                    {
                        "repository": name,
                        "path": str(path.relative_to(sources[name])),
                        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                    }
                )
    provenance = {
        "core_commit": CORE_COMMIT,
        "aioshelly_commit": AIOSHELLY_COMMIT,
        "core_version": CORE_VERSION,
        "image_version": args.image_version,
        "base_image": args.base_image,
        "architecture": "amd64",
        "machine": "qemux86-64",
        "development_dependency_override": "--skip-pip-packages aioshelly",
        "preinstalled_domains": sorted(domains),
        "source_fingerprints": fingerprints,
    }
    (args.output / "provenance.json").write_text(
        json.dumps(provenance, indent=2) + "\n"
    )
    print(f"Prepared {len(domains)} domains and {len(requirements)} requirements")


if __name__ == "__main__":
    main()
