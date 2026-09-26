# MP01 Android 16 Candidate Test Report

This copy is the completed software-audit-only record for 2026-07-15. The formal
build and retained host audit completed, but the artifact was not tested on an
MP01 and no device command was issued. Its unsigned test-key identity is
incompatible with the installed baseline, so this record never authorizes a
flash. Keep private device identifiers and unredacted logs outside git.

## Build and Artifact Identity

- Build and audit result: `PASS_AUDIT_ONLY_NOT_FOR_IN_PLACE_FLASH`
- Earlier completed artifact-building formal attempt: `FAILED (PRESIGNED
  PARTNER APK SIGNING BLOCKS STRIPPED; NO CANDIDATE PRODUCED)`
- First `c88e039` invocation: `PREFLIGHT STOP (227 GIB AVAILABLE;
  BELOW THIS RUN'S CONFIGURED 250 GIB GUARD; NO SOURCE PREPARATION OR ARTIFACT)`;
  retained incomplete-log
  SHA256 `9e51db5870ec7bc14ecdfd953ca509a617181434169987e89db950f39aa81f82`
- Successful formal build: GSI
  `c88e039992760ada12f1df874453c2243d784862`; start epoch `1784095155`;
  artifact epoch `1784126958`; Android build duration `08:47:27`; complete
  contract-v1 log
  `/home/user/MP01-LineageOS/.android-build/logs/mp01-final-c88e03999276-20260715T055915Z-93cb550cc58a.log`,
  SHA256 `87681b4c33c0d9584cb5067b223c2f92219544dfafd1147017511d49d0f25d3a`
- Test date: `2026-07-15` (software audit only)
- Operator: Codex host-side audit; no device operator session was opened
- Build variant: `lineage_arm64_bmN4-bp4a-userdebug`, test-key audit mode
- Signing status and signer-manifest identity: unsigned Android test-key output;
  pinned complete baseline manifest `mp01-1755162498-public-signers-v1.tsv` at
  SHA256
  `0e0313015d4bba28f8fe85d91498d060a7c525d81980f3f100efeb7f3628dd03`
- Complete signer result: `INCOMPATIBLE`, `NOT_FOR_IN_PLACE_FLASH`; 616 APKs,
  44 APEXes, 750 incompatibilities, and 0 warnings
- Software-audit-only record: `YES`; never flash eligible
- Platform: Android 16 / LineageOS 23.2
- Image: `/home/user/MP01-LineageOS/images/MP01-Lineage-1784126958-microG-unsigned.img`
  (2,888,388,608 bytes), SHA256
  `3853a868d0c7ed16a6800e7ca9d677a3223fcf935be7cdc86b3dc61d0ad97400`
- Compressed archive:
  `/home/user/MP01-LineageOS/images/MP01-Lineage-1784126958-microG-unsigned.tar.gz`
  (1,387,725,550 bytes), SHA256
  `cc171a2dabb5ab70d473c875c5420923f5c15a774d516cea5a0129883d787fd7`
- Timestamped `*.sha256sums` completion file:
  `/home/user/MP01-LineageOS/images/metadata/MP01-Lineage-1784126958-microG-unsigned.sha256sums`,
  SHA256 `ebe457232d2d3fa91e39338e29f5860337b9ca5e8b71e5222c7bca9e69cb125b`
- Build-info:
  `/home/user/MP01-LineageOS/images/metadata/MP01-Lineage-1784126958-microG-unsigned.build-info.txt`,
  SHA256 `3c08b7544ea84e5632c6a25cb144683ff7b7ca4c18146b0e4f8a5e96afedd05b`
- Resolved repo manifest:
  `/home/user/MP01-LineageOS/images/metadata/MP01-Lineage-1784126958-microG-unsigned.repo-manifest.xml`,
  SHA256 `ece2fc1f579f006f9f7a71f1adcaae836ed27d7b6bceffc0f852b6984f8930a6`
- Android product output: `$ANDROID_PRODUCT_OUT` with basename
  `generic_arm64`
- Exact target-files archive:
  `/home/user/MP01-LineageOS/.android-build/los23.2-microg/out/target/product/generic_arm64/obj/PACKAGING/target_files_intermediates/lineage_arm64_bmN4-target_files.zip`
  (2,816,727,540 bytes), SHA256
  `86c77ab15594caf1b1dfc5a585c1023b781690489b82507c7a48a347be75fe2a`
- `IMAGES/system.img`: byte-identical to the published image
- Timestamped `*.sha256sums` completion-file verification: `PASS`
- Retained audit evidence:
  `/home/user/MP01-LineageOS/logs/mp01-final-c88e03999276-20260715T055915Z-93cb550cc58a-audit`
- External evidence-root checksum:
  `/home/user/MP01-LineageOS/logs/mp01-final-c88e03999276-20260715T055915Z-93cb550cc58a-audit.root.sha256`
- Evidence manifest SHA256:
  `98351dd90323101da3d8c3a5e88238509974306b748c20553fd406f0ad379ab2`
- Sampled free-space low-water mark: `255.39 GiB`; final ccache size:
  `14.3 GB`. These measurements came from an incremental/cached run and are not
  clean-build calibration. The configured 250 GiB guard was a project
  preflight override, not a LineageOS or platform floor.

These host-artifact checks passed. Do not record a device result unless a future
signer-compatible release identity is separately approved and tested on the
phone.

## Source Provenance

- Final logical `MP01-LineageGSI` build-support commit:
  `c88e039992760ada12f1df874453c2243d784862` (tree
  `9d4bfca308b640e2b28f58f3502af40a7adf0c21`)
