# Upstream Dependencies

This records the maintained forks, external build support, and exact
local-manifest inputs for LineageOS 23.2 / Android 16 as of July 15, 2026.
Android 15 release `1755162498` remains the accepted working baseline, but an
Android 16-to-15 downgrade has not been validated as a safe rollback.

## Maintained Repositories

| Repo | Active role | Branch | Current integration revision | Upstream |
| --- | --- | --- | --- | --- |
| `MP01-LineageGSI` | External build driver, product integration, patches, release inputs, transcript harness, and MP01 vendor content | `lineage-23.2` | final logical/formal head `c88e039992760ada12f1df874453c2243d784862`, tree `9d4bfca308b640e2b28f58f3502af40a7adf0c21`; formal harness unit `16aa5f8d47503debba428c01547aba91232f28b6`; strict patch unit `11bdbbdb9a9789b00b6dfba986bfca4c72735cc7`; no-kernel header unit `cb9eab69b9500fa194a7e4adc72f110656ee2cf2`; partner byte-preservation unit `c88e039992760ada12f1df874453c2243d784862`; tree-equivalent publication squash `ae9299f0819ca9bd564859e96bce965007381e54`, staged as `20260715-111324-MP01-LineageGSI-ae9299f0819c` | `MisterZtr/LineageOS_gsi` |
| `treble_manifest` | Exact non-platform Android source graph | `lineage-23.2` | `fb1e1f76d353591caa2d991a3f8d92266249fe8e` | `MisterZtr/treble_manifest` |
| `device_phh_treble` | PHH/TrebleDroid GSI target support | `android-16.0` | manifest pin `39ba82ef89ff5bf6b22ca8f147dbf317bffa20ed` | `TrebleDroid/device_phh_treble` |
| `vendor_hardware_overlay` | Runtime resource overlays | `lineage-23.2` | `7cf73a0094e6448e0bb830fea996715fbd2fffc3` | `TrebleDroid/vendor_hardware_overlay` |
| `treble_app` | Privileged TrebleDroid settings and preset application | `master` | manifest and dependency-verification pin `9d8a6771d94b7985f515b41bd280f7bdb4554037` | `TrebleDroid/treble_app` |
| `treble_presets` | Validated MP01 device preset | `master` | `5891dba9621542b297acd761dbf3fe98d841c214` | `TrebleDroid/treble_presets` |
| `finqwerty` | Historical Android 15 source only | `master` | staged mitigation `a60a78160be024173c7eac11acc45e4db4e693f0`; local key deletion `1b712b2a725d43233c03d768f4df6d4ef2e18883` is publication-blocked | `vbbot/finqwerty` |
| `Phone` | Possible future Fossify integration | `main` | `aa1bde9909effc5a5b7a3f3d528e15c4377a5b54` | `FossifyOrg/Phone` |
| `Messages` | Possible future Fossify integration | `main` | `9cbf3e46042bfaef02c7b28283c6e5ec50b42ec7` | `FossifyOrg/Messages` |
| `MP01-OS` | Coordination, state, safety, and release documentation | `main` | active documentation tree | none |

`MP01-LineageGSI` is not a project in the local manifest. The build uses it as
an external support checkout and records its revision in build-info. Importing
it through both repo sync and the build driver previously created duplicate
modules, so the build now rejects that source shape.

FinQwerty is not an Android 16 manifest, download, product, or package input.
The MP01 keyboard map is system-owned in `MP01-LineageGSI`. Its former release
keystore is exposed in history and compromised; any future FinQwerty release
requires a new signing identity outside git. That application key is unrelated
to Android OS platform or APEX keys and provides no signer-compatibility
evidence. Mitigation commit `a60a78160be024173c7eac11acc45e4db4e693f0`
disables signing/publication and is staged. Local commit
`1b712b2a725d43233c03d768f4df6d4ef2e18883` deletes the binary key, but current
qpublish policy rejects binary diffs; publishing that deletion needs an approved
qadmin/`git-publish` mechanism.

## Exact Manifest Dependencies

`treble_manifest` commit
`fb1e1f76d353591caa2d991a3f8d92266249fe8e` is a single bounded patch-chain
unit and declares exactly 14 input projects:

