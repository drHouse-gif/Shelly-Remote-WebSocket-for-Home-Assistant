"""Verify a fresh image boot and the native remote Shelly config form."""

import json
import secrets
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

BASE_URL = "http://127.0.0.1:8123"


def request(
    path: str,
    data: dict | None = None,
    *,
    token: str | None = None,
    method: str | None = None,
    form: bool = False,
) -> object:
    """Send a local smoke request without printing credentials or responses."""
    headers = {}
    body = None
    if data is not None:
        body = (urlencode(data) if form else json.dumps(data)).encode()
        headers["Content-Type"] = (
            "application/x-www-form-urlencoded" if form else "application/json"
        )
    if token:
        headers["Authorization"] = f"Bearer {token}"
    with urlopen(
        Request(BASE_URL + path, data=body, headers=headers, method=method),
        timeout=10,
    ) as response:
        content = response.read()
        return json.loads(content) if content else None


def main() -> None:
    """Create an ephemeral smoke user, check boot, and cancel the test flow."""
    deadline = time.monotonic() + 240
    while True:
        try:
            request("/api/onboarding")
            break
        except (HTTPError, URLError, TimeoutError):
            if time.monotonic() >= deadline:
                raise SystemExit("Home Assistant onboarding did not become available")
            time.sleep(2)

    user = request(
        "/api/onboarding/users",
        {
            "client_id": BASE_URL + "/",
            "name": "Image smoke test",
            "username": "image-smoke",
            "password": secrets.token_urlsafe(32),
            "language": "en",
        },
    )
    session = request(
        "/auth/token",
        {
            "client_id": BASE_URL + "/",
            "grant_type": "authorization_code",
            "code": user["auth_code"],
        },
        form=True,
    )
    token = session["access_token"]
    while request("/api/core/state", token=token)["state"] != "RUNNING":
        if time.monotonic() >= deadline:
            raise SystemExit("Home Assistant did not reach RUNNING")
        time.sleep(2)
    config = request("/api/config", token=token)
    if config["version"] != "2026.11.0.dev0":
        raise SystemExit("Unexpected running Core version")
    flow = request(
        "/api/config/config_entries/flow", {"handler": "shelly"}, token=token
    )
    if flow["type"] != "form" or "remote_ws" not in json.dumps(flow["data_schema"]):
        raise SystemExit("Native Shelly remote connection choice is missing")
    request(
        "/api/config/config_entries/flow/" + flow["flow_id"],
        token=token,
        method="DELETE",
    )
    print("Home Assistant reached RUNNING and exposes the native remote Shelly form")


if __name__ == "__main__":
    main()