- Tree-equivalent GSI publication squash:
  `ae9299f0819ca9bd564859e96bce965007381e54`, based on `origin/15`; its tree is
  identical to the logical head. It is staged for target `lineage-23.2` as
  qpublish submission `20260715-111324-MP01-LineageGSI-ae9299f0819c`
- GSI source used by the successful formal build:
  `c88e039992760ada12f1df874453c2243d784862` (tree
  `9d4bfca308b640e2b28f58f3502af40a7adf0c21`)
- Formal harness commit: `16aa5f8d47503debba428c01547aba91232f28b6`
- Formal harness/helper SHA256:
  `938cc2842ca860704f727cfbd4f890227ccb93d44387f64e6be3f704b3403204` /
  `cf8a04c7d334caeb177750b7f2e9c2855e2835e231f9e45d21933619fd9ead07`
- Run mode: cached-local repo reset with `MP01_SKIP_REPO_SYNC=1`, followed by
  full cleanup, exact-head verification, and source preparation
- `treble_manifest`:
  `fb1e1f76d353591caa2d991a3f8d92266249fe8e`
- `treble_app` manifest source:
  `9d8a6771d94b7985f515b41bd280f7bdb4554037`
- TrebleApp build-only CI unit:
  `cee22d352a9c022d43e5384a29646898a94e45cd`
- `treble_presets`:
  `5891dba9621542b297acd761dbf3fe98d841c214`
- `vendor_hardware_overlay`:
  `7cf73a0094e6448e0bb830fea996715fbd2fffc3`
- Overlay framework resources:
  `46fd4b1f8d25b92540048c96ddc625b4ebeb6d60`
- FinQwerty staged signing/publication mitigation:
  `a60a78160be024173c7eac11acc45e4db4e693f0`
- FinQwerty local key deletion, publication-blocked by binary-diff policy:
  `1b712b2a725d43233c03d768f4df6d4ef2e18883`

The preceding build attempt used GSI commit
`ac3f97f43eafbacf4f222a6915429fae9d7c2a69`. It failed at
`//frameworks/base/api:api-stubs-docs-non-updatable metalava merged` with
`java.lang.OutOfMemoryError: Java heap space`; it did not produce a candidate.
Its log is
`/home/user/MP01-LineageOS/.android-build/logs/mp01-final-ac3f97f-20260710T103529Z.log`
at SHA256
`e790c3d04352a436810b4f747ec76aed8763c5052d93f937f4544a8513f71e30`.
Commit `4bb063e28116af3b4f4263c4cf6eed00b3829961` adds the bounded
`-J-Xmx6114m` Metalava policy and serial low-memory build enforcement. The
source patch SHA256 is
`5f1e4852e7455238c9997865bb7ba05a4e72ce2b60a8b07e4ae36e9400ee791c`;
the prepared `build/soong` commit/tree is
`58a9e2c3dced31247cf99651e0fd0bb04b4a4b0c` /
`b603556b58e5f79868622135d82b9f3f111553ae`. The 143-test GSI policy suite,
focused Droidstubs tests, deterministic source replay, and real combined-Ninja
depth check passed. The
isolated replay summary at
`/home/user/MP01-LineageOS/.android-build/tmp/metalava-89e80645-metalava_heap_repro/metalava-heap-repro-summary.log`
has SHA256
`8ec28ac68ac52bedb5b856985a5a19700a445bb23678bc83e01668aedc90a680`;
the exact failed action completed with both 6 GiB and 4 GiB heaps and produced
byte-identical outputs. That validates the Metalava remediation in isolation,
not a complete full build.

The later `4bb063e` full-build log is
`/home/user/MP01-LineageOS/.android-build/logs/mp01-final-4bb063e28116-20260710T150914Z.log`,
SHA256
`e70d2d4655faaecbe6907a5acecb2e1c52fae0e9e42d33fe9ef441686e2a5c8b`.
It stopped during Soong graph generation on Blueprint's
`provider ... was modified after being set` invariant, before Ninja, the target
Metalava action, target-files, or image packaging. The build therefore did not
exercise the Metalava remediation. Its log does not report filesystem I/O
failure.

The synchronous diagnostic then completed the full Soong graph with the
existing provider invariant passing both before and after `WriteBuildFile`.
Compilation was intentionally stopped at 3% because the direct command omitted
`USE_CCACHE` and would serially rebuild roughly 170,000 actions. Its log is
`/home/user/MP01-LineageOS/.android-build/logs/mp01-provider-pre-post-20260710T132726EDT.log`,
SHA256
`dd23b844f916e0a35268a4654978b378e2b57f3369db643c832578bad4b9e4d8`.

GSI commit `4e94263d8871e26b32f8927f6f1d820a830a0a19` commits the
command-only post-write Blueprint patch. It retains the fail-closed invariant
after Ninja writing, flushing, and action caching. The patch SHA256 is
`43cca96d3eb8d04a91a9b0637444889b62fe1a04a064910c68c2358e23326df1`;
the Blueprint base commit/tree is
`c39c8a4c103f1393f015a5befa7726f0c14c9bc2` /
`690ca4cbc4c0d954a5de59dd13b1597f135c243a`, and the prepared commit/tree is
`448557ea39c422f96412af18530133301f12cbb6` /
`5e79a8c9dcde279d368f9fdab2a5b4ff7d28ff35`.

