# Reproducible Build Plan

The current milestone is a traceable LineageOS 23.2 / Android 16 test image for
MP01. It does not claim byte-for-byte reproducibility. It requires exact source
revisions, verified binary inputs, a retained log, and checksummed outputs.

The synchronous Blueprint diagnostic completed a full Soong graph with both
pre- and post-write provider checks passing. The production post-write fix,
strict patch-state handling, no-kernel generated-header policy, e-ink fortify
correction, and presigned-partner byte-preservation policy are committed at GSI
head `c88e039992760ada12f1df874453c2243d784862`. Its formal build and retained
independent audit completed with `PASS_AUDIT_ONLY_NOT_FOR_IN_PLACE_FLASH`.

## Build Identity

- Android source: `https://github.com/LineageOS/android.git`
- Android branch: `lineage-23.2`
- Local manifest commit:
  `fb1e1f76d353591caa2d991a3f8d92266249fe8e`
- External GSI source used by the successful formal build:
  `c88e039992760ada12f1df874453c2243d784862`, tree
  `9d4bfca308b640e2b28f58f3502af40a7adf0c21`
- Complete formal build log:
  `.android-build/logs/mp01-final-c88e03999276-20260715T055915Z-93cb550cc58a.log`,
  SHA256 `87681b4c33c0d9584cb5067b223c2f92219544dfafd1147017511d49d0f25d3a`
- Formal log contract/start epoch: `1` / `1784095155`
- Formal harness/helper SHA256:
  `938cc2842ca860704f727cfbd4f890227ccb93d44387f64e6be3f704b3403204` /
  `cf8a04c7d334caeb177750b7f2e9c2855e2835e231f9e45d21933619fd9ead07`
- Successful run mode: cached-local repo reset with `MP01_SKIP_REPO_SYNC=1`, followed
  by full source cleanup, exact-head verification, and patch application
- Final logical GSI support commit:
  `c88e039992760ada12f1df874453c2243d784862`
- Tree-equivalent publication squash:
  `ae9299f0819ca9bd564859e96bce965007381e54`, staged as
  `20260715-111324-MP01-LineageGSI-ae9299f0819c`
- Lunch target: `lineage_arm64_bmN4-bp4a-userdebug`
- Audited output: local microG userdebug image built with test keys; unsigned,
  not release-signed, software-audit-only, and never flash eligible

`MP01-LineageGSI` is build support, not an Android repo-manifest project. The
build driver clones or uses that checkout separately, verifies its revision,
and copies its product, patch, release-input, and MP01 vendor content into the
source tree. Build-info records its commit separately from the resolved
manifest.

## Exact Manifest Inputs

`treble_manifest` commit
`fb1e1f76d353591caa2d991a3f8d92266249fe8e` is one bounded patch-chain unit. It
declares exactly these 14 projects, all by 40-character commit:

| Path | Project | Pinned input revision |
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

These are 14 pinned input projects. The microG build removes proprietary
`vendor/gapps`, leaving 13 effective custom projects in the normalized resolved
manifest. For patched projects, the final manifest records the prepared commit
as `revision` while retaining the pinned input in `upstream` and `dest-branch`.
That includes prepared `treble_app` revision
`07a1853f2ce624d3102121a9d881d29d62ea57bb`, prepared `vendor/partner_gms`
revision `67e492737184fe9584750e07ad4c0ecfb40af67e`, and prepared
`hardware/oplus` revision `194f449694f9d54cff65cb63b5363de156ad991b`.
The manifest records the complete platform plus all 13 effective custom
projects and must contain neither `vendor/gapps` nor a `LineageOS_gsi` project.

## Verified Non-Manifest Inputs

The build pins and verifies:

| Input | Version or object | SHA256 |
| --- | --- | --- |
| Official repo launcher | `repo-2.65` | `1211b57b57e4122a9c546295a59b37d24068f1164d0e87bef096d5323c413e4f` |
| TrebleApp Gradle distribution | `gradle-7.5-all.zip` | `97a52d145762adc241bad7fd18289bf7f6801e08ece6badf80402fe2b9f250b1` |
| F-Droid | `1.23.2` / version code `1023052` | `985f5181d48bb6bafd54083a048b391271e0ab28385881cc41294fb01a222762` |
| F-Droid privileged extension | `0.2.13` / version code `2130` | `1008525a17b4f6a93ac690f9c50dcb675b6bebf53d2879dbc98ba65a1cb2e28d` |
| GmsCore | `0.3.15.250932` / version code `250932030` | `52597e77fd25fdd347574d0457ed1936a4b9561cf4c8d34e7ac8dd8191dfd4b9` |
| FakeStore | `0.3.15.40226` / version code `84022630` / release tag `v0.3.15.250932` | `a973e0235a2829773a4faf36d235d5f703d1c04a2adff674ebaa535a2e78f937` |
| GsfProxy | `v0.1.0` / version code `8` | `86891b174301f06a1c84187b545a0a2a57044c6b768f3e84e865908743349692` |
| Checked-in inkOS | `v0.1` | `64a3cd323ba484640cb0ba6d6d4ad1855048f0460ad852ef1f610439fa6445f8` |
| Treble presets | commit `5891dba9621542b297acd761dbf3fe98d841c214` | `0e1fc2ea5719181d90bbad8dfec6dc43ac094a2df458b923abff601c3fea0328` |

The launcher URL is immutable:
`https://storage.googleapis.com/git-repo-downloads/repo-2.65`. APK URLs contain
fixed release tags or version codes. Verification checks APK structure and
signing certificates for the downloaded partner APKs in addition to hashes.
Unexpected input stops source preparation.

The partner APK build-policy patch has SHA256
`146aa1a9307452217e087d818028bb158e8adf0a5a3a52e6bcaebe0665e7a1bf`.
It transforms `vendor/partner_gms` base commit/tree
`4b3b48033245800142045ce78038166f8aff6b01` /
`3c554b8fabffd2bdd0727aac770e403d9fec0505` into prepared commit/tree
`67e492737184fe9584750e07ad4c0ecfb40af67e` /
`06afb50166f27672b02c7b168b24de0bf30f8f21`. Source preparation verifies one
exact byte-preserving `PRESIGNED` Make definition for each of `GmsCore`,
`FakeStore`, `GsfProxy`, `FDroid`, and `FDroidPrivilegedExtension`, with no
duplicate or competing Blueprint definition.

The launcher initializes the official implementation from
`https://gerrit.googlesource.com/git-repo` at tag `v2.65`; the checked-out
implementation must resolve exactly to commit
`35bbf701d04de5c6a71937279bc3d16f6ce36808`. Build-info records the launcher
URL/hash, implementation URL/tag/commit/tree, manifest commit/tree, clean live
GSI commit/tree, cloned support commit/tree, and exact TrebleApp and overlay
heads.

The checked-in source inkOS APK check is semantic as well as cryptographic.
Before the Android build, `aapt2` must report package `app.inkos` and an enabled
`com.github.gezimos.inkos.MainActivity` containing both MAIN and HOME in one
intent filter. The later target-files inventory verifies only the exact packaged
path and count; it does not repeat this semantic APK decoding.

Run the independent input gate with:

```bash
bash scripts/verify-release-inputs.sh
```

## Source Preparation Gate

The failed `4bb063e` build completed a cached-local repo reset from the existing
depth-bounded object cache; it did not perform a new network sync. Its old
runner reported the following gate had passed before Soong graph generation:

1. Verifies the launcher and local manifest inputs.
2. Rejects a separately synced `LineageOS_gsi` directory.
3. Removes bounded stale copies of GSI-owned vendor trees.
4. Imports the current external build-support tree.
5. Applies the patch stack.
6. Applies patch commits with committer dates fixed to their author dates.
7. Checks Launcher3, SetupWizard, MP01 service, and TrebleApp postconditions.
8. Makes source-preparation and primary make failures fatal.

Later review invalidated item 5 as historical evidence: GNU reverse dry-run
accepted a forward-applicable patch with fuzz and falsely reported it as already
applied. Commit `11bdbbdb9a9789b00b6dfba986bfca4c72735cc7` now uses exact
`git apply --reverse --check` state detection and a zero-fuzz GNU fallback. Its
regression tests cover the Oplus false positive, idempotence, and divergent
context. The successful run applied the formerly skipped patches under this strict
policy. Duplicate-module failures previously caused by both a manifest GSI
project and an imported GSI tree remain removed by design.

