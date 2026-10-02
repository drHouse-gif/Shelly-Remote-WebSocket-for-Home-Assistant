# Upstream review

The operator explicitly authorized publication on 2026-10-01. Both PRs were opened as drafts and are linked to one another. On 2026-10-02, the library PR is open and no longer a draft; Core remains an open draft.

| Proposal                                                                                                                                    | Target                               | Fork review head                           | Scope                                                                 |
| ------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------ | ------------------------------------------ | --------------------------------------------------------------------- |
| [aioshelly #1304](https://github.com/home-assistant-libs/aioshelly/pull/1304): Add persistent RPC transport for device-initiated WebSockets | `home-assistant-libs/aioshelly:main` | `c7552203fd389c2b68a5fcf80ea1f12fa0e97ae7` | 7 files; library transport, native RpcDevice support and tests        |
| [Core #183944](https://github.com/home-assistant/core/pull/183944): Add remote WebSocket pairing to Shelly                                  | `home-assistant/core:dev`            | `cf8d6a0fe2dee961ac4842f0be87688117db01b1` | 14 files; pairing, security, native lifecycle, translations and tests |

Both fork review branches are named `feature/remote-websocket-transport-upstream`. Their initial cleanup commits remove only the fork-specific development workflows. Review fixes are then added as new commits to both the development and review branches. Local Git comparisons confirm that application and test files are identical between each pair of current heads: aioshelly `74751fcb` / `c755220`, Core `f5e9025` / `cf8d6a0`. The only Core branch difference is the removed development workflow. Both review diffs pass `git diff --check`.

The original `feature/remote-websocket-transport` branches receive the same application changes. The pinned HAOS `2026.11.0.dev2` test image uses Core `f5e9025` and contains these review and rotation fixes; the earlier `dev1` physical pairing report does not validate the new image. The Core upstream comparison at publication was 44 commits behind `dev`; none of those upstream changes touched files in this proposal. GitHub subsequently reported both drafts mergeable. These observations are a publication-time snapshot, not an upstream CI result.

## Automatic-review corrections

The behavior and credential-lifecycle defects were reproduced before applying their fixes on 2026-10-01:

| Correction                                                       | Development commit | PR review commit | Regression coverage                                                                                                                                                                     |
| ---------------------------------------------------------------- | ------------------ | ---------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Show `invalid_auth` after a rejected device password             | `e1b3bd3`          | `cf4b248`        | Initial challenge has no error; rejected password shows the error; correct retry completes pairing                                                                                      |
| Hide remote BLE scanner options and suppress remote RTSP repairs | `defa182`          | `b290aae`        | Frontend metadata does not advertise options; remote-camera setup does not create a repair; stale RTSP issue is deleted                                                                 |
| Reject expired setup/rotation confirmation                       | `69c7690`          | `f1d9f0b`        | Expiry before confirmation and during setup RPC cannot create permanent admission; expired regeneration retains the old verifier                                                        |
| Verify replacement credential before committing rotation         | `f5e9025`          | `cf8d6a0`        | Candidate socket ownership, RPC/auth failures, in-flight expiry/revocation/replacement and entry changes; real native rotation preserves the loaded device and restores a revoked entry |

These are subsequent commits, without rewriting the published PR history. The aioshelly implementation is unchanged. The other automatic-review findings remain open: a published library dependency and the official user documentation PR are still required. Preparing documentation does not authorize another upstream PR.

## Dependency and validation

Core remains a draft dependent on the library proposal. Its current manifest still specifies released aioshelly, which does not provide the new transport API. After the library is reviewed and published, Core needs the normal manifest and generated-requirements update before it is ready. The development dependency override is documented in [TESTING.md](TESTING.md), not included as a production dependency mechanism.

Recorded library validation remains green: 363 tests at `74751fcb`. Core `f5e9025` passed all 790 Shelly tests and 558 snapshots locally, plus Ruff, Mypy, Pylint and Hassfest. The latest [fork CI 36926623186](https://github.com/drHouse-gif/core/actions/runs/36926623186) is green with the same paired library. Earlier expiry-only [CI 36923611635](https://github.com/drHouse-gif/core/actions/runs/36923611635) and behavior-fix [CI 36919929713](https://github.com/drHouse-gif/core/actions/runs/36919929713) are also green. The `dev2` installation is now confirmed and the operator reports successful restart/network recovery, credential rotation with old-URL rejection, and explicit revocation/recovery. See [TESTING.md](TESTING.md) for evidence limits and the remaining deployment/security checks.

## Discussion checked on 2026-10-02

Neither PR has a human review or comment in the retrieved discussion timeline. The library PR has no comments. Core has 14 entries from Home Assistant and Copilot bots only. This is not maintainer approval or rejection.

The latest [Copilot review](https://github.com/home-assistant/core/pull/183944#pullrequestreview-5385600582), submitted on 2026-10-01 at 21:13 UTC, additionally flags trailing-dot local hostnames such as `localhost.` and `device.local.` bypassing public-origin validation. This finding needs reproduction against the pinned implementation; the published dependency and official documentation remain separate blockers. Previously fixed findings must be assessed against the current code rather than the bot's summary alone.

Initial upstream workflow statuses captured on 2026-10-01:

| Workflow                            | Run                                                                                      | Status                          |
| ----------------------------------- | ---------------------------------------------------------------------------------------- | ------------------------------- |
| aioshelly Test                      | [36914908715](https://github.com/home-assistant-libs/aioshelly/actions/runs/36914908715) | `completed` / `action_required` |
| Core CI                             | [36915125263](https://github.com/home-assistant/core/actions/runs/36915125263)           | `completed` / `action_required` |
| Core Quality scale reviewer trigger | [36915125150](https://github.com/home-assistant/core/actions/runs/36915125150)           | `completed` / `action_required` |

These statuses do not establish passed or failed upstream tests. Approval of fork workflow execution is controlled by upstream maintainers.

The PR descriptions disclose AI assistance, preserve Core's full PR template and leave contributor-understanding and human-review attestations unchecked. The remaining review covers the transport API, public bearer admission, source logging filters, credential rotation and deployment validation. Keep review changes in subsequent commits; do not amend, squash or rebase the published PR branch history.
