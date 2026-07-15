# MP01 LineageOS Action Items

This is the working action list for the LineageOS 23.2 / Android 16 migration as
of July 15, 2026. The known source, Android-output, and presigned-partner-APK
blockers are fixed. The formal build from logical GSI head
`c88e039992760ada12f1df874453c2243d784862` and the retained independent audit
completed with `PASS_AUDIT_ONLY_NOT_FOR_IN_PLACE_FLASH`. The unsigned test-key
artifact is software-audit-only and never flash eligible.

## Completed Software Gates

- `treble_manifest` commit
  `fb1e1f76d353591caa2d991a3f8d92266249fe8e` defines 14 input projects,
  each at an exact commit. The microG override removes `vendor/gapps`, so the
  normalized effective manifest has 13 custom projects and no `LineageOS_gsi`.
- `MP01-LineageGSI` is an external build-support checkout, not a repo-manifest
  project. Source preparation rejects a duplicate `LineageOS_gsi` tree and
  removes stale copied vendor inputs before importing the current support tree.
- The failed `4bb063e` build's old source-preparation runner reported that its
  cached-local reset, patch stack, Launcher3 port, SetupWizard changes, and
  duplicate-tree checks passed. Later review proved that the old GNU reverse
  dry-run could falsely classify a forward-applicable patch as already applied,
  so this historical report is not evidence that every patch was present. Its
  source objects came from an earlier network-populated depth-bounded cache; this
  run did not claim a new network sync.
- GSI commit `ac3f97f43eafbacf4f222a6915429fae9d7c2a69` reached the Android
  compile after the old runner reported source preparation passed. That report
  is not proof of a complete patch stack. The build failed at the
  `api-stubs-docs-non-updatable` Metalava action with Java heap exhaustion. Its
  retained log is
  `.android-build/logs/mp01-final-ac3f97f-20260710T103529Z.log`, SHA256
  `e790c3d04352a436810b4f747ec76aed8763c5052d93f937f4544a8513f71e30`.
  It is failed-build evidence, not a candidate.
- The later full build used GSI commit
  `4bb063e28116af3b4f4263c4cf6eed00b3829961`. It still performs full cleanup,
  exact-head verification, and patch application. Its retained log path is
  `.android-build/logs/mp01-final-4bb063e28116-20260710T150914Z.log`, SHA256
  `e70d2d4655faaecbe6907a5acecb2e1c52fae0e9e42d33fe9ef441686e2a5c8b`.
  It stopped during Soong graph generation on Blueprint's
  `provider ... was modified after being set` invariant, before Ninja or the
  target Metalava action and before target-files/artifact packaging. The
  isolated replay and focused policy tests validate the heap remediation; this
  build did not exercise it. The provider failure was not reported as a
  filesystem-I/O failure, and it produced no candidate.
- The retained diagnostic
  `.android-build/logs/mp01-provider-pre-post-20260710T132726EDT.log`, SHA256
  `dd23b844f916e0a35268a4654978b378e2b57f3369db643c832578bad4b9e4d8`,
  completed the full Soong graph with synchronous checks both before and after
  `WriteBuildFile` and no provider error. Compilation was intentionally stopped
  at 3% because the direct command omitted `USE_CCACHE` and would serially
  rebuild roughly 170,000 actions.
- Commit `4e94263d8871e26b32f8927f6f1d820a830a0a19` commits a command-only
  Blueprint patch that retains fail-closed validation after Ninja write, flush,
  and action caching. The patch SHA256 is
  `43cca96d3eb8d04a91a9b0637444889b62fe1a04a064910c68c2358e23326df1`.
  Its first formal invocation failed before source preparation because an
  external Codex workspace helper was unavailable. The retained log is
  `.android-build/logs/mp01-final-4e94263d8871-20260710T203839Z.log`, SHA256
  `2c09d82d450ee803f46fa179c3bfff8f2c2d1ba5ceb3e80d1774abbe29276b8b`.
- Head `3feebebfb20c6b424b05f4cbe5f1e72ca5b3e28f`, tree
  `0e4a1879b5ce602c9e8f3cd61f5699fbe025b4ac`, replaces that external helper
  with repository-owned, hash-checked workspace and build-state policy. Its
  formal run failed closed before graph generation because lunch reported
  `TARGET_PRODUCT=lineage_arm64_bmN4` but resolved the actual product output as
  `generic_arm64`. The retained log is
  `.android-build/logs/mp01-final-3feebebfb20c-20260710T220742Z.log`, SHA256
  `55157ea23dfa8795dbc84b512867eb40d7364a35caed1fa87f394d2f47809691`; no
  artifact was produced.