The first formal `4e94263` invocation failed before source preparation because
the external Codex workspace helper was absent; it produced no artifact. Its log
is `.android-build/logs/mp01-final-4e94263d8871-20260710T203839Z.log`, SHA256
`2c09d82d450ee803f46fa179c3bfff8f2c2d1ba5ceb3e80d1774abbe29276b8b`.
Head `3feebebfb20c6b424b05f4cbe5f1e72ca5b3e28f` replaces that helper with
repository-owned workspace and build-state policy. Its formal run failed closed
before graph generation because lunch reported
`TARGET_PRODUCT=lineage_arm64_bmN4` but placed `ANDROID_PRODUCT_OUT` under
`generic_arm64`. Its log is
`.android-build/logs/mp01-final-3feebebfb20c-20260710T220742Z.log`, SHA256
`55157ea23dfa8795dbc84b512867eb40d7364a35caed1fa87f394d2f47809691`; no
artifact was produced. Head `c890b4015a505bbce0ae09761f0054de24d3d6c0`
pins the actual product output directory. Its formal run passed the product
output and TrebleApp checks and completed bootstrap `284/284`, then failed while
Soong generated the main Ninja file. At `platform_testing/Android.bp:255:1`,
module `continuous_native_tests` rejected the absolute
`out/host/linux-x86/framework/net-tests-utils-host-common.jar` path as outside
the source directory. Main/product Ninja was not regenerated or executed;
target-files, publication, and phone operations were not reached. The retained
log is `.android-build/logs/mp01-final-c890b4015a50-20260710T221230Z.log`, SHA256
`bac623467a00c6ef1c321c3ea1d18ea1370fe023d427f2d74397dfa01a201468`, start
`2026-07-10T22:12:30Z`, end `2026-07-10T23:04:19Z`, wrapper duration `00:51:49`,
Android footer `48:53`, exit `1`. It produced no artifact or publication residue,
and the log contains no I/O or OOM failure evidence. Head
`612997762d55364f14b4157f745dcab190dd468c` supplies Android's relative
`OUT_DIR` interface while retaining canonical absolute containment checks. Its
build was intentionally stopped at action `6632/153795` after review found the
ad hoc wrapper ignored `tee` status. Its evidence log is
`.android-build/logs/mp01-final-612997762d55-20260710T231231Z.log`, SHA256
`8dd8aa7ad75d6c1ac60264612931228bbb6cb6f892ffbbf35f28a76422ad44f5`, from
`2026-07-10T23:12:31Z` to `2026-07-11T01:52:04Z`; duration `02:39:33`,
intentional exit `141`. It produced no artifact or publication residue, and the
log contains no kernel I/O or OOM failure evidence.

Commit `16aa5f8d47503debba428c01547aba91232f28b6` adds the contract-v1
fail-closed transcript harness. Head
`3d1bfa4f4be14857b21dde879ec9f9e64a401c60` removes current test-key device
commands from the GSI guidance. Its formal run exposed the old patch runner's
false ALREADY APPLIED result and later failed when no-kernel generated-header
generation invoked missing `headers_install`. Its retained incomplete log is
`.android-build/logs/mp01-final-3d1bfa4f4be1-20260711T024331Z-fd587786d599.log.incomplete`,
SHA256
`6006d29d4a5f6ec348c3258985bbee2898abfd07bb74a3e042b05811a216dcc1`.
It produced no candidate.

Commit `11bdbbdb9a9789b00b6dfba986bfca4c72735cc7`, tree
`d71e422d41b351cb3ac93bf62f60c1194fb12af4`, replaces fuzzy reverse patch
state detection with exact Git checks and zero-fuzz fallback application.
Commit `cb9eab69b9500fa194a7e4adc72f110656ee2cf2`, tree
`277564406d298e3a0283c7dbfd2a42010715b74a`, exports
`TARGET_NO_KERNEL` and preserves real-kernel header generation while giving
no-kernel targets an empty generated include root. Its formal run passed this
gate, then failed because the e-ink daemon's `_FORTIFY_SOURCE=2` conflicted with
Android 16's toolchain-provided level 3. Its retained incomplete log is
`.android-build/logs/mp01-final-cb9eab69b950-20260711T235938Z-90c3aa8cf054.log.incomplete`,
SHA256
`46bb6fd0eff47ffb14229477afb38c8e25b0ae6f9bdbd9b4d09332b4d36e0d8a`.
It produced no candidate.

Head `2fd5dec31b3b9c98060ed81d29a666b653df05fe`, tree
`a931350da017ad19d18dd1b520c103c7ad417730`, removes that stale fortify
override. The third contract-v1 run, at this head, completed the primary Android
build in `05:34:23`, then failed closed in the post-build signer audit because
`SYSTEM/product/priv-app/FDroidPrivilegedExtension/FDroidPrivilegedExtension.apk`
no longer contained the v2/v3 signing blocks declared by its JAR signature. The
retained staging log is
`.android-build/logs/mp01-final-2fd5dec31b3b-20260712T200339Z-abcc08c367e1.log.incomplete`,
SHA256
`6093a4960140dd5bdd29185cf7788f8c16e8f530f9a260afcc910b7a49e55b8a`.
No final log or candidate was published.

Root-cause comparison showed Android's privileged-prebuilt path had uncompressed
DEX content and realigned `GmsCore`, `FakeStore`, and
`FDroidPrivilegedExtension`, changing their bytes and invalidating the signing
blocks. `FDroid` and `GsfProxy` remained byte-identical. Final head
`c88e039992760ada12f1df874453c2243d784862`, tree
`9d4bfca308b640e2b28f58f3502af40a7adf0c21`, pins a byte-preserving policy for
all five modules. Its patch SHA256 is
`146aa1a9307452217e087d818028bb158e8adf0a5a3a52e6bcaebe0665e7a1bf`;
`vendor/partner_gms` base commit/tree
`4b3b48033245800142045ce78038166f8aff6b01` /
`3c554b8fabffd2bdd0727aac770e403d9fec0505` becomes prepared commit/tree
`67e492737184fe9584750e07ad4c0ecfb40af67e` /
`06afb50166f27672b02c7b168b24de0bf30f8f21`. Source policy rejects missing,
duplicate, or competing definitions, and the artifact gate requires each
source, installed, and target-files copy to match its pinned hash and pass
zipalign. All 143 GSI tests and all 47 auditor unit tests pass. The successful
formal run and the retained independent audit both verified the five exact APK
byte identities and alignment.