The prepared tree was inspected to confirm author and committer dates match.
The inactive `product.prop` patch and its unvalidated tuning properties were
removed. Every candidate run performs full source preparation: it initializes
the pinned manifest inputs, resets and cleans all repo projects, and reapplies
the patch stack. `MP01_SKIP_REPO_SYNC=1` may be used only when the required
objects are already in the local repo cache; it still performs the local reset,
cleanup, exact-source checks, and complete patch application. There is no
skip-source-preparation candidate path.

## Metalava Failure And Low-Memory Policy

The predecessor build used GSI source
`ac3f97f43eafbacf4f222a6915429fae9d7c2a69`. Its retained log is
`.android-build/logs/mp01-final-ac3f97f-20260710T103529Z.log`, SHA256
`e790c3d04352a436810b4f747ec76aed8763c5052d93f937f4544a8513f71e30`.
That run reached the `api-stubs-docs-non-updatable` Metalava action and failed
with `java.lang.OutOfMemoryError: Java heap space`; it did not produce a
candidate artifact.

The failed action was replayed in isolation with the source-tree Android PDK
OpenJDK 21. The retained summary is
`.android-build/tmp/metalava-89e80645-metalava_heap_repro/metalava-heap-repro-summary.log`,
SHA256
`8ec28ac68ac52bedb5b856985a5a19700a445bb23678bc83e01668aedc90a680`.
Both the 6 GiB and 4 GiB trials exited `0` and produced four byte-identical
outputs. The 4 GiB trial reached a Java high-water RSS of 4,191,148 KiB, leaving
essentially no margin; the 6 GiB trial reached 4,231,808 KiB.

GSI commit `4bb063e28116af3b4f4263c4cf6eed00b3829961` commits
`patches/personal/platform_build_soong/0001-soong-java-raise-metalava-heap-on-low-memory-builders.patch`.
The patch adds `-J-Xmx6114m` only to Metalava and has SHA256
`5f1e4852e7455238c9997865bb7ba05a4e72ce2b60a8b07e4ae36e9400ee791c`.
Applying it to pinned `build/soong` base
`4035bec90f84b583a1502b9a546c6117a28fdbe2` deterministically produces commit
`58a9e2c3dced31247cf99651e0fd0bb04b4a4b0c` and tree
`b603556b58e5f79868622135d82b9f3f111553ae`.

The low-memory policy reads a single validated `/proc/meminfo` `MemTotal` and,
at or below 16 GiB, rejects any `MP01_MAKE_JOBS` value other than `1`. It fixes
`NINJA_HIGHMEM_NUM_JOBS=1`; the retained verifier has confirmed that the real
combined Ninja file contains exactly one `highmem_pool` with depth `1`. Before
the copied support tree is removed, the build preserves the source-bound helper
as `.mp01/verify-metalava-heap-policy.py`, verifies its hash, and uses that same
copy for prepared-Soong and post-make Ninja checks.

Build-info is designed to record host memory, repo and make jobs, expected and
actual highmem depth, Metalava heap flag, low-memory threshold, Soong
base/prepared commit and tree, patch path/hash, retained verifier path/hash, and
Android JDK provenance. The failed run did not reach final build-info or artifact
publication.

## Provider Failure, Confirmed Diagnostic, and Formal Fix

The `4bb063e` log stopped during Soong/Blueprint graph validation and reported
`provider ... was modified after being set`. The reports cover
`android.InstallFilesInfo`, `android.ModuleInfoJSONInfo`, `android.PhonyInfo`,
`*android.ComplianceMetadataInfo`, `filesystem.FilesystemInfo`, and
`filesystem.SuperImageInfo`, including the ncurses/tool modules and generated
system, super, and device modules. Soong bootstrap failed before Ninja,
target-files, system-image, or artifact packaging. This run did not reach the
target Metalava action; only the isolated replay and focused policy tests
validate the heap remediation so far. The log does not report a filesystem I/O
failure.

The diagnostic edit invoked the existing validation synchronously both before
and after `WriteBuildFile`. The full Soong graph completed with both checks and
no provider error. The retained log is
`.android-build/logs/mp01-provider-pre-post-20260710T132726EDT.log`, SHA256
`dd23b844f916e0a35268a4654978b378e2b57f3369db643c832578bad4b9e4d8`.
Compilation was then intentionally interrupted at 3% because this direct
diagnostic omitted `USE_CCACHE` and would serially rebuild approximately 170,000
actions. The run localized the provider failure; it was not intended to produce
an artifact.

