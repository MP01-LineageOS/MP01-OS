# Working MP01 Baseline - May 2026

Status: accepted known-good baseline. ADB baseline was captured on May 22,
2026, but the raw logs were not migrated into this development workspace and
are currently unavailable here. Any retained copy remains private because it
contains device identifiers.

## Summary

- Device: Minimal Phone MP01
- Installed OS: LineageOS GSI from the latest original release at install time
- Android base: LineageOS 22.2 / Android 15
- Build variant: `treble_arm64_bvN-userdebug`
- Install verified by: maintainer report and ADB snapshot from the working phone
- Install date: 2025; exact date not recorded
- Current maintainer: not recorded in the public baseline

## Image Details

- Archive filename: `MP01-Lineage-1755162498-signed.tar.gz`
- Archive size: 1,204,341,111 bytes
- Image URL: https://github.com/MP01-LineageOS/MP01-LineageGSI/releases/download/1755162498/MP01-Lineage-1755162498-signed.tar.gz
- Original source URL: https://github.com/MP01Experiments/MP01-LineageGSI/releases/download/1755162498/MP01-Lineage-1755162498-signed.tar.gz
- Archive SHA256: `d6b3f74d30ca84a186b926027afa7340a15450c5fd05720919cde57e1a887b1f`
- Sole inner image: `MP01-Lineage-1755162498-signed.img`
- Inner image size: 2,613,407,744 bytes
- Inner image SHA256: `55e3465f65eaa112bff3cb59f79bbe233d8cb0721a44d29c95d51b6edd3a3d2f`
- Verified local copies:
  `/home/user/MP01-LineageOS/logs/mp01-baseline/release-assets/`
- Release/tag: `1755162498`; device reports `22.2-20250814-VANILLA-EXT4-GSI`
- Release page: https://github.com/MP01-LineageOS/MP01-LineageGSI/releases/tag/1755162498
- Original release page: https://github.com/MP01Experiments/MP01-LineageGSI/releases/tag/1755162498
- Release published: 2025-08-14T10:44:07Z
- Build date shown on device: Thu Aug 14 08:30:17 UTC 2025
- Security patch level: system 2025-07-01; vendor 2025-11-05
- GMS or vanilla: VANILLA; no `com.google.android.gms` or Play Store package observed
- Signed or unsigned: the release asset is named `*-signed`, and the device
  reports `release-keys` tags on a `userdebug` build. Neither is certificate
  evidence. Public identities were instead extracted from the verified image as
  recorded below.

## Public Signing Identity Evidence

The public-identity audit under
`/home/user/MP01-LineageOS/logs/mp01-baseline/release-assets/public-identity-audit/`
records these baseline APK/OTA certificate classes:

| Role | Certificate SHA256 |
| --- | --- |
| Platform | `6a8c75f0fc84f7b4c7a4eadf443ddebe938ff0abde332ee1516fb91e756c447e` |
| Release/OTA | `c495956b1d898dc8731040f4a48256b30144b4958198687e076023f234cf70aa` |
| Shared | `9e8207aa328db085fffc5c2a6e32fa425bed1f6d68e0eb169091e4a4b73e378a` |
| Media | `4decc623b85f6024ffaa39d98f9ea1ba23caf7d82354240b8dcb6dea4c83b499` |
| Network stack | `f96c390a48c0093291ed09714635ccccc4ee6e3e555dd08cb48878377bed1028` |

It also records system AVB public-key SHA1
`cdbb77177f731920bbe0a0f94f84d9038ae0617d`, rollback index `1751328000`,
all 222 released-image APK path/package signer identities, and all 33 baseline
APEX container certificates and payload public keys. The APK signer TSV SHA256
is `ff7167528971e0fccc84cfbfccc2c9842d7be27d1f5cb9b77edea6f234f8da9c`.
The APEX signer TSV SHA256 is
`f7b48cd972fa58e9ce7b9710927edd0772e0792e9706b86ea60c8b9941ead93b`.
This proves public identities, not availability of their private keys or
compatibility of a future candidate.

## Source Mapping

- `MP01-LineageGSI` commit: `99bd410eb7e620998db4be5246b23f36f531d4fe` (`1755162498` tag)
- `treble_manifest` commit: not reconstructable from retained build evidence
- `device_phh_treble` commit: not reconstructable from retained build evidence
- `vendor_hardware_overlay` commit: not reconstructable from retained build evidence
- `treble_app` commit: not reconstructable from retained build evidence
- `treble_presets` commit: not reconstructable from retained build evidence
- `finqwerty` commit: not recorded; the inherited build selected a moving latest
  release
- `Phone` commit: not established as a baseline image input; no commit recorded
- `Messages` commit: not established as a baseline image input; no commit recorded

The bounded, time-based reconstruction is documented in
[`../docs/baseline-source-map-1755162498.md`](../docs/baseline-source-map-1755162498.md),
but it is not exact original-build provenance.

