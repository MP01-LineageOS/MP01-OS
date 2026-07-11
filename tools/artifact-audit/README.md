# MP01 Test-Key Artifact Audit

This directory contains an isolated, host-only, fail-closed audit workflow.
It never invokes a phone command. A successful result is deliberately named
`PASS_AUDIT_ONLY_NOT_FOR_IN_PLACE_FLASH`: the expected test-key signer audit
returns status 3, reports incompatible signer identities, and cannot authorize
an in-place flash.

## Files

- `audit.sh`: isolated Python launcher retained under the familiar entry-point
  name. It does not invoke a shell.
- `audit.py`: artifact auditor and evidence writer.
- `config.example.json`: independently pinned source paths and expectations.
- `test_audit.py`: focused positive and negative unit fixtures.

## Use

1. Copy `config.example.json` to a new file under `/tmp`.
2. Set `after_epoch` to the final build's start/cutoff epoch.
3. After the build process exits, set `build_log` and the matching
   `expected.build_info["Build log"]` entry to that run's complete retained log.
   Set `expected.build_log_sha256` from a separate post-exit SHA256 calculation.
   Configure only the published `.log`, never its `.log.incomplete` staging
   path. The adjacent `<log>.start-epoch` record must contain exactly
   `after_epoch` plus LF. The log must be an absolute, canonical, nonempty
   regular file whose mtime is after both the cutoff and the publication epoch.
4. Replace every `REPLACE_ME...` value. Unresolved values are rejected.
5. Recalculate source, Python-tree, and both Java-tree expectations if a
   pinned input changed.
6. Set `evidence_dir` to a new absolute strict descendant of `logs_root`.
   Every ancestor must be a real directory, and the evidence path must be
   disjoint from source, output, metadata, target-files, build-log, and tool
   roots.
7. Run:

   ```sh
   tools/artifact-audit/audit.sh /tmp/mp01-final-audit.json
   ```

Run the focused unit suite from the repository root with:

```sh
/usr/bin/python3.14 -I -S tools/artifact-audit/test_audit.py
```

The example remains a template until every path and expectation is replaced or
independently revalidated for one completed build. It is not a record of a
completed artifact audit.

The auditor copies the complete build log and start record, formal-build harness
and log helper, every publication input, script, executable, JAR, manifest, and
both complete Java runtimes into the new evidence directory before hashing or
using the applicable retained executable. Every source file is hashed during
the copy, reopened and hashed
again immediately, and reopened and hashed once more before success. Source
and retained stat identities must also remain unchanged. The independently
supplied config pins `audit.py` and `audit.sh` themselves.

## Trust Boundaries

- Child processes receive an explicit nine-variable environment. Python
  children use the retained interpreter with `-I -S`. That interpreter's
  compiled prefix still resolves the host standard-library path, so the exact
  source tree is independently pinned, copied as evidence, and source- and
  retained-revalidated instead of being described as executed from the copy.
  The leading `python314.zip` search path must remain absent. A runtime probe
  imports the retained signer verifier plus the audit's compression, hashing,
  subprocess, tar, XML, ZIP, and TLS closure, then checks the exact `sys.path`
  and every mapped Python/DSO path.
- Native subprocesses still rely on the host kernel's dynamic-loader path.
  That explicit host-runtime trust boundary is pinned before use: loader,
  libpython, libc/libm compatibility DSOs, libgcc, OpenSSL/libz, bz2, lzma,
  zstd, and expat are copied, recorded, and source-revalidated after all
  commands. Before and after substantive commands, the retained loader resolves
  every DT_NEEDED dependency for Python, `env`, both aapt2 binaries, avbtool,
  deapexer, OpenSSL, signer Java, and libjvm. Every canonical dependency must be
  a configured runtime source or part of the retained signer JDK, and both
  resolution snapshots must match. Kernel/vDSO behavior is outside this
  artifact audit.
- The SDK launcher and source JAR are pinned, but the launcher is not executed.
  The immutable JAR snapshot retained by the TrebleApp build must be byte-equal
  to that source JAR. The signer rerun and TrebleApp verification invoke the
  separately retained Temurin 17 runtime and JAR directly; evidence binds both
  executable hashes. The Android build's JDK 21 tree is retained separately.
- `avbtool`'s OpenSSL child is separately retained, hashed, and resolved only
  from the retained tool directory. OpenSSL receives a retained minimal config
  and an empty retained provider-module directory, avoiding host crypto config.
- Marker scanning is implemented in Python, removing `bash`, `grep`, `mktemp`,
  `strings`, and `unzip` dependencies.
