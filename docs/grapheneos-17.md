# MP01 GrapheneOS 17 implementation state

Status: source/build tooling implemented and tested locally; the pinned Android
source sync is **underway** in the Debian 12 container. Full compilation remains
blocked by the current RAM allocation and a missing MP01 device inventory.
There is no prepared-source receipt yet, new image, signed release or hardware
compatibility claim. Android 17 remains the selected base.

The Pixel 8a stays the daily phone. The operator describes the MP01 as empty and
available for connection later. The primary cellular test is **AT&T in the
USA**; include **T-Mobile in the USA** as an additional carrier test. Being
empty does not authorize a wipe in a future flashing session.

## Preserved work and cleanup

The source checkpoint is local and private:
`/home/user/MP01-LineageOS/.checkpoints/before-grapheneos-17-20260922T015345Z`.
It contains verified all-ref Git bundles, index/working-tree binary patches,
untracked files, worktree locations, branch/head records and SHA256 inventories
for all eleven project repositories. Restore a bundle into a new checkout,
then apply the saved index/working-tree state and restore untracked files as
needed; do not apply a combined working-tree patch and the index patch twice.
Original source locations and all legacy branches remain present.

The former uncommitted source-lock/auditor work is preserved in logical local
commits on `grapheneos-17` in `MP01-LineageGSI` and `MP01-OS`. The source-lock
test's dynamic import and the auditor example's stale self-hash were corrected;
all six source-lock and 49 independent auditor tests passed. The old LineageOS
lock files remain provisional historical inputs, not GrapheneOS inputs.

Before cleanup, all **7,708** entries of the sealed historical audit were
verified against evidence manifest SHA256
`98351dd90323101da3d8c3a5e88238509974306b748c20553fd406f0ad379ab2`.
The retained target-files snapshot has SHA256
`86c77ab15594caf1b1dfc5a585c1023b781690489b82507c7a48a347be75fe2a`.
The retained tool/runtime snapshots, source evidence, images and release
metadata were preserved. Both known-good recovery archive/image hashes were
rechecked against the [baseline](../baselines/working-mp01-2026-05.md).
This confirms retained bytes, not a tested downgrade/recovery procedure.

Removed only `.android-build/los23.2-microg/out`, the old compiler cache, and the
four named inactive MP01 build swap files. The build lock was held, active
compiler processes were checked, swap activity was rechecked before removal,
and neither the active swap partition nor source repositories were removed.
Cleanup reclaimed **199,238,901,760 bytes (185.6 GiB)** and left approximately
**429.8 GiB free**. Detailed before/after values and removed paths are in the
checkpoint's `cleanup.json`; retention checks are in `retention-verified.json`.

The prior storage-repair report remains evidence. No new offline filesystem
verification was performed in this session. Checkpoint hashing does not prove
that every retained Android source object is healthy; use a fresh source sync
and complete storage verification before treating builds as release evidence.

## Implemented source path

`MP01-LineageGSI/grapheneos` provides the isolated `mp01-cur-userdebug` and
`mp01-cur-user` product declarations, pinned Debian 12 recipe, rootless Podman
runner, resource preflight, exact upstream source graph, strict patch series,
prepared-source receipts, and unsigned target-files build runner. The existing
MP01 daemon, accessibility UI, defaults and keyboard sources are imported by
an explicit allowlist with the pinned inkOS APK. Existing LineageOS/microG
build entrypoints remain historical and are not called by this workflow.