GSI commit `4e94263d8871e26b32f8927f6f1d820a830a0a19` commits
`patches/personal/platform_build_blueprint/0001-blueprint-serialize-provider-validation.patch`,
SHA256 `43cca96d3eb8d04a91a9b0637444889b62fe1a04a064910c68c2358e23326df1`.
The command-only patch removes the concurrent traversal and invokes the same
fail-closed invariant synchronously after Ninja writing, flushing, and action
caching. Its exact Blueprint base is commit/tree
`c39c8a4c103f1393f015a5befa7726f0c14c9bc2` /
`690ca4cbc4c0d954a5de59dd13b1597f135c243a`; deterministic preparation produces
commit/tree `448557ea39c422f96412af18530133301f12cbb6` /
`5e79a8c9dcde279d368f9fdab2a5b4ff7d28ff35`.

The first formal invocation from `4e94263` stopped at preflight because the
external Codex workspace helper was absent. It performed no source preparation
and produced no artifact. Its log is
`.android-build/logs/mp01-final-4e94263d8871-20260710T203839Z.log`, SHA256
`2c09d82d450ee803f46fa179c3bfff8f2c2d1ba5ceb3e80d1774abbe29276b8b`.
Head `3feebebfb20c6b424b05f4cbe5f1e72ca5b3e28f` replaces that dependency with
repository-owned, hash-checked workspace and build-state policy. Its formal run
passed source preparation and lunch, then failed the output contract before
graph generation: `TARGET_PRODUCT=lineage_arm64_bmN4` resolved
`ANDROID_PRODUCT_OUT` under `generic_arm64`, rather than a directory named for
the lunch product. Its log is
`.android-build/logs/mp01-final-3feebebfb20c-20260710T220742Z.log`, SHA256
`55157ea23dfa8795dbc84b512867eb40d7364a35caed1fa87f394d2f47809691`; it
produced no artifact. Head `c890b4015a505bbce0ae09761f0054de24d3d6c0`
pins that actual product output name. Its formal run passed the lunch/output and
TrebleApp contracts and completed bootstrap `284/284`. It then failed while
Soong generated the main Ninja file: module `continuous_native_tests` at
`platform_testing/Android.bp:255:1` rejected the absolute
`out/host/linux-x86/framework/net-tests-utils-host-common.jar` path as outside
the source directory. Main/product Ninja was not regenerated or executed;
target-files, publication, and device operations were not reached. Its log is
`.android-build/logs/mp01-final-c890b4015a50-20260710T221230Z.log`, SHA256
`bac623467a00c6ef1c321c3ea1d18ea1370fe023d427f2d74397dfa01a201468`;
start `2026-07-10T22:12:30Z`, end `2026-07-10T23:04:19Z`, wrapper duration
`00:51:49`, Android footer `48:53`, exit `1`. It produced no artifact or
publication residue, and the retained log contains no I/O or OOM failure
evidence. Head `612997762d55364f14b4157f745dcab190dd468c` supplies Android's
relative `OUT_DIR` interface while independently verifying canonical absolute
containment. Its build was intentionally stopped at action `6632/153795` after
review found that the ad hoc wrapper ignored `tee` status. The evidence log is
`.android-build/logs/mp01-final-612997762d55-20260710T231231Z.log`, SHA256
`8dd8aa7ad75d6c1ac60264612931228bbb6cb6f892ffbbf35f28a76422ad44f5`, from
`2026-07-10T23:12:31Z` through `2026-07-11T01:52:04Z`; duration `02:39:33`,
intentional exit `141`. It produced no artifact or publication residue, and the
log contains no kernel I/O or OOM failure evidence.

Commit `16aa5f8d47503debba428c01547aba91232f28b6` replaces that wrapper with
the contract-v1 `scripts/run-formal-build.sh` harness. Head
`3d1bfa4f4be14857b21dde879ec9f9e64a401c60` also blocks test-key artifacts
from flashing workflows. Its first contract-v1 run exposed the old patch-state
false positive and later failed when `generated_kernel_includes` invoked a
missing `headers_install` target for the no-kernel GSI. Its retained staging log
is
`.android-build/logs/mp01-final-3d1bfa4f4be1-20260711T024331Z-fd587786d599.log.incomplete`,
SHA256
`6006d29d4a5f6ec348c3258985bbee2898abfd07bb74a3e042b05811a216dcc1`;
it produced no candidate.

