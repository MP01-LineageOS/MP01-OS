# Release Hygiene

The MP01 image affects an in-use phone, telephony, OTA behavior, and user data.
Every candidate must be traceable and fail closed. Recovery planning must
preserve evidence and data; it must not assume an untested Android downgrade is
a safe rollback.

## Current Controls

- The failed cached-local/full-preparation build used `MP01-LineageGSI` commit
  `4bb063e28116af3b4f4263c4cf6eed00b3829961` and failed Soong/Blueprint's
  `provider ... was modified after being set` invariant before Ninja,
  target-files, or artifact packaging. It never exercised the target Metalava
  action; the heap remediation is validated only by the isolated replay and
  focused policy tests so far. Its retained log SHA256 is
  `e70d2d4655faaecbe6907a5acecb2e1c52fae0e9e42d33fe9ef441686e2a5c8b`.
  The preceding attempt at
  `ac3f97f43eafbacf4f222a6915429fae9d7c2a69` reached the Android compile but
  failed at the `api-stubs-docs-non-updatable` Metalava action with Java heap
  exhaustion; it is retained as failed-build evidence, not as a candidate.
- The synchronous diagnostic completed the full Soong graph with the unchanged
  provider invariant passing before and after `WriteBuildFile`. Its retained log
  SHA256 is `dd23b844f916e0a35268a4654978b378e2b57f3369db643c832578bad4b9e4d8`.
  The following compile was intentionally stopped at 3% because the direct
  command omitted `USE_CCACHE` and would serially rebuild roughly 170,000
  actions; it was not an artifact-producing run.
- GSI commit `4e94263d8871e26b32f8927f6f1d820a830a0a19` commits the
  fail-closed command-only post-write Blueprint patch, SHA256
  `43cca96d3eb8d04a91a9b0637444889b62fe1a04a064910c68c2358e23326df1`.
  Its first formal invocation failed an external-helper preflight before source
  preparation and produced no artifact. Head
  `3feebebfb20c6b424b05f4cbe5f1e72ca5b3e28f` then brought workspace and build
  state policy into the repository, but its formal run failed closed before
  graph generation: lunch reported `TARGET_PRODUCT=lineage_arm64_bmN4` while
  the actual product output was `generic_arm64`. Log
  `.android-build/logs/mp01-final-3feebebfb20c-20260710T220742Z.log`, SHA256
  `55157ea23dfa8795dbc84b512867eb40d7364a35caed1fa87f394d2f47809691`;
  no artifact was produced. Head
  `c890b4015a505bbce0ae09761f0054de24d3d6c0`, tree
  `871b1a1e59ee73e6fede1bbc1a7cbf69739c71d6`, pins the actual product output
  directory. Its formal run passed the lunch/output contract and TrebleApp
  preparation, completed bootstrap `284/284`, and then failed during Soong
  graph/main Ninja generation for `continuous_native_tests`: the absolute
  `out/host/linux-x86/framework/net-tests-utils-host-common.jar` path was outside
  the source-directory contract. Log
  `.android-build/logs/mp01-final-c890b4015a50-20260710T221230Z.log`, SHA256
  `bac623467a00c6ef1c321c3ea1d18ea1370fe023d427f2d74397dfa01a201468`;
  wrapper duration `00:51:49`, exit `1`. Main/product Ninja was not regenerated
  or executed, target-files and publication were not reached, and no artifact or
  publication residue was produced. The retained log contains no I/O or OOM
  failure evidence. Head `612997762d55364f14b4157f745dcab190dd468c`, tree
  `491273ae8e6909f4eaf3e30436263fd8ebd8c0ba`, supplies Android's relative
  `OUT_DIR` interface. Its build was intentionally stopped at action
  `6632/153795` after review found that the ad hoc wrapper ignored `tee` status.
  The retained evidence log is
  `.android-build/logs/mp01-final-612997762d55-20260710T231231Z.log`, SHA256
  `8dd8aa7ad75d6c1ac60264612931228bbb6cb6f892ffbbf35f28a76422ad44f5`, from
  `2026-07-10T23:12:31Z` through `2026-07-11T01:52:04Z`; duration `02:39:33`,
  intentional exit `141`. It produced no artifact or publication residue, and
  the log contains no kernel I/O or OOM failure evidence.
