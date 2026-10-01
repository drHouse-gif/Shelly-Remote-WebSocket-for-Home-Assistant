# Roadmap and upstream scope

## Implemented in the forks

- Persistent inbound RPC transport, correlation, auth retries, deadlines and reconnect ownership in aioshelly.
- Separate secure HA endpoint and high-entropy hash-only persistent credentials.
- Queried MAC/device binding, duplicate/revoke/admission race protection.
- Native remote config flow, supported external HTTPS URL fallback and device credential challenge handling.
- Hostless native entry and shared entity platforms; outage availability, resynchronization and startup recovery.
- Local and battery transport isolation; local mains-powered outbound WS Repair retained, remote-only exemption.
- Diagnostics and audited logging redaction; administrator revoke/regenerate and cancellation cleanup.
- Full library and Shelly test suites, fork CI and a physical-device test procedure.

## Before calling this production-ready

- Complete the Internet-separated physical-device procedure for Gen2, Gen3 and Gen4.
- Verify the actual deployment's proxy/CDN/WAF/device logs and certificate trust.
- Reproduce the green fork CI results on a conventional developer environment.
- Validate whether supported HA Cloud external URLs accept this long-lived device WebSocket route.
- Obtain human review and maintainer agreement on public inbound bearer admission and source logging filters.
- Publish the reviewed aioshelly release, then update Core's manifest requirement and generated requirements normally.

No automatic bootstrap-token rotation protocol, remote camera HTTP/RTSP proxy, Internet BLE scanner proxy, remote sleeping-device support or hardware identity attestation is implemented. Native RPC functionality remains available through the shared transport; these separate protocols need their own design if requested.

## Suggested upstream changes

First aioshelly PR: `ConnectionOptions.remote_device_id`, persistent prepared inbound `WsServerConnection`/server APIs, authorized-only remote subscriptions, RPC correlation/auth/timeouts, disconnect/reconnect semantics and transport tests. Keep HA endpoint/credential/UI policy out of the library. Human review is required before submission.

Then Core PR, dependent on that published library release: remote config flow and entry schema, HTTPS endpoint, verifier/identity lifecycle, native setup/coordinator integration, camera/BLE scope guards, remote-only Repair behavior, diagnostics/log redaction, translations and integration/security/regression tests. Development-only fork CI/dependency overrides should not be part of the production dependency mechanism.

Likely maintainer review questions: whether integration-specific logger filters should instead be a common HTTP/API redaction facility; public Internet endpoint support and brute-force/resource policy; UX for external URL and secret copy/rotation; self-reported MAC identity limitations; initial pairing expiry versus reconnect credential lifetime; remote BLE/camera limitations; quality-scale diagnostics and how the integration's `local_push` classification describes this additional remote transport.

No upstream PR, issue/comment or merge is authorized by the work completed here. Keep development on `feature/remote-websocket-transport`; ask before any upstream submission.
