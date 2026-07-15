# LineageOS 23.2 Migration

This records the move from LineageOS 22.2 / Android 15 to LineageOS 23.2 /
Android 16 as of July 15, 2026. The `ac3f97f` build attempt failed in Metalava.
The later `4bb063e` run stopped during Soong/Blueprint graph validation. A
full-graph synchronous diagnostic then passed both provider checks, the
production post-write fix was committed. Subsequent formal runs exposed and
fixed patch-state, no-kernel generated-header, e-ink fortify, and presigned
partner APK byte-preservation defects. The formal build from GSI head
`c88e039992760ada12f1df874453c2243d784862` and its independent audit completed
with `PASS_AUDIT_ONLY_NOT_FOR_IN_PLACE_FLASH`. The unsigned test-key artifact
is software-audit-only and never flash eligible. No Android 16 artifact has
been flashed.

## Prepared Source State

| Repo or input | Branch | Exact revision | Purpose |
| --- | --- | --- | --- |
| Failed predecessor build source | `lineage-23.2` | `ac3f97f43eafbacf4f222a6915429fae9d7c2a69` | The old runner reported source preparation passed, but later patch-state review invalidated that as proof of a complete patch stack. The full run exhausted Metalava's roughly 2 GiB ergonomic heap; it did not produce a candidate artifact. |
| Failed provider-validation build source | `lineage-23.2` | `4bb063e28116af3b4f4263c4cf6eed00b3829961` | Committed low-memory Metalava policy; the old runner reported cached-local reset and full source preparation passed, but that does not prove all patches were present. Blueprint's provider invariant stopped Soong bootstrap before Ninja. |
| Provider-validation fix | `lineage-23.2` | `4e94263d8871e26b32f8927f6f1d820a830a0a19` | Commits the production command-only post-write Blueprint patch. |
| Build-state/output-contract preflight | `lineage-23.2` | `3feebebfb20c6b424b05f4cbe5f1e72ca5b3e28f` | Tree `0e4a1879b5ce602c9e8f3cd61f5699fbe025b4ac`; owns workspace and build-state policy in-repository. Its formal run failed closed before graph generation because lunch reported the expected target product but used the `generic_arm64` product output directory. |
| Failed Soong graph/main Ninja generation | `lineage-23.2` | `c890b4015a505bbce0ae09761f0054de24d3d6c0` | Tree `871b1a1e59ee73e6fede1bbc1a7cbf69739c71d6`; product-output and TrebleApp checks passed and bootstrap reached `284/284`, but `continuous_native_tests` rejected the absolute host-JAR path while generating the main Ninja file. No target-files or artifact was produced. |
| Stopped relative-`OUT_DIR` build evidence | `lineage-23.2` | `612997762d55364f14b4157f745dcab190dd468c` | Tree `491273ae8e6909f4eaf3e30436263fd8ebd8c0ba`; the build was intentionally stopped at action `6632/153795` after review found the ad hoc transcript wrapper ignored `tee` status. It is evidence only and produced no artifact. |
| Formal transcript contract | `lineage-23.2` | `16aa5f8d47503debba428c01547aba91232f28b6` | Tree `8b051d945c9ee54d5429da5084f14cc45e5664b3`; adds the fail-closed contract-v1 `scripts/run-formal-build.sh` harness and isolated log helper. |
| Failed generated-header formal build | `lineage-23.2` | `3d1bfa4f4be14857b21dde879ec9f9e64a401c60` | Tree `8ccbad9c73c512d1f0bd480a78db5e0831a6391c`; the old patch runner falsely skipped forward-applicable patches and the build later failed when a no-kernel generated-header action invoked missing `headers_install`. Incomplete log SHA256 `6006d29d4a5f6ec348c3258985bbee2898abfd07bb74a3e042b05811a216dcc1`; no candidate. |
| Strict patch application | `lineage-23.2` | `11bdbbdb9a9789b00b6dfba986bfca4c72735cc7` | Tree `d71e422d41b351cb3ac93bf62f60c1194fb12af4`; exact Git reverse checks and zero-fuzz fallback fail closed. |
| No-kernel header fix / failed e-ink build | `lineage-23.2` | `cb9eab69b9500fa194a7e4adc72f110656ee2cf2` | Tree `277564406d298e3a0283c7dbfd2a42010715b74a`; exports `TARGET_NO_KERNEL` and preserves real-kernel generation. Its formal run passed generated headers, then failed on the e-ink daemon's stale `_FORTIFY_SOURCE=2`; incomplete log SHA256 `46bb6fd0eff47ffb14229477afb38c8e25b0ae6f9bdbd9b4d09332b4d36e0d8a`; no candidate. |
| Failed partner-APK signer audit | `lineage-23.2` | `2fd5dec31b3b9c98060ed81d29a666b653df05fe` | Tree `a931350da017ad19d18dd1b520c103c7ad417730`; fixes the e-ink fortify conflict and completes Android compilation, then fails closed because `FDroidPrivilegedExtension.apk` has lost its declared v2/v3 signing blocks. Incomplete-log SHA256 `6093a4960140dd5bdd29185cf7788f8c16e8f530f9a260afcc910b7a49e55b8a`; no candidate. |
| Disk-space preflight | `lineage-23.2` | `c88e039992760ada12f1df874453c2243d784862` | The first invocation stopped before source preparation because 227 GiB available was below that run's configured 250 GiB preflight threshold. Incomplete-log SHA256 `9e51db5870ec7bc14ecdfd953ca509a617181434169987e89db950f39aa81f82`; no artifact. |
| Final logical GSI / successful formal build | `lineage-23.2` | `c88e039992760ada12f1df874453c2243d784862` | Tree `9d4bfca308b640e2b28f58f3502af40a7adf0c21`; preserves and verifies the exact aligned bytes of all five presigned partner APKs, blocks test-key flashing workflows, passes all 143 GSI tests, and produced the sealed software-audit artifact set. |
| Publication GSI squash | `lineage-23.2` | `ae9299f0819ca9bd564859e96bce965007381e54` | Tree-identical bounded publication commit based on `origin/15`; staged for target `lineage-23.2` as `20260715-111324-MP01-LineageGSI-ae9299f0819c`. |
| `treble_manifest` | `lineage-23.2` | `fb1e1f76d353591caa2d991a3f8d92266249fe8e` | Fourteen exact input projects; removal of `vendor/gapps` leaves 13 effective custom projects. |
| `treble_app` | `master` | `9d8a6771d94b7985f515b41bd280f7bdb4554037` | Manifest source pin and Gradle dependency verification. |
| TrebleApp CI unit | `master` | `cee22d352a9c022d43e5384a29646898a94e45cd` | Build-only workflow, read-only contents permission, and commit-pinned actions. |
| `treble_presets` | `master` | `5891dba9621542b297acd761dbf3fe98d841c214` | Validated key, type, and action contracts for the MP01 preset. |
| `vendor_hardware_overlay` | `lineage-23.2` | `7cf73a0094e6448e0bb830fea996715fbd2fffc3` | API 36 build and Android 16 resource validation. |
| Overlay framework resources | `lineage-23.2` source | `46fd4b1f8d25b92540048c96ddc625b4ebeb6d60` | Exact public LineageOS framework revision used by overlay CI. |
| `finqwerty` mitigation | `master` | `a60a78160be024173c7eac11acc45e4db4e693f0` | Disables signing/publication; staged as `20260710-090346-finqwerty-a60a78160be0`. |
| `finqwerty` key deletion | `master` | `1b712b2a725d43233c03d768f4df6d4ef2e18883` | Local deletion; publication blocked by the current binary-diff policy pending an approved mechanism. |