- Head `c890b4015a505bbce0ae09761f0054de24d3d6c0`, tree
  `871b1a1e59ee73e6fede1bbc1a7cbf69739c71d6`, pins the actual Android product
  output directory. Its formal run passed lunch/output and TrebleApp checks and
  completed bootstrap `284/284`, then failed during Soong graph/main Ninja-file
  generation at `platform_testing/Android.bp:255:1`: module
  `continuous_native_tests` rejected the absolute
  `out/host/linux-x86/framework/net-tests-utils-host-common.jar` path. Log
  `.android-build/logs/mp01-final-c890b4015a50-20260710T221230Z.log`, SHA256
  `bac623467a00c6ef1c321c3ea1d18ea1370fe023d427f2d74397dfa01a201468`;
  wrapper duration `00:51:49`, exit `1`. Main/product Ninja did not run;
  target-files, publication, and phone operations were not reached. No artifact,
  publication residue, I/O failure, or OOM evidence is present.
- Head `612997762d55364f14b4157f745dcab190dd468c`, tree
  `491273ae8e6909f4eaf3e30436263fd8ebd8c0ba`, supplies the relative `OUT_DIR`
  interface Android expects while retaining canonical absolute containment
  checks. Its build was intentionally stopped at action `6632/153795` after
  review found that the ad hoc wrapper ignored `tee` status. Evidence log
  `.android-build/logs/mp01-final-612997762d55-20260710T231231Z.log`, SHA256
  `8dd8aa7ad75d6c1ac60264612931228bbb6cb6f892ffbbf35f28a76422ad44f5`;
  `2026-07-10T23:12:31Z` to `2026-07-11T01:52:04Z`, duration `02:39:33`,
  intentional exit `141`. It produced no artifact or publication residue, and
  the log contains no kernel I/O or OOM failure evidence.
- Commit `16aa5f8d47503debba428c01547aba91232f28b6` adds the contract-v1
  fail-closed formal build harness. Harness/helper SHA256 values are
  `938cc2842ca860704f727cfbd4f890227ccb93d44387f64e6be3f704b3403204` /
  `cf8a04c7d334caeb177750b7f2e9c2855e2835e231f9e45d21933619fd9ead07`.
- The first contract-v1 run at
  `3d1bfa4f4be14857b21dde879ec9f9e64a401c60` exposed that patch-runner defect
  and later failed in `generated_kernel_includes`: the no-kernel GSI had no
  `headers_install` target. Its retained incomplete log is
  `.android-build/logs/mp01-final-3d1bfa4f4be1-20260711T024331Z-fd587786d599.log.incomplete`,
  SHA256
  `6006d29d4a5f6ec348c3258985bbee2898abfd07bb74a3e042b05811a216dcc1`.
  It produced no candidate.
- Commit `11bdbbdb9a9789b00b6dfba986bfca4c72735cc7` makes patch application
  fail closed: exact Git reverse checks determine already-applied state and GNU
  fallback application uses zero fuzz. Commit
  `cb9eab69b9500fa194a7e4adc72f110656ee2cf2`, tree
  `277564406d298e3a0283c7dbfd2a42010715b74a`, exports
  `TARGET_NO_KERNEL` to Soong and creates only an empty generated include root
  for no-kernel targets while preserving real-kernel header generation.
- The `cb9eab6` formal run passed generated-header generation and reached the
  MP01 e-ink daemon, then failed because its stale `_FORTIFY_SOURCE=2` flag
  conflicted with Android 16's toolchain-provided level 3. Its retained
  incomplete log is
  `.android-build/logs/mp01-final-cb9eab69b950-20260711T235938Z-90c3aa8cf054.log.incomplete`,
  SHA256
  `46bb6fd0eff47ffb14229477afb38c8e25b0ae6f9bdbd9b4d09332b4d36e0d8a`.
  It produced no candidate.
