"""Check the installed source and dependency override inside the test image."""

import hashlib
import importlib.util
import json
from pathlib import Path

from aioshelly.common import ConnectionOptions

from homeassistant.const import __version__


def main() -> None:
    """Verify that the image contains the tested native integration."""
    provenance = json.loads(Path("/REMOTE_SHELLY_BUILD.json").read_text())
    if __version__ != provenance["core_version"]:
        raise SystemExit("Installed Core version does not match provenance")
    ConnectionOptions(remote_device_id="AABBCCDDEEFF")
    roots = {}
    for repository, module in (("core", "homeassistant"), ("aioshelly", "aioshelly")):
        spec = importlib.util.find_spec(module)
        if spec is None or spec.origin is None:
            raise SystemExit(f"Cannot locate {module}")
        roots[repository] = Path(spec.origin).parent.parent
    for fingerprint in provenance["source_fingerprints"]:
        path = roots[fingerprint["repository"]] / fingerprint["path"]
        if hashlib.sha256(path.read_bytes()).hexdigest() != fingerprint["sha256"]:
            raise SystemExit(f"Installed source differs: {fingerprint['path']}")
    translations = json.loads(
        (
            roots["core"] / "homeassistant/components/shelly/translations/en.json"
        ).read_text()
    )
    if "`{connection_url}`" not in translations["config"]["progress"]["remote_connect"]:
        raise SystemExit("The frontend progress text does not expose the pairing URL")
    run_script = Path("/etc/services.d/home-assistant/run").read_text()
    if "--skip-pip-packages aioshelly" not in run_script:
        raise SystemExit("Development library replacement protection is missing")
    print(
        "Verified Core "
        + provenance["core_commit"]
        + " and aioshelly "
        + provenance["aioshelly_commit"]
        + "; pairing URL progress translation is present"
    )


if __name__ == "__main__":
    main()
