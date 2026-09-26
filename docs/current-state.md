# Current State

This captures the project state as of July 15, 2026. The known source,
Android-output, and presigned-partner-APK blockers are fixed. The formal build
from GSI head `c88e039992760ada12f1df874453c2243d784862` and its independent
audit completed with `PASS_AUDIT_ONLY_NOT_FOR_IN_PLACE_FLASH`. The unsigned
test-key artifact is software-audit-only and never flash eligible. No Android 16
image has been flashed, so no source-level result in this document is a hardware
result.

The workspace-root `REBOOT_RESUME_NOTE.md` and
`SESSION_REPORT_2026-06-25.md` are retained only as historical records, not as
operational instructions. Current work must follow this document,
[`action-items.md`](action-items.md), and
[`reproducible-build.md`](reproducible-build.md).

## Accepted Hardware Baseline

The in-use MP01 runs original release `1755162498`, installed in 2025 as a clean
install and accepted as the known-good working baseline. Its reconstructed
source map is incomplete because the inherited build used moving branches and
latest-release downloads. The archive and sole inner image are verified, and a
public audit records all 222 released-image APK signer identities, five named
APK/OTA key classes, the AVB public key, and all 33 APEX identities.
Installed-state compatibility and an Android 16-to-15 hardware downgrade are
unverified, so this is not an authorized downgrade procedure.

See [`../baselines/working-mp01-2026-05.md`](../baselines/working-mp01-2026-05.md)
and
[`baseline-source-map-1755162498.md`](baseline-source-map-1755162498.md).

## Active Android 16 Target

- Android base: LineageOS 23.2 / Android 16.
- Product: `lineage_arm64_bmN4` / Minimal MP01.
- Lunch target: `lineage_arm64_bmN4-bp4a-userdebug`.
- Filesystem: EXT4.
- Intended variant: local microG userdebug image built with test keys; not
  release-signed and not flash-eligible.
- Release signing, OTA publication, and proprietary GMS packaging: disabled.
  Target-files signer compatibility verification is enforced before inventory,
  extraction, hashing, or artifact publication.

The product includes inkOS, `MP01AccessibilityService`,
`MP01_eink_server`, the freshly patched TrebleApp, F-Droid, the F-Droid
privileged extension, and microG packages. The system-owned `aw9523b-key` input
files replace the former FinQwerty product dependency.

## Exact Prepared Inputs

