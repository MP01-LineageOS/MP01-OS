# Baseline Capture

Capture this before making OS changes. The goal is to preserve a known-good
reference point and enough evidence to reproduce the current working image.

Some commands can expose private data. Keep raw logs local unless they have
been reviewed and redacted.

## Device Notes

Record manually:

- Device: Minimal Phone MP01.
- Screen firmware version.
- Installed image filename or release URL.
- Install date.
- Flashing guide and exact commands used.
- Host OS used for flashing.
- Carrier and SIM type.
- Whether GMS build or vanilla build is installed.
- Any first-boot setup choices.
- Current workarounds applied.

Use [`../baselines/working-mp01-2026-05.md`](../baselines/working-mp01-2026-05.md)
as the baseline record.

The current known install was performed using:

```text
https://chardidath.ing/posts/mp01-flashing-guide/
```

That guide uses `fastbootd`, flashes `system.img`, erases `userdata`, erases
`metadata`, and reboots. The working phone was installed from the latest
original `MP01Experiments/MP01-LineageGSI` release:
`MP01-Lineage-1755162498-signed.tar.gz`.

Treat those erase steps as historical clean-install behavior. Future in-place
upgrade sessions must preserve user data by default and require explicit
operator confirmation before erasing `userdata`, erasing `metadata`, running
`fastboot -w`, or factory resetting from recovery.

## Low-Risk ADB Snapshot

Run from the project workspace with the phone connected and USB debugging
enabled. Keep captured artifacts under
`/home/user/MP01-LineageOS/logs/mp01-baseline`;
do not put project artifacts at filesystem root or elsewhere on the host.
The historical May 2026 snapshot at that path was not migrated into this
workspace and is unavailable here; the following commands create evidence for
a new session rather than recovering the missing historical files. This refers
to raw device logs: the verified baseline archive and sole extracted image are
present under `logs/mp01-baseline/release-assets/`.

```bash
mkdir -p /home/user/MP01-LineageOS/logs/mp01-baseline
cd /home/user/MP01-LineageOS/logs/mp01-baseline

adb devices -l | tee adb-devices.txt
adb shell getprop | tee getprop.txt
adb shell uname -a | tee uname.txt
adb shell cat /proc/version | tee proc-version.txt
adb shell df -h | tee df-h.txt
adb shell mount | tee mount.txt
adb shell settings list global | tee settings-global.txt
adb shell settings list secure | tee settings-secure.txt
adb shell settings list system | tee settings-system.txt
adb shell cmd package list packages -f | tee packages.txt
adb shell dumpsys battery | tee dumpsys-battery.txt
adb shell dumpsys display | tee dumpsys-display.txt
adb shell dumpsys power | tee dumpsys-power.txt
adb shell dumpsys input | tee dumpsys-input.txt
adb shell dumpsys telecom | tee dumpsys-telecom.txt
adb shell dumpsys telephony.registry | tee dumpsys-telephony-registry.txt
```

## Optional Raw Bugreport

`bugreportz` is useful but privacy-sensitive. It can contain phone numbers,
network identifiers, accounts, recent app activity, and logs. Do not publish it
unreviewed.

```bash
adb bugreportz
```

After the command finishes, pull the generated zip from the path printed by
`adb`.

## Photos To Capture

Take simple photos of:

- About phone page.
- Build number and Android version.
- PHH Settings -> My device.
- PHH Settings -> IMS features after setup.
- FinQwerty layout selection only when documenting the historical Android 15
  baseline. The Android 16 candidate should use the system-owned
  `aw9523b-key` layout without FinQwerty installed.
- Default launcher prompt or selected launcher.
- Light/dark theme setting.
- E-ink refresh controls.

## Baseline Record Status

The exact original source graph and full installed-device signer state cannot
currently be proven, so this remains a documentation-only baseline rather than
a git tag. All 222 released-image APK signer identities, all 33 released-image
APEX identities, and the system AVB public key are recorded in the local
public-identity audit. Do not
create a source tag that implies the current documentation commit produced the
installed image. Commit documentation locally, begin staging with
`qpublish workspace-status`, and leave publication to the reviewed
qpublish/`git-publish` flow.

The release archive and sole extracted image are now verified by filename, size,
and SHA256, and the released image's public signer identities are inventoried.
Before describing the baseline as a downgrade path, complete a separately
approved, data-preserving hardware downgrade test that accounts for installed
signer and data state. On an Android 16 failure, stop and preserve evidence; do
not wipe or assume that flashing Android 15 is safe.
