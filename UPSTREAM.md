# Upstream draft review

The operator explicitly authorized publication on 2026-10-01. These two draft PRs are open and linked to one another:

| Proposal | Target | Fork review head | Scope |
| --- | --- | --- | --- |
| [aioshelly #1304](https://github.com/home-assistant-libs/aioshelly/pull/1304): Add persistent RPC transport for device-initiated WebSockets | `home-assistant-libs/aioshelly:main` | `c7552203fd389c2b68a5fcf80ea1f12fa0e97ae7` | 7 files; library transport, native RpcDevice support and tests |
| [Core #183944](https://github.com/home-assistant/core/pull/183944): Add remote WebSocket pairing to Shelly | `home-assistant/core:dev` | `b290aae81ab065b8e9165dda81b98878f537973e` | 14 files; pairing, security, native lifecycle, translations and tests |

Both fork review branches are named `feature/remote-websocket-transport-upstream`. Their initial cleanup commits remove only the fork-specific development workflows. Review fixes are then added as new commits to both the development and review branches. Local Git comparisons confirm that application and test files are identical between each pair of current heads: aioshelly `74751fcb` / `c755220`, Core `defa182` / `b290aae`. The only Core branch difference is the removed development workflow. Both review diffs pass `git diff --check`.

The original `feature/remote-websocket-transport` branches receive the same application changes. The pinned HAOS `2026.11.0.dev1` test image remains at Core `b2e5fb3` and does not contain the later review fixes. The Core upstream comparison at publication was 44 commits behind `dev`; none of those upstream changes touched files in this proposal. GitHub subsequently reported both drafts mergeable. These observations are a publication-time snapshot, not an upstream CI result.

## Automatic-review corrections

All three behavior defects were reproduced before applying their fixes on 2026-10-01:

| Correction | Development commit | PR review commit | Regression coverage |
| --- | --- | --- | --- |
| Show `invalid_auth` after a rejected device password | `e1b3bd3` | `cf4b248` | Initial challenge has no error; rejected password shows the error; correct retry completes pairing |
| Hide remote BLE scanner options and suppress remote RTSP repairs | `defa182` | `b290aae` | Frontend metadata does not advertise options; remote-camera setup does not create a repair; stale RTSP issue is deleted |

These are subsequent commits, without rewriting the published PR history. The aioshelly implementation is unchanged. The other automatic-review findings remain open: a published library dependency and the official user documentation PR are still required. Preparing documentation does not authorize another upstream PR.

## Dependency and validation

Core remains a draft dependent on the library proposal. Its current manifest still specifies released aioshelly, which does not provide the new transport API. After the library is reviewed and published, Core needs the normal manifest and generated-requirements update before it is ready. The development dependency override is documented in [TESTING.md](TESTING.md), not included as a production dependency mechanism.

Recorded library validation remains green: 363 tests at `74751fcb`. Core `defa182` passed all 774 Shelly tests and 558 snapshots locally, plus Ruff, Mypy, Pylint and Hassfest. Both the first correction's [fork CI 36919111922](https://github.com/drHouse-gif/core/actions/runs/36919111922) and the latest [fork CI 36919929713](https://github.com/drHouse-gif/core/actions/runs/36919929713) are green. The physical Pro 3EM milestone is native registration of 36 entities with operator-reported pairing; transport diagnostics, live values, outage recovery, TLS/log protection and Internet-separated topology remain pending.

Initial upstream workflow statuses captured on 2026-10-01:

| Workflow | Run | Status |
| --- | --- | --- |
| aioshelly Test | [36914908715](https://github.com/home-assistant-libs/aioshelly/actions/runs/36914908715) | `completed` / `action_required` |
| Core CI | [36915125263](https://github.com/home-assistant/core/actions/runs/36915125263) | `completed` / `action_required` |
| Core Quality scale reviewer trigger | [36915125150](https://github.com/home-assistant/core/actions/runs/36915125150) | `completed` / `action_required` |

These statuses do not establish passed or failed upstream tests. Approval of fork workflow execution is controlled by upstream maintainers.

The PR descriptions disclose AI assistance, preserve Core's full PR template and leave contributor-understanding and human-review attestations unchecked. The remaining review covers the transport API, public bearer admission, source logging filters, credential rotation and deployment validation. Keep review changes in subsequent commits; do not amend, squash or rebase the published PR branch history.