`MP01-LineageGSI` is deliberately not present in `treble_manifest`. The build
driver checks it out separately and copies its build-support content into the
Android tree after rejecting a duplicate `LineageOS_gsi` source and removing
stale copied vendor directories. This keeps build orchestration out of the repo
source graph and prevents duplicate Soong modules.

Publication state varies by repository. Always inspect
`qpublish workspace-status`, outbox, and feedback before staging; do not blindly
restage merged, published, or already staged heads. Commit locally, stage with
`qstage` only where still required, and leave publication to `git-publish`; do
not push from the development qube.

At this capture, TrebleApp `9d8a677` and `treble_manifest` `fb1e1f7` are staged
as `20260710-095532-treble_app-9d8a6771d94b` and
`20260710-095546-treble_manifest-fb1e1f76d353`; their earlier predecessors are
upstream, but these exact heads are not yet published. Overlay `7cf73a0`, presets
`5891dba`, and FinQwerty mitigation `a60a781` are staged as
`20260710-090001-vendor_hardware_overlay-7cf73a0094e6`,
`20260710-090043-treble_presets-5891dba96215`, and
`20260710-090346-finqwerty-a60a78160be0`. The later FinQwerty binary deletion is
blocked by qpublish policy. The final GSI submission already supersedes its June
predecessor. MP01-OS uses its explicit June predecessor when staging the
documentation/auditor chain, as recorded in
[`action-items.md`](action-items.md).