Commit `11bdbbdb9a9789b00b6dfba986bfca4c72735cc7`, tree
`d71e422d41b351cb3ac93bf62f60c1194fb12af4`, makes patch application fail
closed. Commit `cb9eab69b9500fa194a7e4adc72f110656ee2cf2`, tree
`277564406d298e3a0283c7dbfd2a42010715b74a`, exports
`TARGET_NO_KERNEL` to Soong and makes an empty generated include root only for
no-kernel targets while retaining real-kernel header installation. That formal
run passed generated-header generation and reached the MP01 e-ink daemon, then
failed because its `_FORTIFY_SOURCE=2` flag conflicted with Android 16's
toolchain-provided level 3. Its retained staging log is
`.android-build/logs/mp01-final-cb9eab69b950-20260711T235938Z-90c3aa8cf054.log.incomplete`,
SHA256
`46bb6fd0eff47ffb14229477afb38c8e25b0ae6f9bdbd9b4d09332b4d36e0d8a`;
it produced no candidate.

Head `2fd5dec31b3b9c98060ed81d29a666b653df05fe`, tree
`a931350da017ad19d18dd1b520c103c7ad417730`, removes the stale e-ink fortify
override. Its formal run completed the primary Android build in `05:34:23`, then
failed closed in the post-build signer audit because
`FDroidPrivilegedExtension.apk` no longer contained the v2/v3 signing blocks
declared by its JAR signature. Android's privileged-prebuilt path had
uncompressed DEX content and realigned `GmsCore`, `FakeStore`, and
`FDroidPrivilegedExtension`, changing their bytes and invalidating their signing
blocks; `FDroid` and `GsfProxy` remained byte-identical. The retained staging
log is
`.android-build/logs/mp01-final-2fd5dec31b3b-20260712T200339Z-abcc08c367e1.log.incomplete`,
SHA256
`6093a4960140dd5bdd29185cf7788f8c16e8f530f9a260afcc910b7a49e55b8a`.
No final log or candidate was published.

Final logical GSI head `c88e039992760ada12f1df874453c2243d784862`, tree
`9d4bfca308b640e2b28f58f3502af40a7adf0c21`, fixes the byte-preservation
policy. All 143 GSI tests pass. An initial invocation stopped before source
preparation because 227 GiB available was below that run's configured 250 GiB
preflight threshold. Its
retained staging log
`.android-build/logs/mp01-final-c88e03999276-20260715T055348Z-0b4bf6f7177e.log.incomplete`
has SHA256
`9e51db5870ec7bc14ecdfd953ca509a617181434169987e89db950f39aa81f82`;
no artifact was produced. The 250 GiB value is neither a LineageOS requirement
nor a measured build minimum: the harness defaults to 400 GiB, this invocation
overrides it to 250 GiB, and ccache is separately capped at 200G. It is a coarse
guard for possible cache growth plus Android output, temporary, and packaging
space. No retained benchmark justifies the exact threshold; future policy
should use a measured peak or a lower cache cap.

After space was reclaimed, the harness rerun started at epoch `1784095155`,
completed Android in `08:47:27`, and published artifact epoch `1784126958` plus
the complete final log identified above. The sampled free-space low-water was
`255.39 GiB` and final ccache size `14.3 GB`. Those measurements describe an
incremental/cached run, not clean-build calibration; they do not establish the
250 GiB override as a floor.

All 47 auditor unit tests passed. The retained independent audit returned
`PASS_AUDIT_ONLY_NOT_FOR_IN_PLACE_FLASH`. It verified the image, archive,
completion file, build-info, resolved manifest, target-files, all 14 required
paths, and exact bytes/alignment for all five partner APKs. The signer result is
`INCOMPATIBLE` / `NOT_FOR_IN_PLACE_FLASH`: 616 APKs, 44 APEXes, 750
incompatibilities, and 0 warnings. The candidate test report records every
artifact and evidence hash.

This is a system-image-only GSI with `TARGET_NO_KERNEL=true`. Despite requested
enforcement, the Make warning means the kernel inputs to build-time `checkvintf`
and the OTA kernel metadata are omitted, not passed, and supplies no basis for
kernel compatibility or OTA publication. Exact-device
`VtsTrebleVintfTest` `SystemVendorTest.KernelCompatibility` remains pending.
OTA publication is disabled.

