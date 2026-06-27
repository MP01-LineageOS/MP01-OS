# MP01 LineageOS Action Items

This is the working action list from the June 19, 2026 inventory of the
LineageOS 23.2 update. Keep it ordered by release risk unless new findings
change the priority.

## 2026-06-26 qpublish snapshot

This snapshot records the state after restoring validation tools, syncing the
qpublish-rewritten public heads, and staging the remaining GSI 23.2 work.

Active staged submissions:

- `MP01-LineageGSI` creates `lineage-23.2` from `15` at squashed staging commit
  `fef5faf` (`20260626-220521-MP01-LineageGSI-fef5faf729b7`,
  `patch-chain-v1`, one unit). The squashed staging tree matches local
  `lineage-23.2` / `mp01-23.2-release-gate` at `715bcf7`.

Published or merged qpublish work:

- `treble_manifest -> lineage-23.2` is published at `origin/lineage-23.2`
  `f6b1c40`.
- `vendor_hardware_overlay -> lineage-23.2` is published at
  `origin/lineage-23.2` `2f13b59`.
- `treble_app -> master` is merged at `origin/master` `7521ab9`.
- `MP01-OS -> main` is merged at `origin/main` `92b30b9`.

Cleanup already done:

- Synced `MP01-OS`, `treble_app`, and `treble_manifest` to the public
  qpublish-rewritten heads.
- Cancelled stale wrong-target `needs_changes` submissions:
  - `20260619-124539-MP01-LineageGSI-58f8d27e85c1`
  - `20260619-124221-treble_manifest-19c2a81830fc`
- Superseded rejected GSI submission
  `20260626-213616-MP01-LineageGSI-d89a481eaccb` after qpublish feedback
  reported rename/copy detection in the base-to-head range.
- Left `vendor_hardware_overlay` checked out on `lineage-23.2`; its tree
  matches `origin/lineage-23.2`.

Known blockers to address next:

- Wait for review/publish of
  `20260626-220521-MP01-LineageGSI-fef5faf729b7`.
- After GSI publish, sync local branches and run a fresh LineageOS 23.2
  source sync/build from the published branch heads.

## 1. Close the release reproducibility gap

The current LineageOS 23.2 integration is split across local branch heads that
are not all available from the registered `MP01-LineageOS` repositories yet.
Stage the committed branch heads through the qpublish flow so a clean checkout
can reproduce the active build inputs without depending on local-only state.

Current branch heads:

- `MP01-LineageGSI`: local `mp01-23.2-release-gate` at `715bcf7`; staged via
  squashed commit `fef5faf`, targeting `lineage-23.2`.
- `treble_manifest`: `origin/lineage-23.2` at `f6b1c40`.
- `vendor_hardware_overlay`: `origin/lineage-23.2` at `2f13b59`; local
  `lineage-23.2` has an equivalent tree.
- `MP01-OS`: `origin/main` at `92b30b9`.
- `treble_app`: `origin/master` at `7521ab9`.

Definition of done:

- Relevant repos are clean before staging.
- `qstage` submissions exist for each branch head needed to reproduce the
  LineageOS 23.2 build.
- The active build result is recorded against the exact staged commits.
- A fresh sync from the staged branches can resolve every MP01 repo named in
  the manifest.

Progress:

- As of 2026-06-26, every needed 23.2 branch head has either been published or
  staged through qpublish.
- `MP01-LineageGSI -> lineage-23.2` is the only active staged submission still
  awaiting review/publish, restaged as
  `20260626-220521-MP01-LineageGSI-fef5faf729b7` after qpublish rejected the
  previous `d89a481` staging artifact for rename/copy detection.
- The GSI staging branch is intentionally squashed because direct patch-chain
  staging still sees binary markers in intermediate history.
- The new VNDK prebuilt patch payloads were externalized as base64 text under
  `patches/binary-payloads`, and `patches/apply-patches.sh` materializes them
  before applying the text patch.

Open decision:

- Continue using create-target `lineage-23.2` submissions for the 23.2 branch
  heads. Do not publish the Android 16/LineageOS 23.2 content onto the existing
  Android 15 default branches.

## 2. Fix local build tooling blockers

Install or provide the required build validation tools in the development qube:
Java/JDK, `openssl`, `keytool`, and `xmlstarlet`. Re-run Gradle, release input
verification, and overlay tests after the tools are available.

Progress:

- 2026-06-26 recheck: installed `ripgrep`, `openssl`, `xmlstarlet`, and
  `java-21-openjdk-devel` from Fedora repositories. `qpublish workspace-status`
  reports no missing tools.
- Installed Fedora packages for OpenJDK 21, `openssl`, and `xmlstarlet` in the
  development qube. This provides `java`, `javac`, `keytool`, `openssl`, and
  `xmlstarlet`.