- Commit `16aa5f8d47503debba428c01547aba91232f28b6` adds the fail-closed
  contract-v1 formal transcript harness. The harness and retained Python helper
  have SHA256 values
  `938cc2842ca860704f727cfbd4f890227ccb93d44387f64e6be3f704b3403204` and
  `cf8a04c7d334caeb177750b7f2e9c2855e2835e231f9e45d21933619fd9ead07`.
  During a run it writes only a private `*.log.incomplete`; it publishes the
  final log identity and completion record only after the build, capture,
  repository/helper integrity, contract, and fsync checks succeed.
- The first contract-v1 run at `3d1bfa4` exposed an old patch-runner false
  ALREADY APPLIED result and later failed because a no-kernel generated-header
  action invoked missing `headers_install`. Its retained incomplete-log SHA256
  is `6006d29d4a5f6ec348c3258985bbee2898abfd07bb74a3e042b05811a216dcc1`.
  Commit `11bdbbd` replaces fuzzy reverse detection with exact Git checks and
  zero-fuzz fallback application. Commit `cb9eab6` handles generated headers for
  `TARGET_NO_KERNEL=true`; its formal run passed that gate, then failed because
  the MP01 e-ink daemon's `_FORTIFY_SOURCE=2` conflicted with Android 16's
  toolchain-provided level 3. Its retained incomplete-log SHA256 is
  `46bb6fd0eff47ffb14229477afb38c8e25b0ae6f9bdbd9b4d09332b4d36e0d8a`.
- Head `2fd5dec31b3b9c98060ed81d29a666b653df05fe`, tree
  `a931350da017ad19d18dd1b520c103c7ad417730`, removes that stale fortify
  override. The third contract-v1 run, at this head, completed the primary
  Android build in `05:34:23`. Its
  post-build signer audit then failed closed at
  `SYSTEM/product/priv-app/FDroidPrivilegedExtension/FDroidPrivilegedExtension.apk`:
  the APK no longer contained the v2/v3 signing blocks declared by its JAR
  signature. The retained staging log is
  `.android-build/logs/mp01-final-2fd5dec31b3b-20260712T200339Z-abcc08c367e1.log.incomplete`,
  SHA256
  `6093a4960140dd5bdd29185cf7788f8c16e8f530f9a260afcc910b7a49e55b8a`.
  Contract-v1 correctly withheld the final log and no candidate was published.
- Root-cause comparison showed the privileged-prebuilt Make path had
  uncompressed DEX content and realigned `GmsCore`, `FakeStore`, and
  `FDroidPrivilegedExtension`, changing their bytes and invalidating the signing
  blocks. `FDroid` and `GsfProxy` remained byte-identical.
- Final logical head `c88e039992760ada12f1df874453c2243d784862`, tree
  `9d4bfca308b640e2b28f58f3502af40a7adf0c21`, adds source and artifact gates
  that preserve and verify the exact aligned bytes of all five presigned partner
  APKs, continues to block test-key artifacts from flashing workflows, and
  passes all 143 GSI tests. An initial invocation stopped in disk-space preflight
  before source preparation because 227 GiB was below that run's configured
  250 GiB preflight threshold. Its
  retained incomplete-log SHA256 is
  `9e51db5870ec7bc14ecdfd953ca509a617181434169987e89db950f39aa81f82`;
  no artifact was produced. After space was reclaimed, the contract-v1 rerun
  started at epoch `1784095155`, completed Android in `08:47:27`, and published
  artifact epoch `1784126958`. Complete log
  `.android-build/logs/mp01-final-c88e03999276-20260715T055915Z-93cb550cc58a.log`
  has SHA256
  `87681b4c33c0d9584cb5067b223c2f92219544dfafd1147017511d49d0f25d3a`.
  All 47 auditor unit tests passed. The retained independent audit returned
  `PASS_AUDIT_ONLY_NOT_FOR_IN_PLACE_FLASH`, verified the five exact partner
  APKs and 14 required paths, and sealed the evidence directory referenced by
  the candidate test report. Its complete signer result is `INCOMPATIBLE` /
  `NOT_FOR_IN_PLACE_FLASH`: 616 APKs, 44 APEXes, 750 incompatibilities, and 0
  warnings. The unsigned test-key artifact is never flash eligible.
  The sampled free-space low-water was `255.39 GiB` and final ccache `14.3 GB`;
  this incremental/cached run is not clean-build calibration, and the 250 GiB
  guard is not a platform floor.
- This is a system-image-only no-kernel GSI. Despite requested enforcement, the
  Make warning means the kernel inputs to build-time `checkvintf` and the OTA
  kernel metadata are omitted, not passed. It supplies no kernel compatibility
  evidence. Exact-device `VtsTrebleVintfTest`
  `SystemVendorTest.KernelCompatibility` remains pending. OTA publication is
  disabled.