| Input | Exact revision | State |
| --- | --- | --- |
| `treble_manifest` | `fb1e1f76d353591caa2d991a3f8d92266249fe8e` | Fourteen exact input projects; `vendor/gapps` is removed, leaving 13 effective custom projects and no `LineageOS_gsi`; staged as `20260710-095546-treble_manifest-fb1e1f76d353`. |
| `treble_app` | `9d8a6771d94b7985f515b41bd280f7bdb4554037` | Manifest source pin, strict Gradle dependency verification, and passing release build; staged as `20260710-095532-treble_app-9d8a6771d94b`. |
| TrebleApp CI unit | `cee22d352a9c022d43e5384a29646898a94e45cd` | Build-only CI, read-only contents permission, and commit-pinned actions. |
| `treble_presets` | `5891dba9621542b297acd761dbf3fe98d841c214` | Key, type, and action contract tests pass. |
| `vendor_hardware_overlay` | `7cf73a0094e6448e0bb830fea996715fbd2fffc3` | API 36 build and MP01 Android 16 resource validation pass. |
| Overlay framework input | `46fd4b1f8d25b92540048c96ddc625b4ebeb6d60` | Exact public LineageOS framework resource commit used by overlay CI. |
| `finqwerty` mitigation | `a60a78160be024173c7eac11acc45e4db4e693f0` | Signing/publication disabled; staged as `20260710-090346-finqwerty-a60a78160be0`; no Android 16 product role. |
| `finqwerty` key deletion | `1b712b2a725d43233c03d768f4df6d4ef2e18883` | Clean local deletion; publication blocked because current qpublish policy rejects the binary diff. |
| Failed GSI build attempt | `ac3f97f43eafbacf4f222a6915429fae9d7c2a69` | The old runner reported source preparation passed, but later patch-state review invalidated that as proof of a complete patch stack. Metalava exhausted its Java heap; log `.android-build/logs/mp01-final-ac3f97f-20260710T103529Z.log`, SHA256 `e790c3d04352a436810b4f747ec76aed8763c5052d93f937f4544a8513f71e30`. |
| Failed GSI provider-validation build | `4bb063e28116af3b4f4263c4cf6eed00b3829961` | Adds the committed low-memory Metalava controls. The old runner reported full source preparation passed, but that does not prove all patches were present. It failed the final Soong/Blueprint provider invariant. Log `.android-build/logs/mp01-final-4bb063e28116-20260710T150914Z.log`, SHA256 `e70d2d4655faaecbe6907a5acecb2e1c52fae0e9e42d33fe9ef441686e2a5c8b`; no candidate artifact was produced. |
| Confirmed synchronous diagnostic | `dd23b844f916e0a35268a4654978b378e2b57f3369db643c832578bad4b9e4d8` | Log `.android-build/logs/mp01-provider-pre-post-20260710T132726EDT.log`; the full Soong graph passed both synchronous pre- and post-write checks, then compilation was intentionally interrupted at 3% because this direct diagnostic omitted `USE_CCACHE` and would serially rebuild about 170,000 actions. |
| Provider-validation fix | `4e94263d8871e26b32f8927f6f1d820a830a0a19` | Commits the command-only post-write Blueprint patch. The first formal invocation failed an external Codex-helper preflight before source preparation; log `.android-build/logs/mp01-final-4e94263d8871-20260710T203839Z.log`, SHA256 `2c09d82d450ee803f46fa179c3bfff8f2c2d1ba5ceb3e80d1774abbe29276b8b`; no artifact was produced. |
| Build-state/output-contract preflight | `3feebebfb20c6b424b05f4cbe5f1e72ca5b3e28f` | Tree `0e4a1879b5ce602c9e8f3cd61f5699fbe025b4ac`; adds repository-owned workspace and build-state policy. The formal run failed closed before graph generation because lunch reported `TARGET_PRODUCT=lineage_arm64_bmN4` but `ANDROID_PRODUCT_OUT` resolved under `generic_arm64`. Log `.android-build/logs/mp01-final-3feebebfb20c-20260710T220742Z.log`, SHA256 `55157ea23dfa8795dbc84b512867eb40d7364a35caed1fa87f394d2f47809691`; no artifact was produced. |
| Failed Soong graph/main Ninja generation | `c890b4015a505bbce0ae09761f0054de24d3d6c0` | Tree `871b1a1e59ee73e6fede1bbc1a7cbf69739c71d6`; the product-output and TrebleApp checks passed and bootstrap reached `284/284`, but `continuous_native_tests` rejected the absolute host-JAR path while generating the main Ninja file. Log `.android-build/logs/mp01-final-c890b4015a50-20260710T221230Z.log`, SHA256 `bac623467a00c6ef1c321c3ea1d18ea1370fe023d427f2d74397dfa01a201468`; wrapper duration `00:51:49`, exit `1`. No target-files, publication residue, artifact, or phone operation resulted; the log has no I/O or OOM failure evidence. |
| Stopped relative-`OUT_DIR` build evidence | `612997762d55364f14b4157f745dcab190dd468c` | Tree `491273ae8e6909f4eaf3e30436263fd8ebd8c0ba`; supplies Android's relative output interface. The build was intentionally stopped at action `6632/153795` after review found its ad hoc wrapper ignored `tee` status. Log `.android-build/logs/mp01-final-612997762d55-20260710T231231Z.log`, SHA256 `8dd8aa7ad75d6c1ac60264612931228bbb6cb6f892ffbbf35f28a76422ad44f5`; duration `02:39:33`, intentional exit `141`. No artifact, publication residue, kernel I/O failure, or OOM evidence resulted. |
| Formal transcript contract | `16aa5f8d47503debba428c01547aba91232f28b6` | Tree `8b051d945c9ee54d5429da5084f14cc45e5664b3`; adds `scripts/run-formal-build.sh` and its isolated contract-v1 log helper. Harness/helper SHA256: `938cc2842ca860704f727cfbd4f890227ccb93d44387f64e6be3f704b3403204` / `cf8a04c7d334caeb177750b7f2e9c2855e2835e231f9e45d21933619fd9ead07`. |
| Failed generated-header formal build | `3d1bfa4f4be14857b21dde879ec9f9e64a401c60` | Tree `8ccbad9c73c512d1f0bd480a78db5e0831a6391c`; the old patch runner falsely skipped forward-applicable patches, then the no-kernel GSI failed because `generated_kernel_includes` invoked a missing `headers_install` target. Incomplete log `.android-build/logs/mp01-final-3d1bfa4f4be1-20260711T024331Z-fd587786d599.log.incomplete`, SHA256 `6006d29d4a5f6ec348c3258985bbee2898abfd07bb74a3e042b05811a216dcc1`; no candidate. |
| Strict patch application | `11bdbbdb9a9789b00b6dfba986bfca4c72735cc7` | Tree `d71e422d41b351cb3ac93bf62f60c1194fb12af4`; exact Git reverse checks and zero-fuzz fallback prevent false ALREADY APPLIED results. |
| No-kernel generated-header policy | `cb9eab69b9500fa194a7e4adc72f110656ee2cf2` | Tree `277564406d298e3a0283c7dbfd2a42010715b74a`; exports `TARGET_NO_KERNEL` and preserves real-kernel generation while giving no-kernel GSIs an empty include root. Its formal run passed this gate, then failed on the e-ink daemon's stale `_FORTIFY_SOURCE=2` override. Incomplete log `.android-build/logs/mp01-final-cb9eab69b950-20260711T235938Z-90c3aa8cf054.log.incomplete`, SHA256 `46bb6fd0eff47ffb14229477afb38c8e25b0ae6f9bdbd9b4d09332b4d36e0d8a`; no candidate. |
| Failed partner-APK signer audit | `2fd5dec31b3b9c98060ed81d29a666b653df05fe` | Tree `a931350da017ad19d18dd1b520c103c7ad417730`; fixes the e-ink fortify conflict and completes the primary Android build in `05:34:23`, then fails closed when the post-build audit finds `FDroidPrivilegedExtension.apk` missing its declared v2/v3 signing blocks. Incomplete log `.android-build/logs/mp01-final-2fd5dec31b3b-20260712T200339Z-abcc08c367e1.log.incomplete`, SHA256 `6093a4960140dd5bdd29185cf7788f8c16e8f530f9a260afcc910b7a49e55b8a`; no final log or candidate. |
| `c88e039` disk-space preflight | `c88e039992760ada12f1df874453c2243d784862` | Stopped before source preparation because 227 GiB available was below that run's configured 250 GiB preflight threshold. Incomplete log `.android-build/logs/mp01-final-c88e03999276-20260715T055348Z-0b4bf6f7177e.log.incomplete`, SHA256 `9e51db5870ec7bc14ecdfd953ca509a617181434169987e89db950f39aa81f82`; no artifact. |
| Final logical GSI / successful formal build | `c88e039992760ada12f1df874453c2243d784862` | Tree `9d4bfca308b640e2b28f58f3502af40a7adf0c21`; preserves exact bytes and alignment for all five presigned partner APKs and passes 143 GSI tests. Android completed in `08:47:27`; final log `.android-build/logs/mp01-final-c88e03999276-20260715T055915Z-93cb550cc58a.log`, SHA256 `87681b4c33c0d9584cb5067b223c2f92219544dfafd1147017511d49d0f25d3a`. Independent audit result: `PASS_AUDIT_ONLY_NOT_FOR_IN_PLACE_FLASH`. |
| Publication GSI squash | `ae9299f0819ca9bd564859e96bce965007381e54` | Based on `origin/15` with a tree equivalent to the final logical head; staged for target `lineage-23.2` as qpublish submission `20260715-111324-MP01-LineageGSI-ae9299f0819c`, superseding the stale June GSI submission. |

