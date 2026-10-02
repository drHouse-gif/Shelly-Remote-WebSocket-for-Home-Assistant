# Remote Shelly WebSocket for Home Assistant

Development of device-initiated Internet WSS connections inside Home Assistant's official Shelly integration. A mains-powered Gen2, Gen3 or Gen4 device connects from its own network to Home Assistant; HA uses that connection for normal RPC control and notifications. HA never needs the device's private IP address.

This is a fork development project, not a released Home Assistant feature. Upstream drafts are open: [aioshelly #1304](https://github.com/home-assistant-libs/aioshelly/pull/1304) and [Core #183944](https://github.com/home-assistant/core/pull/183944). Core depends on a reviewed, published aioshelly release. See [UPSTREAM.md](UPSTREAM.md) for review branches and current check status. No changes have been merged to `dev` or `main`.

| Repository                                                 | Feature branch                       | Tested implementation                      |
| ---------------------------------------------------------- | ------------------------------------ | ------------------------------------------ |
| [aioshelly](https://github.com/drHouse-gif/aioshelly)      | `feature/remote-websocket-transport` | `74751fcb876cc5fbd993721da765d40cd5b5b750` |
| [Home Assistant Core](https://github.com/drHouse-gif/core) | `feature/remote-websocket-transport` | `f5e9025b01ae70abdb0a94fcbafbaddf2d5070eb` |

The HA implementation includes secure admission, identity binding, a native config flow, hash-only persistent pairing credentials, hostless `RpcDevice` setup, shared platforms, outage availability, reconnect resynchronization, startup recovery, revoke/regenerate, diagnostics and logging redaction. Local Shelly and battery-device behavior remain covered by the complete Shelly test suite.

Local and GitHub CI validation: 790 Core Shelly tests and 558 snapshots passed; the unchanged aioshelly implementation has 363 passing tests. Both fork CI runs are green; see [TESTING.md](TESTING.md). Three automatic-review findings are fixed: rejected device passwords show `invalid_auth`, remote entries do not advertise BLE scanner options, and remote cameras do not create or retain an RTSP repair. Pairing and rotation cannot promote expired credentials; rotation requires RPC proof through the replacement socket before persisting its verifier and revoking the old token.

On the dedicated HAOS VM, the physical Pro 3EM is registered with 36 entities across its main device and three phases. Installation of `2026.11.0.dev2` was confirmed by a terminal screenshot on 2026-10-02; the operator then reported successful recovery after an HA restart and a device-network outage, credential regeneration with a working replacement URL and rejection of the previous URL, and explicit revocation followed by regeneration/recovery through the retained entry. Diagnostics confirming the entry's remote transport, timestamped measurements, recovery timing, unchanged registry identities, the remaining runtime security checks and Internet-separated topology remain pending. See [TESTING.md](TESTING.md) for the distinction between captured evidence and operator reports.

Read [ARCHITECTURE.md](ARCHITECTURE.md), [SECURITY.md](SECURITY.md), [TESTING.md](TESTING.md) and [ROADMAP.md](ROADMAP.md) before trying the forks.

For an isolated `amd64` / `qemux86-64` HAOS test VM, use the pinned development image and installation procedure in [HAOS.md](HAOS.md).

The `2026.11.0.dev2` image is pinned to Core `f5e9025` and includes the review and verified-rotation fixes. It is installed on the dedicated test VM; successful physical rotation, old-URL rejection and explicit revocation/recovery are operator-reported, while unconnected/expired replacement and cancellation checks remain pending.

The complete generated WSS URL is a bearer secret. Protect HA, reverse-proxy, edge and device logs before pairing. Moving a secret into the query string does not make it safe to log.

Known scope limits: remote camera HTTP/RTSP and remote BLE proxy scanning are not supported; sleeping devices continue using the existing local battery path. Public HTTPS/WSS reachability, certificate trust and HA Cloud forwarding still require deployment and physical-device validation. The fork library must be installed explicitly for development; a published aioshelly release and a normal Core dependency bump are required before an upstream Core change can ship.