- Installed Google Android SDK command-line tools under
  `~/.local/share/android-sdk`, accepted the Android SDK license with operator
  approval, and installed `platforms;android-34`, `build-tools;34.0.0`, and
  `platform-tools`.
- Installed checksum-verified Eclipse Temurin JDK 17 under
  `~/.local/share/jdks/temurin-17` for Gradle/AGP 8.2 validation. Fedora's JDK
  21 fails the Android JDK image transform with `ModuleTarget is malformed:
  platformString missing delimiter: android`.
- `bash scripts/verify-release-inputs.sh` now passes in `MP01-LineageGSI`.
- `bash tests/tests.sh` now runs in `vendor_hardware_overlay` and reports real
  overlay failures instead of missing-tool noise:
  - `Minimal/MP01/AndroidManifest.xml` priority 21 conflicts with another
    manifest.
  - `overlay.mk` entries are not sorted.
  - `overlay.mk` is missing the required trailing empty line.
- `JAVA_HOME=~/.local/share/jdks/temurin-17 ANDROID_HOME=~/.local/share/android-sdk
  ANDROID_SDK_ROOT=~/.local/share/android-sdk ./gradlew --no-daemon
  assembleDebug` passes for `MP01_accessibility_service`.
- 2026-06-26 validation passed:
  - `bash scripts/verify-release-inputs.sh` in `MP01-LineageGSI`
  - shell syntax checks for the GSI build and patch scripts
  - `bash tests/tests.sh` in `vendor_hardware_overlay`
  - host C syntax check for `MP01_eink_daemon/eink_daemon.c` with a temporary
    Android log stub

## 3. Secure the e-ink daemon boundary

The daemon previously accepted commands over an abstract Unix socket without
checking peer credentials. Keep explicit client authorization and a dedicated
SELinux domain in the staged 23.2 branch so direct socket access cannot bypass
the permissioned e-ink automation API.

Progress:

- `MP01-LineageGSI` commit `eaee4bb` adds `SO_PEERCRED` checks and restricts
  daemon socket clients to root/system peers.
- The same commit keeps daemon startup at `sys.boot_completed=1` and includes
  the keyboard backlight node in startup clamp success/retry logic.

## 4. Fix SELinux packaging for MP01 services

The MP01 services makefile previously included only the public policy
directory, and the e-ink daemon binary was labeled as `phhsu_exec`. Keep the
intended policy packaging and MP01-specific labels in the staged 23.2 branch.

Progress:

- `MP01-LineageGSI` commit `eaee4bb` adds an `MP01_eink_server` domain and
  `MP01_eink_server_exec` file label, and includes both public and private
  MP01 service policy directories in `BOARD_VENDOR_SEPOLICY_DIRS`.

## 5. Fix the accessibility service compile risk

`SystemSettingsManager.kt` has no package declaration while nearby Kotlin code
imports package-local classes. Confirm with a JDK-backed build and fix the
package/import structure.

Progress:

- The JDK-backed Gradle debug build now passes, so the suspected package/import
  issue is not a current compile blocker. Leave this item for source cleanup
  only if the Android/Soong build later disagrees.

## 6. Fix MP01 preset validation

The MP01 preset uses `key_misc_mediatek_ged_kp`, while TrebleApp defines
`key_misc_mediatek_ged_kpi`. Correct the preset and extend tests so unknown
preference keys fail CI.

## 7. Update overlay workflow and hygiene

Move overlay CI from the old `pie` target to the LineageOS 23.2 branch, update
workflow action versions, and fix the local overlay hygiene failures for
`overlay.mk` ordering and trailing newline handling.

Progress:

- `treble_app` workflow updates are merged at `origin/master` `7521ab9`.
- `vendor_hardware_overlay -> lineage-23.2` is published at
  `origin/lineage-23.2` `2f13b59`.
- `bash tests/tests.sh` passes in `vendor_hardware_overlay`; remaining output
  is inherited warning noise from unrelated overlays.

## 8. Revisit MP01 overlay assumptions

Refresh Android 15-era comments and unresolved TODOs in the MP01 overlay. Check
IMS, VT, WFC, and recents component behavior against the actual LineageOS 23.2
build.

## 9. Quarantine or port signing

`sign.sh` still assumes release keys under `~/.android-certs`. Either port the
signing path for LineageOS 23.2 or move it out of the active release path until
signed artifacts are intentionally supported again.

## 10. Resolve artifact metadata mismatch

The current `images/` directory contains an unsigned image and tarball but no
matching checksum, build-info, or resolved-manifest metadata. Confirm whether
the active build now emits this metadata and document the exact result.

## 11. Run the device gate

After the active build completes, perform a system-only no-wipe flash and run
the hardware test matrix: boot, e-ink refresh modes, keyboard/backlight,
brightness boot clamp, lockscreen clear, Wi-Fi, Bluetooth, suspend/resume,
calls, SMS, Verizon IMS/VoLTE, F-Droid, microG, and permissioned e-ink
automation.