The source pin is GrapheneOS release `2026091900`, manifest commit
`4522145007c563aad00360ab1384e6deca6605bb`, with 1,057 commit-pinned projects.
The release tag signature was verified against the public verification file
downloaded from GrapheneOS over HTTPS, pinned as
`344f59c6f058699e63fea68e35953b341c14e3bf1fbc1256f6baa84aa2aca1d0`.
Only that upstream public material was used; no operator SSH credentials or
private release signing material was accessed.
The single product-scoped patch excludes Auditor on MP01 while retaining it on
other products. Its exact resulting commit was independently reproduced by
applying the patch to the pinned upstream build repository. RestlessOS commit
`d7755a60d2d3f17a64cbe267574c83d6af4e1b2b` remains a reference; no compatibility
patch stack was copied wholesale. The kernel and vendor firmware are retained.
See [upstream build guidance](https://grapheneos.org/build) and the
[pinned reference](https://github.com/cawilliamson/treble_restlessos/tree/d7755a60d2d3f17a64cbe267574c83d6af4e1b2b).

The signer audit interface now distinguishes development, initial-installation
and upgrade profiles. Initial candidates use the new project's trusted public
signing policy. Upgrades additionally compare against a trusted previous MP01
report, including signer continuity, package versions, SDK, timestamp and vendor
baseline. Presigned upstream packages require exact byte hashes. Passing this
signer gate does **not** mean full artifact audit, AVB verification, hardware
validation or installation authorization has passed.

## Current prerequisites

1. Allocate sufficient RAM to this qube: on 2026-09-22 the guest reported
   7.7 GiB allocated and about 6 GiB available. Earlier Xen ballooning had
   reduced the observed allocation to approximately 3.1 GiB; the configured
   maximum cannot be established from guest observations. Builds require
   32 GiB allocated and 28 GiB available, with a four-job cap; prefer a 48 GiB
   maximum/allocation to allow guest overhead. Swap does not satisfy this gate.
2. Rootless Podman 5.8.4 is available. **Fedora stays the host; Debian 12 runs
   inside the container.** The digest-pinned image built successfully after the
   Debian snapshot recipe enabled `contrib` for the `repo` launcher. The
   container source-sync preflight passed. Rootless source sync uses
   `slirp4netns`; verification and builds use no network. The sync is running
   against the pinned 1,057-project graph, with no completion claim or prepared
   receipt yet. Its monitored free-space floor is 240 GiB. The original
   429.8 GiB post-cleanup free-space measurement above is historical; about
   329 GiB remained during the active sync on 2026-09-22.
3. Later, attach the MP01 to a dedicated device-test/flashing qube and
   authorize adb there. No phone needs to be attached to the development qube
   or flashed immediately after a build. Identify the serial and capture the
   fresh, read-only device contract before making vendor compatibility or
   partition decisions, as described below. The retained SDK executable works
   in this qube, but `adb devices -l` currently lists no device.
4. Have qadmin correct the qpublish outbox lock ownership/mode problem.
   `qpublish workspace-status` fails with `outbox lock has unsafe ownership or
   mode`. Do not change its permissions here or bypass the broker. The registry
   still assigns `MP01-LineageGSI` to target `15`, and `MP01-OS` to `main`.
   qadmin must authorize any intended `grapheneos-17` publication target before
   staging; a local branch name is not that authorization. Nothing was staged
   or pushed during this implementation.

The source-sync disk budget passed after cleanup and continues to account for
bytes already allocated by the incomplete pinned checkout when resuming. The
actual build preflight still rejects the present RAM allocation. No memory
stress allocation was used to force balloon growth.

## Verification completed

**127 Python host tests passed:** 49 retained artifact-auditor, six preserved
source-lock, 37 existing signer-inventory, 17 new build/source/transcript, 14 new
signer-profile and four device-selection tests. The new transcript tests cover
nonzero build exit, failed log fsync, exhausted disk reserve and failed resource
monitoring. The existing native e-ink command-stream tests also compiled with
warnings treated as errors and passed.

Additional checks passed for container-shell syntax, signed upstream manifest
verification, exact compatibility-patch commit reproduction and GNU Make
package selection for both `mp01` and `husky`. The device collector failed
cleanly with a disconnected serial and created no inventory directory. The
container runner's earlier refusal to start without Podman was superseded by
a successful pinned image build and container source-sync preflight. Focused
builder tests passed after enabling Debian `contrib`, rootless `slirp4netns`,
tag-limited source fetches and resume-aware disk accounting. These are
host/tooling and container dependency results; source sync, Android compilation
and every device acceptance row remain unverified.

## Fresh device capture

Use the serial printed for the MP01, never an inferred first attached device.
The following paths assume a checkout and adb installation in the qube where
the MP01 is attached; adjust only those paths for the dedicated test qube:

```bash
cd /home/user/MP01-LineageOS
.android-build/android-sdk-test/platform-tools/adb devices -l
python3 MP01-OS/tools/device/inventory.py \
  --adb .android-build/android-sdk-test/platform-tools/adb \
  --serial MP01_SERIAL \
  --output logs/mp01-inventory-TIMESTAMP
```

The tool requires `ro.product.vendor.model=MP01` and rejects Pixel identities.
It never roots, reboots, flashes, writes properties or writes hardware nodes.
Unavailable commands and denied reads are retained as gaps. Raw evidence is
private (directory mode 0700, files 0600); only reviewed summaries belong in Git.
If vendor identity differs, inspect it manually and review the identity rule;
do not add a generic MediaTek or arm64 bypass.

Keep source edits, Android builds and build caches in this development qube,
with Debian 12 inside its pinned container. Keep private release keys in the
separate signing environment. The dedicated MP01 test/flashing qube can remain
offline except for the [manually attached MP01 through `sys-usb`](https://doc.qubes-os.org/en/r4.3/user/how-to-guides/how-to-use-usb-devices.html).
Run read-only device capture there and use [Qubes inter-qube file copy](https://doc.qubes-os.org/en/r4.3/user/how-to-guides/how-to-copy-and-move-files.html)
to transfer its private inventory back to development;
record the source qube, MP01 serial, capture time and file hashes. This is
device evidence, not authorization to flash. The phone need not be connected
until this inventory is needed, and the first installation can wait after the
image is built.

When signed release packaging exists, transfer the complete signed and audited
bundle to the test/flashing qube, not a bare `system.img`. Verify its
authenticated checksums against trusted public project verification material
provisioned independently of the copied bundle. Verify the source/provenance
record, signer inventory, required vendor baseline and intended installation
profile there before any partition operation. A file copy alone proves neither
authenticity nor device compatibility. The exact partition/recovery contract
and USB executor are still unimplemented, so there is no flash-ready bundle or
procedure yet. Ordinary updates must preserve userdata and metadata; a clean
install/data wipe, if one proves necessary, needs explicit confirmation for
that particular flashing session.

Review firmware/kernel versions, bootloader state, ABI/binder, partitions and
fstab, VNDK/VINTF, encryption and keystore services, and the resolved light/e-ink
nodes. Kernel configuration reads may be denied; missing evidence needs a
separate supported read method. Service presence alone does not validate
Keystore or encryption. Confirm the matching recovery procedure before any
installation. Do not infer OEM relocking support or rollback safety.

`clean_a2` and `anti_flicker` keep their existing development-only init path.
The inventory searches for sysfs alternatives. No production debugfs exception
has been added without device evidence. If required, scope it to MP01, init and
exactly those nodes, and test unauthorized app/daemon access plus unrelated
debugfs denial in compiled production policy and on-device.

## Installation and release work still to do

Complete real source sync/build and the device compatibility work first. Stop
with a reproducible Android 17 incompatibility report if the vendor stack
cannot satisfy release requirements; do not weaken compatibility checks or
silently downgrade. Record every hardening exception with component, failure,
test and lost protection. Keep distinct branding and separate framework,
kernel and vendor security status.

Create persistent release keys in the separate signing environment. Extend
the independent whole-artifact audit for this source/provenance format; the
historical LineageOS auditor is preserved and not treated as equivalent. Every
release needs authenticated checksums, source locks, build provenance,
package/signing inventory, required vendor baseline and validation results.
Retain the current and previous signed release artifacts.

The USB executor remains unimplemented until the actual partition/recovery
contract and signed bundle format are validated. It must match the explicit
MP01 serial plus independently captured vendor/fastboot identity, reject the
Pixel, verify authenticated bundle contents and installation profile, then
show every partition operation. The default update operation is limited to the
confirmed system partition and must preserve userdata/metadata. Unknown image
size/partition capacity, downgrade, unexpected slot/layout, unsupported signer
state or vendor mismatch must stop the operation. No automatic relocking,
resizing or wiping is allowed. Prepare an exact initial-install operation list
before asking for session-specific clean-install/data-wipe confirmation.

A second release using the same project keys must demonstrate apps, messages,
settings and authentication surviving a normal USB update. Production policy,
carrier/apps, recovery, overnight standby, seven-day trial and the two phone
handoff round trips remain unrun; use the companion acceptance checklist.