`MP01-LineageGSI` is an external build-support checkout. It supplies the build
driver, product files, patch stack, release-input definitions, and MP01 vendor
files, but it is not a project in `treble_manifest`. The support checkout is
copied into the Android tree only after duplicate-tree and stale-vendor cleanup.

## Gates That Pass

- The failed `4bb063e28116af3b4f4263c4cf6eed00b3829961` run completed a
  cached-local repo reset from the existing depth-bounded object cache. Its old
  runner reported all source-preparation patches applied, but the later fuzzy
  reverse-match finding invalidated that claim as complete-stack evidence. It
  did not claim a new network sync. Commit `11bdbbd` now requires exact reverse
  state and zero-fuzz fallback application; the successful run applied the formerly
  skipped patches and passed the persistent source verifiers.
- Duplicate GSI source and stale copied vendor trees are rejected or removed
  before Soong sees the graph. Primary source and make failures propagate.
- The immutable official `repo-2.65` launcher verifies at SHA256
  `1211b57b57e4122a9c546295a59b37d24068f1164d0e87bef096d5323c413e4f`.
  Repo initialization pins official implementation tag `v2.65` and verifies
  commit `35bbf701d04de5c6a71937279bc3d16f6ce36808`.
- Exact version, URL, SHA256, APK validity, and signing-certificate checks pass
  for the downloaded partner APK inputs, including FakeStore `0.3.15.40226`,
  version code `84022630`, from release tag `v0.3.15.250932`. The checked-in
  source inkOS APK must also be package `app.inkos` with enabled activity
  `com.github.gezimos.inkos.MainActivity` exposing one MAIN/HOME filter. The
  exact preset JSON verifies.