## Source and Patch Gates

The failed `4bb063e` run used `MP01_SKIP_REPO_SYNC=1` only for cached-local repo
reset. Its old runner reported full source preparation, but later review showed
that GNU reverse dry-run could accept an unapplied patch with fuzz and report it
as already applied. That invalidates the old run as evidence of a complete patch
stack. Commit `11bdbbd` now uses an exact Git reverse check for already-applied
state and zero fuzz for the GNU fallback. Required patch tools, source paths,
expected base commits, and post-patch markers are checked before compilation.

The build also enforces bounded cleanup for copied GSI vendor inputs. It rejects
an independently synced `LineageOS_gsi` tree, removes stale `F-Droid`,
`MP01_services`, `finqwerty`, and `inkos` directories, then imports only the
current support versions. Source-preparation and primary make failures are
fatal.

Patch commits use `git am --committer-date-is-author-date`. The prepared tree
was verified to have matching author and committer dates, so patch history does
not vary with build time. The inactive `product.prop` patch, which carried
unverified performance and memory properties, has been removed.

The `2fd5dec` post-build failure was caused by Android's privileged-prebuilt
path uncompressing DEX content and realigning `GmsCore`, `FakeStore`, and
`FDroidPrivilegedExtension`, which changed their bytes and invalidated APK
signing blocks. `FDroid` and `GsfProxy` remained byte-identical. Head `c88e039`
pins patch SHA256
`146aa1a9307452217e087d818028bb158e8adf0a5a3a52e6bcaebe0665e7a1bf`.
It transforms `vendor/partner_gms` base commit/tree
`4b3b48033245800142045ce78038166f8aff6b01` /
`3c554b8fabffd2bdd0727aac770e403d9fec0505` into prepared commit/tree
`67e492737184fe9584750e07ad4c0ecfb40af67e` /
`06afb50166f27672b02c7b168b24de0bf30f8f21`. The source verifier requires one
exact byte-preserving Make definition for each of the five modules and no
competing Blueprint definition; the artifact verifier requires each source,
installed, and target-files APK to match its pinned SHA256 and pass zipalign.

The failed `ac3f97f` run is retained separately at
`.android-build/logs/mp01-final-ac3f97f-20260710T103529Z.log`. It reached the
`api-stubs-docs-non-updatable` Metalava action and stopped with
`java.lang.OutOfMemoryError: Java heap space`; this was a build failure, not a
candidate result.

GSI commit `4bb063e28116af3b4f4263c4cf6eed00b3829961` commits
`patches/personal/platform_build_soong/0001-soong-java-raise-metalava-heap-on-low-memory-builders.patch`.
The pinned patch adds `-J-Xmx6114m` only to Metalava and has SHA256
`5f1e4852e7455238c9997865bb7ba05a4e72ce2b60a8b07e4ae36e9400ee791c`.
Applying it to pinned `build/soong` base
`4035bec90f84b583a1502b9a546c6117a28fdbe2` deterministically produces commit
`58a9e2c3dced31247cf99651e0fd0bb04b4a4b0c` and tree
`b603556b58e5f79868622135d82b9f3f111553ae`.

