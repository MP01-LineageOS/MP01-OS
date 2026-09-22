# MP01 OS

New development targets an MP01-specific GrapheneOS 17 derivative. See the
[implementation status](docs/grapheneos-17.md) and
[acceptance and phone handoff checklist](docs/grapheneos-17-acceptance.md).
No GrapheneOS-based image has been built or flashed. The LineageOS state below
is retained as source history and recovery evidence.

This organization continues the Minimal Phone MP01 LineageOS/Treble GSI work
started in `MP01Experiments`.

## Repositories

- [`MP01-LineageGSI`](https://github.com/MP01-LineageOS/MP01-LineageGSI):
  external build-support, product, patch, release-input, and MP01 vendor repo. It
  is imported by the build driver rather than synced as a manifest project.
- [`treble_manifest`](https://github.com/MP01-LineageOS/treble_manifest): exact
  14-project input manifest for LineageOS/Treble source dependencies. The microG
  build removes `vendor/gapps`, so the normalized effective manifest contains
  13 of those custom projects.
- [`device_phh_treble`](https://github.com/MP01-LineageOS/device_phh_treble): PHH/TrebleDroid device tree and GSI target support.
- [`vendor_hardware_overlay`](https://github.com/MP01-LineageOS/vendor_hardware_overlay): Android runtime resource overlays for device/vendor quirks.
- [`treble_app`](https://github.com/MP01-LineageOS/treble_app): privileged TrebleDroid settings app and preset application logic.
- [`treble_presets`](https://github.com/MP01-LineageOS/treble_presets): device preset database, including the Minimal Phone MP01 entry.
- [`finqwerty`](https://github.com/MP01-LineageOS/finqwerty): historical
  Android 15 baseline input. It is retained for source archaeology but is not
  shipped in the active LineageOS 23.2 product; the MP01 system keymap is owned
  by `MP01-LineageGSI`. Its former repository signing key is compromised and
  must not be reused.
- [`Phone`](https://github.com/MP01-LineageOS/Phone): Fossify Phone fork tracked for possible MP01 image integration.
- [`Messages`](https://github.com/MP01-LineageOS/Messages): Fossify Messages fork tracked for possible MP01 image integration.

## Current Priorities

1. Preserve the completed LineageOS 23.2 / Android 16 software audit from GSI
   head `c88e039`. The earlier source and Android-output blockers are fixed.
   The `6129977` build was intentionally stopped after review found its ad hoc
   wrapper did not preserve `tee` failure status, so it remains evidence only.
   Commit `16aa5f8` adds the fail-closed contract-v1 transcript harness, and
   `3d1bfa4` removes current test-key flashing commands from the GSI guidance.
   The first contract-v1 run then exposed an old patch-runner false positive and
   a no-kernel generated-header failure; `11bdbbd` makes patch application
   fail closed and `cb9eab6` handles generated headers for GSI targets. That
   build reached the MP01 e-ink daemon and exposed a stale fortify override.
   Head `2fd5dec` fixed that defect and completed Android compilation, but its
   post-build signer gate found that the Make prebuilt pipeline had rewritten
   privileged presigned partner APKs and stripped their v2/v3 signing blocks.
   Head `c88e039` preserves and verifies the exact bytes and alignment of all
   five presigned partner APKs, and all 143 GSI tests pass. The Android build
   completed in `08:47:27`. All 47 auditor unit tests pass, and the retained
   independent audit records `PASS_AUDIT_ONLY_NOT_FOR_IN_PLACE_FLASH`. Its
   unsigned test-key output is software-audit-only and is never flash eligible.
2. Keep any output from the current host volume software-audit-only. Take the
   affected filesystem offline for verification/repair, then perform a clean
   candidate-producing build on verified storage and audit its target-files,
   resolved manifest, provenance, log, and checksums.
3. Complete qpublish review of the staged source state without pushing from the
   development qube.
4. Keep the audited test-key, non-release-signed Android 16 artifact blocked
   from flashing: its complete target-files comparison records `INCOMPATIBLE`,
   `NOT_FOR_IN_PLACE_FLASH`, and 750 incompatibilities. Produce a compatible
   final release identity or reviewed rotation path.
5. Install-test that final signed identity as an in-place, data-preserving
   upgrade before running the boot, keyboard, telephony, SMS/MMS, IMS,
   suspend/resume, partner-app, and e-ink matrix.
6. Keep OTA metadata and proprietary GMS packaging disabled until the signed
   in-place hardware gate passes.

## Maintainer Docs

- [Current state](docs/current-state.md)
- [Baseline capture](docs/baseline-capture.md)
- [Upstream dependencies](docs/upstream-dependencies.md)
- [Upstream update policy](docs/upstream-update-policy.md)
- [LineageOS 23.2 migration](docs/lineage-23.2-migration.md)
- [Action items](docs/action-items.md)
- [Reproducible build plan](docs/reproducible-build.md)
- [Release hygiene](docs/release-hygiene.md)
- [Device defaults](docs/device-defaults.md)
- [Hardware test matrix](docs/hardware-test-matrix.md)
- [Candidate test report](docs/candidate-test-report.md)
- [Working MP01 baseline record](baselines/working-mp01-2026-05.md)

## Remote Layout

Local checkouts should use:

- `origin`: active `MP01-LineageOS` fork.
- `mp01experiments`: previous inactive `MP01Experiments` fork.
- `upstream`: original upstream project, such as TrebleDroid, Fossify, FinQwerty, or MisterZtr.

Commits are created locally in the development qube. Every staging sequence
begins with `qpublish workspace-status` before any `qstage` command. Publishing
is delegated to the reviewed qpublish/`git-publish` flow; do not run `git push`
from the development qube.

## Release Policy

Release builds should be reproducible, signed with non-committed private keys,
and published with checksums, source revisions, build notes, and known issues.
Development/userdebug images must be clearly labeled and kept separate from
signed user releases.
