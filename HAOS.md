# HAOS development image

This image runs the tested native Core integration on an isolated HAOS test VM. It targets `amd64` / `qemux86-64`, with Core `f5e9025b01ae70abdb0a94fcbafbaddf2d5070eb` and unchanged aioshelly `74751fcb876cc5fbd993721da765d40cd5b5b750`. It is a development build, not an official HA release.

The image build version is `2026.11.0.dev2`; the pinned Core package still reports `2026.11.0.dev0`. HAOS tracks the container's build version, so this new immutable tag permits an update from the earlier test image without changing Core application version files. The container image name is:

```text
ghcr.io/drhouse-gif/shelly-remote-haos-qemux86-64:2026.11.0.dev2
```

This image includes the progress URL fix, rejected-password feedback, remote BLE/RTSP scope corrections, expired-confirmation guards and verified credential rotation. The pinned Core passed all 790 Shelly tests and 558 snapshots in [fork CI 36926623186](https://github.com/drHouse-gif/core/actions/runs/36926623186).

[Image run 36927098977](https://github.com/drHouse-gif/Shelly-Remote-WebSocket-for-Home-Assistant/actions/runs/36927098977) verifies the pinned source hashes and generated translations, installed dependency consistency and fresh boot to `RUNNING` with the native remote form before publishing. The `dev2` image digest is:

```text
sha256:43c0cebc9b169c13215266ea6112ff8648a234ec555f04c90d06df947c94f4fc
```

The build completed successfully: 55 source fingerprints, 149 installed packages and the native startup/config-flow smoke checks passed. The downloaded provenance archive passed its SHA-256 check; its source fingerprints match the local pinned checkouts and its image report records this exact digest. Anonymous registry access was independently verified with HTTP 200, matching manifest/config hashes, Linux `amd64` architecture and image build version `2026.11.0.dev2`.

## Update the existing dedicated test VM

Keep the original full pre-test checkpoint. Create an additional checkpoint before this update, then run each command separately:

```sh
ha backups new --name before-shelly-remote-dev2
ha core update --version 2026.11.0.dev2
ha core info
```

The existing custom image override should remain `ghcr.io/drhouse-gif/shelly-remote-haos-qemux86-64`; check it before updating. `ha core info` must report image build version `2026.11.0.dev2`. The existing remote entry and device URL should continue working after HA restarts. Inspect diagnostics locally for `transport.type: remote_ws` and `transport.connected: true`, then perform the measurements, outage/recovery and credential rotation steps in [TESTING.md](TESTING.md). Share only sanitized results.

On 2026-10-02, the operator's terminal screenshot confirmed the pre-update backup, successful update and custom image/build version `2026.11.0.dev2` in `ha core info`. The operator subsequently reported successful operation after restarting HA and after disconnecting/restoring the test device's network, then successful credential regeneration with the replacement URL working and the previous URL rejected. These operator reports do not establish the diagnostics transport type, hash-only storage or deployment-wide log redaction; see [TESTING.md](TESTING.md) for the evidence limits and remaining security checks.

## Recorded dev1 validation

The revised image includes the progress-screen URL fix from [Core run 36889581891](https://github.com/drHouse-gif/core/actions/runs/36889581891), which passed 772 tests and 558 snapshots. The first VM UI test exposed that the frontend reads `config.progress.remote_connect`, while the URL instructions were under `config.step.remote_connect.description`. The fix moves the instructions and URL placeholder to the displayed progress text and renders the URL as code for copying. The image check now verifies the generated English progress translation includes that placeholder.

[Revised image run 36890779081](https://github.com/drHouse-gif/Shelly-Remote-WebSocket-for-Home-Assistant/actions/runs/36890779081) passed the source and translation checks, consistency check for 149 installed packages and fresh boot to `RUNNING` with the native remote choice. It published `2026.11.0.dev1` with digest:

```text
sha256:126d50ab8a8fa0a80a076c2e7f8c0e7339a7b3bf846eb226f40c0eb8dd315bed
```

Anonymous registry access to this revised tag was independently verified with HTTP 200 and this exact digest. On 2026-10-01, the operator reported completing the revised-image update and successful Pro 3EM pairing. The native Shelly integration screenshot shows 36 entities across the main device and three phases. A new `ha core info` result was not captured at that milestone; the later `dev2` installation and operator recovery tests are recorded above.

The same VM displays the Supervisor repair `home_assistant_core_custom_image`, consistent with running this custom Core image. Record it as a development-image warning; continue testing on the dedicated VM. See [TESTING.md](TESTING.md) for the observed physical milestone and outstanding checks.

## Recorded first-image validation

On 2026-10-01, [build run 36882493791](https://github.com/drHouse-gif/Shelly-Remote-WebSocket-for-Home-Assistant/actions/runs/36882493791) for the first `2026.11.0.dev0` image, pinned to Core `726a64d`, passed the source checks, consistency check for 149 installed packages, fresh boot to `RUNNING` and native remote Shelly form check. That image was pushed with digest:

```text
sha256:d430b68ac70b5597d79884e61d88a4c568e034358ec62f6bc5e5ddc6a0c52908
```

Anonymous registry pull was independently verified with HTTP 200 and this exact digest. On 2026-10-01, installation on the dedicated HAOS 18.3 `amd64` / `qemux86-64` test VM also completed: after a full backup, `ha core options` and `ha core update` returned success, and `ha core info` showed the custom image and version `2026.11.0.dev0`, replacing the recorded `2026.9.4` image.

The operator's terminal and UI screenshots confirmed installation and opening the native flow on that VM. The Shelly screenshot identified a Pro 3EM on firmware 1.7.5. This first-image result preceded the URL display fix and the revised-image physical pairing report above.

## Build and checks

The feature branch's [image workflow](.github/workflows/haos-image.yml) checks out both commits explicitly. It resolves the official Core base `2026.07.0` to its digest and records that digest, source hashes and preinstalled integration dependencies in the build provenance artifact. It installs Core, the fork library, the default-config dependency closure, Shelly and HAOS/Cloud dependencies; other integration requirements can still be installed normally by HA.

The service uses `--skip-pip-packages aioshelly`. The fork's package version is `0.0.0`, so without this development override HA would replace it with the manifest's published aioshelly version. No upstream manifest or application source is changed by this packaging.

Before publication, CI verifies installed source hashes, checks package dependencies, boots a fresh configuration to `RUNNING` and opens the native Shelly config flow to verify the remote choice exists. CI's temporary onboarding user and tokens stay in the smoke configuration; they are not baked into the image or uploaded as artifacts. The resulting image is published only after these checks pass. English translations are generated from the pinned source.

This startup smoke check does not validate a physical Shelly, HAOS Supervisor deployment, certificates or remote networking. Continue with [TESTING.md](TESTING.md) after installation. Use only an image whose workflow completed successfully.

## Install on the isolated HAOS VM

1. Install and start the official **Terminal & SSH** app, then open its web terminal.
2. Record `ha core info`, including the original image and version. Create a full checkpoint **before** changing the image:

   ```sh
   ha backups new --name before-shelly-remote-test
   ```

   Save the returned backup slug and download the checkpoint from HA's backup UI. The checkpoint contains HA secrets; keep it private.

3. Verify the image workflow is green. Anonymous pull of the recorded image has been checked; registry login is not required. The image contains public fork source and build metadata, not your HA configuration or pairing credentials.
4. Switch the Core image and install the development version. Run each command separately and wait for it to complete:

   ```sh
   ha core options --image ghcr.io/drhouse-gif/shelly-remote-haos-qemux86-64
   ```

   ```sh
   ha core update --version 2026.11.0.dev2
   ```

   HA restarts during the update. Leave the existing HTTP port and external URL settings in place.

5. Check `ha core info`: it should show the custom image and image build version `2026.11.0.dev2`. HA's UI/API still reports the pinned Core package version `2026.11.0.dev0`. Open HA, add the **Shelly** integration and verify the remote connection option appears. The library requirement skip warning is expected for this development image.
6. Validate TLS and HA/proxy log protection before using a real pairing URL. Then follow the Internet-separated test procedure in TESTING.md. Do not paste the generated URL into chat, screenshots or shell commands.

## Return to the checkpoint

The development Core can migrate stored configuration or the recorder database. Restore the full pre-test checkpoint when returning to an older Core; changing only the image is not a complete rollback.

In the Terminal & SSH app, reset the image override and restore the saved backup slug:

```sh
ha core options --image ""
ha backups restore YOUR_PRE_TEST_BACKUP_SLUG
```

The empty image option selects HAOS's default image for this machine. The full checkpoint restores the recorded Core version, configuration and apps. Check `ha core info` after restoration against the original values. Any devices still holding a test pairing URL must have that outbound configuration removed or replaced locally.

Primary sources: [Core image option](https://github.com/home-assistant/cli/blob/master/cmd/core_options.go), [Core update](https://github.com/home-assistant/cli/blob/master/cmd/core_update.go), [backup creation](https://github.com/home-assistant/cli/blob/master/cmd/backups_new.go), [backup restore](https://github.com/home-assistant/cli/blob/master/cmd/backups_restore.go), [Terminal & SSH](https://github.com/home-assistant/addons/blob/master/ssh/DOCS.md), [GHCR visibility](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry).
