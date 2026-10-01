# HAOS development image

This image runs the tested native Core integration on an isolated HAOS test VM. It targets `amd64` / `qemux86-64`, with Core `726a64d62c7a95bb27cec5a72163df3e1c2d822a` and aioshelly `74751fcb876cc5fbd993721da765d40cd5b5b750`. It is a development build, not an official HA release.

The image version is `2026.11.0.dev0`, matching the pinned Core source. The container image name is:

```text
ghcr.io/drhouse-gif/shelly-remote-haos-qemux86-64:2026.11.0.dev0
```

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

3. Verify the image workflow is green. If its summary says anonymous pull is unavailable, open your GitHub profile's **Packages** → **shelly-remote-haos-qemux86-64** → **Package settings** and change the package visibility to **Public**. GHCR packages start private by default. The image contains public fork source and build metadata, not your HA configuration or pairing credentials.
4. Switch the Core image and install the development version:

   ```sh
   ha core options --image ghcr.io/drhouse-gif/shelly-remote-haos-qemux86-64
   ha core update --version 2026.11.0.dev0
   ```

   HA restarts during the update. Leave the existing HTTP port and external URL settings in place.

5. Check `ha core info`: it should show the custom image and `2026.11.0.dev0`. Open HA, add the **Shelly** integration and verify the remote connection option appears. The library requirement skip warning is expected for this development image.
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