- Head `2fd5dec31b3b9c98060ed81d29a666b653df05fe`, tree
  `a931350da017ad19d18dd1b520c103c7ad417730`, removes the stale fortify
  override and blocks current test-key flashing workflows. The third contract-v1
  run, at this head, completed the primary Android build in `05:34:23`, then
  failed closed in the
  post-build signer audit because
  `SYSTEM/product/priv-app/FDroidPrivilegedExtension/FDroidPrivilegedExtension.apk`
  no longer had the v2/v3 signing blocks declared by its JAR signature. The
  retained staging log is
  `.android-build/logs/mp01-final-2fd5dec31b3b-20260712T200339Z-abcc08c367e1.log.incomplete`,
  SHA256
  `6093a4960140dd5bdd29185cf7788f8c16e8f530f9a260afcc910b7a49e55b8a`;
  no final log or candidate was published.
- Root-cause comparison showed Android's privileged-prebuilt path had
  uncompressed DEX content and realigned `GmsCore`, `FakeStore`, and
  `FDroidPrivilegedExtension`, changing their bytes and invalidating their APK
  signing blocks. `FDroid` and `GsfProxy` remained byte-identical; the signer
  gate stopped at the first invalid path.
- Final logical head `c88e039992760ada12f1df874453c2243d784862`, tree
  `9d4bfca308b640e2b28f58f3502af40a7adf0c21`, applies a bounded
  byte-preserving policy to all five `PRESIGNED` partner modules. The
  `vendor/partner_gms` base commit/tree
  `4b3b48033245800142045ce78038166f8aff6b01` /
  `3c554b8fabffd2bdd0727aac770e403d9fec0505` becomes prepared commit/tree
  `67e492737184fe9584750e07ad4c0ecfb40af67e` /
  `06afb50166f27672b02c7b168b24de0bf30f8f21`; the patch SHA256 is
  `146aa1a9307452217e087d818028bb158e8adf0a5a3a52e6bcaebe0665e7a1bf`.
  Source policy rejects competing definitions, and the artifact gate requires
  pinned, byte-identical, zip-aligned source, installed, and target-files APKs.
  All 143 GSI tests pass. An initial invocation stopped in the disk-space
  preflight before source preparation because 227 GiB was below that run's
  configured 250 GiB threshold. Its retained staging log
  `.android-build/logs/mp01-final-c88e03999276-20260715T055348Z-0b4bf6f7177e.log.incomplete`
  has SHA256
  `9e51db5870ec7bc14ecdfd953ca509a617181434169987e89db950f39aa81f82`;
  no artifact was produced. After space was reclaimed, the rerun started at
  epoch `1784095155`, completed Android in `08:47:27`, and published artifact
  epoch `1784126958`. Its complete contract-v1 log is
  `.android-build/logs/mp01-final-c88e03999276-20260715T055915Z-93cb550cc58a.log`,
  SHA256 `87681b4c33c0d9584cb5067b223c2f92219544dfafd1147017511d49d0f25d3a`.
  All 47 auditor unit tests passed. The retained independent audit returned
  `PASS_AUDIT_ONLY_NOT_FOR_IN_PLACE_FLASH`, verified all five partner APKs and
  all 14 required paths, and recorded `INCOMPATIBLE` /
  `NOT_FOR_IN_PLACE_FLASH` for 616 APKs and 44 APEXes, with 750
  incompatibilities and 0 warnings.
- The no-kernel Make warning does not prove kernel compatibility. This build is
  a system-image-only GSI, so kernel VINTF information is not put into an OTA
  package and that kernel check is skipped, not passed. Exact-device
  `VtsTrebleVintfTest` `SystemVendorTest.KernelCompatibility` remains pending;
  OTA publication remains disabled.
- The GSI `README.md`, `ROUGHGUIDE.md`, and
  `vendor/MP01_services/README.md` expose no current test-key device commands.
- Release-input verification passed for the immutable official `repo-2.65`
  launcher and the pinned F-Droid, F-Droid privileged extension, GmsCore,
  FakeStore `0.3.15.40226` (version code `84022630`, release tag
  `v0.3.15.250932`), GsfProxy, inkOS, and preset inputs.
- Source inkOS verification now requires package `app.inkos` and the enabled
  `com.github.gezimos.inkos.MainActivity` MAIN/HOME activity, not only a valid
  archive with the expected hash.