- Root-cause analysis of the `2fd5dec` failure showed the privileged-prebuilt
  Make path uncompressed DEX content and realigned `GmsCore`, `FakeStore`, and
  `FDroidPrivilegedExtension`, invalidating their APK signing blocks. `FDroid`
  and `GsfProxy` stayed byte-identical. Head `c88e039` applies patch SHA256
  `146aa1a9307452217e087d818028bb158e8adf0a5a3a52e6bcaebe0665e7a1bf`
  to `vendor/partner_gms` base commit/tree
  `4b3b48033245800142045ce78038166f8aff6b01` /
  `3c554b8fabffd2bdd0727aac770e403d9fec0505`, producing prepared commit/tree
  `67e492737184fe9584750e07ad4c0ecfb40af67e` /
  `06afb50166f27672b02c7b168b24de0bf30f8f21`.
- The TrebleApp source passes strict Gradle dependency verification. The GSI
  helper applies exactly nine patches, verifies eight artifact markers, builds
  an intentionally unsigned prebuilt with JDK 17, records every non-signature
  ZIP entry deterministically plus a `classes.dex` subcheck, and replaces the
  stale overlay prebuilt. Installed and target-files copies must each have
  exactly one platform signer and identical non-signature content.
- The e-ink command transport creates a connection per command and reports
  delivery failure. Its newline stream parser passes split-frame, multi-frame,
  CRLF, EOF, overflow, and partial-frame discard host tests. A client read has a
  five-second timeout so an incomplete sender cannot hold the single-client
  daemon indefinitely; timed-out partial input is discarded. The JVM command
  runner tests pass.
- The e-ink daemon boundary, init mediation, MP01 SELinux packaging, and focused
  policy checks pass.
- The extensionless `aw9523b-key` IDC reference and system keymap preflight pass.
- Preset contract tests and all 452 API 36 overlay builds pass.
- `git am --committer-date-is-author-date` makes generated patch commits stable;
  author and committer dates were verified equal in the prepared tree. The
  inactive, questionable `product.prop` patch is no longer applied.
- Every candidate performs full source reset, cleanup, exact-head verification,
  and patch application. Optional `MP01_SKIP_REPO_SYNC=1` uses cached repo
  objects but does not skip source preparation. The product must contain exactly
  one preset property equal to the verified URL.