On a host with at most 16 GiB of `MemTotal`, the build rejects any
`MP01_MAKE_JOBS` value other than `1`. It fixes `NINJA_HIGHMEM_NUM_JOBS=1`, and
the retained policy verifier has confirmed that the real combined Ninja file
contains exactly one `highmem_pool` with depth `1`. Before copied support files
are removed, the build preserves the source-bound verifier as
`.mp01/verify-metalava-heap-policy.py` and checks its hash before both prepared
Soong verification and the post-make Ninja attestation.

Every candidate run performs full source preparation. The script resets and
cleans repo projects, verifies exact source heads, and reapplies the complete
patch stack. `MP01_SKIP_REPO_SYNC=1` is optional only when every required object
is already cached locally; it skips network transfer, not reset, cleanup,
source verification, or patch application. There is no supported
skip-source-preparation candidate path.

## Verified Binary Inputs

The source gate verifies exact versions, immutable URLs, SHA256 values, APK
structure, and signing certificates where applicable for F-Droid, its
privileged extension, GmsCore, FakeStore `0.3.15.40226` (version code
`84022630`, release tag `v0.3.15.250932`), and GsfProxy. It also verifies the
checked-in source inkOS APK and exact Treble preset JSON. inkOS must identify as
package `app.inkos`, and
`com.github.gezimos.inkos.MainActivity` must be enabled with a MAIN/HOME intent
filter. A matching ZIP and hash without that semantic identity is rejected.
The later target-files inventory checks only that the exact inkOS path occurs
once; it does not repeat the source APK semantic check.

The source launcher is the immutable official `repo-2.65` object at
`https://storage.googleapis.com/git-repo-downloads/repo-2.65`, SHA256
`1211b57b57e4122a9c546295a59b37d24068f1164d0e87bef096d5323c413e4f`.
It initializes official git-repo tag `v2.65` and requires implementation commit
`35bbf701d04de5c6a71937279bc3d16f6ce36808`. Unexpected content fails before
source initialization.

## TrebleApp Gate

The manifest pins TrebleApp at
`9d8a6771d94b7985f515b41bd280f7bdb4554037`. That revision verifies the Gradle
7.5 distribution checksum and all resolved dependencies. Its strict release
build passes. The workflow grants read-only contents permission and pins
checkout, Java setup, and artifact upload actions by full commit.

The GSI helper applies exactly nine MP01 patches, refuses an unexpected patch
sequence or dirty source, and verifies eight required markers. Its JDK 17
prebuilt must be unsigned. It records every non-signature ZIP entry
deterministically and a `classes.dex` subcheck, then requires installed and
target-files APKs to have exactly one platform signer and identical
non-signature content.

The same target-files gate requires exactly one copy of 14 release-critical
entries: TrebleApp, `MP01AccessibilityService`, the e-ink daemon and init file,
the accessibility privapp whitelist, inkOS, the IDC/KL/KCM keyboard files,
GmsCore, FakeStore, GsfProxy, F-Droid, and the F-Droid privileged extension.
This is a path/count inventory; inkOS package and HOME-activity semantics were
verified earlier against the checked-in source APK.

## MP01 Runtime Corrections

- The e-ink command runner opens a fresh socket per command, propagates connect
  and write failures, and does not report failed automation delivery as success.
- The daemon parses newline-delimited streams correctly across split reads,
  multiple frames, CRLF, EOF, and oversized input. Authorized clients have a
  five-second read timeout; an incomplete frame is discarded on timeout so one
  stalled client cannot monopolize the server. Strict host C and JVM tests pass.
- Peer authorization, init mediation, a dedicated daemon domain, executable
  labels, and public/private MP01 SELinux packaging are present.
- The IDC selects extensionless layout name `aw9523b-key`; `.kl` and `.kcm`
  files are system-owned, and keymap preflight checks pass.
- Accessibility default enablement uses normalized component comparison,
  preserves other enabled services, and enables the platform accessibility
  switch only after the service-list write succeeds. The dead vendor property
  is removed, and the privapp whitelist installs with its required `.xml` name.
