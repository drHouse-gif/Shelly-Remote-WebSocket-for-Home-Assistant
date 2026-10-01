# Testing and real-device validation

## Results recorded on 2026-10-01

| Check                                             | Result                                                                                                                                                                                        |
| ------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| aioshelly full tests at `74751fcb`                | 363 passed                                                                                                                                                                                    |
| aioshelly Ruff, formatter, `ty`, pydocstyle       | Passed                                                                                                                                                                                        |
| aioshelly GitHub CI                               | [Run 36860221316](https://github.com/drHouse-gif/aioshelly/actions/runs/36860221316), success                                                                                                 |
| Core complete `tests/components/shelly` suite     | 772 passed; 558 snapshots passed at `b2e5fb3`                                                                                                                                                    |
| Core remote subset                                | 54 passed at `726a64d`; all 8 config-flow tests passed after adding the progress URL regression at `b2e5fb3` |
| Core Shelly Ruff, Mypy, Pylint                    | Passed                                                                                                                                                                                        |
| Full Hassfest for the Shelly integration          | Passed                                                                                                                                                                                        |
| Fork workflow security/YAML/format checks         | Passed                                                                                                                                                                                        |
| Core GitHub CI                                    | [Run 36889581891](https://github.com/drHouse-gif/core/actions/runs/36889581891), success; 772 tests and 558 snapshots                                                                         |
| HAOS development image build and startup smoke    | [Run 36882493791](https://github.com/drHouse-gif/Shelly-Remote-WebSocket-for-Home-Assistant/actions/runs/36882493791), success; source hashes, 149 packages, `RUNNING` and native remote form |
| Dedicated HAOS 18.3 VM image installation          | Operator terminal screenshot: update completed; `ha core info` reports the custom `qemux86-64` image and `2026.11.0.dev0`; native flow opens; revised image and physical pairing checks pending |
| Native flow on the actual HAOS VM                 | Remote choice and waiting screen load; URL display regression exposed and fixed at `b2e5fb3`; revised image validation pending |
| Physical test device identified                   | Shelly Pro 3EM, firmware 1.7.5; the displayed HTTPS origin is not a complete outbound WSS pairing URL; no connection confirmed |
| Physical Gen2/3/4 device across separate networks | Not yet performed                                                                                                                                                                             |

The native integration test uses actual `RpcDevice` and `WsServerConnection`, with a queue-backed simulated device socket. It exercises endpoint identity query, native entity loading, `Switch.Set`, status/event notifications, availability, replacement socket, unchanged registry identities, diagnostics redaction and remote Repair exemption. A second test restores a hash-only entry while offline and proves setup resumes when the device connects. Existing full-suite tests retain local, battery and local outbound-WS Repair coverage.

## Reproduce development checks

Use Python 3.14 for Core. Check out both forks at the commits shown in README, as sibling directories `core` and `aioshelly`.

For the library:

```sh
cd aioshelly
uv sync --all-groups --frozen
uv run ruff check .
uv run ruff format --check .
uv run ty check
uv run pydocstyle aioshelly
uv run pytest -q
```

For Core, start with the repository's `script/setup` on a supported development host. Then install the feature library in editable compatibility mode, preserving Core's environment:

```sh
cd core
uv pip install --python .venv/bin/python -e ../aioshelly --config-settings editable_mode=compat
uv run --no-sync python -m script.translations develop --all
uv run --no-sync pytest -q tests/components/shelly
uv run --no-sync ruff check homeassistant/components/shelly tests/components/shelly
uv run --no-sync ruff format --check homeassistant/components/shelly tests/components/shelly
uv run --no-sync mypy homeassistant/components/shelly
uv run --no-sync pylint --ignore-missing-annotations=y homeassistant/components/shelly tests/components/shelly
uv run --no-sync python -m script.hassfest --integration-path homeassistant/components/shelly
uv run --no-sync prek run --all-files
```

The fork CI workflow installs the selected integration requirements and the pinned feature library. This is a development dependency override, not an upstream manifest release. Do not run dependency synchronization afterwards if it replaces the feature library with the manifest's released version.

Workspace limitations were handled explicitly: full `script/setup` could not build an unrelated DTLS dependency without `autoconf`; relevant test dependencies were installed separately. The environment restricts AF_UNIX worker sockets and process introspection. Local Mypy ran with zero workers and its optional psutil discovery disabled, Pylint with one worker, and Hassfest with the `fork` start method. Full `prek --all-files` was attempted; its default process-based hooks hit these limits. The same complete Shelly checks passed with the process settings above. These workarounds change runner configuration, not validation rules or production code.

## Internet-separated device test

For a dedicated HAOS `amd64` / `qemux86-64` test VM, use [HAOS.md](HAOS.md) to install the pinned native Core image. The image handles the aioshelly dependency override itself; the direct Core commands below apply to the Linux development environment.

Use an isolated HA Core development instance, not the existing production HAOS system. Network A contains a mains-powered Shelly Plus/Pro or compatible Gen3/4 device. Network B contains the HA instance with publicly reachable HTTPS/WSS, a trusted certificate and WebSocket forwarding. Do not route Network A's private subnet to HA.

1. Verify HA and reverse-proxy/edge log redaction using an expendable canary, including error paths. See SECURITY.md.
2. Run the tested Core/library forks. Start an isolated Core configuration with `uv run --no-sync hass --config /tmp/shelly-remote-test-config --skip-pip` after installing its integration dependencies. `--skip-pip` prevents HA from replacing the development library with the manifest's released version. Check the library's installed version and source path before pairing.
3. In HA: Settings → Devices & Services → Add Integration → Shelly → remote connection type. Supply the public HTTPS origin if the supported URL helper cannot determine it.
4. Copy the generated WSS URL into Shelly's Outbound WebSocket server setting. Set `ssl_ca` to `ca.pem` for the built-in CA bundle, or `user_ca.pem` for an installed custom CA. `ssl_ca: "*"` disables certificate validation and must not be used for this Internet test. See the linked Shelly documentation in SECURITY.md.
5. Enable outbound WebSocket and apply the device settings. Keep the URL out of browser history exports, terminal commands and screenshots.
6. Confirm that HA's waiting step advances and displays the device ID/MAC. Compare it with the physical device label and local `Shelly.GetDeviceInfo`.
7. Confirm setup. Require successful `Shelly.GetDeviceInfo`, `Shelly.GetConfig` and `Shelly.GetStatus`; if challenged, complete the device password step.
8. Inspect the config entry locally: remote mode, expected unique MAC and credential verifier; no `host` or raw URL. Do not export production credential files.
9. Verify the existing native switch/sensors appear. Toggle the relay from the device and observe `NotifyStatus` updating HA.
10. Toggle the native switch from HA. Confirm `Switch.Set` reaches the device, the response completes and the physical relay changes.
11. Trigger a supported input event and confirm `NotifyEvent` reaches the native event/click path.
12. Disconnect Internet access at Network A without deleting the HA entry. Confirm pending calls fail and entities become unavailable; record heartbeat-detection delay.
13. Restore Internet. Confirm Shelly reconnects automatically, HA fetches current config/status and the same entities become available. Verify controls again.
14. Restart HA while the device is offline, then restore the device. Confirm hash-only admission restoration and setup retry recovery without creating another device/entry.
15. Try a separate test device with the same URL and a different MAC; it must be rejected. Use test credentials only.
16. Regenerate through the entry's reconfigure menu, configure the replacement URL on Shelly, then confirm rotation. The old URL must fail. Cancel a second regeneration and verify the active URL still works.
17. Revoke access. The socket must close and reconnect with that URL must fail. Confirm diagnostics and all audited logs contain no raw credential.

Capture firmware, generation/model, HA/library commits, topology, UTC timestamps, command results, reconnect delay and registry IDs. Publish sanitized evidence only. Gen3/4 variations, certificate trust, HA Cloud ingress, NAT/proxy behavior and actual network outages cannot be proven by the simulated test suite.
