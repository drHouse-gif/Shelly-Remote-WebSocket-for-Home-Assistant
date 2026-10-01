# Remote Shelly WebSocket for Home Assistant

Development of device-initiated Internet WSS connections inside Home Assistant's official Shelly integration. A mains-powered Gen2, Gen3 or Gen4 device connects from its own network to Home Assistant; HA uses that connection for normal RPC control and notifications. HA never needs the device's private IP address.

This is a fork development project, not a released Home Assistant feature. Upstream drafts are open: [aioshelly #1304](https://github.com/home-assistant-libs/aioshelly/pull/1304) and [Core #183944](https://github.com/home-assistant/core/pull/183944). Core depends on a reviewed, published aioshelly release. See [UPSTREAM.md](UPSTREAM.md) for review branches and current check status. No changes have been merged to `dev` or `main`.

| Repository                                                 | Feature branch                       | Tested implementation                      |
| ---------------------------------------------------------- | ------------------------------------ | ------------------------------------------ |
| [aioshelly](https://github.com/drHouse-gif/aioshelly)      | `feature/remote-websocket-transport` | `74751fcb876cc5fbd993721da765d40cd5b5b750` |
| [Home Assistant Core](https://github.com/drHouse-gif/core) | `feature/remote-websocket-transport` | `defa18244338ef2d5aa18fa1cdca05cc533d082f` |

The HA implementation includes secure admission, identity binding, a native config flow, hash-only persistent pairing credentials, hostless `RpcDevice` setup, shared platforms, outage availability, reconnect resynchronization, startup recovery, revoke/regenerate, diagnostics and logging redaction. Local Shelly and battery-device behavior remain covered by the complete Shelly test suite.

Local and GitHub CI validation: 774 Core Shelly tests and 558 snapshots passed; the unchanged aioshelly implementation has 363 passing tests. Both fork CI runs are green; see [TESTING.md](TESTING.md). Three automatic-review findings are fixed: rejected device passwords show `invalid_auth`, remote entries do not advertise BLE scanner options, and remote cameras do not create or retain an RTSP repair. On the dedicated HAOS VM, the operator reports successful pairing of a physical Pro 3EM after the progress URL fix and image update. The native integration screenshot shows 36 entities across the main device and its three phases. Confirmation of the entry's remote transport, live measurements, reconnect behavior, runtime log protection and Internet-separated topology remains pending.

Read [ARCHITECTURE.md](ARCHITECTURE.md), [SECURITY.md](SECURITY.md), [TESTING.md](TESTING.md) and [ROADMAP.md](ROADMAP.md) before trying the forks.

For an isolated `amd64` / `qemux86-64` HAOS test VM, use the pinned development image and installation procedure in [HAOS.md](HAOS.md).

That image is still pinned to Core `b2e5fb3` and does not include the newer review fixes. Build a new immutable image before checking those fixes on HAOS; the existing image can still be used for the pending transport and reconnect observations.

The complete generated WSS URL is a bearer secret. Protect HA, reverse-proxy, edge and device logs before pairing. Moving a secret into the query string does not make it safe to log.

Known scope limits: remote camera HTTP/RTSP and remote BLE proxy scanning are not supported; sleeping devices continue using the existing local battery path. Public HTTPS/WSS reachability, certificate trust and HA Cloud forwarding still require deployment and physical-device validation. The fork library must be installed explicitly for development; a published aioshelly release and a normal Core dependency bump are required before an upstream Core change can ship.