- FinQwerty is absent from the Android 16 product. Its historical keystore was
  exposed and is compromised. The text mitigation is staged; local binary
  deletion remains publication-blocked pending an approved qpublish mechanism.
  Any future release requires a new application identity.

## Overlay and CI Gates

Overlay commit `7cf73a0094e6448e0bb830fea996715fbd2fffc3` validates MP01
resources against exact LineageOS framework commit
`46fd4b1f8d25b92540048c96ddc625b4ebeb6d60` and builds all 452 overlays with
API 36. Its workflow uses read-only contents permission and full action commit
pins. The unverified MP01 power profile was removed.

## Provider Diagnostic, Fix, and Active Build Path

The retained log
`.android-build/logs/mp01-final-4bb063e28116-20260710T150914Z.log`, SHA256
`e70d2d4655faaecbe6907a5acecb2e1c52fae0e9e42d33fe9ef441686e2a5c8b`,
reports `provider ... was modified after being set` for install, module-info,
phony, compliance, filesystem, and super-image provider classes. It stopped
during Soong graph generation before Ninja, the target Metalava action,
target-files, or artifact packaging, and produced no candidate. The isolated
replay and policy tests validate the Metalava remediation, not this full build.
The provider failure was not reported as a filesystem I/O failure.

The prepared-tree diagnostic ran provider validation synchronously before and
after `WriteBuildFile`. The full Soong graph passed both checks without a
provider error. Compilation was intentionally stopped at 3% because the direct
command omitted `USE_CCACHE` and would serially rebuild roughly 170,000 actions.
The retained log is
`.android-build/logs/mp01-provider-pre-post-20260710T132726EDT.log`, SHA256
`dd23b844f916e0a35268a4654978b378e2b57f3369db643c832578bad4b9e4d8`.

Commit `4e94263d8871e26b32f8927f6f1d820a830a0a19` moves the unchanged
fail-closed invariant to a synchronous point after Ninja writing, flushing, and
action caching. The patch SHA256 is
`43cca96d3eb8d04a91a9b0637444889b62fe1a04a064910c68c2358e23326df1`;
Blueprint base commit/tree `c39c8a4c103f1393f015a5befa7726f0c14c9bc2` /
`690ca4cbc4c0d954a5de59dd13b1597f135c243a` becomes prepared commit/tree
`448557ea39c422f96412af18530133301f12cbb6` /
`5e79a8c9dcde279d368f9fdab2a5b4ff7d28ff35`.

The first formal `4e94263` invocation failed an external Codex-helper preflight
before source preparation and produced no artifact. Its log is
`.android-build/logs/mp01-final-4e94263d8871-20260710T203839Z.log`, SHA256
`2c09d82d450ee803f46fa179c3bfff8f2c2d1ba5ceb3e80d1774abbe29276b8b`.
Head `3feebebfb20c6b424b05f4cbe5f1e72ca5b3e28f` replaces that helper with
repository-owned, hash-checked workspace and build-state policy. Its formal run
failed closed before graph generation because lunch reported
`TARGET_PRODUCT=lineage_arm64_bmN4` while `ANDROID_PRODUCT_OUT` resolved under
`generic_arm64`. The retained log is
`.android-build/logs/mp01-final-3feebebfb20c-20260710T220742Z.log`, SHA256
`55157ea23dfa8795dbc84b512867eb40d7364a35caed1fa87f394d2f47809691`, and no
artifact was produced. Head `c890b4015a505bbce0ae09761f0054de24d3d6c0`
pins the actual product output name. Its formal run passed that lunch/output
contract and TrebleApp preparation and completed bootstrap `284/284`, then
failed during Soong graph/main Ninja-file generation at
`platform_testing/Android.bp:255:1`. Module `continuous_native_tests` rejected
the absolute `out/host/linux-x86/framework/net-tests-utils-host-common.jar`
path as outside the source directory. Main/product Ninja was not regenerated or
executed; target-files and publication were not reached. Its retained log is
`.android-build/logs/mp01-final-c890b4015a50-20260710T221230Z.log`, SHA256
`bac623467a00c6ef1c321c3ea1d18ea1370fe023d427f2d74397dfa01a201468`, from
`2026-07-10T22:12:30Z` through `2026-07-10T23:04:19Z`; wrapper duration
`00:51:49`, Android footer `48:53`, exit `1`. It produced no artifact or
publication residue and contains no I/O or OOM failure evidence. Head
`612997762d55364f14b4157f745dcab190dd468c` uses Android's relative `OUT_DIR`
interface while retaining canonical absolute containment checks. Its build was
intentionally stopped at action `6632/153795` after review found the ad hoc
wrapper ignored `tee` status. The retained evidence log is
`.android-build/logs/mp01-final-612997762d55-20260710T231231Z.log`, SHA256
`8dd8aa7ad75d6c1ac60264612931228bbb6cb6f892ffbbf35f28a76422ad44f5`, from
`2026-07-10T23:12:31Z` to `2026-07-11T01:52:04Z`; duration `02:39:33`,
intentional exit `141`. It produced no artifact or publication residue, and
the log contains no kernel I/O or OOM failure evidence.