The target is a system-image-only no-kernel GSI. Despite requested enforcement,
the Make warning about missing kernel information means the kernel inputs to
build-time `checkvintf` and the OTA kernel metadata are omitted, not passed. It
is not kernel compatibility or OTA evidence. Exact-device `VtsTrebleVintfTest`
`SystemVendorTest.KernelCompatibility` remains pending. OTA publication remains
disabled.

`MP01-LineageGSI` is an external build-support checkout, not a project in the
repo manifest. The audited resolved manifest contains the LineageOS platform
and 13 effective custom projects: `treble_manifest` declares 14 input projects,
but the microG override removes `vendor/gapps`. It contains neither
`LineageOS_gsi` nor `vendor/gapps`. Build-info embeds both GSI support and
TrebleApp provenance; no standalone TrebleApp provenance artifact is expected.

## Signing Compatibility Evidence

- Baseline public-identity audit:
  `/home/user/MP01-LineageOS/logs/mp01-baseline/release-assets/public-identity-audit/README.md`
- Baseline audit SHA256:
  `0b0d5ad0fbaf69053c8679926b7ff6932cbd11f8b32860c6679fc6aad48c90ff`
- Baseline 222-path APK signer TSV SHA256 (221 unique packages):
  `ff7167528971e0fccc84cfbfccc2c9842d7be27d1f5cb9b77edea6f234f8da9c`
- Baseline 33-entry APEX signer TSV SHA256:
  `f7b48cd972fa58e9ce7b9710927edd0772e0792e9706b86ea60c8b9941ead93b`
- Baseline AVB public-key SHA1:
  `cdbb77177f731920bbe0a0f94f84d9038ae0617d`

| Role | Baseline certificate SHA256 | Current source certificate SHA256 |
| --- | --- | --- |
| Platform | `6a8c75f0fc84f7b4c7a4eadf443ddebe938ff0abde332ee1516fb91e756c447e` | `c8a2e9bccf597c2fb6dc66bee293fc13f2fc47ec77bc6b2b0d52c11f51192ab8` |
| Release/default | `c495956b1d898dc8731040f4a48256b30144b4958198687e076023f234cf70aa` | `a40da80a59d170caa950cf15c18c454d47a39b26989d8b640ecd745ba71bf5dc` |
| Shared | `9e8207aa328db085fffc5c2a6e32fa425bed1f6d68e0eb169091e4a4b73e378a` | `28bbfe4a7b97e74681dc55c2fbb6ccb8d6c74963733f6af6ae74d8c3a6e879fd` |
| Media | `4decc623b85f6024ffaa39d98f9ea1ba23caf7d82354240b8dcb6dea4c83b499` | `465983f7791f2abeb43ea2cbdc7f21a8260b72bc08a55c839fc1a43bc741a81e` |
| Network stack | `f96c390a48c0093291ed09714635ccccc4ee6e3e555dd08cb48878377bed1028` | `e1dbadce60dc080d15b58a014b0dcf9400e24de23fa00b287a5a982bfebda2ee` |

All comparable current source classes differ from the baseline. These source
values are expected test-key identities, not confirmation of actual target-files
contents and not upgrade compatibility.

- Signer-gate mode: `test-key-audit`
- Expected manifest coverage: complete, with 222 APK paths representing 221
  packages and 33 APEX packages
- Durable smoke coverage: `1 APK / 1 APEX`; this was a preliminary gate exercise
- Durable smoke comparison status: `INCOMPATIBLE`
- Durable smoke flash disposition: `NOT_FOR_IN_PLACE_FLASH`
- Audited target-files coverage: 616 APKs and 44 APEXes
- Audited target-files signer comparison: `INCOMPATIBLE`; 750
  incompatibilities and 0 warnings
- Audited target-files flash disposition: `NOT_FOR_IN_PLACE_FLASH`
- Complete target-files signer evidence embedded in build-info: `PASS`
- Compatible final identity or reviewed rotation path: `FAIL (UNAVAILABLE)`
- Durable real-gate smoke evidence:
  `/home/user/MP01-LineageOS/logs/signer-gate/801bf4a-real-smoke-20260710/`
  (`SHA256SUMS` verified); run-log SHA256
  `bf546f21c09ba31c9fe05fc80a9d4e4b0d566cfc524898c8ae38ece2538d1aff`

The durable smoke proved fail-closed gate behavior. The sealed formal build then
produced the complete package/APEX comparison above. Flashing remains blocked
by that incompatible test-key identity, the unavailable compatible
signing/rotation path, and the audit-only disposition.

## Software Gate Evidence