- The GSI `README.md`, `ROUGHGUIDE.md`, and
  `vendor/MP01_services/README.md` no longer expose current test-key device
  commands. They state that current outputs are host-audit-only and
  `NOT_FOR_IN_PLACE_FLASH`.
- The host separately reported an EXT4 inode-checksum error for inode `22850323`
  on `/dev/xvdb`. The retained failed-build logs contain no filesystem I/O
  failure evidence, so this warning is not assigned as the cause of any recorded
  build failure. Before a release build, preserve evidence, take the filesystem
  offline/unmounted for the appropriate check and repair, verify a clean result,
  and rebuild cleanly on verified storage.
  Earlier output remains software-audit-only.
- `treble_manifest` commit
  `fb1e1f76d353591caa2d991a3f8d92266249fe8e` pins 14 Android 16 input projects
  by exact commit. The microG override removes `vendor/gapps`, leaving 13
  effective custom projects. It excludes external `MP01-LineageGSI` support.
- The build records GSI support provenance separately from the resolved
  `repo manifest -r`, so build orchestration is not misrepresented as a
  manifest project.
- The official source launcher is the immutable `repo-2.65` object with SHA256
  `1211b57b57e4122a9c546295a59b37d24068f1164d0e87bef096d5323c413e4f`.
  Repo initialization uses official implementation tag `v2.65` and verifies
  exact commit `35bbf701d04de5c6a71937279bc3d16f6ce36808`.
- Downloaded partner APKs have exact version, URL, and SHA256 pins. FakeStore is
  `0.3.15.40226`, version code `84022630`, from release tag
  `v0.3.15.250932`. APK validity and signing certificates are checked where
  applicable. Checked-in inkOS and exact preset content are also hashed. The
  source inkOS APK must additionally identify as package `app.inkos` with its
  expected enabled MAIN/HOME activity.
- The partner byte-preservation patch has SHA256
  `146aa1a9307452217e087d818028bb158e8adf0a5a3a52e6bcaebe0665e7a1bf`.
  It transforms `vendor/partner_gms` base commit/tree
  `4b3b48033245800142045ce78038166f8aff6b01` /
  `3c554b8fabffd2bdd0727aac770e403d9fec0505` into prepared commit/tree
  `67e492737184fe9584750e07ad4c0ecfb40af67e` /
  `06afb50166f27672b02c7b168b24de0bf30f8f21`. The build rejects missing,
  duplicate, or competing module definitions and verifies pinned SHA256 and
  zipalign for every source, installed, and target-files partner APK.
- TrebleApp commit `9d8a6771d94b7985f515b41bd280f7bdb4554037` adds
  Gradle distribution and dependency verification. Its CI review unit
  `cee22d352a9c022d43e5384a29646898a94e45cd` is build-only, grants read-only
  contents access, and pins actions by commit.
- The GSI build applies and verifies exactly nine TrebleApp patches. Its prebuilt
  is expected to be unsigned. It records a deterministic manifest for every
  non-signature ZIP entry, with `classes.dex` as a focused subcheck, then
  requires installed and target-files copies to have exactly one platform
  signer and identical non-signature content.
- Target-files must contain exactly one of each of 14 critical MP01, inkOS,
  keyboard, F-Droid, and microG paths. This path/count inventory includes the
  accessibility privapp whitelist under its required `.xml` filename; inkOS
  semantics are verified earlier against the checked-in source APK.
- Overlay commit `7cf73a0094e6448e0bb830fea996715fbd2fffc3` validates
  against exact framework commit
  `46fd4b1f8d25b92540048c96ddc625b4ebeb6d60`; its workflow also uses read-only
  permissions and full action commit pins.
- Duplicate GSI source trees and stale copied vendor inputs are removed or
  rejected before Soong graph generation. Patch, source-preparation, manifest,
  and primary make failures are fatal.
- Patch commits use their author date as the committer date, which was verified
  in the prepared tree. The inactive unverified `product.prop` patch is gone.
  Every candidate performs full reset, cleanup, source verification, and patch
  application. Optional `MP01_SKIP_REPO_SYNC=1` skips network transfer only
  when the required objects are already cached.
- Soong invokes Metalava with `-J-Xmx6114m`. On a host with no more than 16 GiB of
  memory, the build requires `MP01_MAKE_JOBS=1`, fixes the combined Ninja
  high-memory pool at depth `1`, and verifies that actual pool after Soong
  generation. A hash-checked verifier is copied into retained `.mp01` state
  before the transient support-tree copy is removed, then the same copy and hash
  are reused before and after the primary make. Build-info records host memory,
  requested and enforced make jobs, expected and actual high-memory pool depth,
  Metalava heap, Soong/JDK identity, and verifier path/hash provenance.