## Verified-Storage Prerequisite

Separately, the host kernel reported
`EXT4-fs error (device xvdb): ext4_lookup:1787: inode #22850323: comm rg: iget: checksum invalid`
during an unrelated search. No build-path filesystem error has been observed,
so this is not assigned as the provider failure's cause. It still prevents any
output on that volume from becoming a release candidate.

Before a candidate-producing run, preserve required evidence, stop writes to and
take the affected filesystem offline/unmounted, complete the appropriate
filesystem check and repair, and verify a clean result outside this live build
session. Then recreate clean Android outputs from the exact committed inputs on
verified storage. Diagnostic outputs and builds created before those steps are
software-audit-only.

## Deterministic TrebleApp Packaging

The manifest pins `treble_app` at
`9d8a6771d94b7985f515b41bd280f7bdb4554037`. This head includes Gradle 7.5
distribution checksum verification and dependency checksums in
`gradle/verification-metadata.xml`. A strict clean release build passes.

Its first review unit, `cee22d352a9c022d43e5384a29646898a94e45cd`, removes
cross-repository publication from CI. The workflow is build-only, grants
read-only contents permission, and pins checkout, Java setup, and artifact
upload actions by full commit.

For the Android image, the GSI helper:

1. Requires the exact pinned clean source.
2. Applies exactly nine MP01 patches in order.
3. Verifies patch identities and eight required APK markers.
4. Builds with JDK 17 and the pinned Gradle dependency graph.
5. Requires the Gradle prebuilt to be unsigned, then creates a deterministic
   manifest of every non-signature ZIP entry and retains `classes.dex` as a
   focused subcheck.
6. Replaces `vendor/hardware_overlay/TrebleApp/app.apk`; the build-info file
   embeds its source, patch, APK-content, and bytecode provenance.
7. Verifies both the installed APK and the target-files APK have exactly one
   signer matching the Android platform certificate, and that every
   non-signature ZIP entry plus the `classes.dex` subcheck matches the unsigned
   prebuilt.

A missing or stale package, a signed Gradle prebuilt, a non-platform or multiple
signer, or any content-manifest/DEX mismatch fails the build.

For the five presigned partner APKs, the build separately verifies that the
source, installed, and target-files copies all match the release-input SHA256
and pass `zipalign -c -p 4`. A missing or duplicate target-files entry, failed
extraction, rewritten APK, symlinked input, hash mismatch, or alignment failure
stops publication.

## Single-Snapshot Signer Gate

After make, the build selects the exact product target-files archive once. The
signer verifier creates one private mode-`0444` snapshot while checking that the
source did not change during copying. It inventories APK and APEX identities
from that snapshot and records the snapshot SHA256 in deterministic evidence.
The build verifies that hash, then uses only the same retained snapshot for the
14-entry inventory, packaged TrebleApp checks, and the sole
`IMAGES/system.img` extraction. Build-info records the original source path and
snapshot hash and embeds the complete signer evidence and actual manifest;
standalone temporary signer files are removed afterward.

The default `test-key-audit` mode always returns exit `3` after valid evidence,
whether the identities compare equal or not. The wrapper accepts only exit `3`
with exact `flash_disposition=NOT_FOR_IN_PLACE_FLASH`; any other exit or
malformed evidence fails closed. The durable 1-APK/1-APEX gate smoke recorded
`INCOMPATIBLE`, proving the wrapper behavior before the full build. The sealed
`c88e039` run then compared 616 APKs and 44 APEXes and embedded complete
evidence: `INCOMPATIBLE`, 750 incompatibilities, 0 warnings, and
`NOT_FOR_IN_PLACE_FLASH`. This test-key audit artifact remains a release and
in-place-flash blocker because of that disposition and the unavailable
compatible signing/rotation path. A future clean verified-storage candidate
must be compared again.

Explicit `release-candidate` mode is stricter. A mismatch returns `1`, a fatal
verification error returns `2`, and exit `0` is possible only with complete
expected APK/APEX coverage and no missing, added, or changed identity. The
wrapper additionally requires
`comparison_status=COMPATIBLE_SIGNER_IDENTITIES` and
`flash_disposition=SIGNER_GATE_PASSED_HARDWARE_TEST_STILL_REQUIRED`. Passing
this gate does not replace the separate hardware upgrade and release gates.