- The formal-build harness and log helper are retained and independently
  SHA256-pinned, but the auditor does not delegate transcript acceptance to the
  producer helper. It parses contract v1 itself and binds header device/inode
  values to its own stable source snapshots.
- `signer_aapt2` is the retained Android host tool selected by the original
  signer gate. `treble_aapt2` is the separately pinned SDK tool recorded by
  TrebleApp provenance.
- The resolved manifest is parsed as XML. Every decoded remote fetch is
  repeatedly percent-decoded until stable, Unicode-normalized, and checked
  against explicit network-scheme and safe-relative allowlists. Empty, local,
  absolute, unlisted relative, and over-nested encodings fail.
- Java receives explicit `user.home` and `java.io.tmpdir` properties inside the
  evidence directory. The signer verifier receives those paths through its
  direct Java/JAR flags and strips ambient Java option/classpath variables. A
  runtime probe requires the confined values and retained signer JDK as
  `java.home`. Its security configuration comes from that JDK.
- The audit assumes other processes running as the audit UID are quiescent and
  non-adversarial. No-follow descriptors, before/after identity checks, repeated
  hashing, manifest regeneration, fsync, and owner-read-only modes detect
  observed replacement or mutation; they cannot make files immutable against a
  hostile same-UID process after the final check or after return. Preserve the
  external root checksum separately or move the sealed evidence to storage with
  a stronger immutability boundary before relying on it later.

## Fail-Closed Checks

- Exactly one unsigned completion marker has an epoch and mtime after the
  cutoff. Its two strict checksum rows bind the retained image and tar.
- The configured complete build log is canonical, nonempty, regular, newer than
  the cutoff and publication epoch, retained as `build.log`, independently
  SHA256-pinned, and byte/stat revalidated at the final success boundary. Its
  adjacent start record is retained separately and must be exactly the decimal
  cutoff plus LF. Contract-v1 parsing independently requires the exact ordered
  format/harness/helper/commit/tree/start/path/inode/signer/output-begin header,
  rejects every reserved-key recurrence in build output, requires exactly one
  build-success line and one recognized signer line with the test-key warning
  last, and requires the ordered legacy/build/capture/completion footer at EOF.
  Header inode identities must match both source files before and after stable
  copies; harness/helper hashes and GSI commit/tree must match retained tools and
  build-info expectations. Build-info must point to that exact final log path.
- The retained gzip tar contains one regular image member byte-equal to the
  retained publication.
- Retained target-files passes full ZIP CRC/decompression validation, has no
  unsafe or duplicate names, and contains all 14 required paths plus one
  `IMAGES/system.img`. Each required entry is a nonempty regular non-symlink
  file, and the system image is byte-equal to the publication.
- Build-info exactly matches independent GSI, Soong, Blueprint, workspace,
  verifier, patch, build-log, relative `OUT_DIR`, product-output-name, and
  output-path expectations.
- The normalized manifest has exactly 1,177 projects, 13 configured prepared
  custom projects, exact revisions, no local fetch URL, no `vendor/gapps`, and
  no GSI support project.
- AVB footer and hashtree verification succeeds and the public-key SHA1 is the
  configured value.
- TrebleApp has the expected package, all eight patched markers, one configured
  platform signer, exact signing-independent content, and exact `classes.dex`.
- The signer verifier rerun returns exactly 3. Its retained snapshot matches
  target-files; actual manifest and evidence match build-info byte-for-byte;
  issue keys are contiguous; rows follow the six-field generator schema and
  sort order; incompatibility/warning counts exactly match row severities.

All generated files and directories are fsynced. On success,
`evidence-sha256sums.txt` records every retained regular file and symlink.
Regular rows are hashed through no-follow descriptors with matching
before/after file and pathname identities; every retained source record must
match one file row's path, type, size, and hash. Before committing success, the
auditor re-reads result, status, and manifest bytes, regenerates the complete
manifest, applies owner-read-only modes, repeats the evidence verification, and
fsyncs the evidence tree and parent. Only then does it create the sibling
`<evidence-name>.root.sha256` as the last commit step, fsync its file and parent,
and stably re-read its exact content. No substantive audit work follows that
readback. Absence of the external root means the evidence is not a completed
audit, even if interrupted provisional files contain PASS text. Failure cleanup
invalidates a created root before durably unlinking it, removes the uncommitted
manifest, and best-effort rewrites and fsyncs `audit-result.json` and
`status.txt` as failed. A cleanup error is surfaced rather than silently leaving
a possibly plausible completion anchor.