| Path | Project | Revision |
| --- | --- | --- |
| `device/phh/treble` | `TrebleDroid/device_phh_treble` | `39ba82ef89ff5bf6b22ca8f147dbf317bffa20ed` |
| `treble_app` | `MP01-LineageOS/treble_app` | `9d8a6771d94b7985f515b41bd280f7bdb4554037` |
| `vendor/hardware_overlay` | `MP01-LineageOS/vendor_hardware_overlay` | `7cf73a0094e6448e0bb830fea996715fbd2fffc3` |
| `vendor/vndk-tests` | `phhusson/vendor_vndk-tests` | `533390a1d6bc98d86de6b9aab56825c1f03fddcb` |
| `vendor/interfaces` | `TrebleDroid/vendor_interfaces` | `a2271d260e226e8de5cb1e8c15a229dc90c007dd` |
| `vendor/lptools` | `phhusson/vendor_lptools` | `c8be7de57b80eab61a6f94ec86464a01fb9056f2` |
| `vendor/magisk` | `phhusson/vendor_magisk` | `d8056f8032a0f60f365ddfe5e9fccd7eaf3a655d` |
| `packages/apps/QcRilAm` | `AndyCGYan/android_packages_apps_QcRilAm` | `dc599b67cc1e7e9a62ca15eef605e3b2546d0d42` |
| `prebuilts/vndk/v28` | `naz664/prebuilts_vndk_v28` | `507526a5b27a170aea338ff747c7d6ecc9bb91bb` |
| `prebuilts/vndk/v29` | `platform/prebuilts/vndk/v29` | `bef5d37dda9360940964f097d612c8032e140961` |
| `prebuilts/vndk/v30` | `platform/prebuilts/vndk/v30` | `5f9884aa352825291757dfd6694b874ad8c1805e` |
| `vendor/gapps` | `MindTheGapps/vendor_gapps` | `f8cdcffc2fb9181b8cc5a9b02d4b5908b64e5cdd` |
| `vendor/partner_gms` | `lineageos4microg/android_vendor_partner_gms` | `4b3b48033245800142045ce78038166f8aff6b01` |
| `hardware/oplus` | `LineageOS/android_hardware_oplus` | `e48aa2ba72191c1d2f9d92ee5bbc26b9f60437f6` |

The microG product removes proprietary `vendor/gapps`, so the normalized
effective manifest contains 13 of these custom projects. The resolved
`repo manifest -r` remains the authoritative record of the complete LineageOS
platform plus those 13 exact effective custom projects.

## Integration Contracts

- The external GSI helper applies exactly nine patches to pinned TrebleApp
  source and requires the resulting prebuilt to remain unsigned. It hashes every
  non-signature ZIP entry deterministically, retains `classes.dex` as a focused
  subcheck, replaces the stale overlay prebuilt, and requires both the installed
  and target-files APKs to have exactly one platform-certificate signer and
  identical non-signature content.
- TrebleApp head `9d8a6771d94b7985f515b41bd280f7bdb4554037` verifies the
  Gradle 7.5 distribution and resolved dependencies. CI unit
  `cee22d352a9c022d43e5384a29646898a94e45cd` makes the workflow build-only,
  read-only, and commit-pinned.
- Preset commit `5891dba9621542b297acd761dbf3fe98d841c214` validates every
  preset key and value type against TrebleApp definitions and excludes
  click-only actions.
- Overlay commit `7cf73a0094e6448e0bb830fea996715fbd2fffc3` validates MP01
  resources against exact LineageOS framework commit
  `46fd4b1f8d25b92540048c96ddc625b4ebeb6d60` and builds all overlays with API
  36. Its workflow uses read-only permissions and commit-pinned actions.
- The immutable source launcher is official `repo-2.65`, SHA256
  `1211b57b57e4122a9c546295a59b37d24068f1164d0e87bef096d5323c413e4f`.
  It initializes official git-repo tag `v2.65` and verifies implementation
  commit `35bbf701d04de5c6a71937279bc3d16f6ce36808`.
- Downloaded partner APKs are pinned by exact version, URL, SHA256, and signing
  certificate where applicable. inkOS and preset content are pinned by hash.
- The presigned-partner patch has SHA256
  `146aa1a9307452217e087d818028bb158e8adf0a5a3a52e6bcaebe0665e7a1bf`.
  It transforms `vendor/partner_gms` base commit/tree
  `4b3b48033245800142045ce78038166f8aff6b01` /
  `3c554b8fabffd2bdd0727aac770e403d9fec0505` into prepared commit/tree
  `67e492737184fe9584750e07ad4c0ecfb40af67e` /
  `06afb50166f27672b02c7b168b24de0bf30f8f21`. The build requires exactly one
  byte-preserving Make definition per pinned partner module, rejects competing
  Blueprint definitions, and verifies source/installed/target-files byte
  identity plus zip alignment before publication.