- TrebleApp commit `9d8a6771d94b7985f515b41bd280f7bdb4554037` is pinned by
  the manifest. Its first review unit,
  `cee22d352a9c022d43e5384a29646898a94e45cd`, limits CI to a build with
  read-only contents permission and commit-pinned actions. The head adds Gradle
  wrapper and dependency verification. A strict release build passed.
- The GSI helper applied exactly nine TrebleApp patches and verified their
  markers. The prebuilt is intentionally unsigned. A deterministic manifest
  covers every non-signature ZIP entry, with `classes.dex` retained as a focused
  subcheck. Installed and target-files APKs must each report exactly one signer
  matching the platform certificate and identical non-signature content.
- `treble_presets` commit
  `5891dba9621542b297acd761dbf3fe98d841c214` passes the preset key, type, and
  action contract tests.
- `vendor_hardware_overlay` commit
  `7cf73a0094e6448e0bb830fea996715fbd2fffc3` passes its API 36 build and
  Android 16 resource checks against framework commit
  `46fd4b1f8d25b92540048c96ddc625b4ebeb6d60`. Its workflow uses read-only
  permissions and commit-pinned actions.
- The e-ink command path uses a fresh socket for each command, reports delivery
  failures, and parses newline-delimited commands across split reads, CRLF,
  EOF, and overflow. An idle client now times out after five seconds and its
  partial frame is discarded. Host C and JVM tests pass.
- The MP01 keyboard is system-owned. Keymap preflight and host checks pass, and
  the IDC names the extensionless `aw9523b-key` layout. FinQwerty is not shipped.
- Accessibility default enablement now uses a normalized component name,
  preserves other enabled services, sets the platform accessibility switch,
  and no longer depends on the dead vendor property. The privapp whitelist is
  installed under its required `.xml` filename.
- Every candidate performs full source reset, cleanup, exact-head checks, and
  patch application. Optional `MP01_SKIP_REPO_SYNC=1` uses only cached repo
  objects but does not skip source preparation.
- The Metalava failure was reproduced independently with successful 4 GiB and
  6 GiB heap runs and byte-identical outputs; the 4 GiB run peaked at about
  3.997 GiB. The summary SHA256 is
  `8ec28ac68ac52bedb5b856985a5a19700a445bb23678bc83e01668aedc90a680`.
  Commit `4bb063e28116af3b4f4263c4cf6eed00b3829961` configures the Metalava
  invocation with `-J-Xmx6114m`, requires `MP01_MAKE_JOBS=1` on hosts with no
  more than 16 GiB,
  fixes and verifies Ninja's combined high-memory pool at depth `1`, and
  hash-checks the same retained `.mp01` verifier before and after primary make.
  Build-info records the host-memory, jobs, pool, heap, Soong/JDK, and verifier
  provenance.
- The old signing script exits with an error, and a separate target-files signer
  gate now runs before inventory, extraction, hashing, or publication. One
  private read-only snapshot feeds every downstream operation. Release mode
  requires verifier exit `0` and compatibility; explicit `test-key-audit` mode
  accepts only exit `3` plus `NOT_FOR_IN_PLACE_FLASH`. Build-info embeds the
  complete baseline identity, SHA256
  `0e0313015d4bba28f8fe85d91498d060a7c525d81980f3f100efeb7f3628dd03`,
  actual manifest, and comparison evidence. That baseline covers 222 APK paths
  for 221 packages and 33 APEX identities. Signing and OTA remain gated until a
  baseline-compatible identity or reviewed rotation path and LineageOS 23.2
  signing flow are reviewed and install-tested.
- The real target-files gate smoke at
  `/home/user/MP01-LineageOS/logs/signer-gate/801bf4a-real-smoke-20260710/` has
  verified checksums and
  records exit `3`, comparison `INCOMPATIBLE`, and disposition
  `NOT_FOR_IN_PLACE_FLASH`. It verifies the gate, not a complete final
  target-files comparison.
- FinQwerty mitigation commit
  `a60a78160be024173c7eac11acc45e4db4e693f0` disables release signing and
  publication, pins CI, ignores the historical key filename, and adds an
  explicit warning. It is staged as
  `20260710-090346-finqwerty-a60a78160be0`.
- Local FinQwerty commit `1b712b2a725d43233c03d768f4df6d4ef2e18883`
  deletes the exposed historical keystore. Its binary deletion cannot pass the
  current qpublish policy, so publication remains blocked pending an approved
  qadmin/`git-publish` binary-deletion mechanism. The compromised identity must
  never be reused.
