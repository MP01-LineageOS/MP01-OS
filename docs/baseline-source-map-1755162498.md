# Baseline Source Map - 1755162498

This records the best available source map for the known-good baseline release:

- Release: `1755162498`
- Release page: https://github.com/MP01Experiments/MP01-LineageGSI/releases/tag/1755162498
- Release asset: `MP01-Lineage-1755162498-signed.tar.gz`
- Asset size: 1,204,341,111 bytes
- Asset SHA256:
  `d6b3f74d30ca84a186b926027afa7340a15450c5fd05720919cde57e1a887b1f`
- Sole inner image: `MP01-Lineage-1755162498-signed.img`
- Inner image size: 2,613,407,744 bytes
- Inner image SHA256:
  `55e3465f65eaa112bff3cb59f79bbe233d8cb0721a44d29c95d51b6edd3a3d2f`
- Published: 2025-08-14T10:44:07Z
- Support repo tag commit:
  `99bd410eb7e620998db4be5246b23f36f531d4fe`

## Important Caveat

The inherited build script used moving branches and "latest release" downloads.
That means this is not a complete, cryptographic source lock. These commits are
the branch heads at or before the GitHub release publish time, which is the best
available reconstruction without an archived `repo manifest -r` output from the
original build.

The original signed tarball also cannot be reproduced byte-for-byte without the
original private signing keys.

The `release-keys` build tag is metadata, not proof of the certificate set used
for platform APKs, APEX payloads, or the system image. Those public identities
were extracted from the verified image instead. The exposed historical
FinQwerty application key is not an Android OS signing key.

## Public Signing Identity Map

The audit at
`/home/user/MP01-LineageOS/logs/mp01-baseline/release-assets/public-identity-audit/README.md`
records these baseline certificate SHA256 values:

| Role | Certificate SHA256 |
| --- | --- |
| Platform | `6a8c75f0fc84f7b4c7a4eadf443ddebe938ff0abde332ee1516fb91e756c447e` |
| Release/OTA | `c495956b1d898dc8731040f4a48256b30144b4958198687e076023f234cf70aa` |
| Shared | `9e8207aa328db085fffc5c2a6e32fa425bed1f6d68e0eb169091e4a4b73e378a` |
| Media | `4decc623b85f6024ffaa39d98f9ea1ba23caf7d82354240b8dcb6dea4c83b499` |
| Network stack | `f96c390a48c0093291ed09714635ccccc4ee6e3e555dd08cb48878377bed1028` |

The same audit records system AVB public-key SHA1
`cdbb77177f731920bbe0a0f94f84d9038ae0617d`, AVB rollback index
`1751328000`, all 222 released-image APK path/package signer identities, and
container-certificate plus payload-public-key identities for all 33 baseline
APEX files. The immutable `baseline-apk-signers.tsv` SHA256 is
`ff7167528971e0fccc84cfbfccc2c9842d7be27d1f5cb9b77edea6f234f8da9c`.
The immutable
`baseline-apex-signers.tsv` SHA256 is
`f7b48cd972fa58e9ce7b9710927edd0772e0792e9706b86ea60c8b9941ead93b`.
This is public identity evidence only. Private-key availability, the full
installed-device signer state, and candidate compatibility remain unproven.

## Reconstructed Inputs

| Input | Ref used by inherited build | Reconstructed commit or digest |
| --- | --- | --- |
| `LineageOS/android` | `lineage-22.2` | `e64bf2e7417450cb61c27a6a8ab45b569bbe7355` |
| `MP01Experiments/treble_manifest` | `15-los-qpr2` | `14b70f55973219b9fb752b4759d178b022906c4e` |
| `TrebleDroid/device_phh_treble` | `android-15.0` | `117638105138feabe2c10c0bf5fccc078dc6b4e5` |
| `MP01Experiments/vendor_hardware_overlay` | `pie` | `12732841e0f1f9764244f10e8d274e2fa761a069` |
| `phhusson/vendor_vndk-tests` | `master` | `533390a1d6bc98d86de6b9aab56825c1f03fddcb` |
| `TrebleDroid/vendor_interfaces` | `android-15.0` | `2d4ede0aee64ae34d3b6ec0815e69928aff055b9` |
| `phhusson/vendor_lptools` | `master` | `c8be7de57b80eab61a6f94ec86464a01fb9056f2` |
| `phhusson/vendor_magisk` | `android-10.0` | `d8056f8032a0f60f365ddfe5e9fccd7eaf3a655d` |
| `AndyCGYan/android_packages_apps_QcRilAm` | `master` | `dc599b67cc1e7e9a62ca15eef605e3b2546d0d42` |
| `naz664/prebuilts_vndk_v28` | `master` | `507526a5b27a170aea338ff747c7d6ecc9bb91bb` |
| `platform/prebuilts/vndk/v29` | fixed revision | `bef5d37dda9360940964f097d612c8032e140961` |
| `ponces/treble_adapter` | `master` | `d8d0eece896bd2b3957bdee893c5f46aa92b211f` |
| `MisterZtr/vendor_gapps` | `vic` | `bad4f18dd566cb6299f40e0f09bbf37a5e5100ac` |
| `Evolution-X/packages_apps_FaceUnlock` | `vic` | `24df19177f0dda70274a1602ecf82dee03c4d44c` |
| F-Droid privileged extension | `refs/tags/0.2.13` | fixed tag |
| `MP01Experiments/finqwerty` | latest release | `76cef2d`; asset SHA256 `d5fedb270671d13fa02177c53191bab6d76f99de133bac4c48efec65ed8d683e` |

## Local Artifact Status

The release archive and its sole extracted image are present at
`/home/user/MP01-LineageOS/logs/mp01-baseline/release-assets/`. Their filenames,
sizes, and SHA256 values match the records above.

The following historical source-reconstruction artifacts are absent and were
not migrated into this development workspace:

- Detached support worktree (unavailable):
  `/home/user/MP01-LineageOS/.worktrees/reproduce-1755162498`
- Local source-map TSV (unavailable):
  `/home/user/MP01-LineageOS/logs/mp01-baseline/source-map-1755162498.tsv`

## Downgrade Status

The archive and sole inner image are verified by filename, size, and SHA256, and
the released image's public APK/APEX/AVB identities are recorded. This
establishes availability, artifact integrity, and released-image identity, not
Android 16-to-15 downgrade safety. A usable downgrade procedure still needs an
explicitly approved hardware downgrade test that accounts for installed-state
signer and data compatibility and preserves user data.

Until that hardware gate passes, do not treat release `1755162498` as an
automatic recovery action after an Android 16 failure. Stop, preserve logs and
partition evidence, and do not wipe or downgrade the in-use phone.