## Flashing Notes

- Host OS: not recorded
- Tools used: ADB and fastboot were used; exact versions are not recorded
- Unlock state: unlocked; the later ADB capture reported verified boot state
  `orange`
- Flashing guide: https://chardidath.ing/posts/mp01-flashing-guide/
- Commands used: historical report only; no exact command transcript was retained

> **WARNING: CLEAN-INSTALL HISTORY ONLY. Do not run the following commands for
> an in-place upgrade. The erase operations destroy user data and require
> explicit operator approval for that exact clean-install session.**

  - `adb reboot bootloader`
  - `fastboot flashing unlock`
  - `fastboot reboot fastboot` or `adb reboot fastboot`
  - `fastboot flash system <path to system.img>`
  - `fastboot erase userdata`
  - `fastboot erase metadata`
  - `fastboot reboot`
- Recovery/rollback notes: no contemporaneous recovery notes were retained; the
  verified baseline is not an authorized Android 16-to-15 rollback path

The guide instructs users to download the latest image from the original
`MP01Experiments/MP01-LineageGSI` releases page, extract the `.tar.gz`, flash
the resulting `.img` from `fastbootd`, then erase `userdata` and `metadata`.
The phone was installed from the current latest original release,
`1755162498`.

This records the historical clean-install path for the accepted baseline. For
future upgrades of an in-use MP01, do not erase `userdata`, erase `metadata`,
run `fastboot -w`, or factory reset unless the operator explicitly confirms a
data wipe for that session.

The archive and its sole inner image now match the filename, size, and SHA256
recorded above, and public APK/APEX/AVB identities are inventoried. That proves
artifact availability, integrity, and public identity; it does not prove that
downgrading an in-use phone from Android 16 to Android 15 is safe. Before any
downgrade can be called a rollback path, pass a separately approved hardware
downgrade test that accounts for installed-state signer and data compatibility
and preserves data. Until then, an Android 16 failure requires stopping and
preserving evidence without wiping or attempting a downgrade.

## Hardware Notes

- Screen firmware version: not recorded
- Carrier: tested by maintainer; exact carrier not recorded in this public doc
- SIM type: tested by maintainer; exact SIM details not recorded in this public doc
- Region/country: locale `en-US`
- Bootloader state: unlocked; verified boot state `orange`
- Storage size: `/data` reports 228G total, 226G available at capture time
- Kernel: 5.10.233 Android 12 vendor kernel, built Feb 20 2025
- SoC: MediaTek MT6789

## Manual Workarounds Applied

- PHH presets: MP01 overlay enabled (`me.phh.treble.overlay.minimal.mp01`)
- IMS APN: not recorded in the retained public evidence
- IMS APK: MTK IMS telephony overlay enabled
- FinQwerty layout: package installed; selected physical layout still needs manual verification
- Default launcher: `app.inkos/com.github.gezimos.inkos.MainActivity`
- Light theme: enabled (`ui_night_mode=1`)
- E-ink refresh setting: not recorded

## Test Results

| Area | Status | Notes |
| --- | --- | --- |
| Boot/setup | Pass | User reported working install; ADB reports setup complete |
| Wi-Fi | Unknown | Wi-Fi was off during ADB capture |
| Bluetooth | Unknown | Not recorded in the retained baseline evidence |
| Mobile data | Pass | Tested by maintainer on the accepted baseline image |
| Calls | Pass | Tested by maintainer on the accepted baseline image |
| SMS | Pass | Tested by maintainer on the accepted baseline image |
| MMS | Unknown | Not separately recorded |
| VoLTE/IMS | Pass | Radio/SIM behavior reported working on the accepted baseline image |
| Physical keyboard | Unknown | FinQwerty is installed; layout still needs manual verification |
| E-ink refresh | Unknown | Not recorded in the retained baseline evidence |
| Suspend/resume | Unknown | Not recorded in the retained baseline evidence |
| Charging | Unknown | Battery service reported charging and 13% level during capture |
| OTA | Unknown | Installed baseline image still points at `MP01Experiments/MP01-LineageGSI`. Dormant repository configuration records `MP01-LineageOS/MP01-LineageGSI` for a possible future release, but OTA publication remains disabled and no audit/test artifact is authorized to use it. |

## Raw Evidence

Keep raw bugreports private unless redacted.

- ADB snapshot folder:
  the historical raw ADB snapshot was not migrated and is unavailable; the
  verified release archive and extracted image now exist separately under
  `/home/user/MP01-LineageOS/logs/mp01-baseline/release-assets/`
- Bugreport filename: not captured
- Photos/screenshots: none retained in this development workspace
- Notes: captured `getprop`, package list, settings, mount/df, input, display,
  power, battery, telecom, telephony registry, overlays, launcher resolution,
  and recent activity state.

The historical FinQwerty application signing key is unrelated to the Android OS
platform and APEX signing identities. It cannot establish baseline OS signer
compatibility.
