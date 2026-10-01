# Testing and real-device validation

## Results recorded on 2026-10-01

| Check                                                | Result                                                                                                                                                                                                                                                                    |
| ---------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| aioshelly full tests at `74751fcb`                   | 363 passed                                                                                                                                                                                                                                                                |
| aioshelly Ruff, formatter, `ty`, pydocstyle          | Passed                                                                                                                                                                                                                                                                    |
| aioshelly GitHub CI                                  | [Run 36860221316](https://github.com/drHouse-gif/aioshelly/actions/runs/36860221316), success                                                                                                                                                                             |
| Core complete `tests/components/shelly` suite        | 790 passed; 558 snapshots passed at `f5e9025`                                                                                                                                                                                                                             |
| Core remote config-flow and native integration tests | 26 passed at `f5e9025`, including verified credential rotation and recovery of a revoked entry                                                                                                                                                                            |
| Core automatic-review regressions                    | Reproduced all three failures before their fixes: rejected password, advertised remote BLE options and remote RTSP repair; regression tests pass in the complete suite                                                                                                    |
| Core Shelly Ruff, Mypy, Pylint                       | Passed                                                                                                                                                                                                                                                                    |
| Full Hassfest for the Shelly integration             | Passed                                                                                                                                                                                                                                                                    |
| Fork workflow security/YAML/format checks            | Passed                                                                                                                                                                                                                                                                    |
| Core GitHub CI                                       | [Run 36926623186](https://github.com/drHouse-gif/core/actions/runs/36926623186), success at `f5e9025`; 790 tests and 558 snapshots with unchanged aioshelly `74751fcb`                                                                                                    |
| Upstream draft PR checks                             | [aioshelly #1304](https://github.com/home-assistant-libs/aioshelly/pull/1304) and [Core #183944](https://github.com/home-assistant/core/pull/183944) are open; initial upstream workflows report `action_required`, not test results; see [UPSTREAM.md](UPSTREAM.md)      |
| HAOS development image build and startup smoke       | [Run 36882493791](https://github.com/drHouse-gif/Shelly-Remote-WebSocket-for-Home-Assistant/actions/runs/36882493791), success; source hashes, 149 packages, `RUNNING` and native remote form                                                                             |
| Revised HAOS image with progress URL fix             | [Run 36890779081](https://github.com/drHouse-gif/Shelly-Remote-WebSocket-for-Home-Assistant/actions/runs/36890779081), success; `2026.11.0.dev1`, source/translation checks, 149 packages and fresh boot                                                                  |
| HAOS image with verified credential rotation         | [Run 36927098977](https://github.com/drHouse-gif/Shelly-Remote-WebSocket-for-Home-Assistant/actions/runs/36927098977), success; `2026.11.0.dev2` at Core `f5e9025`, 55 source fingerprints, 149 packages, fresh boot and independently verified anonymous registry access |
| Dedicated HAOS 18.3 VM image installation            | First image installation confirmed by terminal screenshot; operator subsequently reports completing the `2026.11.0.dev1` update; updated `ha core info` result not captured                                                                                               |
| Native flow on the actual HAOS VM                    | URL display regression fixed at `b2e5fb3`; operator reports successful pairing after the revised-image update                                                                                                                                                             |
| Physical Pro 3EM native entity registration          | Firmware 1.7.5 identified earlier; integration screenshot shows 36 entities: 12 on the main device and 8 on each of three phase devices                                                                                                                                   |
| Physical remote transport and live measurements      | Diagnostics `transport.type` / `connected` and changing sensor values not yet captured                                                                                                                                                                                    |
| Physical reconnect and runtime security checks       | Still pending: outage/recovery, storage inspection, TLS trust, log redaction and credential rotation/revocation                                                                                                                                                           |
| Physical Gen2/3/4 device across separate networks    | Not yet performed                                                                                                                                                                                                                                                         |

The native integration test uses actual `RpcDevice` and `WsServerConnection`, with a queue-backed simulated device socket. It exercises endpoint identity query, native entity loading, `Switch.Set`, status/event notifications, availability, replacement socket, unchanged registry identities, diagnostics redaction and remote Repair exemption. Another test restores a hash-only entry while offline and proves setup resumes when the device connects. Rotation tests use the real admission manager and native device: an old socket cannot approve a replacement, successful config/status proof preserves the loaded device and entities, the old credential is revoked, and a previously revoked entry resumes setup after new admission is verified. Existing full-suite tests retain local, battery and local outbound-WS Repair coverage.

The new regressions exercise the user-facing authentication form, frontend `supports_options` metadata and native remote-camera setup. A rejected password must display `invalid_auth` and a correct retry must complete pairing. Remote entries must not advertise the BLE scanner options. Remote-camera setup must not create an RTSP repair, and the issue manager must remove a stale one. Existing local BLE options and local-camera repairs remain covered by the full suite.

The HAOS `2026.11.0.dev2` image includes these fixes at Core `f5e9025`; installation and physical validation of this image are pending. Also test a rejected device password followed by a correct retry, the absence of remote BLE options, and RTSP repair suppression on a compatible camera. The rotation procedure below requires rejection of an unconnected or expired replacement, successful verified handover, old-token rejection, cancellation and recovery after revocation. Do not claim these physical checks from the simulated tests or from the older Pro 3EM image.

## Recorded Pro 3EM milestone

On 2026-10-01, the operator reported that pairing worked after completing the revised-image update. The native Shelly integration screenshot confirms registration of the physical Pro 3EM's main device and Phase A, B and C devices, with 36 entities in total. A separate screenshot shows the Supervisor repair `home_assistant_core_custom_image`, consistent with the custom development container. No raw pairing URL is included in these screenshots or this record.

This evidence confirms native entity registration. It does not independently establish the entry's transport type, a currently connected socket, live measurement updates or absence of a route between the two private networks. The remaining physical tests below still apply.

For the next check, download diagnostics from the Shelly entry's menu and inspect them locally. Require `transport.type` to be `remote_ws` and `transport.connected` to be `true`; share only these two fields. Then open a phase device and compare changing voltage/current/power measurements with the device's local UI. Temporarily disconnect the test device's network, restore it and verify that the same entities recover automatically. Keep diagnostics, stored entries and logs private until their redaction has been checked.

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

Workspace limitations were handled explicitly: full `script/setup` could not build an unrelated DTLS dependency without `autoconf`; relevant test dependencies were installed separately. The environment restricts AF_UNIX worker sockets and process introspection. Local Mypy ran with zero workers and its optional psutil discovery disabled, Pylint with one worker, and Hassfest with the `fork` start method. The interrupted workspace's Mypy SQLite cache was malformed; a fresh cache was used for the latest check. Full `prek --all-files` was attempted; its default process-based hooks hit these limits. Its Ruff, formatting, spelling, workflow security, JSON, branch, YAML, generated-file and metadata hooks passed. The same complete Shelly checks passed with the process settings above. These workarounds change runner configuration, not validation rules or production code.

## Internet-separated device test

For a dedicated HAOS `amd64` / `qemux86-64` test VM, use [HAOS.md](HAOS.md) to install the pinned native Core image. The image handles the aioshelly dependency override itself; the direct Core commands below apply to the Linux development environment.

Use an isolated HA Core development instance, not the existing production HAOS system. Network A contains a mains-powered Shelly Plus/Pro or compatible Gen3/4 device. Network B contains the HA instance with publicly reachable HTTPS/WSS, a trusted certificate and WebSocket forwarding. Do not route Network A's private subnet to HA.

For the current Pro 3EM test device, validate its native EM/EMData measurements and status notifications. The relay and input steps below apply to devices with those components. A Pro 3EM without the switch add-on can exercise outbound RPC and reconnection using its native reboot button on the test device; verify that the same measurement entities recover afterwards. Record which component-specific steps apply.

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
16. Start regeneration through the entry's reconfigure menu. Submit before configuring the replacement on Shelly: HA must show `cannot_connect`, retain the old verifier and continue accepting the old URL. Leave this unused replacement for more than ten minutes, then submit: the flow must abort as expired without changing the stored verifier.
17. Start a fresh regeneration, configure its replacement URL on Shelly within ten minutes, then confirm. HA must verify config/status RPC before saving the new verifier. Require the same entities, a connected remote transport and working measurements/control afterwards. Test reconnect with the old URL on the same test device: it must be rejected; restore the new URL afterwards. Keep both URLs private.
18. Start and cancel another regeneration without changing the device's configured URL. The active URL must still work. Revoke access: its socket must close and reconnect must fail. Regenerate again, configure and verify the replacement; the retained native entry must resume setup without duplicate entities. Confirm diagnostics and all audited logs contain no raw credential.

Capture firmware, generation/model, HA/library commits, topology, UTC timestamps, command results, reconnect delay and registry IDs. Publish sanitized evidence only. Gen3/4 variations, certificate trust, HA Cloud ingress, NAT/proxy behavior and actual network outages cannot be proven by the simulated test suite.