## Exact Target-Files Inventory

Before artifact packaging, the selected target-files archive must contain
exactly one of every entry below:

| Role | Required entry |
| --- | --- |
| TrebleApp | `SYSTEM/priv-app/TrebleApp/TrebleApp.apk` |
| Accessibility service | `SYSTEM/priv-app/MP01AccessibilityService/MP01AccessibilityService.apk` |
| E-ink daemon | `SYSTEM/bin/MP01_eink_server` |
| E-ink init | `SYSTEM/etc/init/MP01_eink_daemon.rc` |
| Accessibility whitelist | `SYSTEM/etc/permissions/privapp-permissions-accessibility.xml` |
| inkOS | `SYSTEM/app/inkos/inkos.apk` |
| Input device configuration | `SYSTEM/usr/idc/aw9523b-key.idc` |
| Key layout | `SYSTEM/usr/keylayout/aw9523b-key.kl` |
| Key character map | `SYSTEM/usr/keychars/aw9523b-key.kcm` |
| GmsCore | `SYSTEM/product/priv-app/GmsCore/GmsCore.apk` |
| FakeStore | `SYSTEM/product/priv-app/FakeStore/FakeStore.apk` |
| GsfProxy | `SYSTEM/product/app/GsfProxy/GsfProxy.apk` |
| F-Droid | `SYSTEM/product/app/FDroid/FDroid.apk` |
| F-Droid privileged extension | `SYSTEM/product/priv-app/FDroidPrivilegedExtension/FDroidPrivilegedExtension.apk` |

The exact-count rule detects both missing packages and accidental duplicate
paths. The whitelist filename is part of the contract; Soong now preserves the
source `.xml` name instead of installing it under the module name. The inkOS row
proves packaging at that path; semantic package/activity verification belongs
to the checked-in source APK gate described above.

The archive selected for this product is exactly
`$ANDROID_PRODUCT_OUT/obj/PACKAGING/target_files_intermediates/lineage_arm64_bmN4-target_files.zip`.
The audited `$ANDROID_PRODUCT_OUT` basename is `generic_arm64`. Build-info records
that archive path and SHA256. Publication requires exactly one
`IMAGES/system.img` entry and extracts the published image only from that entry;
it does not independently select an image from `$ANDROID_PRODUCT_OUT`.

## Resolved Manifest And Atomic Publication

The resolved `repo manifest -r` is parsed and validated as XML. When local exact
TrebleApp/overlay overrides are active, only the host-specific `mp01-local`
`file://` fetch URL is normalized to `https://github.com/`; all exact revisions
are retained. The effective custom-project count is 13 because `vendor/gapps`
is removed before sync.

A workspace build lock prevents concurrent source builds, and a publication
lock prevents concurrent writers to the image directory. Existing final paths
are never overwritten. The image, archive, normalized manifest, and build-info
are prepared under staged names, then moved into place; the timestamped
`*.sha256sums` file is moved last as the completion marker. Failure cleanup
removes both staged files and any incomplete final set.

## Other Focused Gates

- `treble_presets` contract tests pass for 60 presets and 111 definitions.
- All 452 overlays build with API 36 and the MP01 resources validate against
  exact LineageOS framework commit
  `46fd4b1f8d25b92540048c96ddc625b4ebeb6d60`.
- Overlay and TrebleApp CI use explicit read-only permissions and commit-pinned
  actions.
- The e-ink stream parser passes split-read, multiple-frame, CRLF, EOF, and
  overflow host C tests. The five-second client timeout discards a partial frame
  rather than executing it or letting an idle client block the daemon. JVM
  runner tests verify per-command connections and failure propagation.
- The e-ink service boundary and focused SELinux checks pass.
- MP01 keymap preflight passes with extensionless IDC layout name
  `aw9523b-key`. FinQwerty is not an image input.
- Accessibility boot setup uses normalized component names, preserves existing
  enabled services, sets the platform enable flag, and no longer reads the dead
  vendor property.
- The obsolete signing script exits nonzero. Signing and OTA remain unavailable
  until a baseline-compatible identity or reviewed rotation path and an Android
  16 signing map are separately reviewed.
- GSI `README.md`, `ROUGHGUIDE.md`, and `vendor/MP01_services/README.md` no
  longer expose current test-key device commands. They explicitly block current
  audit artifacts from device workflows.