- Successful packaging requires the image, archive, timestamped
  `*.sha256sums`, build-info with embedded TrebleApp provenance, normalized
  resolved manifest, and retained build log. Build/publication locks, staged
  paths, and no-overwrite checks prevent concurrent or partial presentation;
  the timestamped `*.sha256sums` file is published last as completion marker.
- The selected target-files archive is exactly
  `$ANDROID_PRODUCT_OUT/obj/PACKAGING/target_files_intermediates/lineage_arm64_bmN4-target_files.zip`.
  The audited `$ANDROID_PRODUCT_OUT` basename is `generic_arm64`. Its path and
  SHA256 are recorded, exactly one `IMAGES/system.img` is required, and the
  published image is extracted only from that member.
- Before target-files inventory, TrebleApp inspection, image extraction, hashing,
  or publication, the build creates one private read-only target-files snapshot.
  Every downstream check and output uses that same snapshot. The signer gate
  compares its APK package signers and APEX container/payload identities against
  `signing/mp01-1755162498-public-signers-v1.tsv`, SHA256
  `0e0313015d4bba28f8fe85d91498d060a7c525d81980f3f100efeb7f3628dd03`.
  That complete baseline contains 222 APK paths for 221 packages and 33 APEX
  identities.
  Release mode requires verifier exit `0` and a compatible result. The explicit
  `test-key-audit` mode may continue only on verifier exit `3` with disposition
  `NOT_FOR_IN_PLACE_FLASH`; all validation, tool, coverage, and unexpected-exit
  failures stop without presenting output. The actual manifest and complete
  comparison evidence are embedded in build-info, and output no-clobber checks
  remain in force.
- The baseline public-identity audit records all 222 released-image APK
  path/package signer identities, including five named OS APK/OTA certificate
  classes, the system AVB public key, and all 33 APEX container/payload
  identities. Its report SHA256 is
  `0b0d5ad0fbaf69053c8679926b7ff6932cbd11f8b32860c6679fc6aad48c90ff`;
  the APK TSV SHA256 is
  `ff7167528971e0fccc84cfbfccc2c9842d7be27d1f5cb9b77edea6f234f8da9c`;
  the APEX TSV SHA256 is
  `f7b48cd972fa58e9ce7b9710927edd0772e0792e9706b86ea60c8b9941ead93b`.
- The current test-key source certificates do not match the baseline platform,
  release/default, shared, media, or network-stack classes. The image is not
  release-signed and is blocked from flashing. OTA publication and proprietary
  GMS packaging remain disabled.
- `sign.sh` exits nonzero with an explanatory error. The inherited Android 15
  signing map cannot produce an apparent LineageOS 23.2 release.

The active TrebleApp and overlay workflows grant only `contents: read` and use
these exact action revisions:

| Action | Revision |
| --- | --- |
| `actions/checkout` | `34e114876b0b11c390a56381ad16ebd13914f8d5` |
| `actions/setup-java` | `c1e323688fd81a25caa38c78aa6df2d33d3e20d9` |
| `android-actions/setup-android` | `9fc6c4e9069bf8d3d10b2204b1fb8f6ef7065407` |
| `actions/upload-artifact` | `ea165f8d65b6e75b540449e92b4886f43607fa02` |

Overlay CI checks out LineageOS framework resources at
`46fd4b1f8d25b92540048c96ddc625b4ebeb6d60`, not a moving branch.

## Compromised Historical Key

The former FinQwerty release keystore was committed in repository history and
must be treated as compromised. Staged mitigation commit
`a60a78160be024173c7eac11acc45e4db4e693f0` disables signing/publication, pins
CI, ignores the key filename, and warns about the exposed identity. Local commit
`1b712b2a725d43233c03d768f4df6d4ef2e18883` deletes the tracked key, but current
qpublish policy rejects that binary deletion. Publishing it is blocked pending
an approved qadmin/`git-publish` mechanism. Deleting the current-tree copy does
not restore trust in that identity.

FinQwerty is not shipped in LineageOS 23.2. Any future FinQwerty release must use
a new signing identity generated and stored outside git and outside the
development qube. The old certificate must never be used to authorize an update,
and it is unrelated to Android platform/APEX signing identities.

## Artifact Checklist

Every candidate must retain:

- Exact image filename and SHA256.
- Exact compressed archive filename and SHA256.
- Timestamped `*.sha256sums` completion file verified against both outputs.
- Build-info with target, variant, exact source/tool identities, exact
  `$ANDROID_PRODUCT_OUT/obj/PACKAGING/target_files_intermediates/lineage_arm64_bmN4-target_files.zip`
  path/SHA256, embedded TrebleApp provenance, low-memory build controls, and the
  baseline/actual signer manifests plus complete comparison evidence.
- Normalized resolved `repo manifest -r` for the platform and 13 effective
  custom projects.
- Passing exact 14-entry target-files path inventory and separate source inkOS
  semantic-verification evidence.
- Full build log.
- Install and non-destructive rollback notes.
- Known issues and completed hardware report.

A test-key, non-release-signed, unflashed userdebug artifact must be labeled
accordingly, kept separate from release output, and never used for the in-place
device test.

## Signing Policy

Android's release-signing guidance requires update identities to remain
compatible with the installed packages and distinguishes APK, APEX, AVB, and
OTA keys. See [AOSP: Sign builds for release](https://source.android.com/docs/core/ota/sign_builds).

- Private keys never enter git, build logs, CI artifacts, or the development
  qube.
- Use the pinned public-identity audit, not the baseline `release-keys` property,
  as evidence for released-image APK/APEX/AVB identities.
- Verify actual candidate target-files APK signers package-by-package and every
  overlapping APEX container certificate and payload public key against the
  baseline inventory. Candidate source certificates alone are not sufficient.
- Run that comparison against the one immutable target-files snapshot before
  inventory, extraction, hashing, or publication. Release output requires a
  compatible exit; audit-only test-key output must carry the explicit
  `NOT_FOR_IN_PLACE_FLASH` disposition.
- Record public certificate fingerprints, not private material or passwords.
- Treat every identity exposed in source history as permanently compromised.
- Use corresponding baseline keys or a reviewed, baseline-authorized rotation
  wherever Android supports one; a newly generated identity is not automatically
  compatible, and public-key evidence does not prove private-key availability.
- Build and install-test the exact final signed identity as an in-place upgrade
  before it becomes a release. Do not test one identity and sign another later.
- Keep the fail-closed signing stub until a complete Android 16 signing map and
  OTA flow are reviewed with a compatible release identity or rotation path.

## CI and Publication Policy

- Grant workflow permissions explicitly and minimally.
- Pin third-party and GitHub Actions by full commit, with the readable release
  version in a comment.
- Verify Gradle wrappers, distributions, and dependencies rather than trusting
  mutable resolution results.
- Create small local commits. Begin every staging sequence with
  `qpublish workspace-status`, then use `qstage`.
- Do not use GitHub credentials or run `git push` in the development qube.
- Publication is performed only by the reviewed qpublish/`git-publish` flow.

## OTA Policy

OTA metadata remains disabled until:

1. A signed release artifact exists at its final location.
2. Its checksum and source record are published.
3. The download URL returns the exact recorded bytes.
4. The final signed identity passes an in-place install on MP01 hardware.
5. Any claimed Android 16-to-15 rollback separately passes a verified,
   data-preserving hardware downgrade test.
6. The candidate report records a passing result.

Do not publish OTA metadata for experimental, unsigned, or unflashed builds.

## Device Safety

The audited test-key artifact is blocked from flashing because its complete
target-files identity is incompatible with the baseline. A later device test may use only a final
release-signed identity whose actual target-files package/APEX identities are
shown compatible with the baseline. Before any command, verify the timestamped
`*.sha256sums` completion file and signer evidence. Approval to flash `system`
is not approval to erase partitions, wipe, factory reset, or downgrade. On
failure, stop and preserve evidence. Archive availability alone never authorizes
an Android 16-to-15 downgrade.

## Next Gates

1. Preserve the sealed `PASS_AUDIT_ONLY_NOT_FOR_IN_PLACE_FLASH` evidence.
2. Verify/repair the affected filesystem offline and run a clean build on
   verified storage, then audit its complete Android 16 artifact set.
3. Complete review of tree-equivalent GSI squash
   `ae9299f0819ca9bd564859e96bce965007381e54`, staged as
   `20260715-111324-MP01-LineageGSI-ae9299f0819c`, and the exact staged MP01-OS
   documentation/auditor state.
4. Produce a compatible final release-signed identity or reviewed rotation
   path; the current complete comparison is incompatible.
5. Run the no-wipe candidate report for that exact signed identity after
   operator approval.
6. Enable OTA only after the signed in-place update path passes.
