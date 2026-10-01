# Upstream draft review

The operator explicitly authorized publication on 2026-10-01. These two draft PRs are open and linked to one another:

| Proposal | Target | Fork review head | Scope |
| --- | --- | --- | --- |
| [aioshelly #1304](https://github.com/home-assistant-libs/aioshelly/pull/1304): Add persistent RPC transport for device-initiated WebSockets | `home-assistant-libs/aioshelly:main` | `c7552203fd389c2b68a5fcf80ea1f12fa0e97ae7` | 7 files; library transport, native RpcDevice support and tests |
| [Core #183944](https://github.com/home-assistant/core/pull/183944): Add remote WebSocket pairing to Shelly | `home-assistant/core:dev` | `672274e1ec11b3ab6516be29583105f3ebd88f48` | 13 files; pairing, security, native lifecycle, translations and tests |

Both fork review branches are named `feature/remote-websocket-transport-upstream`. Each adds one commit to the tested feature head to remove only its fork-specific development workflow. Local Git comparisons confirm that application and test files are identical to the green tested heads: aioshelly `74751fcb` and Core `b2e5fb3`. Both review diffs pass `git diff --check`.

The original `feature/remote-websocket-transport` branches and pinned HAOS test image retain the tested implementation. The Core upstream comparison at publication was 44 commits behind `dev`; none of those upstream changes touched files in this proposal. GitHub subsequently reported both drafts mergeable. These observations are a publication-time snapshot, not an upstream CI result.

## Dependency and validation

Core remains a draft dependent on the library proposal. Its current manifest still specifies released aioshelly, which does not provide the new transport API. After the library is reviewed and published, Core needs the normal manifest and generated-requirements update before it is ready. The development dependency override is documented in [TESTING.md](TESTING.md), not included as a production dependency mechanism.

Existing fork validation remains green: 363 aioshelly tests; 772 Core Shelly tests and 558 snapshots. The physical Pro 3EM milestone is native registration of 36 entities with operator-reported pairing; transport diagnostics, live values, outage recovery, TLS/log protection and Internet-separated topology remain pending.

Initial upstream workflow statuses captured on 2026-10-01:

| Workflow | Run | Status |
| --- | --- | --- |
| aioshelly Test | [36914908715](https://github.com/home-assistant-libs/aioshelly/actions/runs/36914908715) | `completed` / `action_required` |
| Core CI | [36915125263](https://github.com/home-assistant/core/actions/runs/36915125263) | `completed` / `action_required` |
| Core Quality scale reviewer trigger | [36915125150](https://github.com/home-assistant/core/actions/runs/36915125150) | `completed` / `action_required` |

These statuses do not establish passed or failed upstream tests. Approval of fork workflow execution is controlled by upstream maintainers.

The PR descriptions disclose AI assistance, preserve Core's full PR template and leave contributor-understanding and human-review attestations unchecked. The remaining review covers the transport API, public bearer admission, source logging filters, credential rotation and deployment validation. Keep review changes in subsequent commits; do not amend, squash or rebase the published PR branch history.