- The archived unsigned Android 15 files remain under
  `images/archive/lineage-22.2-unsigned-20260617/`. They are not an Android 16
  candidate or the accepted working baseline.

The final logical GSI revision is
`c88e039992760ada12f1df874453c2243d784862`, tree
`9d4bfca308b640e2b28f58f3502af40a7adf0c21`. Its formal and independent audit
result is `PASS_AUDIT_ONLY_NOT_FOR_IN_PLACE_FLASH`. Tree-equivalent publication
squash `ae9299f0819ca9bd564859e96bce965007381e54` is staged as qpublish
submission `20260715-111324-MP01-LineageGSI-ae9299f0819c`.

## 1. Preserve the Audit and Rebuild on Verified Storage

Do not promote an artifact until all of these checks pass:

- Preserve needed evidence, take the affected development filesystem
  offline/unmounted, and complete the appropriate check and repair before any
  release build.
  On July 10 the host kernel reported an EXT4 inode-checksum error for inode
  `22850323` on `/dev/xvdb` while an unrelated broad search was running. The
  failed build did not report a read or write failure, so the disk warning is
  not claimed as its cause. After a clean filesystem result, rebuild cleanly
  from the exact committed inputs on verified storage. Earlier outputs remain
  software-audit-only.
- Preserve the completed formal Android policy, target-files, system-image, and
  retained-audit evidence. Treat its output as software-audit-only permanently;
  `PASS_AUDIT_ONLY_NOT_FOR_IN_PLACE_FLASH` never authorizes flashing.
- The sampled free-space low-water mark was `255.39 GiB` and final ccache size
  was `14.3 GB`. This was an incremental/cached run, not clean-build
  calibration. Calibrate `MP01_MIN_FREE_GB` and the ccache cap from the future
  verified-storage clean build; do not promote the configured 250 GiB guard as
  a platform minimum.
- Require the signer gate to create one private read-only target-files snapshot,
  compare its complete APK/APEX identities before any inventory or publication,
  and embed the actual manifest and comparison evidence in build-info. An
  audit-mode `INCOMPATIBLE` result is acceptable only with verifier exit `3` and
  `NOT_FOR_IN_PLACE_FLASH`; it never authorizes device testing.
- Confirm installed and target-files TrebleApp each have exactly one platform
  signer and match the unsigned prebuilt's deterministic non-signature ZIP-entry
  manifest plus `classes.dex` subcheck.
- Confirm each of the five presigned partner APKs is zip-aligned and exactly
  byte-identical to its pinned source in both the installed tree and target-files
  snapshot.
- Require exactly one of each of the 14 inventoried MP01 service, whitelist,
  inkOS, input-map, TrebleApp, F-Droid, and microG target-files paths. This is a
  path/count gate, not a second semantic decode of inkOS.
- Confirm the separately recorded source inkOS identity and enabled MAIN/HOME
  activity, MP01 service policy, product identity, and normalized accessibility
  behavior.
- Capture, XML-validate, and normalize the resolved `repo manifest -r` before
  presenting final artifacts. A manifest-capture failure must leave no
  plausible partial candidate.
- Retain the image, compressed archive, timestamped `*.sha256sums` completion
  file, build-info with embedded TrebleApp, low-memory, and signer provenance,
  normalized resolved manifest, and complete build log together.
- Verify all recorded revisions and checksums. Preserve the legacy `-unsigned`
  artifact filename, but label the output accurately as test-key, microG,
  userdebug, unflashed, and not release-signed.

## 2. Finalize and Stage Source

- Preserve logical GSI head `c88e039992760ada12f1df874453c2243d784862`
  as the source identity for the successful formal build.
- Preserve bounded publication squash
  `ae9299f0819ca9bd564859e96bce965007381e54`, whose tree matches the final
  logical GSI head and whose publication diff contains no rename or copy entries.
- Keep these docs synchronized with the sealed build and audit record.
- Commit each repository locally and stage it through qpublish on its intended
  branch. Publishing remains delegated to `git-publish`; do not push from the
  development qube.
- The final GSI submission already supersedes its stale June predecessor.
  Supersede only the stale June MP01-OS submission. Do not publish Android 16
  work onto an Android 15 branch.

