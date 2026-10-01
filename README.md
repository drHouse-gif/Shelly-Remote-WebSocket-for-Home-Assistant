# Remote Shelly WebSocket for Home Assistant

Development of device-initiated Internet WSS connections inside Home Assistant's official Shelly integration. A mains-powered Gen2, Gen3 or Gen4 device connects from its own network to Home Assistant; HA uses that connection for normal RPC control and notifications. HA never needs the device's private IP address.

This is a fork development project, not a released Home Assistant feature. No upstream pull request has been opened and no changes have been merged to `dev` or `main`.

| Repository                                                 | Feature branch                       | Tested implementation                      |
| ---------------------------------------------------------- | ------------------------------------ | ------------------------------------------ |
| [aioshelly](https://github.com/drHouse-gif/aioshelly)      | `feature/remote-websocket-transport` | `74751fcb876cc5fbd993721da765d40cd5b5b750` |
| [Home Assistant Core](https://github.com/drHouse-gif/core) | `feature/remote-websocket-transport` | `b2e5fb3eba8645cce0453829c12f02a9c4b2135f` |

The HA implementation includes secure admission, identity binding, a native config flow, hash-only persistent pairing credentials, hostless `RpcDevice` setup, shared platforms, outage availability, reconnect resynchronization, startup recovery, revoke/regenerate, diagnostics and logging redaction. Local Shelly and battery-device behavior remain covered by the complete Shelly test suite.

Local and GitHub CI validation: 772 Core Shelly tests and 558 snapshots passed; 363 aioshelly tests passed. Both fork CI runs are green; see [TESTING.md](TESTING.md). The actual HAOS VM loads the native flow; its first UI check exposed a pairing URL display regression, now fixed. A physical Internet-separated Shelly has not yet connected.

Read [ARCHITECTURE.md](ARCHITECTURE.md), [SECURITY.md](SECURITY.md), [TESTING.md](TESTING.md) and [ROADMAP.md](ROADMAP.md) before trying the forks.

For an isolated `amd64` / `qemux86-64` HAOS test VM, use the pinned development image and installation procedure in [HAOS.md](HAOS.md).

The complete generated WSS URL is a bearer secret. Protect HA, reverse-proxy, edge and device logs before pairing. Moving a secret into the query string does not make it safe to log.

Known scope limits: remote camera HTTP/RTSP and remote BLE proxy scanning are not supported; sleeping devices continue using the existing local battery path. Public HTTPS/WSS reachability, certificate trust and HA Cloud forwarding still require deployment and physical-device validation. The fork library must be installed explicitly for development; a published aioshelly release and a normal Core dependency bump are required before an upstream Core change can ship.
