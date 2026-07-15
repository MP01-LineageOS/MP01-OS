# Upstream Update Policy

This records issue `#11`: upstream changes should be deliberate, testable, and
reversible. The MP01 image affects telephony, OTA behavior, keyboard input, and
e-ink readability, so bulk merges are not accepted without a release-candidate
test pass on hardware.

## Branch Policy

The active migration line is Android 16 / LineageOS 23.2. Keep the Android 15 /
LineageOS 22.2 accepted working baseline separate from 23.2 release candidates.
It is not an authorized rollback procedure until a data-preserving hardware
downgrade passes. Newer Android, LineageOS, or TrebleDroid migration work should
stay on separate branches until the 23.2 image has a reproducible build and a
passing MP01 smoke test with its final signer-compatible identity.

Do not mix these in one release candidate:

- Android base updates.
- TrebleDroid component updates.
- Fossify app updates.
- MP01 behavior changes.
- Signing, OTA, or release-script changes.

Each update should have a source revision note, expected user-visible effect,
non-destructive recovery evidence, and hardware test result before release. Do
not label an untested downgrade as a rollback path.

Create commits locally. Begin every staging sequence with
`qpublish workspace-status`, then stage with `qstage`. The development qube must
not push; reviewed publication is delegated to `git-publish`.

## Update Classes

| Component | Security sensitivity | Update cadence | Merge rule |
| --- | --- | --- | --- |
| LineageOS Android base | High | Track Android security releases, but stage them as explicit release candidates. | Update only with a full image build, complete signer comparison, and hardware smoke test of the final signer-compatible identity. |
| External `MP01-LineageGSI` build support | High | Update when fixing MP01 defaults, build reproducibility, release hygiene, or security-sensitive packaging. | Keep it outside the repo manifest, record its revision in build-info, reject duplicate source imports, and require script checks plus flashed-image validation for behavior changes. |
| `treble_manifest` | High | Update when pinning source revisions, moving maintained forks, or intentionally changing Android/Treble inputs. | Keep every project at an exact commit, record every changed revision, and keep external build support out of the source graph. |
| `device_phh_treble` | High | Conservative, coordinated with `vendor_hardware_overlay`, `treble_app`, and `treble_presets`. | No blind merge. Build, verify signing compatibility, and test the final signed identity before release because boot, sepolicy, and telephony can regress. |
| `vendor_hardware_overlay` | High | Conservative, MP01 overlay changes only when tied to a testable device outcome. | Pin the framework resource revision and workflow actions, build with the target API, and require MP01 hardware smoke testing for behavior changes. |
| `treble_app` | Medium-high | Update for preset handling, IMS controls, and MP01 source URL fixes. | Require Gradle distribution/dependency verification, minimal workflow permissions, commit-pinned actions, and target-files APK verification; flashed test required for behavior changes. |
| `treble_presets` | Medium-high | Update MP01 preset only when a setting is understood and testable. | IMS and radio preferences require SIM/radio regression testing. |
| `finqwerty` | Historical only | Retain for Android 15 source archaeology; it is not an active 23.2 dependency. | Its exposed historical application key is compromised and unrelated to OS keys. Do not re-add the APK without a new application identity, integration rationale, and full physical-keyboard testing. |
| `Phone` and `Messages` | Medium | Track for possible future MP01 image integration. | Not active 23.2 image inputs. Do not bulk-merge or add to the image without MP01 UI/e-ink review, default-app testing, calls, SMS, and MMS coverage. |
| Downloaded APK inputs | Medium-high | Pin by URL, version, SHA256, and signing certificate where available. | Verification failures must fail closed. Update only with a release-input commit. |

## Minimum Smoke Test

Before accepting an upstream update into a release candidate:

- Build the intended variant from recorded source revisions.
- Keep any resulting test-key artifact unflashed and non-release. The completed
  `c88e039` target-files comparison covered 616 APKs and 44 APEXes and returned
  750 incompatibilities, `INCOMPATIBLE`, and `NOT_FOR_IN_PLACE_FLASH`; no
  compatible signing or rotation path is available. A future clean
  verified-storage candidate must be compared again.