- Source preparation rejects a duplicate GSI tree and removes only the bounded
  stale vendor paths owned by the support checkout.
- Soong gives Metalava a `6114m` Java heap. Hosts with no more than 16 GiB of
  memory must use `MP01_MAKE_JOBS=1`; the combined Ninja high-memory pool is
  fixed at and verified as depth `1`. The verifier is hash-checked from the same
  retained `.mp01` copy before and after primary make; that copy survives
  support-tree cleanup. Build-info records the host-memory, jobs, pool, heap,
  Soong/JDK, and verifier provenance.
- The recorded `4bb063e` run stopped on Blueprint's provider-mutation invariant
  during Soong graph generation before Ninja and did not exercise the target
  Metalava action. The synchronous pre/post-write diagnostic subsequently
  completed the full graph with both checks passing; its log SHA256 is
  `dd23b844f916e0a35268a4654978b378e2b57f3369db643c832578bad4b9e4d8`.
  Commit `4e94263d8871e26b32f8927f6f1d820a830a0a19` serializes the existing
  fail-closed check after output writing and caching. Head `3feebeb` adds
  repository-owned workspace and build-state policy. Its formal run failed
  closed before graph generation when lunch selected the expected
  `TARGET_PRODUCT` but placed output under `generic_arm64`; `c890b40` pins that
  actual product output name. Its formal run passed the product-output and
  TrebleApp checks and completed bootstrap `284/284`, then failed during Soong
  graph/main Ninja generation because an absolute host-JAR path was outside the
  source directory contract. Head `6129977` exposes Android's expected relative
  `OUT_DIR` while independently verifying its canonical absolute containment.
  That run was intentionally stopped at action `6632/153795` after review found
  the ad hoc wrapper did not preserve `tee` failure status; it is evidence only.
  Commit `16aa5f8` adds the repository-owned contract-v1 formal transcript
  harness, with harness/helper SHA256 values
  `938cc2842ca860704f727cfbd4f890227ccb93d44387f64e6be3f704b3403204` /
  `cf8a04c7d334caeb177750b7f2e9c2855e2835e231f9e45d21933619fd9ead07`.
  Head `3d1bfa4` also removes current test-key device commands from the GSI
  `README.md`, `ROUGHGUIDE.md`, and `vendor/MP01_services/README.md`. Its formal
  run exposed the old patch-runner false-positive behavior and later failed on
  no-kernel generated headers; incomplete-log SHA256
  `6006d29d4a5f6ec348c3258985bbee2898abfd07bb74a3e042b05811a216dcc1`.
  Commit `11bdbbd` makes already-applied detection exact, and `cb9eab6` handles
  no-kernel generated headers. The `cb9eab6` run then failed on the e-ink
  daemon's stale fortify override; incomplete-log SHA256
  `46bb6fd0eff47ffb14229477afb38c8e25b0ae6f9bdbd9b4d09332b4d36e0d8a`.
  Head `2fd5dec` removes that override and completes the primary Android build,
  but its post-build signer audit fails because the privileged-prebuilt Make path
  rewrote `GmsCore`, `FakeStore`, and `FDroidPrivilegedExtension`, invalidating
  APK signing blocks. The retained staging log SHA256 is
  `6093a4960140dd5bdd29185cf7788f8c16e8f530f9a260afcc910b7a49e55b8a`;
  no final log or candidate was published. Head `c88e039`, tree
  `9d4bfca308b640e2b28f58f3502af40a7adf0c21`, adds the byte-preservation
  policy. All 143 GSI tests pass. Its first invocation stopped before source
  preparation on that run's configured 250 GiB disk-space preflight; retained
  incomplete-log
  SHA256 `9e51db5870ec7bc14ecdfd953ca509a617181434169987e89db950f39aa81f82`.
  The formal rerun completed Android in `08:47:27`; final log SHA256 is
  `87681b4c33c0d9584cb5067b223c2f92219544dfafd1147017511d49d0f25d3a`.
  All 47 auditor unit tests passed. The retained independent audit returned
  `PASS_AUDIT_ONLY_NOT_FOR_IN_PLACE_FLASH`, verified all five partner APKs and
  the 14-entry inventory, and recorded `INCOMPATIBLE` /
  `NOT_FOR_IN_PLACE_FLASH` for 616 APKs, 44 APEXes, 750 incompatibilities, and
  0 warnings. A clean rebuild on verified storage is still required for release
  provenance; this unsigned test-key artifact is never flash eligible.