| Gate | Result | Evidence / notes |
| --- | --- | --- |
| Historical cached-local source-preparation claim | `INVALIDATED` | Failed `4bb063e` reached Soong after the old runner reported preparation passed, but the later fuzzy reverse-match finding means that run does not prove a complete patch stack. |
| Duplicate GSI tree and stale-vendor cleanup passed | `PASS` | Preparation rejected duplicate/stale paths and continued. |
| Strict complete patch stack applied without fuzz | `PASS` | Commit `11bdbbd` uses exact reverse checks and zero-fuzz fallback; the successful run applied the formerly skipped patches and source verifiers passed. |
| Prepared patch commits have matching author/committer dates | `PASS` | Deterministic prepared-source audit passed. |
| Inactive `product.prop` patch is absent | `PASS` | Source audit passed. |
| `2fd5dec` full source preparation and exact preset URL check passed | `PASS` | The failed run completed strict reset, patch application, source verification, and the preset gate before compilation. |
| Historical `4bb063e` Soong/Blueprint provider validation | `FAIL` | The run stopped on the provider-mutation invariant before Ninja and produced no candidate. |
| Synchronous pre/post-write provider diagnostic | `PASS` | The full graph passed both checks; compilation was intentionally interrupted at 3% because the direct diagnostic omitted `USE_CCACHE`. |
| Production post-write patch and repository-owned workspace/build-state policy | `PASS` | Exact Blueprint provenance is pinned and all 143 GSI tests pass. |
| `3feebeb` product-output contract | `FAIL CLOSED` | Lunch selected `TARGET_PRODUCT=lineage_arm64_bmN4` but resolved output under `generic_arm64`; the run stopped before graph generation and produced no artifact. |
| `c890b40` Soong graph/main Ninja-file generation | `FAIL CLOSED` | The corrected product-output and TrebleApp contracts passed and bootstrap reached `284/284`; `continuous_native_tests` then rejected an absolute host-JAR path. Main/product Ninja did not run and no target-files, publication, or artifact resulted. |
| `6129977` relative-`OUT_DIR` build | `STOPPED` | Intentionally stopped at `6632/153795` after the ad hoc wrapper was found not to preserve `tee` status; retained as evidence only, with no artifact or publication residue. |
| Contract-v1 formal transcript harness | `PASS` | Commit `16aa5f8`; exact harness/helper hashes are pinned, both pipeline statuses are captured, and final log publication is fail-closed. |
| Current test-key device-command exposure | `PASS` | GSI `README.md`, `ROUGHGUIDE.md`, and `vendor/MP01_services/README.md` no longer expose current test-key device commands. |
| `3d1bfa4` no-kernel generated-header build | `FAIL CLOSED` | The retained incomplete log records missing `headers_install`; no candidate or final log was published. |
| Strict patch-state policy | `PASS` | Commit `11bdbbd` fixes the false ALREADY APPLIED classification and regression-tests the exact Oplus case. |
| `cb9eab6` no-kernel header / e-ink build | `FAIL CLOSED` | Generated headers passed; the e-ink daemon's stale fortify override then failed compilation. No candidate or final log was published. |
| `2fd5dec` formal full build | `FAIL CLOSED` | Primary Android compilation completed; the post-build signer audit detected stripped v2/v3 signing blocks in `FDroidPrivilegedExtension.apk`. Retained incomplete-log SHA256 `6093a4960140dd5bdd29185cf7788f8c16e8f530f9a260afcc910b7a49e55b8a`; no final log or candidate was published. |
| Presigned partner APK source/build policy | `PASS` | Head `c88e039` pins the exact partner patch/prepared tree, requires one byte-preserving definition for each of five modules, rejects competing definitions, and passes all 143 GSI tests. |
| First `c88e039` invocation | `FAIL CLOSED` | Disk-space preflight stopped before source preparation with 227 GiB available against that run's configured 250 GiB threshold. Retained incomplete-log SHA256 `9e51db5870ec7bc14ecdfd953ca509a617181434169987e89db950f39aa81f82`; no artifact. |
| `c88e039` formal full build and retained audit | `PASS_AUDIT_ONLY_NOT_FOR_IN_PLACE_FLASH` | Android completed in `08:47:27`; the complete contract-v1 log and independently sealed evidence are identified above. This is software-audit-only, not flash authorization. |
| Kernel VINTF compatibility | `PENDING` | `TARGET_NO_KERNEL=true` makes this a system-image-only GSI; despite requested enforcement, the Make warning means kernel inputs to build-time `checkvintf` and OTA kernel metadata are omitted rather than passed. Exact-device `VtsTrebleVintfTest` `SystemVendorTest.KernelCompatibility` has not run, and OTA remains disabled. |
| Immutable official `repo-2.65` hash and implementation commit `35bbf701d04de5c6a71937279bc3d16f6ce36808` verified | `PASS` | Exact launcher and implementation inputs were verified. |
| Clean live/support, manifest, TrebleApp, and overlay exact heads verified and recorded in build-info | `PASS` | Exact heads and source attestations are embedded in the audited build-info. |
| Partner APK version, URL, hash, and certificate checks passed | `PASS` | Pinned input checks passed during preparation. |
| Installed and target-files partner APK byte identity and alignment | `PASS` | The build and independent auditor verified all five source, installed, and target-files copies against their pinned SHA256 values and canonical zipalign checks. |
| Source inkOS package and enabled MAIN/HOME activity verified | `PASS` | Pinned source APK audit passed. |
| Treble preset contract tests passed | `PASS` | 60 presets and 111 definitions passed contract validation. |
| TrebleApp Gradle dependency verification passed | `PASS` | Pinned Gradle build completed during preparation. |
| Exactly nine TrebleApp patches and eight APK markers verified | `PASS` | Persistent provenance records 9 patches and 8 markers. |
| TrebleApp prebuilt is unsigned; deterministic non-signature ZIP manifest and DEX subcheck recorded | `PASS` | Expected unsigned prebuilt and deterministic content evidence are present. |
| Installed TrebleApp has exactly one platform signer and matches all prebuilt non-signature ZIP entries | `PASS` | Installed APK SHA256 `2a81f826c6cab70ae6a98c5e4d22ef2e11565cb995646f97f413c4d5b8a8fe11`; content manifest and DEX checks passed. |
| Target-files TrebleApp has exactly one platform signer and matches all prebuilt non-signature ZIP entries | `PASS` | Target-files APK has the same SHA256, platform signer, content manifest, and DEX identity as the installed copy. |
| Exact 14-entry target-files path/count inventory verified | `PASS` | Each required path occurs exactly once. |
| Accessibility whitelist installed under its source `.xml` name | `PASS` | The final target-files inventory contains the exact required path once. |
| E-ink stream/framing host tests passed | `PASS` | Host C framing tests passed. |
| Five-second e-ink timeout and partial-frame discard test passed | `PASS` | Timeout and next-client recovery host tests passed. |
| E-ink command-runner JVM tests passed | `PASS` | Per-command connection and failure propagation tests passed. |
| MP01 service and SELinux policy compiled | `PASS` | Focused service/policy validation and final target-files integration passed. |
| Extensionless `aw9523b-key` input mapping validated | `PASS` | Host keymap preflight passed. |
| API 36 overlay build and exact framework-resource check passed | `PASS` | All 452 overlays passed against the pinned resources. |
| Effective manifest has 13 custom projects, exact revisions, normalized local fetch URL, and valid XML | `PASS` | The captured manifest SHA256 is `ece2fc1f579f006f9f7a71f1adcaae836ed27d7b6bceffc0f852b6984f8930a6`. |
| Exact target-files archive path/SHA256 recorded; sole `IMAGES/system.img` used for publication | `PASS` | The audited `IMAGES/system.img` is byte-identical to the published image. |
| Build/publication locks, no-overwrite checks, staged output, and checksum-last completion passed | `PASS` | The complete contract-v1 log and timestamped completion file were independently audited. |
| Obsolete signing path fails closed and OTA is disabled | `PASS` | Signing cannot create an obsolete partial release; OTA remains disabled. |
| Image/archive checksums verified | `PASS` | The retained audit independently verified both artifacts and the completion file. |

