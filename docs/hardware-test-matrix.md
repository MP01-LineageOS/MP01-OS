# Hardware Test Matrix

Use this checklist to record the known-good baseline and, subject to the session
safety gate below, every release candidate. Record candidate-specific evidence in
[`candidate-test-report.md`](candidate-test-report.md). Use `PASS`, `FAIL`,
`BLOCKED`, or `NOT TESTED`; do not silently omit unavailable hardware checks.

## Session Safety

The audited Android test-key output must not be flashed: its complete
target-files comparison covered 616 APKs and 44 APEXes and returned 750
incompatibilities, `comparison_status=INCOMPATIBLE`, and
`flash_disposition=NOT_FOR_IN_PLACE_FLASH`. No compatible signing or rotation
path is available, and a future clean verified-storage candidate must be
compared again.
For an Android 16 candidate flash session, apply the candidate portions of this
matrix only when `release-candidate` exits `0` with
`comparison_status=COMPATIBLE_SIGNER_IDENTITIES` and
`flash_disposition=SIGNER_GATE_PASSED_HARDWARE_TEST_STILL_REQUIRED` for the
exact target-files identity under test.

- From the image output directory, the timestamped `*.sha256sums` completion
  file is verified before any device command; both image and archive report
  `OK`.
- The candidate image, SHA256, build-info file, resolved manifest, and build log
  are recorded before connecting the phone.
- The candidate report records a passing exact 14-entry target-files inventory.
- The separate source APK gate records inkOS package and enabled MAIN/HOME
  activity semantics; the target-files inventory records only its exact path
  and count.
- The operator approved a `system`-only in-place flash for this specific session.
- Existing user data is the default preservation target.
- The baseline archive and sole inner image match their recorded size and
  SHA256, but availability is not treated as proof of downgrade safety.
- The baseline 222-APK signer manifest, AVB key, and 33 APEX container/payload
  identities come from the pinned audit; a `release-keys` property is not
  treated as certificate evidence.
- The actual candidate target-files signer gate exited `0` in
  `release-candidate` mode with `COMPATIBLE_SIGNER_IDENTITIES` and
  `SIGNER_GATE_PASSED_HARDWARE_TEST_STILL_REQUIRED`; the exact resulting signed
  identity is under test. The intended test-key source identity remains blocked,
  and the FinQwerty application key is not treated as an OS key.
- A no-kernel system-image build warning is not recorded as a kernel
  compatibility pass. Exact-device `VtsTrebleVintfTest`
  `SystemVendorTest.KernelCompatibility` passes before release work begins.
  This matrix does not authorize OTA publication.
- No data or metadata partition is erased.
- No command or recovery action that wipes user data is run.
- Recovery wipe and factory reset are not performed.
- A failure stops the test for evidence capture; a wipe is not used as a
  troubleshooting step.

Any exception requires explicit clean-install/data-wipe approval for that exact
session. Permission to flash `system` is not permission to wipe data.
Permission to test Android 16 is also not permission to downgrade to Android 15.
On failure, stop and preserve evidence without wiping or assuming a rollback.

## Device Identity

- Device boots into the existing user session without requiring setup or a data
  reset.
- About phone shows expected Android and LineageOS version.
- Build fingerprint and vendor fingerprint are recorded.
- `ro.product.brand`, `ro.product.model`, and `ro.product.device` look sane.
- Screen firmware version is recorded.

## User Session And Defaults

- First upgraded boot completes without crash loops.
- Existing user files, apps, accounts, and settings remain present.
- Default launcher resolves to inkOS.
- The resolved launcher is package `app.inkos`, activity
  `com.github.gezimos.inkos.MainActivity`.
- Light theme is active and readable on e-ink.
- `settings get secure mp01_defaults_version` returns the expected defaults version.
- The MP01 accessibility component appears exactly once among enabled services,
  other enabled services remain present, and the platform accessibility switch
  is enabled.
- PHH Settings opens.
- My Device preset entry appears for Minimal Phone MP01.

## Display And E-Ink

- Text is readable in Settings, launcher, dialer, and messaging.
- Light theme is usable outdoors and indoors.
- E-ink refresh button works.
- Per-app refresh mode can be changed.
- Permissioned automation can deliver refresh commands, and a failed delivery
  is reported as a failure rather than success.
- An authorized incomplete command frame times out after about five seconds,
  executes no partial command, and does not block the next client.
- Ghosting is acceptable after normal navigation.
- Lock screen and always-on behavior are acceptable.
- Rotation and resolution are stable.

## Keyboard And Buttons

- Physical keyboard types expected letters.
- Shift, symbol, enter, delete, space, and punctuation work.
- System input files for `aw9523b-key` are active.
- The IDC resolves extensionless layout name `aw9523b-key`.
- The system-owned `aw9523b-key` layout works without FinQwerty installed.
- Hardware refresh button behavior is documented.
- Volume/power buttons work.

## Connectivity

- Wi-Fi connects and survives suspend/resume.
- Bluetooth can pair with a basic accessory.
- Mobile data works.
- Airplane mode toggles cleanly.
- Hotspot behavior is tested or marked untested.

## Telephony

- SIM is detected.
- Incoming call works.
- Outgoing call works.
- Audio routing works for earpiece and speaker.
- SMS send and receive work.
- MMS send and receive are tested or marked untested.
- VoLTE/IMS status is recorded.
- IMS APN creation behavior is recorded.
- Carrier and country are recorded.

## Power

- Charging works while powered on.
- Offline charging behavior is tested.
- Battery percentage updates.
- Suspend/resume works.
- Overnight idle drain is measured.
- Device does not overheat during normal use.

## Apps

- Inherited dialer opens and can be set as default.
- Inherited messaging app opens and can be set as default.
- Fossify Phone/Messages forks are tested here only after they are explicitly
  added to the 23.2 image.
- inkOS opens and can be set as default launcher.
- F-Droid opens.
- F-Droid privileged install/update behavior is tested.
- microG self-check and required account/push behavior are recorded.
- TrebleDroid Settings opens.
- FinQwerty is absent from the active LineageOS 23.2 product.

## OTA And Recovery

- Current slot/partition state is recorded.
- OTA metadata remains disabled for the candidate under hardware test.
- An audit or test artifact is never pointed at an `MP01-LineageOS` release
  URL.
- No update install is attempted until signing and OTA work is separately
  enabled and reviewed.
- Recovery evidence is documented without calling an untested downgrade a
  rollback path.
- Any separately approved rollback/downgrade test preserves user data unless the
  operator explicitly approves a distinct wipe session.

## Pass Criteria

A final signer-compatible candidate passes the hardware gate only when all
required sections pass and all evidence is recorded. Existing-data loss, boot
failure, keyboard/e-ink regression, telephony failure, signer incompatibility,
or a required wipe blocks release. OTA stays disabled until that exact final
signed identity is install-tested and OTA metadata is separately enabled and
reviewed.

An Android 16-to-15 downgrade is a separate hardware procedure. The baseline
archive, inner image, and released-image public identities are verified, but a
data-preserving downgrade that accounts for installed signer and data state has
not passed on hardware. Archive availability alone is insufficient.