- The failed `ac3f97f43eafbacf4f222a6915429fae9d7c2a69` action was reproduced
  independently: both 4 GiB and 6 GiB heap replays completed with byte-identical
  outputs, while the 4 GiB replay used about 3.997 GiB at peak. The retained
  replay summary has SHA256
  `8ec28ac68ac52bedb5b856985a5a19700a445bb23678bc83e01668aedc90a680`.
  Commit `4bb063e28116af3b4f4263c4cf6eed00b3829961` configures the Metalava
  invocation with `-J-Xmx6114m`; on hosts with no more than 16 GiB it requires
  `MP01_MAKE_JOBS=1`, fixes and verifies the combined Ninja high-memory pool at
  depth `1`, and hash-checks the same retained `.mp01` verifier before and after
  primary make. Build-info records host-memory, jobs, pool, heap, Soong/JDK, and
  verifier provenance.
- The retained synchronous diagnostic log has SHA256
  `dd23b844f916e0a35268a4654978b378e2b57f3369db643c832578bad4b9e4d8`.
  Its complete Soong graph passed the existing provider invariant both before
  and after `WriteBuildFile`. Compilation was intentionally stopped at 3% after
  5,669 of roughly 177,000 actions because the direct command omitted
  `USE_CCACHE`; this was not a provider-validation failure.
- GSI commit `4e94263d8871e26b32f8927f6f1d820a830a0a19` moves the unchanged
  fail-closed provider check out of the concurrent writer path and runs it after
  Ninja serialization and action caching. Head `3feebeb` adds repository-owned
  workspace and build-state policy; its output-contract preflight exposed the
  `generic_arm64` product-directory mapping before graph generation. Head
  `c890b4015a505bbce0ae09761f0054de24d3d6c0` pins that mapping; its formal run
  subsequently exposed Android's relative-`OUT_DIR` requirement during Soong
  graph/main Ninja generation. Head
  `612997762d55364f14b4157f745dcab190dd468c` supplies that interface, but its
  build was stopped after the transcript wrapper was found not to preserve
  `tee` status. Commit `16aa5f8` adds the fail-closed contract-v1 harness.
  Commit `11bdbbd` makes patch-state detection exact; `cb9eab6` handles
  generated headers for no-kernel targets; `2fd5dec` removes the e-ink daemon's
  stale fortify override; and final head `c88e039` adds the fail-closed
  presigned-partner byte policy. All 143 GSI policy tests pass.
- Accessibility boot setup compares normalized component names, preserves other
  enabled services, sets `ACCESSIBILITY_ENABLED`, and removes the dead
  `persist.accessibility.enabled_service` product property. The whitelist keeps
  its source `.xml` filename when installed under `system/etc/permissions`.
- `sign.sh` fails closed because LineageOS 23.2 release signing is not ported. It
  cannot emit a plausible signed artifact or update OTA state. Separately, the
  build creates one private read-only target-files snapshot and uses only that
  snapshot for signer comparison, inventory, TrebleApp verification,
  `system.img` extraction, hashing, and publication. Release mode requires
  verifier exit `0` and compatibility. Explicit `test-key-audit` mode accepts
  only exit `3` plus `NOT_FOR_IN_PLACE_FLASH`; every other outcome fails closed.
  The pinned complete baseline manifest has SHA256
  `0e0313015d4bba28f8fe85d91498d060a7c525d81980f3f100efeb7f3628dd03`
  and covers 222 APK paths for 221 packages plus 33 APEX identities. Build-info
  embeds that baseline identity, the actual manifest, and complete comparison
  evidence.
- The real target-files signer-gate smoke under
  `/home/user/MP01-LineageOS/logs/signer-gate/801bf4a-real-smoke-20260710/` has a
  passing `SHA256SUMS` and
  records verifier exit `3`, comparison `INCOMPATIBLE`, and disposition
  `NOT_FOR_IN_PLACE_FLASH`. This proves gate behavior, not completion of a full
  target-files build or comparison.