Any failed software gate blocks flashing. Passing them does not authorize the
intended test-key output.

## Target-Files Inventory

Each exact path below occurs once in the audited archive. This inventory does
not decode inkOS package/activity semantics; that separate source APK gate is
recorded in the software evidence table above.

| Required path | Result |
| --- | --- |
| `SYSTEM/priv-app/TrebleApp/TrebleApp.apk` | `PASS` |
| `SYSTEM/priv-app/MP01AccessibilityService/MP01AccessibilityService.apk` | `PASS` |
| `SYSTEM/bin/MP01_eink_server` | `PASS` |
| `SYSTEM/etc/init/MP01_eink_daemon.rc` | `PASS` |
| `SYSTEM/etc/permissions/privapp-permissions-accessibility.xml` | `PASS` |
| `SYSTEM/app/inkos/inkos.apk` | `PASS` |
| `SYSTEM/usr/idc/aw9523b-key.idc` | `PASS` |
| `SYSTEM/usr/keylayout/aw9523b-key.kl` | `PASS` |
| `SYSTEM/usr/keychars/aw9523b-key.kcm` | `PASS` |
| `SYSTEM/product/priv-app/GmsCore/GmsCore.apk` | `PASS` |
| `SYSTEM/product/priv-app/FakeStore/FakeStore.apk` | `PASS` |
| `SYSTEM/product/app/GsfProxy/GsfProxy.apk` | `PASS` |
| `SYSTEM/product/app/FDroid/FDroid.apk` | `PASS` |
| `SYSTEM/product/priv-app/FDroidPrivilegedExtension/FDroidPrivilegedExtension.apk` | `PASS` |

`TARGET_NO_KERNEL=true`. The archive contains no `IMAGES/boot.img`,
`META/kernel_configs.txt`, or `META/kernel_version.txt`; absence is expected for
this system-image-only GSI and is not kernel compatibility evidence.

| Partner APK | Audited source/installed/target-files SHA256 | Alignment |
| --- | --- | --- |
| GmsCore | `52597e77fd25fdd347574d0457ed1936a4b9561cf4c8d34e7ac8dd8191dfd4b9` | `PASS` |
| FakeStore | `a973e0235a2829773a4faf36d235d5f703d1c04a2adff674ebaa535a2e78f937` | `PASS` |
| GsfProxy | `86891b174301f06a1c84187b545a0a2a57044c6b768f3e84e865908743349692` | `PASS` |
| F-Droid | `985f5181d48bb6bafd54083a048b391271e0ab28385881cc41294fb01a222762` | `PASS` |
| F-Droid Privileged Extension | `1008525a17b4f6a93ac690f9c50dcb675b6bebf53d2879dbc98ba65a1cb2e28d` | `PASS` |

## TrebleApp Provenance

The following fields are embedded entries in build-info. Do not expect or
publish a standalone TrebleApp provenance file.

- Pinned source commit:
  `9d8a6771d94b7985f515b41bd280f7bdb4554037`
- Expected patch count: `9`
- Observed patch count: `9`
- Expected required artifact markers: `8`
- Observed required artifact markers: `8`
- Patched source head: `07a1853f2ce624d3102121a9d881d29d62ea57bb`
  (tree `85c79fb8a6e03599afc7f88ec7349148dff88f0c`)
- Verified prebuilt APK SHA256:
  `83ddd4b4ad2aba66b4152dcb2c2d207d36511406567ef58d75e1ca7fcdd01bda`