- In `test-key-audit` mode, accept the verifier only when it exits `3` and the
  evidence has `flash_disposition=NOT_FOR_IN_PLACE_FLASH`. That combination
  permits retention of an evidence-bound audit artifact; it is not a
  compatibility pass or flash approval. In `release-candidate` mode, require
  exit `0`, `comparison_status=COMPATIBLE_SIGNER_IDENTITIES`, and
  `flash_disposition=SIGNER_GATE_PASSED_HARDWARE_TEST_STILL_REQUIRED`. Every
  other exit/evidence combination fails closed.
- Before any device test, verify actual target-files APK signers and every
  overlapping APEX container certificate/payload public key against the baseline
  public-identity inventory. Use only the final compatible signed identity or a
  reviewed signer-rotation path, and obtain operator approval for that exact
  artifact. Preserve existing phone data.
- Treat a no-kernel system-image build warning as a skipped kernel VINTF check,
  not a pass. Require exact-device `VtsTrebleVintfTest`
  `SystemVendorTest.KernelCompatibility` before release or OTA work; OTA
  publication remains disabled for the current migration artifact.
- Confirm the existing user session returns and home resolves to inkOS. Treat an
  unexpected setup/reset flow as a failure.
- Record light mode and `mp01_defaults_version`. Do not clear data or force
  defaults solely to exercise first-boot behavior.
- Confirm physical keyboard input, including symbol/alt mappings.
- Confirm TrebleDroid Settings opens and the Minimal Phone MP01 preset is
  available.
- Confirm mobile data, incoming call, outgoing call, SMS, and IMS/VoLTE status
  when a SIM is available.
- Confirm the inherited dialer, inherited messaging app, F-Droid, and inkOS
  open. Confirm the system-owned MP01 keyboard map works without FinQwerty
  installed. If the Fossify forks are later integrated, test those exact
  packages as replacements.
- Confirm e-ink refresh button behavior and per-app refresh mode are not worse
  than the accepted baseline.
- Keep OTA metadata disabled for every audit or test artifact, and never point
  one at an `MP01-LineageOS` release URL. Enabling release OTA metadata requires
  a separate review after the release-candidate signer gate passes; it is not
  implied by an audit build or a hardware-test approval.

Do not erase data or metadata partitions, invoke any command that wipes user
data, wipe from recovery, or factory reset unless the operator grants explicit
clean-install/data-wipe approval for that specific session. A failed update
remains failed; stop and preserve evidence rather than wiping the device or
attempting an unverified Android 15 downgrade to obtain a passing result.

Use [`hardware-test-matrix.md`](hardware-test-matrix.md) for the full release
candidate checklist.

## Rollback Expectations

Every release candidate should keep enough information to evaluate a possible
recovery without implying that reflashing an older Android version is safe:

- Previous release tag, verified archive filename/size/SHA256, and sole inner
  image filename/size/SHA256.
- System-only fastboot and data-preservation notes, including any behavior that
  would block an in-place upgrade.
- Source revisions for the candidate and the previous known-good build.
- The immutable 222-entry baseline APK path/package signer inventory, AVB
  public key, and 33-entry APEX container/payload signer inventory, without
  private key material.
- Actual candidate package/APEX identities and an explicit compatibility result.
- User-visible rollback risk, especially data wipe, telephony state, and OTA
  compatibility.
- A separately approved, passing data-preserving hardware downgrade result
  before calling Android 15 a rollback path.

The current accepted working baseline is release `1755162498`, documented in
[`../baselines/working-mp01-2026-05.md`](../baselines/working-mp01-2026-05.md).
Its archive, inner image, and released-image public signer identities are
verified. Hardware downgrade behavior and the installed device's complete
signer/data state are not, so it is not yet an authorized rollback action.

## Issue 11 Status

This policy defines the initial update categories, minimum smoke test, and
rollback expectations. Keep issue `#11` open until the policy is applied to the
next actual upstream update and the result is recorded in release notes.