## Successful Formal Build Command

This records the exact successful invocation. The 250 GiB value is the run-specific
preflight guard described above, not a general build recommendation.

```bash
workspace=/home/user/MP01-LineageOS
cd "$workspace/MP01-LineageGSI"
set -euo pipefail

export MP01_MIN_FREE_GB=250
export MP01_REPO_SYNC_JOBS=8
export MP01_MAKE_JOBS=1
export MP01_SIGNER_COMPATIBILITY_MODE=test-key-audit
export MP01_TREBLE_APP_JAVA_HOME=/home/user/.local/share/jdks/temurin-17
export MP01_TREBLE_APP_ANDROID_SDK_ROOT=/home/user/.local/share/android-sdk
export SOONG_FINDER_THREADS=1
export BLUEPRINT_PARSE_THREADS=1

# This run used cached objects but still performed full source preparation.
export MP01_SKIP_REPO_SYNC=1

bash scripts/run-formal-build.sh
```

The committed harness captures both pipeline statuses, so neither a build
failure nor a `tee` failure can be hidden. It requires a clean committed GSI
HEAD, binds the transcript to the exact commit/tree, harness/helper hashes,
signer mode, start-epoch record, and log inode, rechecks integrity after the
build, validates the complete contract-v1 transcript, and fsyncs before atomic
publication. The final log path is embedded in build-info through the
harness-supplied `MP01_BUILD_LOG_PATH`. The successful run used
`MP01_SKIP_REPO_SYNC=1` only because all objects were already cached. Omitting
that optional setting selects network sync; either path
resets and cleans repo projects, verifies exact heads, and performs full source
preparation.
`MP01_SIGNER_COMPATIBILITY_MODE=test-key-audit` permits only the documented
exit-`3` non-flash audit result. Proprietary GMS, release signing, and OTA
publication remain disabled.

## Output Requirements

Every successful build must produce and retain:

- `system.img` whose legacy filename ends in `-unsigned`, but whose contents are
  accurately labeled test-key and not release-signed
- compressed image archive
- timestamped `*.sha256sums` completion file
- normalized, XML-validated resolved `repo manifest -r`
- build-info with target, support revision, source revisions, tools, and paths
- TrebleApp source, patch, signer, deterministic APK-content, and bytecode
  provenance embedded in build-info
- complete build log

Resolved-manifest capture must succeed before final image/archive copying and
checksum presentation. A failed manifest capture must not leave an apparently
complete candidate directory.

Before any device command, run `sha256sum --check` on the timestamped
`*.sha256sums` completion file from the image output directory. Both the image
and compressed archive must report `OK`; otherwise the test session stops.

## Candidate Criteria

The intended test-key output cannot enter device testing. A later artifact can
enter testing only after:

1. The committed post-write provider validation passes in the complete build
   without weakening the invariant.
2. The affected filesystem is verified/repaired offline and the build is rerun
   cleanly on verified storage.
3. Android policy, target-files, system image, and packaging complete.
4. Target-files TrebleApp and exact 14-entry inventory verification pass.
5. Outputs and metadata are audited together and all checksums pass.
6. Its exact target-files snapshot passes `release-candidate` mode at exit `0`
   with compatible APK and APEX container/payload identities and the required
   release-candidate disposition.
7. The exact final source state is staged through qpublish.
8. The operator approves the exact final signed artifact for a `system`-only,
   in-place flash and existing user data is preserved.

A `release-keys` property on the baseline is not certificate proof, and the
historical FinQwerty application key is unrelated to OS platform/APEX keys. The
final signed identity must pass an in-place hardware test. A clean install is
not the default and cannot turn a failed in-place candidate into a pass.

## Rollback Baseline

The accepted known-good baseline remains release `1755162498`, documented
in [`baseline-source-map-1755162498.md`](baseline-source-map-1755162498.md) and
[`../baselines/working-mp01-2026-05.md`](../baselines/working-mp01-2026-05.md).
Archive availability does not establish Android 16-to-15 downgrade safety. A
verified archive, sole extracted image filename/hash, complete 222-APK signer
inventory, five named OS APK/OTA key classes, AVB public key, and all 33 APEX
identities are now recorded. A separately approved, data-preserving hardware
downgrade that accounts for installed signer and data state is still required.
On failure, stop and preserve evidence without wiping or attempting a downgrade.