Commit `16aa5f8d47503debba428c01547aba91232f28b6` adds the fail-closed
contract-v1 transcript harness. The harness/helper SHA256 values are
`938cc2842ca860704f727cfbd4f890227ccb93d44387f64e6be3f704b3403204` /
`cf8a04c7d334caeb177750b7f2e9c2855e2835e231f9e45d21933619fd9ead07`.
Head `3d1bfa4f4be14857b21dde879ec9f9e64a401c60` also removes current
test-key device commands from the GSI `README.md`, `ROUGHGUIDE.md`, and
`vendor/MP01_services/README.md`. Its formal run failed at no-kernel generated
headers; the retained incomplete log has SHA256
`6006d29d4a5f6ec348c3258985bbee2898abfd07bb74a3e042b05811a216dcc1`.
Commit `11bdbbd` makes patch application fail closed. Commit `cb9eab6` handles
generated headers for `TARGET_NO_KERNEL=true`; its formal run then exposed the
e-ink daemon's stale fortify override, with incomplete-log SHA256
`46bb6fd0eff47ffb14229477afb38c8e25b0ae6f9bdbd9b4d09332b4d36e0d8a`.
Head `2fd5dec31b3b9c98060ed81d29a666b653df05fe`, tree
`a931350da017ad19d18dd1b520c103c7ad417730`, removes that override. Its formal
run completed the primary Android build in `05:34:23`, then the signer audit
failed on the stripped `FDroidPrivilegedExtension.apk` signing blocks. The
retained staging log
`.android-build/logs/mp01-final-2fd5dec31b3b-20260712T200339Z-abcc08c367e1.log.incomplete`
has SHA256
`6093a4960140dd5bdd29185cf7788f8c16e8f530f9a260afcc910b7a49e55b8a`;
no final log or candidate was published. Final head
`c88e039992760ada12f1df874453c2243d784862`, tree
`9d4bfca308b640e2b28f58f3502af40a7adf0c21`, fixes that policy. All 143 GSI
tests pass.

The following block records the exact successful invocation. Its 250 GiB value is
the run-specific preflight guard, not a measured minimum or a LineageOS
requirement.

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

# Optional only when the complete source objects are already cached locally.
export MP01_SKIP_REPO_SYNC=1