- Prebuilt signing state: `UNSIGNED (EXPECTED)`
- Expected deterministic non-signature ZIP-entry manifest SHA256:
  `60c9df24f04edf98000d84028a1192266a08a6cbf2113a690cc523118ed7b169`
- Verified prebuilt `classes.dex` SHA256:
  `0aaf330c7a23420bf99067f0d2da9a15f6dc2237d8222a01f5ff43097c92dbc4`
- Installed APK SHA256:
  `2a81f826c6cab70ae6a98c5e4d22ef2e11565cb995646f97f413c4d5b8a8fe11`
- Installed signer count: `1`
- Installed platform certificate SHA256:
  `c8a2e9bccf597c2fb6dc66bee293fc13f2fc47ec77bc6b2b0d52c11f51192ab8`
- Installed non-signature content match: `PASS`
- Target-files APK path:
  `SYSTEM/priv-app/TrebleApp/TrebleApp.apk`
- Target-files APK SHA256:
  `2a81f826c6cab70ae6a98c5e4d22ef2e11565cb995646f97f413c4d5b8a8fe11`
- Target-files signer count: `1`
- Target-files platform certificate SHA256:
  `c8a2e9bccf597c2fb6dc66bee293fc13f2fc47ec77bc6b2b0d52c11f51192ab8`
- Target-files non-signature content match: `PASS`
- Target-files `classes.dex` SHA256:
  `0aaf330c7a23420bf99067f0d2da9a15f6dc2237d8222a01f5ff43097c92dbc4`
- Prebuilt, installed, and target-files `classes.dex` match: `PASS`
- Embedded provenance is present in build-info: `PASS`

## Session Safety Gate

Use this section only when the signing fields above identify a final
release-signed artifact whose actual target-files signer manifest is compatible
with the baseline. For the intended test-key output, record `ABORTED`, perform
no device action, and leave all hardware results `NOT TESTED`.

| Safety condition | Result / record |
| --- | --- |
| Operator approval for this exact artifact | `NOT APPROVED`; no device session was opened. |
| Baseline APK/APEX identities inventoried without relying on `release-keys` | `PASS`; complete public-identity evidence is pinned above. |
| Complete APK/APEX comparison with the pinned baseline | `FAIL`; the audited target-files result is `INCOMPATIBLE` with 750 incompatibilities and disposition `NOT_FOR_IN_PLACE_FLASH`. |
| Reviewed compatible final release identity or rotation path | `FAIL`; none is available. |
| FinQwerty key excluded from Android OS identity decisions | `PASS`; it was not treated as an OS key. |
| In-use phone and data-preservation policy acknowledged | `PASS`; no phone was connected or acted upon. |
| Clean-install/data-wipe exception | `NOT APPROVED`. |
| Pre-flash ADB identity, partition, and low-risk snapshot | `NOT TESTED`; no device commands were issued. |
| Image/archive completion-file check | `PASS`; the retained host audit independently verified the image, archive, and timestamped completion file. |
| Baseline archive | `PASS`; `MP01-Lineage-1755162498-signed.tar.gz`, 1,204,341,111 bytes, SHA256 `d6b3f74d30ca84a186b926027afa7340a15450c5fd05720919cde57e1a887b1f`. |
| Baseline sole inner image | `PASS`; `MP01-Lineage-1755162498-signed.img`, 2,613,407,744 bytes, SHA256 `55e3465f65eaa112bff3cb59f79bbe233d8cb0721a44d29c95d51b6edd3a3d2f`. |
| Baseline treated as downgrade authorization | `NO`; Android 16-to-15 data preservation remains unverified. |
| Battery level and USB connection | `NOT TESTED`; there was no device session. |

Approval to flash `system` does not authorize erasing data partitions, wiping
from recovery, factory resetting, or downgrading. Stop and preserve evidence if
behavior is unexpected; do not use a wipe or Android 15 flash as a diagnostic
step.

Safety gate result: `ABORTED`

Checksum evidence: `PASS` in the retained audit directory identified above. No
device session was started.

The checksum verification above is the pre-device-session host gate. Both image
and archive must report `OK` before connecting or issuing any ADB/fastboot
command.

## Pre-Flash Evidence

- Baseline capture directory:
  `NOT USED (NO DEVICE SESSION)`; retained host baseline evidence is under
  `/home/user/MP01-LineageOS/logs/mp01-baseline/`
- Previous build fingerprint: `NOT COLLECTED (NO DEVICE COMMANDS)`
- Previous Android / LineageOS version: `NOT COLLECTED (NO DEVICE COMMANDS)`
- Bootloader and fastbootd device identity verified: `NOT TESTED`
- Current partition/slot state recorded: `NOT TESTED`
- Existing user data spot check recorded: `NOT TESTED`
- Candidate metadata identifies Android 16 / LineageOS 23.2: `PASS`
- Candidate differs from the quarantined unsigned Android 15 files:
  `PASS`; exact paths and hashes are recorded above
- Audited artifact platform/APEX signer compatibility with baseline:
  `FAIL (INCOMPATIBLE; NOT_FOR_IN_PLACE_FLASH)`; the unavailable compatible
  signing/rotation path independently blocks flashing

## Flash Record

- Entered fastbootd successfully: `NOT TESTED`
- Partition flashed: `NONE (NOT FLASHED)`
- Exact image filename: `NONE (NOT FLASHED)`
- Flash transcript location: `NONE (NO DEVICE COMMANDS)`
- No erase, wipe, or reset operation was run:
  `PASS (NO DEVICE COMMANDS; NO ERASE, WIPE, OR RESET WAS ISSUED)`
