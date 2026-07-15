# MP01 Device Defaults

This tracks issue `#10`: turning inherited manual setup workarounds into
defaults without changing radio-sensitive behavior before device testing.

## Ownership Matrix

| Default | Owning repo | Current state |
| --- | --- | --- |
| Physical keyboard | `MP01-LineageGSI` | `vendor/MP01_services` installs `aw9523b-key.idc`, `.kl`, and `.kcm` into `system/usr`. The IDC uses extensionless `keyboard.layout = aw9523b-key`, matching Android input discovery. Preflight and host keymap checks pass. FinQwerty is not shipped. |
| Default launcher | `MP01-LineageGSI` | SetupWizard assigns `app.inkos` as home and launches `app.inkos/com.github.gezimos.inkos.MainActivity` after setup. Release-input verification requires that exact package and enabled MAIN/HOME activity. The Android 16 patch keeps Launcher3 as fallback but lowers its HOME priority to `-999` at `packages/apps/Launcher3`. |
| Light theme | `MP01-LineageGSI` | `MP01AccessibilityService` seeds `ui_night_mode=1` before setup completes. It records `mp01_defaults_version=1` and does not overwrite configured phones unless `persist.mp01.defaults.force=1`. |
| Accessibility service | `MP01-LineageGSI` | Boot setup compares normalized component names, preserves other enabled services, appends the MP01 service only when absent, and sets the platform accessibility switch after the list write. It no longer depends on `persist.accessibility.enabled_service`. The privapp whitelist installs as `privapp-permissions-accessibility.xml`. |
| PHH presets | `treble_app`, `treble_presets`, `MP01-LineageGSI` | MP01 product makefiles point `ro.system.treble.presets` at validated commit `5891dba9621542b297acd761dbf3fe98d841c214`. Every fully prepared candidate requires exactly one property equal to the verified URL; optional local-only repo sync does not skip preparation. Contract tests reject unknown keys, wrong value types, and action-only preferences. |
| TrebleApp package | `MP01-LineageGSI`, `treble_app` | The manifest pins source commit `9d8a6771d94b7985f515b41bd280f7bdb4554037`. The build applies nine MP01 patches and expects the resulting prebuilt to be unsigned. It records every non-signature ZIP entry deterministically plus a focused `classes.dex` subcheck, replaces the stale prebuilt, and requires installed and target-files copies to each have exactly one platform signer with identical non-signature content. |
| IMS setup | `treble_presets`, `vendor_hardware_overlay`, `treble_app` | Inventoried only. Existing SIM/radio behavior is accepted from baseline testing; further IMS defaults need flashed-image testing. |
| E-ink refresh tuning | `MP01-LineageGSI` | Still manual. Current service defaults and README guidance do not agree strongly enough to change without hardware testing. |

## Issue 10 Progress

- Implemented the lowest-risk defaults first: keyboard ownership documentation,
  inkOS home component cleanup, light theme seeding, and pinned PHH preset
  source.
- Deferred IMS and e-ink behavior changes because they can affect telephony or
  user-visible display behavior and need a flashed test image.
- Do not close issue `#10` until a test image passes the device acceptance
  checklist.

## Device Acceptance Checklist

The audited test-key build is not eligible for this checklist. Its complete
target-files comparison covered 616 APKs and 44 APEXes and returned 750
incompatibilities, `comparison_status=INCOMPATIBLE`, and
`flash_disposition=NOT_FOR_IN_PLACE_FLASH`; no compatible signing or rotation
path is available. A future clean verified-storage candidate must be compared
again. Run these checks
only when `release-candidate` exits `0` with
`comparison_status=COMPATIBLE_SIGNER_IDENTITIES` and
`flash_disposition=SIGNER_GATE_PASSED_HARDWARE_TEST_STILL_REQUIRED` for the
exact target-files APK and APEX container/payload identities under test.
Because this is a system-image-only GSI with no built kernel, the build-time
kernel VINTF warning is a skipped check, not a pass. Exact-device
`VtsTrebleVintfTest` `SystemVendorTest.KernelCompatibility` must pass separately;
OTA publication remains disabled.

- The in-place upgrade returns to the existing user session without setup or a
  reset; record `settings get secure ui_night_mode` without overwriting the
  user's choice.
- Record `settings get secure mp01_defaults_version` after the upgraded boot.
  Do not wipe data to exercise fresh-setup behavior.
- Home resolves to `app.inkos/com.github.gezimos.inkos.MainActivity`.
- `dumpsys input` shows `aw9523b-key.idc`, `aw9523b-key.kl`, and
  `aw9523b-key.kcm`.
- MP01 accessibility service remains enabled.
- Other previously enabled accessibility services remain in the secure setting,
  with no duplicate MP01 component, and `accessibility_enabled` is `1`.
- `system/etc/permissions/privapp-permissions-accessibility.xml` is installed
  and the service has its expected privileged permission state.
- Basic typing works, including MP01 symbol and alt mappings.
- PHH preset source property points at the pinned `MP01-LineageOS` raw URL.
- SIM/radio behavior has no regression when a SIM is available.