TrebleApp head `9d8a6771d94b7985f515b41bd280f7bdb4554037` is staged as
`20260710-095532-treble_app-9d8a6771d94b`, and manifest head
`fb1e1f76d353591caa2d991a3f8d92266249fe8e` is staged as
`20260710-095546-treble_manifest-fb1e1f76d353`; only their predecessors are
currently upstream. Overlay head
`7cf73a0094e6448e0bb830fea996715fbd2fffc3` is staged for the existing
`lineage-23.2` target as
`20260710-090001-vendor_hardware_overlay-7cf73a0094e6`. Presets head
`5891dba9621542b297acd761dbf3fe98d841c214` is staged as
`20260710-090043-treble_presets-5891dba96215`. FinQwerty mitigation head
`a60a78160be024173c7eac11acc45e4db4e693f0` is staged as
`20260710-090346-finqwerty-a60a78160be0`; the later local binary-deletion commit
`1b712b2a725d43233c03d768f4df6d4ef2e18883` is blocked from staging until
qadmin/`git-publish` provides an approved binary-deletion mechanism. The GSI
publication squash is staged as
`20260715-111324-MP01-LineageGSI-ae9299f0819c`. The MP01-OS
documentation/auditor chain is staged separately through the explicit June
predecessor recorded below; inspect the outbox for its current submission state.

After all affected repositories have clean local commits, begin with workspace,
outbox, and feedback inspection. Stage a listed head only if that inspection
still shows it needs a submission; state may advance during review. Only
MP01-OS requires the explicit predecessor ID below:

```bash
qpublish workspace-status
qpublish outbox
qpublish feedback list

qstage MP01-OS \
  --repo /home/user/MP01-LineageOS/MP01-OS \
  --head HEAD \
  --target-branch main \
  --supersedes 20260626-220711-MP01-OS-03739f0b972d
```

Publishing remains delegated to `git-publish`; these commands do not authorize
a direct push from the development qube.

## 3. Resolve Signing Compatibility Before Device Testing

The audited output uses Android test keys and is not release-signed. Its source
platform, shared, media, release/default, and network-stack certificate
fingerprints all differ from the inventoried baseline key classes. The enforced
complete target-files gate records `INCOMPATIBLE`, 750 incompatibilities, and
`NOT_FOR_IN_PLACE_FLASH`. No current test-key output may be flashed even though
its build and checksums pass. A baseline `release-keys` tag is not certificate proof, and
the historical FinQwerty application key is unrelated to platform or APEX keys.

Before any device test, compare actual candidate target-files APK and APEX
container/payload identities against the baseline public-identity inventory,
produce a compatible final release-signed identity or reviewed rotation path,
and obtain operator approval for that exact signed candidate. Then use the
[`candidate test report`](candidate-test-report.md) and
[`hardware test matrix`](hardware-test-matrix.md).

Verify the timestamped `*.sha256sums` completion file against both the image and
archive before running any device command. A checksum failure aborts the
session.

The only admissible migration test is a `system`-only in-place flash of the final
signer-compatible candidate. Existing phone data must be preserved. Approval to
flash `system` does not authorize erasing data, wiping from recovery, or factory
resetting. Any clean-install exception needs separate, explicit operator
approval for that exact session.

Required results include boot to the existing user session, data preservation,
keyboard and backlight, e-ink refresh, brightness clamp, lock-screen clear,
Wi-Fi, Bluetooth, suspend/resume, calls, SMS/MMS, carrier IMS/VoLTE, F-Droid,
microG, inkOS, TrebleApp presets, and the permissioned e-ink automation path.

## 4. Keep Downgrade And OTA Gated

Do not publish a release or enable OTA metadata until the final signed identity
passes the in-place device gate. Private keys and publishing credentials must
remain outside git and the development qube.

The baseline archive, inner image, complete 222-APK signer inventory, 33 APEX
identities, and AVB public key are now locally recorded, but that evidence does
not prove Android 16-to-15 downgrade compatibility on the installed phone. A
separately approved data-preserving hardware downgrade test remains pending. If
Android 16 testing fails, stop and preserve evidence; do not wipe or attempt an
assumed downgrade.

After signer compatibility and the hardware gate pass:

- Publish checksums, resolved source revisions, install/rollback notes, and
  known issues.
- Enable OTA metadata only after its exact artifact URL, checksum, and update
  behavior are verified.