bash scripts/run-formal-build.sh
```

The committed harness captures both build and `tee` status and refuses to
publish a final log on either failure. It binds contract v1 to the exact clean
GSI HEAD/tree, harness/helper hashes, signer mode, start-epoch inode, and log
inode; it rechecks repository and helper integrity after the build and fsyncs
before atomic final publication. An initial `c88e039` invocation stopped in the
disk-space preflight with 227 GiB available against that run's configured
250 GiB threshold; its
retained incomplete-log SHA256 is
`9e51db5870ec7bc14ecdfd953ca509a617181434169987e89db950f39aa81f82`.
After space was reclaimed, the successful run used cached-local repo reset, not
preparation reuse: it still performed full cleanup, exact-head verification,
and patch application. It started at epoch `1784095155`, completed Android in
`08:47:27`, and published artifact epoch `1784126958`. The complete final log is
`.android-build/logs/mp01-final-c88e03999276-20260715T055915Z-93cb550cc58a.log`,
SHA256 `87681b4c33c0d9584cb5067b223c2f92219544dfafd1147017511d49d0f25d3a`.
The explicit `test-key-audit` signer mode retained verifier exit `3`,
`INCOMPATIBLE`, and `NOT_FOR_IN_PLACE_FLASH`; it cannot authorize an in-place
flash or release. The sampled free-space low-water was `255.39 GiB` and final
ccache was `14.3 GB`; this incremental/cached run is not clean-build
calibration.

This target intentionally builds only a system image and has
`TARGET_NO_KERNEL=true`. Despite requested enforcement, the Make warning means
the kernel inputs to build-time `checkvintf` and the OTA kernel metadata are
omitted, not passed; it is not kernel compatibility or OTA evidence.
Exact-device `VtsTrebleVintfTest`
`SystemVendorTest.KernelCompatibility` remains pending, and OTA publication is
disabled.

The target is `lineage_arm64_bmN4-bp4a-userdebug`. FinQwerty, signed release
packaging, OTA publication, and proprietary GMS packaging remain disabled.
`sign.sh` now exits with an error instead of invoking an obsolete Android 15
key map, so it cannot create a misleading partial release. GSI `README.md`,
`ROUGHGUIDE.md`, and `vendor/MP01_services/README.md` no longer expose current
test-key device commands.

The full build completed Android policy, target-files, system image, and
artifact packaging. It retained the resolved manifest, image, archive,
timestamped `*.sha256sums` completion file, build-info with embedded TrebleApp
provenance, and full log. The XML-validated normalized manifest records the
LineageOS platform and 13 effective custom projects; GSI support is recorded
separately in build-info. All 47 auditor unit tests passed, and the retained
independent audit sealed the evidence directory documented in the candidate
test report.

The selected archive is exactly
`.android-build/los23.2-microg/out/target/product/generic_arm64/obj/PACKAGING/target_files_intermediates/lineage_arm64_bmN4-target_files.zip`,
SHA256 `86c77ab15594caf1b1dfc5a585c1023b781690489b82507c7a48a347be75fe2a`.
Its sole `IMAGES/system.img` is byte-identical to the published image. All 14
required entries and all five partner APK hashes/alignment checks passed.
`TARGET_NO_KERNEL=true`; no kernel image or metadata is present. Build and publication locks,
no-overwrite checks, staged files, cleanup, and checksum-last publication prevent
plausible partial output sets.

## Remaining Before Device Testing

1. Preserve the sealed `PASS_AUDIT_ONLY_NOT_FOR_IN_PLACE_FLASH` software evidence.
2. Take the affected `xvdb` filesystem offline for the appropriate check and
   repair, verify a clean result, and rebuild cleanly on verified storage. The
   filesystem warning is not claimed as the provider failure's cause.
3. Re-run and audit the full package set on verified storage.
4. Complete qpublish review of staged GSI submission
   `20260715-111324-MP01-LineageGSI-ae9299f0819c` and the exact staged MP01-OS
   documentation/auditor state.
5. Produce a compatible final release-signed candidate or reviewed rotation
   path; the complete current comparison has 750 incompatibilities and cannot be
   flashed.
6. Verify the timestamped `*.sha256sums` completion file against both the image
   and archive before any device command.
7. Flash `system` only for that final signer-compatible identity as an in-place
   upgrade and run the candidate report and hardware matrix.

Existing phone data is the default preservation target. Approval to flash
`system` does not authorize a wipe, erase, recovery reset, or factory reset.
Any clean-install exception requires separate explicit approval for that exact
session. A baseline `release-keys` tag and the FinQwerty application key are not
OS signer proof. On failure, stop and preserve evidence without wiping or
assuming an Android 16-to-15 downgrade is safe. OTA remains blocked until the
final signed identity passes the hardware gate.
