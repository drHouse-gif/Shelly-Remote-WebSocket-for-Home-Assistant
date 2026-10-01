# Security model

## Credential lifecycle

The complete pairing URL, including its query, is sensitive. `secrets.token_urlsafe(32)` generates the credential. HA uses SHA-256 for its verifier and constant-time comparison for verifier equality. A salt is unnecessary for a uniformly random 256-bit token; this is not a password hash.

HA's persistent config entry and credential manager keep only the verifier. The secret is available during the active flow and remains in Shelly's own outbound WebSocket configuration for reconnect. Requests, flow responses and device RPC config replies necessarily carry it in memory. This implementation does not claim memory zeroization or protection from compromised HA/device processes.

Temporary credentials have a ten-minute deadline for new socket admission and setup confirmation. HA checks expiry before upgrade, after identity resolution, before confirmation and after its RPC calls return. The deadline does not independently close an already admitted socket or dismiss an idle confirmation screen, but submitting after expiry cannot promote that verifier to permanent admission. Flow cancellation revokes the temporary credential. Successful setup converts the temporary verifier into a persistent, MAC-bound device credential. It is not single-use for reconnect. Automatic rotation would require reliably updating Shelly's stored `Ws.SetConfig` URL before closing the old connection; that recovery protocol is intentionally deferred.

Administrator-triggered regeneration creates a temporary replacement bound to the same entry and MAC. Confirmation requires an identified, currently connected socket admitted with that exact replacement credential, followed by successful `Shelly.GetConfig` and `Shelly.GetStatus` on that connection. Before committing, HA checks that the credential is still valid, the same socket remains active and the stored entry credential has not changed during those RPC calls. Only then does it persist the new verifier, remove its deadline and revoke the old credential. An old live socket, an expired replacement or failed RPC cannot approve rotation. The loaded native device remains in place; a revoked entry waiting for setup is retried after confirmation. Cancellation preserves the old credential and revokes only the replacement. A candidate connection can replace the old socket before confirmation, so preserving the old credential does not promise an uninterrupted old socket. Removing an entry revokes its admission.

A stolen credential is a device-scoped bearer capability. An attacker who knows the expected MAC can emulate matching `GetDeviceInfo`; MAC binding is not proof of physical hardware. Revoke/regenerate after exposure. Pairing credentials are not HA user access tokens and grant no access to HA's general authenticated API.

## Admission and resource limits

HA accepts only requests considered secure by its HTTP framework. HTTPS termination therefore requires correctly restricted `trusted_proxies`; arbitrary forwarded headers must not be trusted. Browser Origin headers are rejected. Token verification precedes WebSocket upgrade.

Identity is queried with a ten-second deadline and a maximum of 32 messages. There are at most 16 concurrent identity handshakes and one handshake per verifier; each message is limited to 1 MiB. Revocation and expiry are checked again after identity resolution. Duplicate MACs across entries/credentials and mismatched bound MACs are rejected. Legitimate reconnect replaces the old socket. Invalid token requests do not incur RPC handshake work. These limits do not replace edge protection against TCP/TLS floods.

## Source audit: logging and diagnostics

The audit uses Core base `836bce064b1b0cedd3773ecad867929d71826fc8` and installed aiohttp `3.14.3` source.

| Source                                                      | What may be logged                                             | Mitigation                                                                                      |
| ----------------------------------------------------------- | -------------------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| `homeassistant/helpers/http.py` request handler             | `request.path` at debug level                                  | Fixed route has no credential in its path; source also has a redaction filter                   |
| `http/auth.py`                                              | Request path in auth messages                                  | Source filter                                                                                   |
| `http/security_filter.py`                                   | `request.raw_path`, including query                            | Source filter removes the complete URL                                                          |
| `http/ban.py` wrong-login handling                          | `request.rel_url`, including query                             | Invalid credential returns a plain 401 response instead of raising; source filter still applies |
| `websocket_api/http.py` writer and pending-message warnings | Entire frontend response bytes, including pairing placeholders | Exact `homeassistant.components.websocket_api.http.connection` logger filter                    |
| aiohttp access logging                                      | Default request-line logging includes query                    | `aiohttp.access` filter                                                                         |
| aiohttp server/task/config-flow errors                      | Exception text and formatted arguments may contain URLs        | Audited HA/aiohttp/aioshelly source filters, including `homeassistant.core`                     |
| Shelly diagnostics                                          | Device config, status or errors may contain URL strings        | Verifier/credentials redacted, selected config fields only, recursive URL scrubbing             |
| Reverse proxy/CDN/WAF/device/export tools                   | May record the entire URL independently                        | Operator must redact or suppress these logs before pairing; HA cannot control them              |