- GSI commit `3d1bfa4f4be14857b21dde879ec9f9e64a401c60` removes current
  test-key device commands from `README.md`, `ROUGHGUIDE.md`, and
  `vendor/MP01_services/README.md`. Those files now state the signer, storage,
  hardware, and operator-approval blockers instead of offering a current
  flashing workflow.

## Provider Diagnostic and Formal Fix

The retained `4bb063e` log records `provider ... was modified after being set`
for install-file, module-info, phony, compliance-metadata, filesystem, and super
image providers. Affected modules include `vim`, `bash`, `nano`, `htop`,
`libncurses` variants, `libncurses-terminfo-a`, and the generated system, super,
and device modules. Soong bootstrap stopped before target-files or image
packaging. This was not another Metalava heap failure, and the build log does
not attribute it to a filesystem read or write error. The run stopped during
Soong graph generation before Ninja and did not exercise the target Metalava
action; only the isolated replay and focused policy tests validate the heap
remediation so far.

The prepared-tree diagnostic ran the existing invariant synchronously before and
after `WriteBuildFile`. The full Soong graph completed both checks without any
provider mutation report. Its retained log is
`.android-build/logs/mp01-provider-pre-post-20260710T132726EDT.log`, SHA256
`dd23b844f916e0a35268a4654978b378e2b57f3369db643c832578bad4b9e4d8`.
The following compile reached 3% before an intentional interruption: the direct
diagnostic omitted `USE_CCACHE` and would have serially rebuilt approximately
170,000 actions. It was a localization run, not a final artifact build.

The production patch is
`patches/personal/platform_build_blueprint/0001-blueprint-serialize-provider-validation.patch`,
SHA256 `43cca96d3eb8d04a91a9b0637444889b62fe1a04a064910c68c2358e23326df1`.
It applies to Blueprint base commit/tree
`c39c8a4c103f1393f015a5befa7726f0c14c9bc2` /
`690ca4cbc4c0d954a5de59dd13b1597f135c243a` and produces prepared commit/tree
`448557ea39c422f96412af18530133301f12cbb6` /
`5e79a8c9dcde279d368f9fdab2a5b4ff7d28ff35`. The command-only change preserves
the existing fail-closed check and executes it synchronously after writing,
flushing, and caching Ninja actions, without a competing graph traversal.

The first formal invocation from `4e94263` stopped at preflight because it still
depended on an external Codex workspace-path helper. It performed no source
preparation and produced no artifact. Commit `3feebebfb20c6b424b05f4cbe5f1e72ca5b3e28f`
replaces that dependency with hash-checked repository-owned workspace and build
state policy. Its formal run reached lunch, then failed the output contract
before graph generation because `TARGET_PRODUCT=lineage_arm64_bmN4` maps to
the `generic_arm64` product directory. Commit
`c890b4015a505bbce0ae09761f0054de24d3d6c0` pins that actual directory. Its
formal run passed the corrected product-output and TrebleApp contracts and
completed bootstrap `284/284`. During Soong graph/main Ninja-file generation,
module `continuous_native_tests` at `platform_testing/Android.bp:255:1` rejected
the absolute `out/host/linux-x86/framework/net-tests-utils-host-common.jar` path
as outside the source directory. Main/product Ninja was not regenerated or
executed, and target-files and publication were not reached. The retained log
contains no I/O or OOM failure evidence. Commit
`612997762d55364f14b4157f745dcab190dd468c` changes only the Android-facing
interface to relative `OUT_DIR=out` while retaining the canonical absolute path
checks. Its build was intentionally stopped at action `6632/153795` after
review found the ad hoc wrapper ignored `tee` status. The retained log covers
`2026-07-10T23:12:31Z` through `2026-07-11T01:52:04Z`, has SHA256
`8dd8aa7ad75d6c1ac60264612931228bbb6cb6f892ffbbf35f28a76422ad44f5`, and
ends with intentional exit `141`; it produced no artifact or publication
residue and contains no kernel I/O or OOM failure evidence.