- The target is a system-image-only GSI with `TARGET_NO_KERNEL=true`. Despite
  requested enforcement, its Make warning means the kernel inputs to build-time
  `checkvintf` and the OTA kernel metadata are omitted, not passed, and does not
  authorize OTA packaging. Exact-device `VtsTrebleVintfTest`
  `SystemVendorTest.KernelCompatibility` remains pending; OTA publication is
  disabled.
- Before inventory, TrebleApp verification, `system.img` extraction, hashing, or
  publication, the build makes one private read-only target-files snapshot and
  uses only that snapshot for every downstream operation. The pre-publication
  signer gate compares actual APK and APEX container/payload identities with the
  complete pinned baseline manifest, SHA256
  `0e0313015d4bba28f8fe85d91498d060a7c525d81980f3f100efeb7f3628dd03`.
  It covers 222 APK paths for 221 packages and all 33 baseline APEX identities.
  Release mode requires verifier exit `0` and compatibility; explicit
  `test-key-audit` mode accepts only exit `3` plus
  `NOT_FOR_IN_PLACE_FLASH`. Other outcomes fail closed, and build-info embeds
  the actual signer manifest and complete evidence.
- The current test-key platform, release/default, shared, media, and
  network-stack source certificate classes all differ from the baseline. Source
  identities are an early warning only; the snapshot comparison above is the
  authoritative candidate gate.
- The e-ink command stream, delivery failure propagation, system keymap, and
  focused service/SELinux gates pass before the full Android artifact gate.
- Phone and Messages are not active image inputs. Adding them requires explicit
  product changes and MP01 default-app, e-ink, call, SMS, and MMS testing.

## Maintenance Rules

- Update coordinated TrebleDroid components together only when their shared
  runtime contracts remain validated.
- Any manifest change requires a new exact revision, source-preparation gate,
  full Android build, artifact audit, and MP01 hardware test.
- Any external GSI support change must be recorded in build-info even though it
  does not appear in the resolved manifest.
- TrebleApp provenance is embedded in build-info; it is not a separately
  published artifact.
- Commit locally and stage through qpublish. Publication belongs to
  `git-publish`; do not push from the development qube.
- Retain resolved source, checksums, build logs, and candidate reports before
  signing or OTA work begins.

## Current Qpublish State

- `treble_app` at `9d8a6771d94b7985f515b41bd280f7bdb4554037` is staged as
  `20260710-095532-treble_app-9d8a6771d94b`; only its predecessor is currently
  upstream.
- `treble_manifest` at `fb1e1f76d353591caa2d991a3f8d92266249fe8e` is staged
  as `20260710-095546-treble_manifest-fb1e1f76d353`; only its predecessor is
  currently upstream.
- Overlay `7cf73a0094e6448e0bb830fea996715fbd2fffc3` is staged for the
  existing `lineage-23.2` target as
  `20260710-090001-vendor_hardware_overlay-7cf73a0094e6`; do not restage it.
- Presets `5891dba9621542b297acd761dbf3fe98d841c214` is staged as
  `20260710-090043-treble_presets-5891dba96215`; do not restage it.
- FinQwerty mitigation `a60a78160be024173c7eac11acc45e4db4e693f0` is
  staged as `20260710-090346-finqwerty-a60a78160be0`. Local deletion commit
  `1b712b2a725d43233c03d768f4df6d4ef2e18883` remains publication-blocked
  because current qpublish policy rejects the keystore binary deletion.
- Tree-equivalent GSI squash `ae9299f0819ca9bd564859e96bce965007381e54`
  is staged as `20260715-111324-MP01-LineageGSI-ae9299f0819c`, superseding its
  June submission. MP01-OS uses its June submission as the explicit predecessor
  when staging the documentation/auditor chain; inspect the outbox for current
  submission state.

Always run `qpublish workspace-status` and inspect outbox/feedback before any
`qstage`; state may advance while review is in progress.

See [`upstream-update-policy.md`](upstream-update-policy.md) for update and
rollback requirements.