The filter formats arguments, removes the complete absolute or relative pairing URL, handles percent-encoded URL text and redacts formatted exception/stack text. Tests cover every configured logger, frontend response bytes, encoded requests and nested diagnostics. Library remote send logs include only method names; pending-call timeout/disconnect errors exclude sensitive RPC parameters.

This is an audit of known sources, not a guarantee for arbitrary third-party middleware, future logger names, custom handlers, crash dumps or edge telemetry. Re-audit source changes before release. A logger filter does not propagate automatically to child loggers; the exact emitting sources are registered explicitly. No raw pairing URL should be pasted into tickets, CI output, screenshots or exported device config.

## Native Home Assistant Cloud route

The audited image uses `hass-nabucasa` 2.7.0 and `snitun` 0.47.0. In `hass_nabucasa/remote.py`, the certificate context and HA's existing aiohttp runner are passed to `SniTunClientAioHttp`. Its `TransportConnector` terminates TLS locally with `start_tls(..., server_side=True)` and hands the resulting transport to HA's HTTP protocol. The inspected lifecycle/connector log calls contain connection metadata and transport errors; they do not log HTTP request lines. HA/aiohttp's decrypted-request logging still requires the filters audited above.

[Nabu Casa's deep dive](https://support.nabucasa.com/hc/en-us/articles/25619268678557-Remote-access-Deep-dive) documents TCP forwarding of encrypted traffic and decryption on the HA instance; its [security documentation](https://support.nabucasa.com/hc/en-us/articles/26508882007581-Remote-access-Security-aspects) places the certificate private key on HA. Under that documented model, the relay cannot read the pairing query string. This is a source/model inference, not a claim to have inspected deployed relay telemetry, and it does not apply to a separate TLS-terminating proxy.

Initialize an expendable remote flow first: the endpoint and filters are registered lazily. Keep its generated URL private and unused on a device. Send a request to `/api/shelly/remote` through the intended HTTPS origin with the public test marker `remote_key=HA_REMOTE_LOG_CANARY_20261001`, using normal certificate verification and no browser `Origin` header. The endpoint returns 401 for that invalid marker after the secure-request check; a 403 or a 404 after initialization needs investigation. Check locally that HA and any other plaintext log sinks contain no raw canary, then cancel the expendable flow to revoke its credential. The invalid-marker check proves neither successful WebSocket admission nor all error paths; complete the remaining canary and physical-device procedure too. Publish only the HTTP status and redaction result, then start a fresh flow for the device.

## Reverse-proxy configuration

NGINX's default combined access log uses `$request`; `$request_uri` also includes arguments. Replacing an access log with a whitelist that excludes the request line, arguments and headers avoids recording the secret for that log. For example, define in `http`:

```nginx
log_format shelly_remote '$remote_addr [$time_local] $status $bytes_sent';
```

In the exact remote endpoint location, use that format or `access_log off`, alongside the deployment's WebSocket upgrade forwarding. Audit every inherited/duplicate access log, including upstream and edge logs. This example alone does not protect NGINX error logs: failures and debug output can include the original request URI. Use a redaction sink before persistence or suppress request-bearing error output for the dedicated listener, and verify pre-routing errors too. Increasing the error-log severity alone is not a reliable redaction strategy.

Use an expendable canary URL to test successful upgrade, rejected token, malformed request, upstream outage and timeout paths. Search HA, proxy, edge, tracing and device logs locally for the canary; do not print a real credential while auditing. Confirm that both successful and failed requests leave no raw credential. Rotate any credential used before log protection was verified.

Primary references: [NGINX access log format](https://nginx.org/en/docs/http/ngx_http_log_module.html), [NGINX variables](https://nginx.org/en/docs/http/ngx_http_core_module.html#var_request_uri), [NGINX error logging](https://nginx.org/en/docs/ngx_core_module.html#error_log), [Shelly outbound WebSocket](https://shelly-api-docs.shelly.cloud/gen2/ComponentsAndServices/Ws/), [Shelly authentication exemptions](https://shelly-api-docs.shelly.cloud/gen2/General/Authentication/).