Commit `16aa5f8d47503debba428c01547aba91232f28b6` replaces that ad hoc
wrapper with `scripts/run-formal-build.sh`. During execution, contract v1 writes
only the private `.log.incomplete` staging file. It publishes the final `.log`
identity and completion sentinel only after build/capture success, exact GSI
HEAD/tree and harness/helper integrity checks, contract validation, and fsync.
The `2fd5dec` run started at epoch `1783886619`, completed Android compilation,
and then failed its post-build signer audit. Its retained `.log.incomplete`
hashes to `6093a4960140dd5bdd29185cf7788f8c16e8f530f9a260afcc910b7a49e55b8a`;
the corresponding final `.log` was never published. The first `c88e039`
invocation stopped in disk-space preflight and retained no candidate. The rerun
started at epoch `1784095155`, completed Android in `08:47:27`, and published
artifact epoch `1784126958`. Its complete contract-v1 log is
`.android-build/logs/mp01-final-c88e03999276-20260715T055915Z-93cb550cc58a.log`,
SHA256 `87681b4c33c0d9584cb5067b223c2f92219544dfafd1147017511d49d0f25d3a`.
The independently sealed result is
`PASS_AUDIT_ONLY_NOT_FOR_IN_PLACE_FLASH`.

This is a system-image-only no-kernel GSI. Despite requested enforcement, the
Make warning about absent kernel information means the kernel inputs to
build-time `checkvintf` and the OTA kernel metadata are omitted, not passed.
Exact-device `VtsTrebleVintfTest`
`SystemVendorTest.KernelCompatibility` remains pending. OTA publication stays
disabled.

The completed Android build used `$ANDROID_PRODUCT_OUT` basename
`generic_arm64`. The post-build gate and independent auditor verified target
files at
`.android-build/los23.2-microg/out/target/product/generic_arm64/obj/PACKAGING/target_files_intermediates/lineage_arm64_bmN4-target_files.zip`,
SHA256 `86c77ab15594caf1b1dfc5a585c1023b781690489b82507c7a48a347be75fe2a`.
They verified its complete 616-APK/44-APEX signer manifest, target-files
TrebleApp signer, whole non-signature ZIP-entry manifest, and `classes.dex`
subcheck. Each of these 14 MP01/microG paths occurs exactly once:
TrebleApp, the accessibility service and its privapp whitelist, the e-ink daemon
and init file, inkOS, three keyboard-map files, GmsCore, FakeStore, GsfProxy,
F-Droid, and the F-Droid privileged extension. That target-files check is a
path/count inventory; the source inkOS package and HOME activity are verified
separately before the Android build.

The published image is byte-identical to the archive's sole
`IMAGES/system.img`. `TARGET_NO_KERNEL=true`; no kernel image or kernel metadata
is present. The resolved manifest was XML-validated and normalizes only the
local override fetch URL while retaining exact revisions. Build and publication
locks rejected concurrency, output paths were not overwritten, outputs were
staged, and the timestamped `*.sha256sums` completion file was published last.

## Release Inputs and CI

Release inputs fail closed. The build pins the immutable repo launcher and exact
F-Droid, F-Droid privileged extension, GmsCore, FakeStore, GsfProxy, inkOS, and
preset payloads. It records their provenance rather than accepting latest
downloads.

TrebleApp and overlay workflows grant only read access to repository contents
and pin `actions/checkout`, `actions/setup-java`,
`android-actions/setup-android`, and `actions/upload-artifact` by full commit.
TrebleApp also checks the Gradle distribution checksum and dependency metadata.

## FinQwerty Status

FinQwerty is retained only for Android 15 source archaeology. Its former release
keystore was committed in repository history and must be treated as compromised.
Staged commit `a60a78160be024173c7eac11acc45e4db4e693f0` disables release
signing/publication, pins CI, and warns about the exposed identity. Local commit
`1b712b2a725d43233c03d768f4df6d4ef2e18883` deletes the tracked keystore, but
publication is blocked pending an approved qadmin/`git-publish` mechanism for
the binary deletion. Any future FinQwerty release needs a newly generated
application identity kept outside the repository.

## Artifact State