- Reboot initiated normally: `NOT TESTED`

Any `FAIL` in this section blocks the test and release path.

## Post-Flash Results

Use `PASS`, `FAIL`, `BLOCKED`, or `NOT TESTED`. Record evidence or an issue for
every result other than `PASS`.

| Area | Result | Evidence / notes |
| --- | --- | --- |
| Boot reaches the existing user session | `NOT TESTED` | Session aborted before device connection. |
| Existing apps, accounts, settings, and user data remain present | `NOT TESTED` | No device inspection or write occurred. |
| Android 16 / LineageOS 23.2 identity | `NOT TESTED` | No artifact was flashed. |
| inkOS home and light theme | `NOT TESTED` | No artifact was flashed. |
| Exact inkOS package/activity resolves as HOME | `NOT TESTED` | No device commands were issued. |
| MP01 accessibility enabled once; existing services preserved | `NOT TESTED` | No artifact was flashed. |
| Physical keyboard, symbols, and alt mappings | `NOT TESTED` | No hardware session occurred. |
| `aw9523b-key` system layout active without FinQwerty | `NOT TESTED` | No hardware session occurred. |
| Keyboard backlight and boot clamp | `NOT TESTED` | No hardware session occurred. |
| E-ink refresh button and per-app modes | `NOT TESTED` | No hardware session occurred. |
| Lock-screen clear and display readability | `NOT TESTED` | No hardware session occurred. |
| TrebleDroid Settings and MP01 preset | `NOT TESTED` | No artifact was flashed. |
| Permissioned e-ink automation path | `NOT TESTED` | No artifact was flashed. |
| Failed e-ink delivery is reported to automation | `NOT TESTED` | Host tests passed, but no device result exists. |
| Incomplete e-ink frame times out, is discarded, and next client works | `NOT TESTED` | Host tests passed, but no device result exists. |
| Wi-Fi and suspend/resume | `NOT TESTED` | No hardware session occurred. |
| Bluetooth | `NOT TESTED` | No hardware session occurred. |
| Mobile data | `NOT TESTED` | No hardware session occurred. |
| Incoming/outgoing calls and audio routing | `NOT TESTED` | No hardware session occurred. |
| SMS send/receive | `NOT TESTED` | No hardware session occurred. |
| MMS send/receive | `NOT TESTED` | No hardware session occurred. |
| Carrier IMS/VoLTE | `NOT TESTED` | No hardware session occurred. |
| Charging, battery reporting, and thermals | `NOT TESTED` | No hardware session occurred. |
| F-Droid, privileged extension, and microG | `NOT TESTED` | No artifact was flashed. |
| OTA remains disabled for this test artifact | `NOT TESTED` | Host policy disables OTA; no on-device result exists. |

Complete [`hardware-test-matrix.md`](hardware-test-matrix.md) and attach its
results or reference the corresponding issue for a future eligible candidate.
No hardware matrix was run in this blocked session.

## Failures And Recovery Evidence

- Failure summary: Device session blocked before connection because the complete
  target-files signer audit records `INCOMPATIBLE`, 750 incompatibilities, and
  `NOT_FOR_IN_PLACE_FLASH`, and no compatible signing/rotation path is
  available. Historical build `4bb063e` failed Blueprint provider validation;
  later formal runs failed no-kernel header generation, the stale e-ink fortify
  override, and post-build presigned-APK signature verification. Those source
  and build defects are fixed, and `c88e039` completed the sealed software audit.
  The host separately reported
  `EXT4-fs error (device xvdb): ext4_lookup:1787: inode #22850323: comm rg: iget: checksum invalid`.
- Logs captured before reboot: `NOT APPLICABLE`; no device reboot or command
  occurred. Host build and signer evidence paths are recorded above.
- Issue/reference: signing compatibility, verified-storage clean rebuild, and
  Android 16-to-15 data-preservation gates remain open. The filesystem must be
  checked/repaired offline and the build rerun cleanly on verified storage; the
  disk warning is not claimed as the provider failure's cause.
- Non-destructive recovery attempted: `NO`; nothing was flashed.
- Evidence preserved before any additional partition write:
  `PASS (HOST EVIDENCE ONLY; NO DEVICE WRITE OCCURRED)`
- Existing user data preserved: `NOT TESTED`; no device inspection occurred,
  although no device write, erase, wipe, or reset command was issued.
- Android 16-to-15 downgrade attempted: `NO`

A candidate that requires a clean install remains blocked unless that
requirement is understood and the operator deliberately approves a separate
clean-install session. A reset or unverified downgrade cannot turn a failed
candidate into a pass.

## Decision

- Overall result: `PASS_AUDIT_ONLY_NOT_FOR_IN_PLACE_FLASH`
- Final release signer compatibility established: `NO`
- Eligible for OTA work: `NO`
- Known issues recorded: complete target-files signer result `INCOMPATIBLE` with
  750 incompatibilities and `NOT_FOR_IN_PLACE_FLASH`; no compatible private
  signing/rotation path; hardware and data preservation not tested;
  Android 16-to-15 downgrade
  unverified; host `xvdb` EXT4 checksum error requires offline filesystem
  repair/verification and a clean rebuild on verified storage before release;
  FinQwerty key deletion remains blocked by qpublish binary-diff policy.
- Operator sign-off: `SOFTWARE AUDIT ONLY`; no device approval or hardware
  sign-off was given.

Final release signer compatibility must be `YES` before the hardware portion of
this report is started. OTA eligibility remains `NO` until that exact
signer-compatible artifact also passes every release-blocking hardware check.