The unsigned Android 15 image and archive under
`../images/archive/lineage-22.2-unsigned-20260617/` are quarantined historical
artifacts. They are neither the Android 16 candidate nor the accepted working
baseline.

The audited Android 16 software artifact set is:

- image `MP01-Lineage-1784126958-microG-unsigned.img`, 2,888,388,608 bytes,
  SHA256 `3853a868d0c7ed16a6800e7ca9d677a3223fcf935be7cdc86b3dc61d0ad97400`;
- archive `MP01-Lineage-1784126958-microG-unsigned.tar.gz`, 1,387,725,550
  bytes, SHA256
  `cc171a2dabb5ab70d473c875c5420923f5c15a774d516cea5a0129883d787fd7`;
- completion-file, resolved-manifest, and build-info SHA256 values
  `ebe457232d2d3fa91e39338e29f5860337b9ca5e8b71e5222c7bca9e69cb125b`,
  `ece2fc1f579f006f9f7a71f1adcaae836ed27d7b6bceffc0f852b6984f8930a6`,
  and `3c08b7544ea84e5632c6a25cb144683ff7b7ca4c18146b0e4f8a5e96afedd05b`;
- retained evidence directory
  `/home/user/MP01-LineageOS/logs/mp01-final-c88e03999276-20260715T055915Z-93cb550cc58a-audit`,
  with its external sibling `.root.sha256`; evidence-manifest SHA256
  `98351dd90323101da3d8c3a5e88238509974306b748c20553fd406f0ad379ab2`.

All 47 auditor unit tests passed. The retained independent audit returned
`PASS_AUDIT_ONLY_NOT_FOR_IN_PLACE_FLASH`. It verified all five partner APKs,
the 14-entry target-files inventory, and image equality. The signer result is
`INCOMPATIBLE` / `NOT_FOR_IN_PLACE_FLASH`: 616 APKs, 44 APEXes, 750
incompatibilities, and 0 warnings. This unsigned test-key output is never flash
eligible.

The sampled free-space low-water mark was `255.39 GiB` and final ccache size
was `14.3 GB`. This was an incremental/cached run, not clean-build calibration;
the configured 250 GiB preflight override is not a LineageOS or platform floor.

The development host logged one EXT4 inode-checksum error for inode `22850323`
on `/dev/xvdb` during an unrelated broad file search on July 10. The failed
build path did not emit a filesystem read or write error, so that warning is not
claimed as the cause of the provider failure. It nevertheless leaves the build
volume unverified. Outside the live build session, the operator must preserve
needed evidence, take the affected filesystem offline/unmounted, complete the
appropriate filesystem check and repair, and verify a clean result. Android
outputs must then be rebuilt cleanly from the exact committed inputs on verified
storage. Work produced before those steps remains software-audit-only and cannot
be treated as a release candidate.

The formal artifact set and complete target-files comparison are audited
together, but that software result does not make an Android 16 artifact eligible
for device testing. Its platform, shared, media, release/default, network-stack,
APK, and APEX identities are incompatible with the baseline. A compatible final
identity or reviewed rotation path remains required before any device test.

## Remaining Gates

1. Preserve the sealed audit and keep its output software-audit-only.
2. Verify/repair the affected filesystem offline, then run a clean full build on
   verified storage and complete post-build package verification.
3. Capture and audit all artifact metadata and checksums from that clean build;
   use its resource measurements to calibrate a clean-build disk guard.
4. Complete qpublish review for the staged tree-equivalent GSI and MP01-OS
   documentation/auditor states. Do not push from the development qube.
5. Produce a compatible final release-signed candidate or reviewed rotation
   path; the current complete comparison is incompatible.
6. Obtain operator approval and test that exact signed identity as a
   `system`-only, in-place upgrade that preserves data. Keep OTA disabled until
   this hardware gate passes.

Before any future device command, verify the timestamped `*.sha256sums`
completion file and signer-compatibility evidence. A `release-keys` tag is not
certificate proof, and FinQwerty keys are unrelated to OS keys. On failure, stop
and preserve evidence; do not erase, wipe, factory reset, or assume an Android
15 downgrade is safe.
