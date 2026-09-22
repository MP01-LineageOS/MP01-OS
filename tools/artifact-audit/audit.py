#!/usr/bin/env -S /usr/bin/python3.14 -I -S
"""Fail-closed, host-only audit of one MP01 test-key build publication."""

from __future__ import annotations

import dataclasses
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tarfile
import time
import unicodedata
import urllib.parse
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path, PurePosixPath
from typing import BinaryIO, Callable


SHA256_RE = re.compile(r"[0-9a-f]{64}")
SHA1_RE = re.compile(r"[0-9a-f]{40}")
REVISION_RE = re.compile(r"[0-9a-f]{40}")
MARKER_RE = re.compile(
    r"MP01-Lineage-(?P<epoch>[0-9]+)-microG-unsigned\.sha256sums"
)
CHECKSUM_RE = re.compile(r"(?P<sha>[0-9a-f]{64})  (?P<name>[^/\n]+)")
ISSUE_KEY_RE = re.compile(r"issue\.(?P<index>[0-9]{4})")
PLACEHOLDER_RE = re.compile(r"(?:REPLACE_ME|__FILL|<FILL|PENDING)", re.I)
CHUNK = 4 * 1024 * 1024
FORMAL_BUILD_LOG_FORMAT_VERSION = "1"
FORMAL_BUILD_LOG_HEADER_KEYS = (
    "MP01_FORMAL_BUILD_LOG_FORMAT_VERSION",
    "MP01_FORMAL_BUILD_HARNESS_SHA256",
    "MP01_FORMAL_BUILD_LOG_HELPER_SHA256",
    "MP01_FORMAL_BUILD_GSI_COMMIT",
    "MP01_FORMAL_BUILD_GSI_TREE",
    "MP01_FORMAL_BUILD_START_EPOCH",
    "MP01_FORMAL_BUILD_START_RECORD_ST_DEV",
    "MP01_FORMAL_BUILD_START_RECORD_ST_INO",
    "MP01_FORMAL_BUILD_LOG_PATH",
    "MP01_FORMAL_BUILD_LOG_SOURCE_ST_DEV",
    "MP01_FORMAL_BUILD_LOG_SOURCE_ST_INO",
    "MP01_FORMAL_BUILD_SIGNER_COMPATIBILITY_MODE",
    "MP01_FORMAL_BUILD_OUTPUT_BEGIN",
)
FORMAL_BUILD_LOG_FOOTER_LINES = (
    b"MP01_BUILD_EXIT_STATUS=0\n",
    b"MP01_BUILD_COMMAND_EXIT_STATUS=0\n",
    b"MP01_BUILD_LOG_CAPTURE_EXIT_STATUS=0\n",
    b"MP01_FORMAL_BUILD_LOG_COMPLETE=1\n",
)
FORMAL_BUILD_LOG_FOOTER_KEYS = tuple(
    line.decode("ascii").split("=", 1)[0]
    for line in FORMAL_BUILD_LOG_FOOTER_LINES
)
FORMAL_BUILD_LOG_RESERVED_PREFIXES = tuple(
    key.encode("ascii") + b"="
    for key in (*FORMAL_BUILD_LOG_HEADER_KEYS, *FORMAL_BUILD_LOG_FOOTER_KEYS)
)
BUILD_LOG_SUCCESS_LINE = b"Build completed successfully.\n"
BUILD_LOG_SIGNING_LINE = (
    b"Signing status: unsigned local test image; NOT FOR IN-PLACE FLASH\n"
)
BUILD_LOG_RELEASE_SIGNING_LINE = (
    b"Signing status: signer-compatible release candidate; "
    b"hardware gate still required\n"
)
BUILD_LOG_RECOGNIZED_SIGNING_LINES = frozenset(
    (BUILD_LOG_SIGNING_LINE, BUILD_LOG_RELEASE_SIGNING_LINE)
)
SOURCE_INPUT_MANIFEST_LOCK = "source-locks/lineage-23.2-microg-input.xml"
PREPARED_SOURCE_MANIFEST_LOCK = "source-locks/lineage-23.2-microg-prepared.xml"

REQUIRED_TARGET_FILES = (
    "SYSTEM/priv-app/TrebleApp/TrebleApp.apk",
    "SYSTEM/priv-app/MP01AccessibilityService/MP01AccessibilityService.apk",
    "SYSTEM/bin/MP01_eink_server",
    "SYSTEM/etc/init/MP01_eink_daemon.rc",
    "SYSTEM/etc/permissions/privapp-permissions-accessibility.xml",
    "SYSTEM/app/inkos/inkos.apk",
    "SYSTEM/usr/idc/aw9523b-key.idc",
    "SYSTEM/usr/keylayout/aw9523b-key.kl",
    "SYSTEM/usr/keychars/aw9523b-key.kcm",
    "SYSTEM/product/priv-app/GmsCore/GmsCore.apk",
    "SYSTEM/product/priv-app/FakeStore/FakeStore.apk",
    "SYSTEM/product/app/GsfProxy/GsfProxy.apk",
    "SYSTEM/product/app/FDroid/FDroid.apk",
    "SYSTEM/product/priv-app/FDroidPrivilegedExtension/FDroidPrivilegedExtension.apk",
)
SYSTEM_IMAGE_ENTRY = "IMAGES/system.img"
TREBLE_APP_ENTRY = "SYSTEM/priv-app/TrebleApp/TrebleApp.apk"
PARTNER_APK_TARGETS = (
    ("GmsCore", "SYSTEM/product/priv-app/GmsCore/GmsCore.apk"),
    ("FakeStore", "SYSTEM/product/priv-app/FakeStore/FakeStore.apk"),
    ("GsfProxy", "SYSTEM/product/app/GsfProxy/GsfProxy.apk"),
    ("FDroid", "SYSTEM/product/app/FDroid/FDroid.apk"),
    (
        "FDroidPrivilegedExtension",
        "SYSTEM/product/priv-app/FDroidPrivilegedExtension/FDroidPrivilegedExtension.apk",
    ),
)
TREBLE_MARKERS = (
    "persist.sys.phh.securize",
    "elixir_system_extra_pref",
    "persist.sys.phh.disable_display_doze_suspend",
    "persist.sys.phh.status_bar_padding_top",
    "persist.sys.phh.sf_auto_latch_unsignaled",
    "persist.sys.activity_anim_perf_override",
    "persist.sys.phh.prefer_hw_codecs",
    "IMS download failed: ",
)

MANDATORY_BUILD_INFO_KEYS = (
    "Live MP01-LineageGSI commit",
    "Live MP01-LineageGSI tree",
    "Cloned support commit",
    "Cloned support tree",
    "Workspace path policy",
    "Workspace path policy SHA256",
    "Minimum free space GiB",
    "Allow non-workspace build",
    "build/soong base commit",
    "build/soong base tree",
    "build/soong prepared commit",
    "build/soong prepared tree",
    "build/soong Metalava patch",
    "build/soong Metalava patch SHA256",
    "Metalava policy verifier",
    "Metalava policy verifier SHA256",
    "build/blueprint base commit",
    "build/blueprint base tree",
    "build/blueprint prepared commit",
    "build/blueprint prepared tree",
    "build/blueprint provider-validation patch",
    "build/blueprint provider-validation patch SHA256",
    "Blueprint provider-validation verifier",
    "Blueprint provider-validation verifier SHA256",
    "vendor/lineage base commit",
    "vendor/lineage base tree",
    "vendor/lineage prepared commit",
    "vendor/lineage prepared tree",
    "vendor/lineage no-kernel header patch",
    "vendor/lineage no-kernel header patch SHA256",
    "No-kernel header policy verifier",
    "No-kernel header policy verifier SHA256",
    "Android TARGET_NO_KERNEL",
    "vendor/partner_gms base commit",
    "vendor/partner_gms base tree",
    "vendor/partner_gms prepared commit",
    "vendor/partner_gms prepared tree",
    "vendor/partner_gms presigned APK patch",
    "vendor/partner_gms presigned APK patch SHA256",
    "Presigned partner APK policy verifier",
    "Presigned partner APK policy verifier SHA256",
    "Presigned partner APK byte preservation",
    "Presigned partner APK alignment",
    "Android JDK home",
    "Android JDK version",
    "TrebleApp APK signer temporary directory",
    "TrebleApp APK signer Java",
    "TrebleApp APK signer Java SHA256",
    "TrebleApp APK signer Java user home",
    "TrebleApp APK signer Java temp directory",
    "Expected TrebleApp APK signer Java SHA256",
    "TrebleApp APK signer JAR",
    "TrebleApp APK signer JAR SHA256",
    "Expected TrebleApp APK signer JAR SHA256",
    "Build root",
    "Android OUT_DIR interface",
    "Android output root",
    "Android product output",
    "Android product output name",
    "Android host output",
    "Android dist directory",
    "Go temporary directory",
    "ccache temporary directory",
    "TrebleApp Gradle user home",
    "Build lock path",
    "Publication lock path",
    "Build log",
    "Source input manifest lock",
    "Source input manifest lock SHA256",
    "Prepared source manifest lock",
    "Prepared source manifest lock SHA256",
    "Resolved manifest SHA256",
)

REQUIRED_PATH_KEYS = {
    "android_host_out",
    "python_executable",
    "python_stdlib",
    "java_home",
    "signer_java_home",
    "signer_verifier",
    "signer_manifest",
    "signer_aapt2",
    "treble_aapt2",
    "avbtool",
    "deapexer",
    "openssl",
    "env_executable",
    "runtime_loader",
    "runtime_libpython",
    "runtime_libc",
    "runtime_libm",
    "runtime_libpthread",
    "runtime_libdl",
    "runtime_librt",
    "runtime_libgcc",
    "runtime_libutil",
    "runtime_libssl",
    "runtime_libcrypto",
    "runtime_libz",
    "runtime_libbz2",
    "runtime_liblzma",
    "runtime_libzstd",
    "runtime_libexpat",
    "runtime_libcxx",
    "apksigner_launcher",
    "apksigner_source_jar",
    "apksigner_jar",
    "apk_content_manifest",
    "treble_expected_content_manifest",
    "workspace_path_policy",
    "metalava_patch",
    "metalava_policy_verifier",
    "blueprint_patch",
    "blueprint_provider_validation_verifier",
    "vendor_lineage_no_kernel_patch",
    "no_kernel_header_policy_verifier",
    "partner_gms_presigned_apk_patch",
    "presigned_partner_apk_policy_verifier",
    "partner_zipalign",
    "formal_build_harness",
    "formal_build_log_helper",
    "source_input_manifest_lock",
    "prepared_source_manifest_lock",
}

EVIDENCE_BASE_KEYS = (
    "format",
    "mode",
    "comparison_status",
    "flash_disposition",
    "target_files_sha256",
    "expected_manifest_sha256",
    "expected_baseline_archive_sha256",
    "expected_baseline_image_sha256",
    "expected_baseline_apk_inventory_sha256",
    "expected_baseline_apex_inventory_sha256",
    "expected_apk_coverage",
    "expected_apex_coverage",
    "actual_manifest_sha256",
    "actual_apk_count",
    "actual_apex_count",
    "incompatibility_count",
    "warning_count",
    "apksigner_execution",
    "apksigner_java_sha256",
    "apksigner_jar_sha256",
)


class AuditError(RuntimeError):
    """An artifact or audit precondition failed."""


@dataclasses.dataclass(frozen=True)
class StatSignature:
    device: int
    inode: int
    mode: int
    links: int
    uid: int
    gid: int
    size: int
    mtime_ns: int
    ctime_ns: int

    @classmethod
    def from_stat(cls, value: os.stat_result) -> "StatSignature":
        return cls(
            value.st_dev,
            value.st_ino,
            value.st_mode,
            value.st_nlink,
            value.st_uid,
            value.st_gid,
            value.st_size,
            value.st_mtime_ns,
            value.st_ctime_ns,
        )


@dataclasses.dataclass(frozen=True)
class SourceFileRecord:
    label: str
    source: Path
    retained: Path
    signature: StatSignature
    retained_signature: StatSignature
    sha256: str


@dataclasses.dataclass(frozen=True)
class EvidenceManifestEntry:
    kind: str
    sha256: str
    relative: str
    size: int | None = None
    target: str | None = None


@dataclasses.dataclass(frozen=True)
class SourceSymlinkRecord:
    source: Path
    signature: StatSignature
    target: str
    retained: Path
    retained_signature: StatSignature


@dataclasses.dataclass(frozen=True)
class SourceDirectoryRecord:
    source: Path
    signature: StatSignature
    retained: Path
    retained_signature: StatSignature


@dataclasses.dataclass(frozen=True)
class AbsentPathRecord:
    path: Path
    parent_signature: StatSignature


def fail(message: str) -> None:
    raise AuditError(message)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def cfg(config: dict, *keys: str):
    value = config
    traversed: list[str] = []
    for key in keys:
        traversed.append(key)
        if not isinstance(value, dict) or key not in value:
            fail(f"missing config value: {'.'.join(traversed)}")
        value = value[key]
    return value


def string_cfg(config: dict, *keys: str) -> str:
    value = cfg(config, *keys)
    require(
        isinstance(value, str) and value != "",
        f"{'.'.join(keys)} must be nonempty text",
    )
    require(
        not PLACEHOLDER_RE.search(value),
        f"{'.'.join(keys)} contains an unresolved placeholder",
    )
    return value


def integer_cfg(config: dict, *keys: str) -> int:
    value = cfg(config, *keys)
    require(
        isinstance(value, int) and not isinstance(value, bool),
        f"{'.'.join(keys)} must be an integer",
    )
    return value


def require_digest(value: str, regex: re.Pattern[str], label: str) -> str:
    normalized = value.lower().replace(":", "")
    require(regex.fullmatch(normalized) is not None, f"{label} is not a valid digest")
    return normalized


def fsync_dir(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def write_new_fsynced(path: Path, content: bytes, mode: int = 0o600) -> None:
    descriptor = os.open(
        path,
        os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_CLOEXEC", 0),
        mode,
    )
    try:
        with os.fdopen(descriptor, "wb") as output:
            output.write(content)
            output.flush()
            os.fsync(output.fileno())
    except BaseException:
        path.unlink(missing_ok=True)
        raise
    fsync_dir(path.parent)


def write_new_stream_fsynced(
    path: Path, source: BinaryIO, mode: int = 0o600
) -> None:
    descriptor = os.open(
        path,
        os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_CLOEXEC", 0),
        mode,
    )
    try:
        with os.fdopen(descriptor, "wb") as output:
            while True:
                block = source.read(CHUNK)
                if not block:
                    break
                output.write(block)
            output.flush()
            os.fsync(output.fileno())
    except BaseException:
        path.unlink(missing_ok=True)
        raise
    fsync_dir(path.parent)


def replace_fsynced(path: Path, content: bytes, mode: int = 0o600) -> None:
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.unlink(missing_ok=True)
    write_new_fsynced(temporary, content, mode)
    os.replace(temporary, path)
    fsync_dir(path.parent)


def sha256_stream(stream: BinaryIO) -> str:
    digest = hashlib.sha256()
    while True:
        block = stream.read(CHUNK)
        if not block:
            return digest.hexdigest()
        digest.update(block)


def sha256_file(path: Path) -> str:
    with path.open("rb") as source:
        return sha256_stream(source)


def lstat_signature(path: Path, label: str) -> StatSignature:
    try:
        return StatSignature.from_stat(path.lstat())
    except OSError as exc:
        raise AuditError(f"cannot inspect {label} pathname {path}: {exc}") from exc


def open_source(path: Path, label: str, allow_empty: bool = False) -> int:
    require(path.is_absolute(), f"{label} path must be absolute: {path}")
    no_symlink_ancestors(path, label)
    flags = (
        os.O_RDONLY
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
        | getattr(os, "O_NONBLOCK", 0)
    )
    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        raise AuditError(f"cannot open {label} without following a symlink: {path}: {exc}") from exc
    metadata = os.fstat(descriptor)
    if not stat.S_ISREG(metadata.st_mode) or (metadata.st_size <= 0 and not allow_empty):
        os.close(descriptor)
        fail(f"{label} is not a nonempty regular file: {path}")
    return descriptor


def read_source_stably(path: Path, label: str) -> tuple[bytes, StatSignature, str]:
    descriptor = open_source(path, label)
    try:
        before = StatSignature.from_stat(os.fstat(descriptor))
        with os.fdopen(os.dup(descriptor), "rb") as source:
            raw = source.read()
        after = StatSignature.from_stat(os.fstat(descriptor))
        require(before == after, f"{label} changed while being read: {path}")
        require(len(raw) == before.size, f"{label} stable-read byte count mismatch")
    finally:
        os.close(descriptor)
    require(
        lstat_signature(path, label) == before,
        f"{label} pathname changed while being read: {path}",
    )
    digest = hashlib.sha256(raw).hexdigest()
    descriptor = open_source(path, label)
    try:
        current = StatSignature.from_stat(os.fstat(descriptor))
        with os.fdopen(os.dup(descriptor), "rb") as source:
            second_digest = sha256_stream(source)
        final = StatSignature.from_stat(os.fstat(descriptor))
    finally:
        os.close(descriptor)
    require(
        current == before
        and final == before
        and lstat_signature(path, label) == before
        and second_digest == digest,
        f"{label} changed after its stable read",
    )
    return raw, before, digest


def stable_regular_file_digest(
    path: Path,
    label: str,
    allow_empty: bool = True,
    read_hook: Callable[[Path], None] | None = None,
) -> tuple[StatSignature, str]:
    descriptor = open_source(path, label, allow_empty)
    try:
        before = StatSignature.from_stat(os.fstat(descriptor))
        if read_hook is not None:
            read_hook(path)
        digest = hashlib.sha256()
        read_size = 0
        with os.fdopen(os.dup(descriptor), "rb") as source:
            while True:
                block = source.read(CHUNK)
                if not block:
                    break
                digest.update(block)
                read_size += len(block)
        after = StatSignature.from_stat(os.fstat(descriptor))
    finally:
        os.close(descriptor)
    pathname_signature = lstat_signature(path, label)
    require(
        stat.S_ISREG(before.mode)
        and before == after
        and before == pathname_signature
        and read_size == before.size,
        f"{label} changed or was replaced while being hashed: {path}",
    )
    return before, digest.hexdigest()


def parse_json_bytes(raw: bytes, label: str) -> dict:
    require(b"\r" not in raw, f"{label} must use LF line endings")
    try:
        value = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AuditError(f"invalid UTF-8 JSON {label}: {exc}") from exc
    require(isinstance(value, dict), f"{label} root must be an object")
    return value


def copy_stable_file(
    source: Path,
    destination: Path,
    label: str,
    records: list[SourceFileRecord],
    retained_mode: int | None = None,
    allow_empty: bool = False,
) -> SourceFileRecord:
    descriptor = open_source(source, label, allow_empty)
    try:
        signature = StatSignature.from_stat(os.fstat(descriptor))
        mode = retained_mode
        if mode is None:
            mode = 0o500 if signature.mode & 0o111 else 0o400
        output_fd = os.open(
            destination,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_CLOEXEC", 0),
            mode,
        )
        digest = hashlib.sha256()
        copied = 0
        try:
            with os.fdopen(os.dup(descriptor), "rb") as source_file, os.fdopen(
                output_fd, "wb"
            ) as destination_file:
                while True:
                    block = source_file.read(CHUNK)
                    if not block:
                        break
                    destination_file.write(block)
                    digest.update(block)
                    copied += len(block)
                destination_file.flush()
                os.fsync(destination_file.fileno())
        except BaseException:
            destination.unlink(missing_ok=True)
            raise
        require(
            StatSignature.from_stat(os.fstat(descriptor)) == signature,
            f"{label} changed while its retained copy was created",
        )
        require(copied == signature.size, f"{label} retained byte count mismatch")
    finally:
        os.close(descriptor)
    os.chmod(destination, mode)
    fsync_dir(destination.parent)
    source_digest = digest.hexdigest()
    require(sha256_file(destination) == source_digest, f"retained {label} hash mismatch")

    check_fd = open_source(source, label, allow_empty)
    try:
        check_signature = StatSignature.from_stat(os.fstat(check_fd))
        with os.fdopen(os.dup(check_fd), "rb") as check_file:
            check_digest = sha256_stream(check_file)
    finally:
        os.close(check_fd)
    require(
        check_signature == signature and check_digest == source_digest,
        f"source {label} changed after retained copy",
    )
    retained_signature = StatSignature.from_stat(destination.lstat())
    require(
        stat.S_ISREG(retained_signature.mode)
        and retained_signature.size == signature.size,
        f"retained {label} type or size is invalid",
    )
    record = SourceFileRecord(
        label,
        source,
        destination,
        signature,
        retained_signature,
        source_digest,
    )
    records.append(record)
    return record


def revalidate_source_file(
    record: SourceFileRecord,
    read_hook: Callable[[Path], None] | None = None,
) -> None:
    signature, digest = stable_regular_file_digest(
        record.source,
        record.label,
        record.signature.size == 0,
        read_hook,
    )
    require(
        signature == record.signature and digest == record.sha256,
        f"source changed after audit snapshot: {record.label}: {record.source}",
    )
    retained_signature, retained_digest = stable_regular_file_digest(
        record.retained,
        f"retained {record.label}",
        record.retained_signature.size == 0,
        read_hook,
    )
    require(
        retained_signature == record.retained_signature
        and retained_digest == record.sha256,
        f"retained input changed during audit: {record.label}: {record.retained}",
    )


def attest_absent_path(path: Path, label: str) -> AbsentPathRecord:
    require(path.is_absolute(), f"{label} path must be absolute")
    existing_real_dir(path.parent, f"{label} parent")
    require(not os.path.lexists(path), f"{label} must be absent: {path}")
    record = AbsentPathRecord(path, StatSignature.from_stat(path.parent.lstat()))
    require(not os.path.lexists(path), f"{label} appeared during absence attestation")
    return record


def revalidate_absent_path(record: AbsentPathRecord, label: str) -> None:
    require(not os.path.lexists(record.path), f"{label} appeared during audit: {record.path}")
    require(
        StatSignature.from_stat(record.path.parent.lstat()) == record.parent_signature,
        f"{label} parent directory changed during audit: {record.path.parent}",
    )


def no_symlink_ancestors(path: Path, label: str, leaf_may_be_missing: bool = False) -> None:
    require(path.is_absolute(), f"{label} must be absolute: {path}")
    current = Path(path.anchor)
    parts = path.parts[1:]
    for index, part in enumerate(parts):
        current = current / part
        if leaf_may_be_missing and index == len(parts) - 1 and not current.exists():
            break
        try:
            metadata = current.lstat()
        except OSError as exc:
            raise AuditError(f"cannot inspect {label} ancestor {current}: {exc}") from exc
        require(not stat.S_ISLNK(metadata.st_mode), f"{label} has symlink ancestor: {current}")


def existing_real_dir(path: Path, label: str) -> Path:
    no_symlink_ancestors(path, label)
    try:
        metadata = path.lstat()
    except OSError as exc:
        raise AuditError(f"cannot inspect {label}: {path}: {exc}") from exc
    require(stat.S_ISDIR(metadata.st_mode), f"{label} is not a real directory: {path}")
    require(path.resolve(strict=True) == path, f"{label} is not canonical: {path}")
    return path


def validate_build_log_source(
    config: dict, after_epoch: int
) -> tuple[Path, StatSignature, Path, StatSignature, str]:
    require(after_epoch > 0, "after_epoch must be positive")
    source = Path(string_cfg(config, "build_log"))
    require(
        re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*\.log", source.name)
        is not None,
        "build_log must name a final .log file, never a staging path",
    )
    descriptor = open_source(source, "build log")
    try:
        signature = StatSignature.from_stat(os.fstat(descriptor))
    finally:
        os.close(descriptor)
    try:
        canonical = source.resolve(strict=True)
    except OSError as exc:
        raise AuditError(f"cannot resolve build log: {source}: {exc}") from exc
    require(canonical == source, f"build log path is not canonical: {source}")
    require_build_log_mtime_after(signature, after_epoch, "cutoff")
    start_record = Path(f"{source}.start-epoch")
    start_raw, start_signature, start_sha256 = read_source_stably(
        start_record, "formal build start record"
    )
    require(
        start_raw == f"{after_epoch}\n".encode("ascii"),
        "formal build start record does not exactly match after_epoch",
    )
    require(
        start_record.resolve(strict=True) == start_record,
        f"formal build start-record path is not canonical: {start_record}",
    )
    return source, signature, start_record, start_signature, start_sha256


def require_build_log_mtime_after(
    signature: StatSignature, epoch: int, label: str
) -> None:
    require(epoch > 0, f"{label} epoch must be positive")
    require(
        signature.mtime_ns > epoch * 1_000_000_000,
        f"build log mtime is not after {label}",
    )


def formal_build_log_header(
    build_log_record: SourceFileRecord,
    start_record: SourceFileRecord,
    after_epoch: int,
    harness_sha256: str,
    helper_sha256: str,
    gsi_commit: str,
    gsi_tree: str,
) -> bytes:
    values = (
        FORMAL_BUILD_LOG_FORMAT_VERSION,
        require_digest(harness_sha256, SHA256_RE, "formal build harness"),
        require_digest(helper_sha256, SHA256_RE, "formal build log helper"),
        require_digest(gsi_commit, REVISION_RE, "formal build GSI commit"),
        require_digest(gsi_tree, REVISION_RE, "formal build GSI tree"),
        str(after_epoch),
        str(start_record.signature.device),
        str(start_record.signature.inode),
        str(build_log_record.source),
        str(build_log_record.signature.device),
        str(build_log_record.signature.inode),
        "test-key-audit",
        "1",
    )
    return b"".join(
        f"{key}={value}\n".encode("utf-8")
        for key, value in zip(FORMAL_BUILD_LOG_HEADER_KEYS, values, strict=True)
    )


def validate_retained_build_log(
    build_log_record: SourceFileRecord,
    start_record: SourceFileRecord,
    expected_sha256: str,
    after_epoch: int,
    harness_sha256: str,
    helper_sha256: str,
    gsi_commit: str,
    gsi_tree: str,
) -> dict[str, str | int]:
    expected = require_digest(expected_sha256, SHA256_RE, "build log")
    require(after_epoch > 0, "formal build start epoch must be positive")
    require(
        start_record.source == Path(f"{build_log_record.source}.start-epoch"),
        "formal build start-record source path is not derived from build_log",
    )
    require(
        build_log_record.signature.device >= 0
        and build_log_record.signature.inode > 0
        and start_record.signature.device >= 0
        and start_record.signature.inode > 0,
        "formal build log/start-record source identities are invalid",
    )
    require(
        re.fullmatch(
            r"[A-Za-z0-9][A-Za-z0-9._-]*\.log", build_log_record.source.name
        )
        is not None,
        "formal build log source is not a final .log path",
    )
    start_raw, retained_start_signature, retained_start_sha = read_source_stably(
        start_record.retained, "retained formal build start record"
    )
    require(
        retained_start_signature == start_record.retained_signature
        and retained_start_sha == start_record.sha256
        and start_raw == f"{after_epoch}\n".encode("ascii"),
        "retained formal build start record differs from its source contract",
    )

    expected_header = formal_build_log_header(
        build_log_record,
        start_record,
        after_epoch,
        harness_sha256,
        helper_sha256,
        gsi_commit,
        gsi_tree,
    )
    expected_footer = b"".join(FORMAL_BUILD_LOG_FOOTER_LINES)
    descriptor = open_source(build_log_record.retained, "retained formal build log")
    digest = hashlib.sha256()
    try:
        before = StatSignature.from_stat(os.fstat(descriptor))
        require(
            before == build_log_record.retained_signature,
            "retained formal build log identity changed before parsing",
        )
        require(
            before.size >= len(expected_header) + len(expected_footer),
            "formal build log is shorter than contract v1",
        )
        with os.fdopen(os.dup(descriptor), "rb") as source:
            header = source.read(len(expected_header))
            digest.update(header)
            require(
                header == expected_header,
                "formal build log header does not exactly match contract v1",
            )
            body_remaining = before.size - len(expected_header) - len(expected_footer)
            success_count = 0
            signing_count = 0
            recognized_signing_count = 0
            last_output_line = b""
            while body_remaining > 0:
                line_limit = min(1024 * 1024, body_remaining)
                line = source.readline(line_limit + 1)
                require(line, "formal build log ended inside the output body")
                require(
                    len(line) <= line_limit,
                    "formal build output contains an overlong contract line",
                )
                require(
                    line.endswith(b"\n"),
                    "formal build output contains an unterminated line",
                )
                require(
                    not any(
                        line.startswith(prefix)
                        for prefix in FORMAL_BUILD_LOG_RESERVED_PREFIXES
                    ),
                    "formal build output repeats a reserved contract key",
                )
                digest.update(line)
                body_remaining -= len(line)
                if line == BUILD_LOG_SUCCESS_LINE:
                    success_count += 1
                if line == BUILD_LOG_SIGNING_LINE:
                    signing_count += 1
                if line in BUILD_LOG_RECOGNIZED_SIGNING_LINES:
                    recognized_signing_count += 1
                last_output_line = line
            require(success_count == 1, "formal build output must have one success line")
            require(
                signing_count == 1
                and recognized_signing_count == 1
                and last_output_line == BUILD_LOG_SIGNING_LINE,
                "formal build output must end in its sole test-key-audit signer line",
            )
            footer = source.read(len(expected_footer))
            digest.update(footer)
            require(
                footer == expected_footer,
                "formal build log footer does not exactly match contract v1",
            )
            require(not source.read(1), "formal build log has trailing data after completion")
        after = StatSignature.from_stat(os.fstat(descriptor))
    finally:
        os.close(descriptor)
    actual = digest.hexdigest()
    require(
        before == after
        and lstat_signature(
            build_log_record.retained, "retained formal build log"
        )
        == before,
        "retained formal build log changed while parsing contract v1",
    )
    require(
        actual == expected and actual == build_log_record.sha256,
        "formal build log does not match its independent SHA256 pin",
    )
    return {
        "format_version": int(FORMAL_BUILD_LOG_FORMAT_VERSION),
        "gsi_commit": gsi_commit,
        "gsi_tree": gsi_tree,
        "harness_sha256": harness_sha256,
        "helper_sha256": helper_sha256,
        "log_source_st_dev": build_log_record.signature.device,
        "log_source_st_ino": build_log_record.signature.inode,
        "sha256": actual,
        "signer_mode": "test-key-audit",
        "start_epoch": after_epoch,
        "start_record_sha256": start_record.sha256,
        "start_record_st_dev": start_record.signature.device,
        "start_record_st_ino": start_record.signature.inode,
    }


def record_file_result(
    result: dict, key: str, record: SourceFileRecord
) -> None:
    result[f"{key}_source"] = str(record.source)
    result[f"{key}_sha256"] = record.sha256
    result[f"{key}_size"] = record.signature.size


def paths_overlap(left: Path, right: Path) -> bool:
    return left == right or left.is_relative_to(right) or right.is_relative_to(left)


def validate_evidence_location(config: dict, config_path: Path) -> tuple[Path, Path, Path]:
    logs_root = Path(string_cfg(config, "logs_root"))
    evidence_dir = Path(string_cfg(config, "evidence_dir"))
    logs_root = existing_real_dir(logs_root, "logs root")
    require(evidence_dir.is_absolute(), "evidence_dir must be absolute")
    require(not evidence_dir.exists() and not evidence_dir.is_symlink(), "evidence_dir must not exist")
    existing_real_dir(evidence_dir.parent, "evidence parent")
    require(
        evidence_dir.parent / evidence_dir.name == evidence_dir,
        "evidence_dir must be canonical and contain no dot components",
    )
    require(evidence_dir != logs_root and evidence_dir.is_relative_to(logs_root), "evidence_dir must be a strict descendant of logs_root")
    root_checksum = evidence_dir.with_name(evidence_dir.name + ".root.sha256")
    require(not root_checksum.exists() and not root_checksum.is_symlink(), "external root checksum path already exists")

    paths_config = cfg(config, "paths")
    require(isinstance(paths_config, dict), "paths must be an object")
    input_roots = {
        Path(string_cfg(config, "image_dir")),
        Path(string_cfg(config, "metadata_dir")),
        Path(string_cfg(config, "target_files")).parent,
        Path(string_cfg(config, "build_log")).parent,
        config_path.parent,
        Path(__file__).resolve().parent,
    }
    for key, value in paths_config.items():
        require(isinstance(key, str) and isinstance(value, str), "all paths entries must be text")
        require(not PLACEHOLDER_RE.search(value), f"paths.{key} contains an unresolved placeholder")
        candidate = Path(value)
        require(candidate.is_absolute(), f"paths.{key} must be absolute")
        input_roots.add(candidate if candidate.is_dir() else candidate.parent)
    for root in input_roots:
        canonical = root.resolve(strict=True)
        require(
            not paths_overlap(evidence_dir, canonical),
            f"evidence directory overlaps input root: {canonical}",
        )
        require(
            not paths_overlap(root_checksum, canonical),
            f"root checksum overlaps input root: {canonical}",
        )
    return logs_root, evidence_dir, root_checksum


def safe_tree_relative(path: str) -> None:
    require("\t" not in path and "\n" not in path and "\r" not in path, "unsafe tree path")


def copy_stable_tree(
    source_root: Path,
    destination_root: Path,
    file_records: list[SourceFileRecord],
    tree_label: str,
) -> tuple[str, list[SourceSymlinkRecord], list[SourceDirectoryRecord], bytes]:
    source_root = existing_real_dir(source_root, tree_label)
    destination_root.mkdir(mode=0o700)
    fsync_dir(destination_root.parent)
    symlink_records: list[SourceSymlinkRecord] = []
    directory_records: list[SourceDirectoryRecord] = []
    manifest_lines: list[str] = []

    def visit(source_dir: Path, destination_dir: Path, relative: Path) -> None:
        directory_signature = StatSignature.from_stat(source_dir.lstat())
        rel_text = relative.as_posix() if relative.parts else "."
        safe_tree_relative(rel_text)
        manifest_lines.append(f"D\t0500\t{rel_text}")
        with os.scandir(source_dir) as iterator:
            entries = sorted(iterator, key=lambda item: item.name)
        for entry in entries:
            safe_tree_relative(entry.name)
            source_path = source_dir / entry.name
            destination_path = destination_dir / entry.name
            child_relative = relative / entry.name
            child_text = child_relative.as_posix()
            metadata = source_path.lstat()
            if stat.S_ISDIR(metadata.st_mode):
                destination_path.mkdir(mode=0o700)
                visit(source_path, destination_path, child_relative)
            elif stat.S_ISREG(metadata.st_mode):
                mode = 0o500 if metadata.st_mode & 0o111 else 0o400
                record = copy_stable_file(
                    source_path,
                    destination_path,
                    f"{tree_label} {child_text}",
                    file_records,
                    mode,
                    True,
                )
                manifest_lines.append(
                    f"F\t{mode:04o}\t{record.signature.size}\t{record.sha256}\t{child_text}"
                )
            elif stat.S_ISLNK(metadata.st_mode):
                target = os.readlink(source_path)
                safe_tree_relative(target)
                require(
                    not os.path.isabs(target),
                    f"{tree_label} has absolute symlink: {child_text}",
                )
                resolved = (source_path.parent / target).resolve(strict=True)
                require(
                    resolved == source_root or resolved.is_relative_to(source_root),
                    f"{tree_label} symlink escapes source root: {child_text} -> {target}",
                )
                os.symlink(target, destination_path)
                symlink_records.append(
                    SourceSymlinkRecord(
                        source_path,
                        StatSignature.from_stat(metadata),
                        target,
                        destination_path,
                        StatSignature.from_stat(destination_path.lstat()),
                    )
                )
                manifest_lines.append(f"L\t{target}\t{child_text}")
            else:
                fail(f"{tree_label} contains unsupported file type: {source_path}")
        require(
            StatSignature.from_stat(source_dir.lstat()) == directory_signature,
            f"{tree_label} source directory changed during copy: {source_dir}",
        )
        fsync_dir(destination_dir)
        os.chmod(destination_dir, 0o500)
        fsync_dir(destination_dir.parent)
        directory_records.append(
            SourceDirectoryRecord(
                source_dir,
                directory_signature,
                destination_dir,
                StatSignature.from_stat(destination_dir.lstat()),
            )
        )

    visit(source_root, destination_root, Path())
    manifest = ("\n".join(manifest_lines) + "\n").encode("utf-8")
    return hashlib.sha256(manifest).hexdigest(), symlink_records, directory_records, manifest


def revalidate_tree_metadata(
    symlinks: list[SourceSymlinkRecord],
    directories: list[SourceDirectoryRecord],
) -> None:
    for record in symlinks:
        require(
            StatSignature.from_stat(record.source.lstat()) == record.signature
            and os.readlink(record.source) == record.target,
            f"source tree symlink changed: {record.source}",
        )
        require(
            StatSignature.from_stat(record.retained.lstat())
            == record.retained_signature
            and stat.S_ISLNK(record.retained_signature.mode)
            and os.readlink(record.retained) == record.target,
            f"retained tree symlink changed: {record.retained}",
        )
    for record in directories:
        require(
            StatSignature.from_stat(record.source.lstat()) == record.signature,
            f"source tree directory changed: {record.source}",
        )
        require(
            StatSignature.from_stat(record.retained.lstat())
            == record.retained_signature
            and stat.S_ISDIR(record.retained_signature.mode),
            f"retained tree directory changed: {record.retained}",
        )


def retained_tree_manifest(root: Path) -> bytes:
    lines: list[str] = []

    def visit(directory: Path, relative: Path) -> None:
        metadata = directory.lstat()
        require(stat.S_ISDIR(metadata.st_mode), f"retained tree path is not a directory: {directory}")
        rel_text = relative.as_posix() if relative.parts else "."
        lines.append(f"D\t{stat.S_IMODE(metadata.st_mode):04o}\t{rel_text}")
        with os.scandir(directory) as iterator:
            entries = sorted(iterator, key=lambda item: item.name)
        for entry in entries:
            path = directory / entry.name
            child_relative = relative / entry.name
            child_text = child_relative.as_posix()
            child = path.lstat()
            if stat.S_ISDIR(child.st_mode):
                visit(path, child_relative)
            elif stat.S_ISREG(child.st_mode):
                descriptor = open_source(path, f"retained tree {child_text}", child.st_size == 0)
                try:
                    opened = os.fstat(descriptor)
                    with os.fdopen(os.dup(descriptor), "rb") as source:
                        digest = sha256_stream(source)
                finally:
                    os.close(descriptor)
                require(StatSignature.from_stat(opened) == StatSignature.from_stat(child), f"retained tree file raced: {path}")
                lines.append(
                    f"F\t{stat.S_IMODE(child.st_mode):04o}\t{child.st_size}\t{digest}\t{child_text}"
                )
            elif stat.S_ISLNK(child.st_mode):
                target = os.readlink(path)
                safe_tree_relative(target)
                resolved = (path.parent / target).resolve(strict=True)
                require(
                    resolved == root or resolved.is_relative_to(root),
                    f"retained tree symlink escapes root: {child_text}",
                )
                lines.append(f"L\t{target}\t{child_text}")
            else:
                fail(f"retained tree has unsupported file type: {path}")

    visit(root, Path())
    return ("\n".join(lines) + "\n").encode("utf-8")


def read_lf_text(path: Path, label: str, ascii_only: bool = False) -> str:
    raw = path.read_bytes()
    require(b"\r" not in raw, f"{label} must use LF line endings")
    require(raw.endswith(b"\n"), f"{label} must end with LF")
    try:
        return raw.decode("ascii" if ascii_only else "utf-8")
    except UnicodeDecodeError as exc:
        raise AuditError(f"{label} has invalid encoding: {exc}") from exc


def safe_zip_name(name: str) -> None:
    path = PurePosixPath(name)
    require(name != "" and "\\" not in name, f"unsafe ZIP entry name: {name!r}")
    require(not path.is_absolute(), f"absolute ZIP entry name: {name!r}")
    require(".." not in path.parts, f"parent traversal in ZIP entry: {name!r}")


def validate_zip(archive: zipfile.ZipFile, label: str) -> dict[str, zipfile.ZipInfo]:
    entries = archive.infolist()
    require(entries, f"{label} has no entries")
    by_name: dict[str, zipfile.ZipInfo] = {}
    for entry in entries:
        safe_zip_name(entry.filename)
        require(entry.filename not in by_name, f"{label} has duplicate entry {entry.filename!r}")
        by_name[entry.filename] = entry
    bad = archive.testzip()
    require(bad is None, f"{label} failed CRC/decompression validation at {bad!r}")
    return by_name


def require_regular_zip_entry(entry: zipfile.ZipInfo, label: str) -> None:
    mode = entry.external_attr >> 16
    require(entry.file_size > 0, f"{label} is empty")
    require(not entry.is_dir(), f"{label} is a directory")
    require(not stat.S_ISLNK(mode), f"{label} is a symlink")
    require(stat.S_ISREG(mode), f"{label} lacks regular-file ZIP metadata: mode={mode:o}")


def streams_equal(left: BinaryIO, right: BinaryIO) -> tuple[bool, str, int]:
    digest = hashlib.sha256()
    count = 0
    while True:
        left_block = left.read(CHUNK)
        right_block = right.read(CHUNK)
        if left_block != right_block:
            return False, digest.hexdigest(), count
        if not left_block:
            return True, digest.hexdigest(), count
        digest.update(left_block)
        count += len(left_block)


def command_environment(evidence_dir: Path, java_home: Path, tool_bin: Path) -> dict[str, str]:
    return {
        "HOME": str(evidence_dir / "home"),
        "JAVA_HOME": str(java_home),
        "LANG": "C",
        "LC_ALL": "C",
        "OPENSSL_CONF": str(evidence_dir / "tools" / "openssl.cnf"),
        "OPENSSL_MODULES": str(evidence_dir / "tools" / "openssl-modules"),
        "PATH": f"{tool_bin}:{java_home / 'bin'}",
        "TMPDIR": str(evidence_dir / "tmp"),
        "TZ": "UTC",
    }


def java_system_properties(evidence_dir: Path) -> list[str]:
    return [
        f"-Duser.home={evidence_dir / 'home'}",
        f"-Djava.io.tmpdir={evidence_dir / 'tmp'}",
    ]


def verify_native_dependency_resolution(
    evidence_dir: Path,
    phase: str,
    retained_loader: Path,
    executables: dict[str, Path],
    signer_java_home_retained: Path,
    source_paths: dict[str, Path],
    environment: dict[str, str],
) -> dict[str, list[str]]:
    require(phase in {"initial", "final"}, f"invalid native probe phase: {phase}")
    runtime_sources = {
        path.resolve(strict=True)
        for key, path in source_paths.items()
        if key.startswith("runtime_")
    }
    retained_runtime_paths = {
        (evidence_dir / "tools" / "otatools" / "lib64" / "libc++.so").resolve(
            strict=True
        )
    }
    retained_loader_path = retained_loader.resolve(strict=True)
    retained_java_root = signer_java_home_retained.resolve(strict=True)
    resolution: dict[str, list[str]] = {}
    for label, executable in sorted(executables.items()):
        require(
            re.fullmatch(r"[a-z0-9-]+", label) is not None,
            f"unsafe native dependency label: {label}",
        )
        completed = run_command(
            evidence_dir,
            f"native-deps-{phase}-{label}",
            [str(retained_loader), "--list", str(executable)],
            environment,
        )
        output = completed.stdout.decode("utf-8", errors="strict")
        require("not found" not in output, f"{label} has an unresolved native dependency")
        resolved: set[Path] = set()
        for line in output.splitlines():
            candidate = ""
            if "=>" in line:
                candidate = line.split("=>", 1)[1].rsplit(" (", 1)[0].strip()
            else:
                prefix = line.rsplit(" (", 1)[0].strip()
                if prefix.startswith("/"):
                    candidate = prefix
            if not candidate.startswith("/"):
                continue
            try:
                path = Path(candidate).resolve(strict=True)
            except OSError as exc:
                raise AuditError(
                    f"cannot canonicalize {label} dependency {candidate}: {exc}"
                ) from exc
            require(
                path == retained_loader_path
                or path in runtime_sources
                or path in retained_runtime_paths
                or path.is_relative_to(retained_java_root),
                f"{label} resolves an unpinned native dependency: {path}",
            )
            resolved.add(path)
        require(resolved, f"{label} native dependency probe returned no paths")
        resolution[label] = sorted(map(str, resolved))
    return resolution


def verify_runtime_configuration(
    evidence_dir: Path,
    retained_python: Path,
    retained_signer_verifier: Path,
    python_stdlib_source: Path,
    signer_java_home_retained: Path,
    retained_openssl: Path,
    source_paths: dict[str, Path],
    environment: dict[str, str],
    result: dict,
) -> None:
    probe_source = """
import bz2
import gzip
import hashlib
import json
import lzma
import runpy
import ssl
import subprocess
import sys
import tarfile
import xml.etree.ElementTree
import zipfile
import zlib

runpy.run_path(sys.argv[1], run_name='mp01_signer_runtime_probe')
mapped = set()
with open('/proc/self/maps', encoding='ascii') as maps:
    for line in maps:
        fields = line.split()
        if len(fields) >= 6 and fields[-1].startswith('/'):
            mapped.add(fields[-1])
print(json.dumps({
    'executable': sys.executable,
    'prefix': sys.prefix,
    'path': sys.path,
    'mapped_files': sorted(mapped),
}, sort_keys=True))
""".strip()
    python_probe = run_command(
        evidence_dir,
        "python-runtime-probe",
        [
            str(retained_python),
            "-I",
            "-S",
            "-c",
            probe_source,
            str(retained_signer_verifier),
        ],
        environment,
    )
    try:
        python_runtime = json.loads(python_probe.stdout)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AuditError(f"Python runtime probe returned invalid JSON: {exc}") from exc
    require(
        isinstance(python_runtime, dict)
        and python_runtime.get("executable") == str(retained_python),
        "Python runtime probe did not execute the retained interpreter",
    )
    expected_python_path = [
        str(python_stdlib_source.parent / (python_stdlib_source.name.replace(".", "") + ".zip")),
        str(python_stdlib_source),
        str(python_stdlib_source / "lib-dynload"),
    ]
    require(
        python_runtime.get("path") == expected_python_path,
        f"isolated Python loaded an unexpected sys.path: {python_runtime.get('path')!r}",
    )
    mapped_values = python_runtime.get("mapped_files")
    require(
        isinstance(mapped_values, list)
        and mapped_values
        and all(isinstance(value, str) for value in mapped_values),
        "Python runtime probe returned an invalid mapped-file list",
    )
    mapped_paths = {Path(value) for value in mapped_values}
    runtime_sources = {
        path for key, path in source_paths.items() if key.startswith("runtime_")
    }
    unexpected_mappings = sorted(
        str(path)
        for path in mapped_paths
        if path != retained_python
        and not path.is_relative_to(python_stdlib_source)
        and path not in runtime_sources
    )
    require(
        not unexpected_mappings,
        f"Python loaded files outside the attested runtime closure: {unexpected_mappings}",
    )
    required_mappings = {
        source_paths[key]
        for key in (
            "runtime_loader",
            "runtime_libpython",
            "runtime_libc",
            "runtime_libm",
            "runtime_libssl",
            "runtime_libcrypto",
            "runtime_libz",
            "runtime_libbz2",
            "runtime_liblzma",
            "runtime_libzstd",
            "runtime_libexpat",
        )
    }
    require(
        required_mappings <= mapped_paths,
        f"Python runtime mappings omit configured dependencies: {sorted(map(str, required_mappings - mapped_paths))}",
    )
    result["python_runtime_prefix"] = python_runtime.get("prefix")
    result["python_runtime_sys_path"] = expected_python_path
    result["python_runtime_mapped_files"] = sorted(map(str, mapped_paths))

    signer_java = signer_java_home_retained / "bin" / "java"
    java_probe = run_command(
        evidence_dir,
        "signer-java-runtime-probe",
        [
            str(signer_java),
            *java_system_properties(evidence_dir),
            "-XshowSettings:properties",
            "-version",
        ],
        environment,
    )
    java_settings = (java_probe.stdout + java_probe.stderr).decode(
        "utf-8", errors="strict"
    )
    for key, expected_value in (
        ("java.home", signer_java_home_retained),
        ("user.home", evidence_dir / "home"),
        ("java.io.tmpdir", evidence_dir / "tmp"),
    ):
        matches = re.findall(
            rf"^\s*{re.escape(key)} = (.+?)\s*$", java_settings, re.MULTILINE
        )
        require(
            matches == [str(expected_value)],
            f"signer Java runtime property mismatch for {key}: {matches}",
        )
    result["signer_java_runtime_home"] = str(signer_java_home_retained)
    result["signer_java_runtime_user_home"] = str(evidence_dir / "home")
    result["signer_java_runtime_tmpdir"] = str(evidence_dir / "tmp")

    openssl_probe = run_command(
        evidence_dir,
        "openssl-runtime-probe",
        [str(retained_openssl), "list", "-providers", "-verbose"],
        environment,
    )
    openssl_output = (openssl_probe.stdout + openssl_probe.stderr).decode(
        "utf-8", errors="strict"
    )
    require(
        re.search(r"^\s*name: OpenSSL Default Provider\s*$", openssl_output, re.MULTILINE)
        is not None,
        "OpenSSL did not activate the configured built-in default provider",
    )
    require(
        not any((evidence_dir / "tools" / "openssl-modules").iterdir()),
        "OpenSSL module directory is not empty",
    )
    result["openssl_config"] = environment["OPENSSL_CONF"]
    result["openssl_modules"] = environment["OPENSSL_MODULES"]


def run_command(
    evidence_dir: Path,
    label: str,
    command: list[str],
    environment: dict[str, str],
    expected_rc: int = 0,
    timeout: int = 7200,
) -> subprocess.CompletedProcess[bytes]:
    invocation = {
        "argv": command,
        "cwd": str(evidence_dir),
        "environment": environment,
        "expected_rc": expected_rc,
        "timeout_seconds": timeout,
    }
    write_new_fsynced(
        evidence_dir / f"{label}.invocation.json",
        (json.dumps(invocation, indent=2, sort_keys=True) + "\n").encode("utf-8"),
    )
    try:
        completed = subprocess.run(
            command,
            cwd=evidence_dir,
            env=environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            timeout=timeout,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise AuditError(f"could not execute {label}: {exc}") from exc
    write_new_fsynced(evidence_dir / f"{label}.stdout", completed.stdout)
    write_new_fsynced(evidence_dir / f"{label}.stderr", completed.stderr)
    require(
        completed.returncode == expected_rc,
        f"{label} returned {completed.returncode}, expected {expected_rc}",
    )
    return completed


def parse_build_info_fields(text: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    duplicates: list[str] = []
    for line in text.splitlines():
        if line.startswith((" ", "\t")) or ": " not in line:
            continue
        key, value = line.split(": ", 1)
        if key in fields:
            duplicates.append(key)
        fields[key] = value
    require(not duplicates, f"build-info has duplicate fields: {sorted(set(duplicates))}")
    return fields


def verify_build_info_expectations(
    build_fields: dict[str, str], build_expectations: dict
) -> None:
    require(isinstance(build_expectations, dict), "expected.build_info must be object")
    missing = sorted(set(MANDATORY_BUILD_INFO_KEYS) - set(build_expectations))
    require(not missing, f"build-info expectations omit mandatory keys: {missing}")
    for key, value in build_expectations.items():
        require(
            isinstance(key, str) and isinstance(value, str) and value,
            "build-info expectations must be text",
        )
        require(
            not PLACEHOLDER_RE.search(value),
            f"build-info expectation unresolved: {key}",
        )
        require(
            build_fields.get(key) == value,
            f"build-info mismatch for {key}: {build_fields.get(key)!r}",
        )


def verify_derived_build_info_fields(
    build_fields: dict[str, str], derived_fields: dict[str, str]
) -> None:
    for key, value in derived_fields.items():
        require(
            build_fields.get(key) == value,
            f"derived build-info mismatch for {key}",
        )


def verify_no_kernel_policy_build_info(
    build_fields: dict[str, str],
    source_paths: dict[str, Path],
    retained: dict[str, Path],
) -> None:
    require(
        build_fields["No-kernel header policy verifier"]
        == str(source_paths["no_kernel_header_policy_verifier"]),
        "build-info path mismatch: No-kernel header policy verifier",
    )
    require(
        build_fields["No-kernel header policy verifier SHA256"]
        == sha256_file(retained["no_kernel_header_policy_verifier"]),
        "build-info hash mismatch: No-kernel header policy verifier SHA256",
    )
    require(
        build_fields["vendor/lineage no-kernel header patch SHA256"]
        == sha256_file(retained["vendor_lineage_no_kernel_patch"]),
        "vendor/lineage no-kernel header patch hash differs from retained input",
    )


def verify_partner_apk_policy_build_info(
    build_fields: dict[str, str],
    source_paths: dict[str, Path],
    retained: dict[str, Path],
) -> None:
    require(
        build_fields["Presigned partner APK policy verifier"]
        == str(source_paths["presigned_partner_apk_policy_verifier"]),
        "build-info path mismatch: Presigned partner APK policy verifier",
    )
    require(
        build_fields["Presigned partner APK policy verifier SHA256"]
        == sha256_file(retained["presigned_partner_apk_policy_verifier"]),
        "build-info hash mismatch: Presigned partner APK policy verifier SHA256",
    )
    require(
        build_fields["vendor/partner_gms presigned APK patch SHA256"]
        == sha256_file(retained["partner_gms_presigned_apk_patch"]),
        "vendor/partner_gms presigned APK patch hash differs from retained input",
    )


def verify_partner_apk_artifacts(
    evidence_dir: Path,
    target_apks: dict[str, Path],
    expected_hashes: dict,
    zipalign: Path,
    environment: dict[str, str],
) -> dict[str, str]:
    modules = {module for module, _ in PARTNER_APK_TARGETS}
    require(
        isinstance(expected_hashes, dict) and set(expected_hashes) == modules,
        "expected.partner_apk_sha256 must exactly pin all five partner APKs",
    )
    require(
        set(target_apks) == modules,
        "extracted target-files partner APK set is incomplete or unexpected",
    )
    zipalign_signature, _ = stable_regular_file_digest(
        zipalign, "retained partner APK zipalign", False
    )
    require(
        zipalign.resolve(strict=True) == zipalign
        and (stat.S_IMODE(zipalign_signature.mode) & 0o111) != 0
        and os.access(zipalign, os.X_OK),
        "retained partner APK zipalign is not a canonical executable",
    )

    verified: dict[str, str] = {}
    for module, _ in PARTNER_APK_TARGETS:
        expected_sha256 = require_digest(
            string_cfg(expected_hashes, module),
            SHA256_RE,
            f"{module} partner APK",
        )
        target_apk = target_apks[module]
        _, actual_sha256 = stable_regular_file_digest(
            target_apk, f"target-files {module} APK", False
        )
        require(
            actual_sha256 == expected_sha256,
            f"target-files {module} APK SHA256 mismatch",
        )
        run_command(
            evidence_dir,
            f"partner-apk-{module.casefold()}-alignment",
            [str(zipalign), "-c", "-p", "4", str(target_apk)],
            environment,
        )
        _, final_sha256 = stable_regular_file_digest(
            target_apk, f"target-files {module} APK after zipalign", False
        )
        require(
            final_sha256 == expected_sha256,
            f"target-files {module} APK changed during alignment verification",
        )
        verified[module] = actual_sha256
    return verified


def extract_indented_block(text: str, start: str, end: str) -> bytes:
    lines = text.splitlines()
    require(lines.count(start) == 1, f"build-info must contain exactly one {start!r}")
    require(lines.count(end) == 1, f"build-info must contain exactly one {end!r}")
    first = lines.index(start)
    last = lines.index(end)
    require(first < last, f"build-info block {start!r} is out of order")
    body = lines[first + 1 : last]
    require(body, f"build-info block {start!r} is empty")
    require(all(line.startswith("  ") for line in body), f"malformed indentation in {start!r}")
    return ("\n".join(line[2:] for line in body) + "\n").encode("utf-8")


def parse_signer_evidence(raw: bytes) -> tuple[dict[str, str], list[tuple[str, ...]]]:
    require(b"\r" not in raw and raw.endswith(b"\n"), "signer evidence must be LF-terminated")
    try:
        lines = raw.decode("ascii").splitlines()
    except UnicodeDecodeError as exc:
        raise AuditError(f"signer evidence is not ASCII: {exc}") from exc
    values: dict[str, str] = {}
    for line in lines:
        require("=" in line, f"malformed signer evidence line: {line!r}")
        key, value = line.split("=", 1)
        require(key not in values, f"duplicate signer evidence key: {key}")
        values[key] = value

    for key in EVIDENCE_BASE_KEYS:
        require(key in values, f"signer evidence lacks {key}")
    require(
        values["format"] == "mp01-signer-compatibility-evidence-v1",
        "signer evidence format is unsupported",
    )
    require(values["mode"] in {"test-key-audit", "release-candidate"}, "invalid signer mode")
    for hash_key in (
        "target_files_sha256",
        "expected_manifest_sha256",
        "expected_baseline_archive_sha256",
        "expected_baseline_image_sha256",
        "expected_baseline_apk_inventory_sha256",
        "expected_baseline_apex_inventory_sha256",
        "actual_manifest_sha256",
        "apksigner_java_sha256",
        "apksigner_jar_sha256",
    ):
        require(SHA256_RE.fullmatch(values[hash_key]) is not None, f"invalid signer hash: {hash_key}")
    require(
        values["apksigner_execution"] == "direct_java_jar",
        "signer evidence did not use direct Java/JAR execution",
    )
    require(values["expected_apk_coverage"] == "complete", "APK coverage is not complete")
    require(values["expected_apex_coverage"] == "complete", "APEX coverage is not complete")
    for count_key in (
        "actual_apk_count",
        "actual_apex_count",
        "incompatibility_count",
        "warning_count",
    ):
        require(values[count_key].isdigit(), f"signer evidence {count_key} is not decimal")
    incompatibilities = int(values["incompatibility_count"])
    warnings = int(values["warning_count"])
    total = incompatibilities + warnings
    expected_issue_keys = [f"issue.{index:04d}" for index in range(1, total + 1)]
    actual_issue_keys = [key for key in values if ISSUE_KEY_RE.fullmatch(key)]
    require(actual_issue_keys == expected_issue_keys, "signer issue indices are not contiguous/in order")
    require(
        set(values) == set(EVIDENCE_BASE_KEYS) | set(expected_issue_keys),
        "signer evidence contains missing or unknown schema keys",
    )
    issues: list[tuple[str, ...]] = []
    for key in expected_issue_keys:
        fields = tuple(values[key].split("\t"))
        require(len(fields) == 6, f"{key} must contain six TSV fields")
        severity, kind, package, code, expected_value, actual_value = fields
        require(severity in {"incompatibility", "warning"}, f"{key} has invalid severity")
        require(kind in {"apk", "apex"}, f"{key} has invalid kind")
        require(package != "" and code != "", f"{key} has blank package or code")
        require(expected_value != "" and actual_value != "", f"{key} has blank comparison values")
        issues.append(fields)
    require(issues == sorted(issues), "signer issue rows are not in generator sort order")
    require(
        sum(issue[0] == "incompatibility" for issue in issues) == incompatibilities,
        "signer incompatibility_count does not match issue severities",
    )
    require(
        sum(issue[0] == "warning" for issue in issues) == warnings,
        "signer warning_count does not match issue severities",
    )
    require(
        values["comparison_status"]
        == ("INCOMPATIBLE" if incompatibilities else "COMPATIBLE_SIGNER_IDENTITIES"),
        "signer comparison status disagrees with issue counts",
    )
    return values, issues


def signer_manifest_counts(raw: bytes) -> tuple[int, int]:
    require(b"\r" not in raw and raw.endswith(b"\n"), "actual signer manifest must be LF-terminated")
    try:
        lines = raw.decode("ascii").splitlines()
    except UnicodeDecodeError as exc:
        raise AuditError(f"actual signer manifest is not ASCII: {exc}") from exc
    data_lines = [line for line in lines if line and not line.startswith("#")]
    require(data_lines, "actual signer manifest has no TSV header")
    require(
        data_lines[0]
        == "kind\tpackage\tsource_path\tformat\tversion_code\tsigner_cert_sha256\tcontainer_cert_sha256\tpayload_pubkey_sha256",
        "actual signer manifest header is unexpected",
    )
    apk_count = 0
    apex_count = 0
    for line in data_lines[1:]:
        fields = line.split("\t")
        require(len(fields) == 8, "actual signer manifest row must have eight fields")
        require(fields[0] in {"apk", "apex"}, "actual signer manifest has invalid kind")
        apk_count += fields[0] == "apk"
        apex_count += fields[0] == "apex"
    require(apk_count + apex_count > 0, "actual signer manifest has no identities")
    return apk_count, apex_count


def normalized_uri(value: str) -> str:
    decoded = value
    for _ in range(32):
        next_value = urllib.parse.unquote(decoded)
        if next_value == decoded:
            return unicodedata.normalize("NFKC", decoded).strip()
        decoded = next_value
    fail("remote fetch URI did not reach a stable decoded form")


def reject_local_remote_fetch(
    fetch: str,
    label: str,
    allowed_schemes: set[str] | None = None,
    allowed_relative_fetches: set[str] | None = None,
) -> None:
    if allowed_schemes is None:
        allowed_schemes = {"https", "ssh"}
    if allowed_relative_fetches is None:
        allowed_relative_fetches = set()
    decoded = normalized_uri(fetch)
    require(decoded != "", f"{label} has an empty fetch")
    if decoded in allowed_relative_fetches:
        return
    compact = re.sub(r"[\x00-\x20\x7f]+", "", decoded).casefold()
    scheme = urllib.parse.urlsplit(decoded).scheme.casefold()
    require(scheme != "file" and not compact.startswith("file:"), f"{label} uses local file URI")
    require(scheme != "" and scheme in allowed_schemes, f"{label} uses disallowed or local fetch form: {decoded!r}")


def verify_manifest(manifest_path: Path, expected: dict, result: dict) -> None:
    raw = manifest_path.read_bytes()
    expected_sha256 = require_digest(
        string_cfg(expected, "resolved_manifest_sha256"),
        SHA256_RE,
        "resolved manifest",
    )
    actual_sha256 = hashlib.sha256(raw).hexdigest()
    require(
        actual_sha256 == expected_sha256,
        "resolved manifest SHA256 mismatch",
    )
    require(b"<!doctype" not in raw.lower(), "resolved manifest must not contain a DOCTYPE")
    try:
        root = ET.fromstring(raw)
    except ET.ParseError as exc:
        raise AuditError(f"resolved manifest is not valid XML: {exc}") from exc
    require(root.tag == "manifest", f"resolved manifest root is {root.tag!r}")
    allowed_schemes_value = cfg(expected, "allowed_remote_schemes")
    allowed_relative_value = cfg(expected, "allowed_relative_remote_fetches")
    require(
        isinstance(allowed_schemes_value, list)
        and allowed_schemes_value
        and all(isinstance(value, str) and value == value.casefold() for value in allowed_schemes_value),
        "allowed_remote_schemes must be a nonempty lowercase text list",
    )
    require(
        isinstance(allowed_relative_value, list)
        and all(isinstance(value, str) and value for value in allowed_relative_value),
        "allowed_relative_remote_fetches must be a text list",
    )
    allowed_schemes = set(allowed_schemes_value)
    allowed_relative_fetches = set(allowed_relative_value)
    for remote in root.findall(".//remote"):
        fetch = remote.get("fetch", "")
        reject_local_remote_fetch(
            fetch,
            f"remote {remote.get('name', '<unnamed>')}",
            allowed_schemes,
            allowed_relative_fetches,
        )

    projects = root.findall(".//project")
    project_count = integer_cfg(expected, "project_count")
    require(len(projects) == project_count, f"manifest has {len(projects)} projects, expected {project_count}")
    identities: dict[str, tuple[str, str]] = {}
    for project in projects:
        name = project.get("name", "")
        path = project.get("path") or name
        revision = project.get("revision", "")
        require(name != "", "resolved manifest project lacks a name")
        require(REVISION_RE.fullmatch(revision) is not None, f"project {path} lacks exact revision")
        require(path not in identities, f"resolved manifest has duplicate path: {path}")
        identities[path] = (name, revision)

    custom = cfg(expected, "custom_projects")
    require(isinstance(custom, list) and len(custom) == 13, "custom_projects must have 13 entries")
    configured_paths: set[str] = set()
    for index, item in enumerate(custom):
        require(isinstance(item, dict), f"custom_projects[{index}] must be an object")
        path = string_cfg(item, "path")
        name = string_cfg(item, "name")
        revision = require_digest(string_cfg(item, "revision"), REVISION_RE, f"custom {path}")
        require(path not in configured_paths, f"duplicate custom project path: {path}")
        configured_paths.add(path)
        require(identities.get(path) == (name, revision), f"custom project mismatch: {path}")

    excluded_paths = cfg(expected, "excluded_project_paths")
    excluded_names = cfg(expected, "excluded_project_names")
    require(isinstance(excluded_paths, list), "excluded_project_paths must be a list")
    require(isinstance(excluded_names, list), "excluded_project_names must be a list")
    names = {name for name, _ in identities.values()}
    for path in excluded_paths:
        require(isinstance(path, str) and path not in identities, f"excluded path is present: {path}")
    for name in excluded_names:
        require(isinstance(name, str) and name not in names, f"excluded name is present: {name}")
    require(
        all("lineageos_gsi" not in path.casefold() and "lineageos_gsi" not in name.casefold() for path, (name, _) in identities.items()),
        "resolved manifest contains a LineageOS_gsi project",
    )

    remote_count = integer_cfg(expected, "mp01_local_remote_count")
    local_remotes = [remote for remote in root.findall("./remote") if remote.get("name") == "mp01-local"]
    require(len(local_remotes) == remote_count, "mp01-local remote count mismatch")
    expected_fetch = string_cfg(expected, "mp01_local_fetch")
    require(all(remote.get("fetch") == expected_fetch for remote in local_remotes), "mp01-local fetch mismatch")
    result["resolved_manifest_expected_sha256"] = expected_sha256
    result["resolved_manifest_sha256"] = actual_sha256
    result["resolved_manifest_project_count"] = len(projects)
    result["resolved_manifest_custom_project_count"] = len(custom)


def verify_treble_markers(
    apk_path: Path,
    aapt2: Path,
    evidence_dir: Path,
    environment: dict[str, str],
) -> None:
    with zipfile.ZipFile(apk_path) as archive:
        entries = validate_zip(archive, "TrebleApp APK")
        selected = [
            entry
            for name, entry in entries.items()
            if name in {"AndroidManifest.xml", "resources.arsc"}
            or re.fullmatch(r"classes[^/]*\.dex", name)
        ]
        require(selected, "TrebleApp APK has no marker-bearing entries")
        payloads = [archive.read(entry) for entry in selected]
    missing = []
    for marker in TREBLE_MARKERS:
        ascii_marker = marker.encode("ascii")
        utf16_marker = marker.encode("utf-16le")
        if not any(ascii_marker in payload or utf16_marker in payload for payload in payloads):
            missing.append(marker)
    require(not missing, f"TrebleApp APK lacks patched markers: {missing}")
    completed = run_command(
        evidence_dir,
        "treble-badging",
        [str(aapt2), "dump", "badging", str(apk_path)],
        environment,
    )
    badging = completed.stdout.decode("utf-8", errors="strict")
    packages = re.findall(r"^package: name='([^']+)'", badging, flags=re.MULTILINE)
    require(packages == ["me.phh.treble.app"], f"unexpected TrebleApp package badging: {packages}")
    write_new_fsynced(
        evidence_dir / "treble-marker-check.json",
        (json.dumps({"markers": list(TREBLE_MARKERS), "status": "PASS"}, indent=2) + "\n").encode("utf-8"),
    )


def safe_evidence_relative(relative: str) -> None:
    safe_tree_relative(relative)
    parsed = PurePosixPath(relative)
    require(
        relative != ""
        and not parsed.is_absolute()
        and relative == parsed.as_posix()
        and all(part not in {"", ".", ".."} for part in parsed.parts),
        f"unsafe evidence-manifest path: {relative!r}",
    )


def evidence_manifest(
    evidence_dir: Path,
    read_hook: Callable[[Path], None] | None = None,
) -> bytes:
    destination = evidence_dir / "evidence-sha256sums.txt"
    lines: list[str] = ["# mp01-evidence-manifest-v2"]
    for path in sorted(evidence_dir.rglob("*")):
        if path == destination:
            continue
        try:
            metadata = path.lstat()
        except OSError as exc:
            raise AuditError(f"cannot inspect evidence path {path}: {exc}") from exc
        initial_signature = StatSignature.from_stat(metadata)
        relative = path.relative_to(evidence_dir).as_posix()
        safe_evidence_relative(relative)
        if stat.S_ISREG(metadata.st_mode):
            signature, digest = stable_regular_file_digest(
                path,
                f"evidence regular file {relative}",
                True,
                read_hook,
            )
            require(
                signature == initial_signature,
                f"evidence regular file changed before hashing: {relative}",
            )
            lines.append(f"F\t{digest}\t{signature.size}\t{relative}")
        elif stat.S_ISLNK(metadata.st_mode):
            try:
                target = os.readlink(path)
                final_signature = StatSignature.from_stat(path.lstat())
            except OSError as exc:
                raise AuditError(f"cannot read evidence symlink {relative}: {exc}") from exc
            require(
                final_signature == initial_signature,
                f"evidence symlink changed while being read: {relative}",
            )
            safe_tree_relative(target)
            target_hash = hashlib.sha256(target.encode("utf-8")).hexdigest()
            lines.append(f"L\t{target_hash}\t{relative}\t{target}")
        elif not stat.S_ISDIR(metadata.st_mode):
            fail(f"unsupported evidence file type: {path}")
    return ("\n".join(lines) + "\n").encode("utf-8")


def parse_evidence_manifest(raw: bytes) -> dict[str, EvidenceManifestEntry]:
    require(b"\r" not in raw and raw.endswith(b"\n"), "evidence manifest must be LF-terminated")
    try:
        lines = raw.decode("utf-8").splitlines()
    except UnicodeDecodeError as exc:
        raise AuditError(f"evidence manifest is not UTF-8: {exc}") from exc
    require(lines and lines[0] == "# mp01-evidence-manifest-v2", "unsupported evidence manifest")
    entries: dict[str, EvidenceManifestEntry] = {}
    for line in lines[1:]:
        fields = line.split("\t", 3)
        require(len(fields) == 4, f"malformed evidence-manifest row: {line!r}")
        kind, digest, third, fourth = fields
        require(SHA256_RE.fullmatch(digest) is not None, "invalid evidence-manifest digest")
        if kind == "F":
            require(third.isdigit(), "invalid evidence-manifest file size")
            relative = fourth
            target = None
            size = int(third)
        elif kind == "L":
            relative = third
            target = fourth
            size = None
            safe_tree_relative(target)
            require(
                hashlib.sha256(target.encode("utf-8")).hexdigest() == digest,
                "evidence-manifest symlink target hash mismatch",
            )
        else:
            fail(f"unsupported evidence-manifest row kind: {kind!r}")
        safe_evidence_relative(relative)
        require(relative not in entries, f"duplicate evidence-manifest path: {relative}")
        entries[relative] = EvidenceManifestEntry(
            kind, digest, relative, size, target
        )
    return entries


def verify_retained_records_in_manifest(
    records: list[SourceFileRecord], evidence_dir: Path, manifest_bytes: bytes
) -> None:
    entries = parse_evidence_manifest(manifest_bytes)
    retained_paths: set[str] = set()
    for record in records:
        require(
            record.retained.is_absolute()
            and record.retained.is_relative_to(evidence_dir),
            f"retained source record is outside evidence: {record.retained}",
        )
        relative = record.retained.relative_to(evidence_dir).as_posix()
        safe_evidence_relative(relative)
        require(relative not in retained_paths, f"duplicate retained source path: {relative}")
        retained_paths.add(relative)
        entry = entries.get(relative)
        require(entry is not None, f"retained source is absent from evidence manifest: {relative}")
        require(
            entry.kind == "F"
            and entry.sha256 == record.sha256
            and entry.size == record.retained_signature.size
            and stat.S_ISREG(record.retained_signature.mode),
            f"retained source record differs from evidence manifest: {relative}",
        )


def verify_exact_file_stably(path: Path, expected: bytes, label: str) -> str:
    raw, _, digest = read_source_stably(path, label)
    require(raw == expected, f"{label} differs from finalized content")
    return digest


def verify_finalized_evidence(
    evidence_dir: Path,
    root_checksum_path: Path,
    manifest_bytes: bytes,
    result_bytes: bytes,
    status_bytes: bytes,
    source_records: list[SourceFileRecord],
) -> None:
    manifest_path = evidence_dir / "evidence-sha256sums.txt"
    result_path = evidence_dir / "audit-result.json"
    status_path = evidence_dir / "status.txt"

    parsed_result = parse_json_bytes(result_bytes, "final audit result")
    expected_status = string_cfg(parsed_result, "status")
    require(
        expected_status == "PASS_AUDIT_ONLY_NOT_FOR_IN_PLACE_FLASH"
        and status_bytes == (expected_status + "\n").encode("ascii"),
        "final audit result/status bytes are inconsistent",
    )
    require(
        string_cfg(parsed_result, "external_root_checksum")
        == str(root_checksum_path),
        "final audit result names a different external root checksum",
    )

    verify_exact_file_stably(result_path, result_bytes, "final audit result")
    verify_exact_file_stably(status_path, status_bytes, "final audit status")
    manifest_digest = verify_exact_file_stably(
        manifest_path, manifest_bytes, "final evidence manifest"
    )
    require(
        manifest_digest == hashlib.sha256(manifest_bytes).hexdigest(),
        "final evidence manifest hash mismatch",
    )
    verify_retained_records_in_manifest(
        source_records, evidence_dir, manifest_bytes
    )

    regenerated_manifest = evidence_manifest(evidence_dir)
    require(
        regenerated_manifest == manifest_bytes,
        "evidence tree changed after final manifest was written",
    )
    verify_retained_records_in_manifest(
        source_records, evidence_dir, regenerated_manifest
    )

    # Re-read the generated seal after regenerating every evidence row.
    verify_exact_file_stably(result_path, result_bytes, "sealed audit result")
    verify_exact_file_stably(status_path, status_bytes, "sealed audit status")
    verify_exact_file_stably(manifest_path, manifest_bytes, "sealed evidence manifest")


def external_root_content(
    evidence_dir: Path, logs_root: Path, manifest_bytes: bytes
) -> bytes:
    relative_manifest = (evidence_dir / "evidence-sha256sums.txt").relative_to(
        logs_root
    ).as_posix()
    safe_evidence_relative(relative_manifest)
    return (
        "format=mp01-evidence-root-v1\n"
        f"evidence_manifest={relative_manifest}\n"
        f"evidence_manifest_sha256={hashlib.sha256(manifest_bytes).hexdigest()}\n"
    ).encode("ascii")


def remove_external_root_durably(root_checksum_path: Path) -> None:
    parent = root_checksum_path.parent
    try:
        metadata = root_checksum_path.lstat()
    except FileNotFoundError:
        fsync_dir(parent)
        return
    except OSError as exc:
        raise AuditError(f"cannot inspect external root during cleanup: {exc}") from exc

    invalidated = False
    if stat.S_ISREG(metadata.st_mode):
        descriptor = open_source(
            root_checksum_path, "external root cleanup", True
        )
        try:
            os.fchmod(descriptor, 0o600)
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
        flags = (
            os.O_WRONLY
            | os.O_TRUNC
            | getattr(os, "O_CLOEXEC", 0)
            | getattr(os, "O_NOFOLLOW", 0)
        )
        try:
            descriptor = os.open(root_checksum_path, flags)
        except OSError as exc:
            raise AuditError(f"cannot invalidate external root during cleanup: {exc}") from exc
        try:
            with os.fdopen(descriptor, "wb") as output:
                output.write(b"INVALID_MP01_EVIDENCE_ROOT\n")
                output.flush()
                os.fsync(output.fileno())
            invalidated = True
        except BaseException:
            raise
        fsync_dir(parent)

    try:
        root_checksum_path.unlink()
    except FileNotFoundError:
        fsync_dir(parent)
        return
    except OSError as exc:
        state = "invalidated" if invalidated else "not safely invalidated"
        raise AuditError(
            f"cannot remove external root during cleanup ({state}): {exc}"
        ) from exc
    fsync_dir(parent)


def publish_external_root(
    root_checksum_path: Path,
    root_content: bytes,
    after_create_hook: Callable[[Path], None] | None = None,
) -> None:
    try:
        write_new_fsynced(root_checksum_path, root_content, 0o400)
        if after_create_hook is not None:
            after_create_hook(root_checksum_path)
        verify_exact_file_stably(
            root_checksum_path, root_content, "committed external root checksum"
        )
    except BaseException as exc:
        try:
            remove_external_root_durably(root_checksum_path)
        except BaseException as cleanup_exc:
            raise AuditError(
                "external root publication failed and its completion anchor "
                f"could not be durably removed: {cleanup_exc}"
            ) from exc
        if isinstance(exc, AuditError):
            raise
        raise AuditError(f"external root publication failed: {exc}") from exc


def make_read_only(evidence_dir: Path) -> None:
    paths = sorted(evidence_dir.rglob("*"), key=lambda item: len(item.parts), reverse=True)
    for path in paths:
        initial = lstat_signature(path, f"evidence seal {path}")
        if stat.S_ISREG(initial.mode):
            descriptor = open_source(path, f"evidence seal {path}", True)
            try:
                require(
                    StatSignature.from_stat(os.fstat(descriptor)) == initial,
                    f"evidence file changed before sealing: {path}",
                )
                os.fchmod(descriptor, 0o400)
                os.fsync(descriptor)
                sealed = StatSignature.from_stat(os.fstat(descriptor))
            finally:
                os.close(descriptor)
            require(
                stat.S_ISREG(sealed.mode)
                and sealed.device == initial.device
                and sealed.inode == initial.inode
                and sealed.links == initial.links
                and sealed.uid == initial.uid
                and sealed.gid == initial.gid
                and sealed.size == initial.size
                and sealed.mtime_ns == initial.mtime_ns
                and lstat_signature(path, f"sealed evidence file {path}") == sealed,
                f"evidence file changed while being sealed: {path}",
            )
        elif stat.S_ISDIR(initial.mode):
            no_symlink_ancestors(path, f"evidence directory seal {path}")
            flags = (
                os.O_RDONLY
                | getattr(os, "O_DIRECTORY", 0)
                | getattr(os, "O_CLOEXEC", 0)
                | getattr(os, "O_NOFOLLOW", 0)
            )
            try:
                descriptor = os.open(path, flags)
            except OSError as exc:
                raise AuditError(f"cannot open evidence directory for sealing {path}: {exc}") from exc
            try:
                require(
                    StatSignature.from_stat(os.fstat(descriptor)) == initial,
                    f"evidence directory changed before sealing: {path}",
                )
                os.fchmod(descriptor, 0o500)
                os.fsync(descriptor)
                sealed = StatSignature.from_stat(os.fstat(descriptor))
            finally:
                os.close(descriptor)
            require(
                stat.S_ISDIR(sealed.mode)
                and lstat_signature(path, f"sealed evidence directory {path}") == sealed,
                f"evidence directory changed while being sealed: {path}",
            )
    root_initial = lstat_signature(evidence_dir, "evidence root seal")
    require(stat.S_ISDIR(root_initial.mode), "evidence root is not a directory")
    flags = (
        os.O_RDONLY
        | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    descriptor = os.open(evidence_dir, flags)
    try:
        require(
            StatSignature.from_stat(os.fstat(descriptor)) == root_initial,
            "evidence root changed before sealing",
        )
        os.fchmod(descriptor, 0o500)
        os.fsync(descriptor)
        sealed_root = StatSignature.from_stat(os.fstat(descriptor))
    finally:
        os.close(descriptor)
    require(
        lstat_signature(evidence_dir, "sealed evidence root") == sealed_root,
        "evidence root changed while being sealed",
    )


def prepare_failure_evidence(evidence_dir: Path) -> None:
    try:
        os.chmod(evidence_dir, 0o700, follow_symlinks=False)
    except OSError:
        return
    for name in ("audit-result.json", "status.txt"):
        path = evidence_dir / name
        try:
            metadata = path.lstat()
            if stat.S_ISREG(metadata.st_mode):
                os.chmod(path, 0o600, follow_symlinks=False)
        except OSError:
            continue


def audit(config_path: Path) -> tuple[dict, Path, Path]:
    bootstrap_raw, bootstrap_signature, bootstrap_sha = read_source_stably(config_path, "audit config")
    bootstrap_config = parse_json_bytes(bootstrap_raw, "audit config")
    bootstrap_after_epoch = integer_cfg(bootstrap_config, "after_epoch")
    (
        bootstrap_build_log,
        bootstrap_build_log_signature,
        bootstrap_start_record,
        bootstrap_start_record_signature,
        bootstrap_start_record_sha256,
    ) = validate_build_log_source(bootstrap_config, bootstrap_after_epoch)
    logs_root, evidence_dir, root_checksum_path = validate_evidence_location(
        bootstrap_config, config_path
    )
    evidence_dir.mkdir(mode=0o700)
    fsync_dir(evidence_dir.parent)
    for directory in (evidence_dir / "tools", evidence_dir / "tmp", evidence_dir / "home"):
        directory.mkdir(mode=0o700)
    fsync_dir(evidence_dir)

    result: dict = {
        "format": "mp01-host-artifact-audit-v2",
        "audit_started_epoch": int(time.time()),
        "status": "IN_PROGRESS",
        "phone_commands_used": False,
    }
    source_records: list[SourceFileRecord] = []
    java_symlinks: list[SourceSymlinkRecord] = []
    java_directories: list[SourceDirectoryRecord] = []
    signer_java_symlinks: list[SourceSymlinkRecord] = []
    signer_java_directories: list[SourceDirectoryRecord] = []
    python_symlinks: list[SourceSymlinkRecord] = []
    python_directories: list[SourceDirectoryRecord] = []
    try:
        retained_config_record = copy_stable_file(
            config_path,
            evidence_dir / "audit-config.json",
            "audit config",
            source_records,
        )
        require(
            retained_config_record.signature == bootstrap_signature
            and retained_config_record.sha256 == bootstrap_sha,
            "audit config changed after bootstrap validation",
        )
        config = parse_json_bytes(
            (evidence_dir / "audit-config.json").read_bytes(), "retained audit config"
        )
        audit_implementation_record = copy_stable_file(
            Path(__file__).resolve(),
            evidence_dir / "audit.py",
            "audit implementation",
            source_records,
        )
        audit_entry_record = copy_stable_file(
            Path(__file__).with_name("audit.sh").resolve(),
            evidence_dir / "audit.sh",
            "audit entry point",
            source_records,
        )
        audit_expectations = cfg(config, "expected", "audit_sha256")
        require(
            isinstance(audit_expectations, dict)
            and set(audit_expectations) == {"audit.py", "audit.sh"},
            "expected.audit_sha256 must pin audit.py and audit.sh",
        )
        require(
            audit_implementation_record.sha256
            == require_digest(
                string_cfg(audit_expectations, "audit.py"), SHA256_RE, "audit.py"
            ),
            "audit.py does not match its independent config pin",
        )
        require(
            audit_entry_record.sha256
            == require_digest(
                string_cfg(audit_expectations, "audit.sh"), SHA256_RE, "audit.sh"
            ),
            "audit.sh does not match its independent config pin",
        )
        result["audit_sha256"] = {
            "audit.py": audit_implementation_record.sha256,
            "audit.sh": audit_entry_record.sha256,
        }

        after_epoch = integer_cfg(config, "after_epoch")
        require(after_epoch > 0, "after_epoch must be positive")
        require(after_epoch == bootstrap_after_epoch, "after_epoch changed after bootstrap")
        result["after_epoch"] = after_epoch
        build_log_source = Path(string_cfg(config, "build_log"))
        require(
            build_log_source == bootstrap_build_log,
            "build_log changed after bootstrap",
        )
        build_log_record = copy_stable_file(
            build_log_source,
            evidence_dir / "build.log",
            "build log",
            source_records,
        )
        require(
            build_log_record.signature == bootstrap_build_log_signature,
            "build log changed after bootstrap validation",
        )
        record_file_result(result, "build_log", build_log_record)
        start_record = copy_stable_file(
            bootstrap_start_record,
            evidence_dir / "build.start-epoch",
            "formal build start record",
            source_records,
        )
        require(
            start_record.signature == bootstrap_start_record_signature
            and start_record.sha256 == bootstrap_start_record_sha256,
            "formal build start record changed after bootstrap validation",
        )
        record_file_result(result, "build_start_record", start_record)
        image_dir = existing_real_dir(Path(string_cfg(config, "image_dir")), "image directory")
        metadata_dir = existing_real_dir(Path(string_cfg(config, "metadata_dir")), "metadata directory")
        target_files_source = Path(string_cfg(config, "target_files"))
        paths_config = cfg(config, "paths")
        expected = cfg(config, "expected")
        require(isinstance(paths_config, dict) and isinstance(expected, dict), "paths/expected must be objects")
        require(set(paths_config) == REQUIRED_PATH_KEYS, "paths keys do not exactly match the audit contract")

        source_paths = {key: Path(string_cfg(paths_config, key)) for key in paths_config}
        require(
            source_paths["formal_build_harness"].name == "run-formal-build.sh"
            and source_paths["formal_build_log_helper"].name
            == "formal-build-log.py"
            and source_paths["formal_build_harness"].parent
            == source_paths["formal_build_log_helper"].parent,
            "formal build harness/helper paths do not match the repository contract",
        )
        android_host_out = existing_real_dir(source_paths["android_host_out"], "Android host output")
        python_stdlib_source = source_paths["python_stdlib"]
        python_stdlib_archive = python_stdlib_source.parent / (
            python_stdlib_source.name.replace(".", "") + ".zip"
        )
        python_stdlib_archive_absence = attest_absent_path(
            python_stdlib_archive, "isolated Python standard-library ZIP"
        )
        require(source_paths["signer_aapt2"] == android_host_out / "bin" / "aapt2", "signer_aapt2 does not match original host selection")
        require(
            source_paths["partner_zipalign"] == android_host_out / "bin" / "zipalign",
            "partner_zipalign does not match Android host output",
        )
        require(
            source_paths["runtime_libcxx"] == android_host_out / "lib64" / "libc++.so",
            "runtime_libcxx does not match Android host output",
        )
        require(source_paths["avbtool"] == android_host_out / "bin" / "avbtool", "avbtool does not match host selection")
        require(source_paths["deapexer"] == android_host_out / "bin" / "deapexer", "deapexer does not match host selection")
        require(
            source_paths["apksigner_source_jar"]
            == source_paths["apksigner_launcher"].parent / "lib" / "apksigner.jar",
            "apksigner source JAR does not match SDK launcher",
        )
        content_manifest_suffix = ".apk-content-manifest.json"
        content_manifest_path = str(source_paths["treble_expected_content_manifest"])
        require(
            content_manifest_path.endswith(content_manifest_suffix),
            "Treble content-manifest path does not match provenance naming",
        )
        require(
            source_paths["apksigner_jar"]
            == Path(content_manifest_path.removesuffix(content_manifest_suffix) + ".apksigner.jar"),
            "apksigner JAR is not the retained TrebleApp provenance snapshot",
        )
        adjacent_apksigner_jar = attest_absent_path(
            source_paths["apksigner_launcher"].parent / "apksigner.jar",
            "higher-priority adjacent apksigner JAR",
        )

        tool_destinations = {
            "python_executable": evidence_dir / "tools" / "python3",
            "signer_verifier": evidence_dir / "tools" / "signer_compatibility.py",
            "signer_aapt2": evidence_dir / "tools" / "otatools" / "bin" / "aapt2",
            "treble_aapt2": evidence_dir / "tools" / "treble-aapt2",
            "avbtool": evidence_dir / "tools" / "otatools" / "bin" / "avbtool",
            "deapexer": evidence_dir / "tools" / "otatools" / "bin" / "deapexer",
            "openssl": evidence_dir / "tools" / "otatools" / "bin" / "openssl",
            "env_executable": evidence_dir / "tools" / "env",
            "runtime_loader": evidence_dir / "tools" / "runtime" / "ld-linux-x86-64.so.2",
            "runtime_libpython": evidence_dir / "tools" / "runtime" / "libpython3.14.so.1.0",
            "runtime_libc": evidence_dir / "tools" / "runtime" / "libc.so.6",
            "runtime_libm": evidence_dir / "tools" / "runtime" / "libm.so.6",
            "runtime_libpthread": evidence_dir / "tools" / "runtime" / "libpthread.so.0",
            "runtime_libdl": evidence_dir / "tools" / "runtime" / "libdl.so.2",
            "runtime_librt": evidence_dir / "tools" / "runtime" / "librt.so.1",
            "runtime_libgcc": evidence_dir / "tools" / "runtime" / "libgcc_s.so.1",
            "runtime_libutil": evidence_dir / "tools" / "runtime" / "libutil.so.1",
            "runtime_libssl": evidence_dir / "tools" / "runtime" / "libssl.so.3",
            "runtime_libcrypto": evidence_dir / "tools" / "runtime" / "libcrypto.so.3",
            "runtime_libz": evidence_dir / "tools" / "runtime" / "libz.so.1",
            "runtime_libbz2": evidence_dir / "tools" / "runtime" / "libbz2.so.1",
            "runtime_liblzma": evidence_dir / "tools" / "runtime" / "liblzma.so.5",
            "runtime_libzstd": evidence_dir / "tools" / "runtime" / "libzstd.so.1",
            "runtime_libexpat": evidence_dir / "tools" / "runtime" / "libexpat.so.1",
            "runtime_libcxx": evidence_dir / "tools" / "otatools" / "lib64" / "libc++.so",
            "apksigner_launcher": evidence_dir / "tools" / "source-apksigner-launcher",
            "apksigner_source_jar": evidence_dir / "tools" / "source-apksigner.jar",
            "apksigner_jar": evidence_dir / "tools" / "apksigner.jar",
            "apk_content_manifest": evidence_dir / "tools" / "apk-content-manifest.py",
            "signer_manifest": evidence_dir / "inputs" / "expected-signers.tsv",
            "treble_expected_content_manifest": evidence_dir / "inputs" / "treble-content.json",
            "workspace_path_policy": evidence_dir / "inputs" / "workspace-paths.sh",
            "metalava_patch": evidence_dir / "inputs" / "metalava.patch",
            "metalava_policy_verifier": evidence_dir / "inputs" / "verify-metalava.py",
            "blueprint_patch": evidence_dir / "inputs" / "blueprint.patch",
            "blueprint_provider_validation_verifier": evidence_dir / "inputs" / "verify-blueprint.py",
            "vendor_lineage_no_kernel_patch": evidence_dir / "inputs" / "vendor-lineage-no-kernel.patch",
            "no_kernel_header_policy_verifier": evidence_dir / "inputs" / "verify-no-kernel-header-policy.py",
            "partner_gms_presigned_apk_patch": evidence_dir / "inputs" / "partner-gms-presigned-apk.patch",
            "presigned_partner_apk_policy_verifier": evidence_dir / "inputs" / "verify-presigned-partner-apk-policy.py",
            "partner_zipalign": evidence_dir / "tools" / "otatools" / "bin" / "zipalign",
            "formal_build_harness": evidence_dir / "tools" / "run-formal-build.sh",
            "formal_build_log_helper": evidence_dir / "tools" / "formal-build-log.py",
            "source_input_manifest_lock": evidence_dir / "inputs" / "source-input-manifest.xml",
            "prepared_source_manifest_lock": evidence_dir / "inputs" / "prepared-source-manifest.xml",
        }
        for destination in tool_destinations.values():
            destination.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        for directory in {destination.parent for destination in tool_destinations.values()}:
            fsync_dir(directory)

        expected_tool_hashes = cfg(expected, "tool_sha256")
        require(
            isinstance(expected_tool_hashes, dict)
            and set(expected_tool_hashes) == set(tool_destinations),
            "expected.tool_sha256 keys must exactly match retained file inputs",
        )
        retained: dict[str, Path] = {}
        result["tool_sha256"] = {}
        for key, destination in tool_destinations.items():
            record = copy_stable_file(
                source_paths[key], destination, key, source_records
            )
            expected_hash = require_digest(
                string_cfg(expected_tool_hashes, key), SHA256_RE, f"tool {key}"
            )
            require(record.sha256 == expected_hash, f"{key} SHA256 mismatch")
            retained[key] = destination
            result["tool_sha256"][key] = record.sha256

        build_info_expectations = cfg(expected, "build_info")
        formal_log_contract = validate_retained_build_log(
            build_log_record,
            start_record,
            string_cfg(expected, "build_log_sha256"),
            after_epoch,
            string_cfg(expected_tool_hashes, "formal_build_harness"),
            string_cfg(expected_tool_hashes, "formal_build_log_helper"),
            string_cfg(build_info_expectations, "Live MP01-LineageGSI commit"),
            string_cfg(build_info_expectations, "Live MP01-LineageGSI tree"),
        )
        require(
            formal_log_contract["harness_sha256"]
            == result["tool_sha256"]["formal_build_harness"]
            and formal_log_contract["helper_sha256"]
            == result["tool_sha256"]["formal_build_log_helper"],
            "formal build log contract differs from retained harness inputs",
        )
        require(
            formal_log_contract["gsi_commit"]
            == string_cfg(build_info_expectations, "Cloned support commit")
            and formal_log_contract["gsi_tree"]
            == string_cfg(build_info_expectations, "Cloned support tree"),
            "formal build log commit/tree differ from cloned build-info expectations",
        )
        result["build_log_expected_sha256"] = formal_log_contract["sha256"]
        result["formal_build_log_contract"] = formal_log_contract

        require(
            retained["apksigner_source_jar"].read_bytes()
            == retained["apksigner_jar"].read_bytes(),
            "retained TrebleApp signer JAR differs from the pinned SDK source JAR",
        )

        java_home_source = source_paths["java_home"]
        java_home_retained = evidence_dir / "tools" / "java-home"
        java_tree_sha, java_symlinks, java_directories, java_manifest = copy_stable_tree(
            java_home_source, java_home_retained, source_records, "Java home"
        )
        expected_java_tree = require_digest(
            string_cfg(expected, "java_home_tree_sha256"),
            SHA256_RE,
            "Java home tree SHA256",
        )
        require(java_tree_sha == expected_java_tree, "retained Java home tree hash mismatch")
        require(
            hashlib.sha256(retained_tree_manifest(java_home_retained)).hexdigest()
            == java_tree_sha,
            "retained Java home does not reproduce its normalized tree manifest",
        )
        write_new_fsynced(evidence_dir / "java-home-tree-manifest.txt", java_manifest)
        result["java_home_tree_sha256"] = java_tree_sha

        signer_java_home_source = source_paths["signer_java_home"]
        signer_java_home_retained = evidence_dir / "tools" / "signer-java-home"
        (
            signer_java_tree_sha,
            signer_java_symlinks,
            signer_java_directories,
            signer_java_manifest,
        ) = copy_stable_tree(
            signer_java_home_source,
            signer_java_home_retained,
            source_records,
            "Signer Java home",
        )
        expected_signer_java_tree = require_digest(
            string_cfg(expected, "signer_java_home_tree_sha256"),
            SHA256_RE,
            "Signer Java home tree SHA256",
        )
        require(
            signer_java_tree_sha == expected_signer_java_tree,
            "retained signer Java home tree hash mismatch",
        )
        require(
            hashlib.sha256(retained_tree_manifest(signer_java_home_retained)).hexdigest()
            == signer_java_tree_sha,
            "retained signer Java home does not reproduce its normalized tree manifest",
        )
        write_new_fsynced(
            evidence_dir / "signer-java-home-tree-manifest.txt", signer_java_manifest
        )
        result["signer_java_home_tree_sha256"] = signer_java_tree_sha
        signer_java_source = signer_java_home_source / "bin" / "java"
        signer_java_retained = signer_java_home_retained / "bin" / "java"
        signer_java_sha = require_digest(
            string_cfg(expected, "apksigner_java_sha256"),
            SHA256_RE,
            "APK signer Java SHA256",
        )
        require(
            sha256_file(signer_java_retained) == signer_java_sha,
            "retained APK signer Java SHA256 mismatch",
        )

        python_stdlib_retained = evidence_dir / "tools" / "python-stdlib"
        (
            python_tree_sha,
            python_symlinks,
            python_directories,
            python_manifest,
        ) = copy_stable_tree(
            python_stdlib_source,
            python_stdlib_retained,
            source_records,
            "Python standard library",
        )
        expected_python_tree = require_digest(
            string_cfg(expected, "python_stdlib_tree_sha256"),
            SHA256_RE,
            "Python standard-library tree SHA256",
        )
        require(
            python_tree_sha == expected_python_tree,
            "Python standard-library tree hash mismatch",
        )
        require(
            hashlib.sha256(retained_tree_manifest(python_stdlib_retained)).hexdigest()
            == python_tree_sha,
            "retained Python standard library does not reproduce its tree manifest",
        )
        write_new_fsynced(
            evidence_dir / "python-stdlib-tree-manifest.txt", python_manifest
        )
        result["python_stdlib_tree_sha256"] = python_tree_sha
        result["python_stdlib_archive_absent"] = str(python_stdlib_archive)

        openssl_modules = evidence_dir / "tools" / "openssl-modules"
        openssl_modules.mkdir(mode=0o500)
        fsync_dir(openssl_modules)
        openssl_config = (
            "openssl_conf = openssl_init\n"
            "[openssl_init]\n"
            "providers = provider_sect\n"
            "[provider_sect]\n"
            "default = default_sect\n"
            "[default_sect]\n"
            "activate = 1\n"
        ).encode("ascii")
        write_new_fsynced(evidence_dir / "tools" / "openssl.cnf", openssl_config)

        environment = command_environment(
            evidence_dir,
            signer_java_home_retained,
            evidence_dir / "tools" / "otatools" / "bin",
        )
        native_executables = {
            "avbtool": retained["avbtool"],
            "deapexer": retained["deapexer"],
            "env": retained["env_executable"],
            "openssl": retained["openssl"],
            "partner-zipalign": retained["partner_zipalign"],
            "python": retained["python_executable"],
            "signer-aapt2": retained["signer_aapt2"],
            "signer-java": signer_java_retained,
            "signer-jvm": signer_java_home_retained / "lib" / "server" / "libjvm.so",
            "treble-aapt2": retained["treble_aapt2"],
        }
        native_dependency_resolution = verify_native_dependency_resolution(
            evidence_dir,
            "initial",
            retained["runtime_loader"],
            native_executables,
            signer_java_home_retained,
            source_paths,
            environment,
        )
        result["native_dependency_resolution"] = native_dependency_resolution
        verify_runtime_configuration(
            evidence_dir,
            retained["python_executable"],
            retained["signer_verifier"],
            python_stdlib_source,
            signer_java_home_retained,
            retained["openssl"],
            source_paths,
            environment,
            result,
        )

        signer_manifest_sha = require_digest(
            string_cfg(expected, "signer_manifest_sha256"), SHA256_RE, "signer manifest"
        )
        require(sha256_file(retained["signer_manifest"]) == signer_manifest_sha, "signer manifest hash mismatch")
        content_manifest_sha = require_digest(
            string_cfg(expected, "treble_content_manifest_sha256"), SHA256_RE, "Treble content manifest"
        )
        require(sha256_file(retained["treble_expected_content_manifest"]) == content_manifest_sha, "Treble content manifest hash mismatch")

        markers: list[tuple[int, Path]] = []
        for candidate in metadata_dir.iterdir():
            match = MARKER_RE.fullmatch(candidate.name)
            if match and int(match.group("epoch")) > after_epoch:
                metadata = candidate.lstat()
                require(stat.S_ISREG(metadata.st_mode), f"completion marker is not regular: {candidate}")
                require(metadata.st_mtime_ns > after_epoch * 1_000_000_000, "marker mtime is not after cutoff")
                markers.append((int(match.group("epoch")), candidate))
        require(len(markers) == 1, f"expected one completion marker after cutoff, found {len(markers)}")
        build_epoch, marker_source = markers[0]
        require_build_log_mtime_after(
            build_log_record.signature, build_epoch, "publication epoch"
        )
        stem = marker_source.name.removesuffix(".sha256sums")
        image_name = f"MP01-Lineage-{build_epoch}-microG-unsigned.img"
        tar_name = f"MP01-Lineage-{build_epoch}-microG-unsigned.tar.gz"
        publication_sources = {
            "marker": marker_source,
            "image": image_dir / image_name,
            "archive": image_dir / tar_name,
            "build_info": metadata_dir / f"{stem}.build-info.txt",
            "manifest": metadata_dir / f"{stem}.repo-manifest.xml",
            "target_files": target_files_source,
        }
        publication_destinations = {
            "marker": evidence_dir / "publication.sha256sums",
            "image": evidence_dir / "publication.img",
            "archive": evidence_dir / "publication.tar.gz",
            "build_info": evidence_dir / "publication.build-info.txt",
            "manifest": evidence_dir / "publication.repo-manifest.xml",
            "target_files": evidence_dir / "target-files.snapshot.zip",
        }
        publication: dict[str, Path] = {}
        for key in publication_sources:
            record = copy_stable_file(
                publication_sources[key],
                publication_destinations[key],
                f"publication {key}",
                source_records,
            )
            publication[key] = record.retained
            record_file_result(result, key, record)

        checksum_text = read_lf_text(publication["marker"], "retained completion marker", True)
        checksum_lines = checksum_text.splitlines()
        require(len(checksum_lines) == 2, "completion marker must contain two lines")
        parsed_checksums: list[tuple[str, str]] = []
        for line in checksum_lines:
            match = CHECKSUM_RE.fullmatch(line)
            require(match is not None, f"malformed checksum line: {line!r}")
            parsed_checksums.append((match.group("sha"), match.group("name")))
        image_sha = sha256_file(publication["image"])
        tar_sha = sha256_file(publication["archive"])
        require(
            parsed_checksums == [(image_sha, image_name), (tar_sha, tar_name)],
            "published checksums, names, or ordering differ",
        )
        result["build_epoch"] = build_epoch
        result["image_sha256"] = image_sha
        result["archive_sha256"] = tar_sha

        with tarfile.open(publication["archive"], mode="r:gz") as archive:
            members = archive.getmembers()
            require(len(members) == 1, "published tar must contain exactly one member")
            member = members[0]
            require(member.name == image_name and member.isfile(), "tar member is not expected image")
            extracted = archive.extractfile(member)
            require(extracted is not None, "cannot open tar member")
            with extracted, publication["image"].open("rb") as image_stream:
                equal, member_sha, member_size = streams_equal(extracted, image_stream)
            require(
                equal and member_sha == image_sha and member_size == member.size,
                "tar member is not byte-equal to image",
            )

        treble_apk = evidence_dir / "TrebleApp.apk"
        partner_apk_dir = evidence_dir / "partner-apks"
        partner_apk_dir.mkdir(mode=0o700)
        fsync_dir(evidence_dir)
        target_partner_apks: dict[str, Path] = {}
        with zipfile.ZipFile(publication["target_files"]) as target_zip:
            entries = validate_zip(target_zip, "target-files snapshot")
            inventory = ("\n".join(sorted(entries)) + "\n").encode("utf-8")
            write_new_fsynced(evidence_dir / "target-files-inventory.txt", inventory)
            for name in (*REQUIRED_TARGET_FILES, SYSTEM_IMAGE_ENTRY):
                require(name in entries, f"target-files lacks required entry: {name}")
                require_regular_zip_entry(entries[name], f"target-files {name}")
            for module, entry_name in PARTNER_APK_TARGETS:
                target_apk = partner_apk_dir / f"{module}.apk"
                with target_zip.open(entries[entry_name]) as source:
                    write_new_stream_fsynced(target_apk, source, 0o400)
                target_partner_apks[module] = target_apk
            with target_zip.open(entries[SYSTEM_IMAGE_ENTRY]) as zip_image, publication["image"].open("rb") as image_stream:
                equal, target_image_sha, target_image_size = streams_equal(zip_image, image_stream)
            require(
                equal and target_image_sha == image_sha and target_image_size == entries[SYSTEM_IMAGE_ENTRY].file_size,
                "target-files system image is not byte-equal to publication",
            )
            with target_zip.open(entries[TREBLE_APP_ENTRY]) as source:
                write_new_fsynced(treble_apk, source.read(), 0o400)
        result["target_files_entry_count"] = len(entries)
        result["required_target_files_entries"] = len(REQUIRED_TARGET_FILES)
        result["target_files_system_image_sha256"] = target_image_sha

        verify_manifest(publication["manifest"], expected, result)
        result["source_input_manifest_lock_sha256"] = result["tool_sha256"][
            "source_input_manifest_lock"
        ]
        result["prepared_source_manifest_lock_sha256"] = result["tool_sha256"][
            "prepared_source_manifest_lock"
        ]
        require(
            result["prepared_source_manifest_lock_sha256"]
            == result["resolved_manifest_expected_sha256"],
            "prepared source manifest lock differs from expected resolved manifest",
        )

        build_info_text = read_lf_text(publication["build_info"], "retained build-info")
        require(
            build_info_text.splitlines()[0] == "MP01 LineageOS 23.2 microG unsigned test build",
            "build-info does not identify unsigned test build",
        )
        build_fields = parse_build_info_fields(build_info_text)
        build_expectations = cfg(expected, "build_info")
        verify_build_info_expectations(build_fields, build_expectations)
        signer_build_user_home = Path(
            string_cfg(build_expectations, "TrebleApp Gradle user home")
        )
        signer_build_tmpdir = Path(
            string_cfg(
                build_expectations, "TrebleApp APK signer temporary directory"
            )
        )
        require(
            signer_build_tmpdir == signer_build_user_home / "apksigner-tmp",
            "build-info APK signer temporary directory is not under the Gradle home",
        )
        android_product_output = Path(
            string_cfg(build_expectations, "Android product output")
        )
        direct_fields = {
            "Build date epoch": str(build_epoch),
            "Image": str(publication_sources["image"]),
            "Archive": str(publication_sources["archive"]),
            "SHA256 sums": str(publication_sources["marker"]),
            "Target-files source path": str(target_files_source),
            "Target-files snapshot SHA256": sha256_file(publication["target_files"]),
            "Published system image source": SYSTEM_IMAGE_ENTRY,
            "Signer compatibility mode": "test-key-audit",
            "Signer compatibility expected manifest": source_paths["signer_manifest"].name,
            "Signer compatibility expected manifest SHA256": signer_manifest_sha,
            "Resolved manifest": str(publication_sources["manifest"]),
            "Source input manifest lock": SOURCE_INPUT_MANIFEST_LOCK,
            "Source input manifest lock SHA256": result[
                "source_input_manifest_lock_sha256"
            ],
            "Prepared source manifest lock": PREPARED_SOURCE_MANIFEST_LOCK,
            "Prepared source manifest lock SHA256": result[
                "prepared_source_manifest_lock_sha256"
            ],
            "Resolved manifest SHA256": result["resolved_manifest_sha256"],
            "Android host output": str(android_host_out),
            "Android JDK home": str(java_home_source),
            "TrebleApp APK signer Java": str(signer_java_source),
            "TrebleApp APK signer Java SHA256": signer_java_sha,
            "TrebleApp APK signer Java user home": str(signer_build_user_home),
            "TrebleApp APK signer Java temp directory": str(signer_build_tmpdir),
            "Expected TrebleApp APK signer Java SHA256": signer_java_sha,
            "TrebleApp APK signer JAR": str(source_paths["apksigner_jar"]),
            "TrebleApp APK signer JAR SHA256": sha256_file(retained["apksigner_jar"]),
            "Expected TrebleApp APK signer JAR SHA256": sha256_file(
                retained["apksigner_jar"]
            ),
            "Android OUT_DIR interface": "out",
            "Android product output name": android_product_output.name,
            "Android TARGET_NO_KERNEL": "true",
            "Presigned partner APK byte preservation": "verified",
            "Presigned partner APK alignment": "verified",
            "Publication lock path": str(image_dir),
            "Build log": str(build_log_source),
        }
        verify_derived_build_info_fields(build_fields, direct_fields)
        path_hash_pairs = (
            ("Workspace path policy", "Workspace path policy SHA256", "workspace_path_policy"),
            ("Metalava policy verifier", "Metalava policy verifier SHA256", "metalava_policy_verifier"),
            ("Blueprint provider-validation verifier", "Blueprint provider-validation verifier SHA256", "blueprint_provider_validation_verifier"),
        )
        for path_key, hash_key, retained_key in path_hash_pairs:
            require(build_fields[path_key] == str(source_paths[retained_key]), f"build-info path mismatch: {path_key}")
            require(build_fields[hash_key] == sha256_file(retained[retained_key]), f"build-info hash mismatch: {hash_key}")
        require(
            build_fields["build/soong Metalava patch SHA256"] == sha256_file(retained["metalava_patch"]),
            "Metalava patch hash differs from retained input",
        )
        require(
            build_fields["build/blueprint provider-validation patch SHA256"] == sha256_file(retained["blueprint_patch"]),
            "Blueprint patch hash differs from retained input",
        )
        verify_no_kernel_policy_build_info(build_fields, source_paths, retained)
        verify_partner_apk_policy_build_info(build_fields, source_paths, retained)
        partner_apk_sha256 = verify_partner_apk_artifacts(
            evidence_dir,
            target_partner_apks,
            cfg(expected, "partner_apk_sha256"),
            retained["partner_zipalign"],
            environment,
        )
        result["partner_apk_sha256"] = partner_apk_sha256
        result["partner_apk_byte_preservation"] = "verified"
        result["partner_apk_alignment"] = "verified"
        result["build_info_sha256"] = sha256_file(publication["build_info"])
        result["build_info_expectation_count"] = len(build_expectations)

        avb_info = run_command(
            evidence_dir,
            "avb-info",
            [str(retained["avbtool"]), "info_image", "--image", str(publication["image"])],
            environment,
        )
        alias = evidence_dir / "system.img"
        os.symlink(publication["image"], alias)
        try:
            run_command(
                evidence_dir,
                "avb-verify",
                [str(retained["avbtool"]), "verify_image", "--image", str(alias)],
                environment,
            )
        finally:
            alias.unlink(missing_ok=True)
            fsync_dir(evidence_dir)
        info_text = avb_info.stdout.decode("utf-8", errors="strict")
        key_matches = re.findall(r"^Public key \(sha1\):\s*([0-9a-fA-F]{40})\s*$", info_text, re.MULTILINE)
        require(len(key_matches) == 1, "AVB info does not contain exactly one public key SHA1")
        avb_sha1 = key_matches[0].lower()
        require(
            avb_sha1 == require_digest(string_cfg(expected, "avb_public_key_sha1"), SHA1_RE, "AVB key"),
            "AVB public-key SHA1 mismatch",
        )
        result["avb_public_key_sha1"] = avb_sha1

        verify_treble_markers(
            treble_apk, retained["treble_aapt2"], evidence_dir, environment
        )
        apksigner = run_command(
            evidence_dir,
            "treble-apksigner",
            [
                str(signer_java_retained),
                *java_system_properties(evidence_dir),
                "-jar",
                str(retained["apksigner_jar"]),
                "verify",
                "--print-certs",
                str(treble_apk),
            ],
            environment,
        )
        signer_output = (apksigner.stdout + b"\n" + apksigner.stderr).decode("utf-8", errors="strict")
        signer_matches = re.findall(r"^Signer #[0-9]+ certificate SHA-256 digest: (.+?)\s*$", signer_output, re.MULTILINE)
        require(len(signer_matches) == 1, "TrebleApp must report exactly one signer")
        treble_signer = require_digest(signer_matches[0], SHA256_RE, "TrebleApp signer")
        require(
            treble_signer == require_digest(string_cfg(expected, "treble_platform_certificate_sha256"), SHA256_RE, "platform signer"),
            "TrebleApp is not signed by configured platform certificate",
        )
        run_command(
            evidence_dir,
            "treble-content",
            [str(retained["python_executable"]), "-I", "-S", str(retained["apk_content_manifest"]), str(treble_apk), "--verify", str(retained["treble_expected_content_manifest"])],
            environment,
        )
        with zipfile.ZipFile(treble_apk) as treble_zip:
            treble_entries = validate_zip(treble_zip, "TrebleApp APK")
            require("classes.dex" in treble_entries, "TrebleApp lacks classes.dex")
            with treble_zip.open(treble_entries["classes.dex"]) as dex:
                dex_sha = sha256_stream(dex)
        require(
            dex_sha == require_digest(string_cfg(expected, "treble_classes_dex_sha256"), SHA256_RE, "Treble dex"),
            "TrebleApp classes.dex hash mismatch",
        )
        treble_apk_sha = sha256_file(treble_apk)
        provenance_lines = (
            f"  AAPT2: {source_paths['treble_aapt2']}",
            f"  APK signer SDK launcher: {source_paths['apksigner_launcher']}",
            f"  APK signer Java: {signer_java_source}",
            f"  APK signer Java SHA256: {signer_java_sha}",
            f"  APK signer Java user home: {signer_build_user_home}",
            f"  APK signer Java temp directory: {signer_build_tmpdir}",
            f"  APK signer JAR source: {source_paths['apksigner_source_jar']}",
            f"  APK signer JAR: {source_paths['apksigner_jar']}",
            f"  APK signer JAR SHA256: {sha256_file(retained['apksigner_jar'])}",
            f"  Packaged target-files snapshot SHA256: {sha256_file(publication['target_files'])}",
            f"  Packaged target-files APK SHA256: {treble_apk_sha}",
            "  Packaged target-files APK signing: verified",
            "  Packaged target-files APK content manifest: verified",
            f"  Packaged target-files APK classes.dex SHA256: {dex_sha}",
        )
        build_lines = build_info_text.splitlines()
        for line in provenance_lines:
            require(build_lines.count(line) == 1, f"build-info lacks Treble provenance: {line}")
        result.update(
            {
                "treble_app_apk_sha256": treble_apk_sha,
                "treble_app_signer_sha256": treble_signer,
                "treble_app_classes_dex_sha256": dex_sha,
                "treble_app_content_manifest_sha256": content_manifest_sha,
            }
        )

        signer_actual = evidence_dir / "signer-actual.tsv"
        signer_evidence = evidence_dir / "signer-evidence.txt"
        signer_snapshot = evidence_dir / "signer-target-files.snapshot.zip"
        signer_command = [
            str(retained["python_executable"]),
            "-I",
            "-S",
            str(retained["signer_verifier"]),
            "--target-files",
            str(publication["target_files"]),
            "--expected-manifest",
            str(retained["signer_manifest"]),
            "--expected-manifest-sha256",
            signer_manifest_sha,
            "--otatools-dir",
            str(evidence_dir / "tools" / "otatools"),
            "--apksigner-java",
            str(signer_java_retained),
            "--apksigner-java-home",
            str(evidence_dir / "home"),
            "--apksigner-java-tmpdir",
            str(evidence_dir / "tmp"),
            "--apksigner-java-sha256",
            signer_java_sha,
            "--apksigner-jar",
            str(retained["apksigner_jar"]),
            "--apksigner-jar-sha256",
            sha256_file(retained["apksigner_jar"]),
            "--aapt2",
            str(retained["signer_aapt2"]),
            "--mode",
            "test-key-audit",
            "--actual-manifest-out",
            str(signer_actual),
            "--evidence-out",
            str(signer_evidence),
            "--snapshot-out",
            str(signer_snapshot),
        ]
        run_command(
            evidence_dir,
            "signer-audit",
            signer_command,
            environment,
            expected_rc=3,
        )
        for path in (signer_actual, signer_evidence, signer_snapshot):
            require(path.is_file() and path.stat().st_size > 0, f"missing signer output: {path}")
            descriptor = os.open(path, os.O_RDONLY)
            try:
                os.fsync(descriptor)
            finally:
                os.close(descriptor)
        fsync_dir(evidence_dir)
        target_sha = sha256_file(publication["target_files"])
        require(sha256_file(signer_snapshot) == target_sha, "signer snapshot differs from retained target-files")
        embedded_evidence = extract_indented_block(build_info_text, "Signer compatibility evidence:", "Signer compatibility actual manifest:")
        embedded_actual = extract_indented_block(build_info_text, "Signer compatibility actual manifest:", "Verified packaged APK inputs:")
        rerun_evidence = signer_evidence.read_bytes()
        rerun_actual = signer_actual.read_bytes()
        require(embedded_evidence == rerun_evidence, "embedded signer evidence differs from rerun")
        require(embedded_actual == rerun_actual, "embedded signer manifest differs from rerun")
        evidence_values, issues = parse_signer_evidence(rerun_evidence)
        actual_apk_count, actual_apex_count = signer_manifest_counts(rerun_actual)
        require(
            int(evidence_values["actual_apk_count"]) == actual_apk_count,
            "signer evidence APK count differs from actual manifest",
        )
        require(
            int(evidence_values["actual_apex_count"]) == actual_apex_count,
            "signer evidence APEX count differs from actual manifest",
        )
        required_evidence = {
            "format": "mp01-signer-compatibility-evidence-v1",
            "mode": "test-key-audit",
            "comparison_status": "INCOMPATIBLE",
            "flash_disposition": "NOT_FOR_IN_PLACE_FLASH",
            "target_files_sha256": target_sha,
            "expected_manifest_sha256": signer_manifest_sha,
            "actual_manifest_sha256": sha256_file(signer_actual),
            "apksigner_execution": "direct_java_jar",
            "apksigner_java_sha256": signer_java_sha,
            "apksigner_jar_sha256": sha256_file(retained["apksigner_jar"]),
        }
        for key, value in required_evidence.items():
            require(evidence_values[key] == value, f"signer evidence mismatch: {key}")
        require(int(evidence_values["incompatibility_count"]) > 0, "test-key audit must have incompatibilities")
        result["signer_comparison_status"] = evidence_values["comparison_status"]
        result["signer_flash_disposition"] = evidence_values["flash_disposition"]
        result["signer_incompatibility_count"] = int(evidence_values["incompatibility_count"])
        result["signer_warning_count"] = int(evidence_values["warning_count"])
        result["signer_issue_count"] = len(issues)
        result["signer_actual_manifest_sha256"] = sha256_file(signer_actual)

        final_native_dependency_resolution = verify_native_dependency_resolution(
            evidence_dir,
            "final",
            retained["runtime_loader"],
            native_executables,
            signer_java_home_retained,
            source_paths,
            environment,
        )
        require(
            final_native_dependency_resolution == native_dependency_resolution,
            "native dependency resolution changed during the audit",
        )

        final_markers = sorted(
            candidate
            for candidate in metadata_dir.iterdir()
            if MARKER_RE.fullmatch(candidate.name)
            and int(MARKER_RE.fullmatch(candidate.name).group("epoch")) > after_epoch
        )
        require(
            final_markers == [marker_source],
            "completion-marker set changed during audit",
        )
        revalidate_absent_path(
            adjacent_apksigner_jar, "higher-priority adjacent apksigner JAR"
        )
        revalidate_absent_path(
            python_stdlib_archive_absence,
            "isolated Python standard-library ZIP",
        )
        for record in source_records:
            revalidate_source_file(record)
        revalidate_tree_metadata(java_symlinks, java_directories)
        revalidate_tree_metadata(signer_java_symlinks, signer_java_directories)
        revalidate_tree_metadata(python_symlinks, python_directories)
        require(
            hashlib.sha256(retained_tree_manifest(java_home_retained)).hexdigest()
            == java_tree_sha,
            "retained Java tree changed before PASS",
        )
        require(
            hashlib.sha256(retained_tree_manifest(signer_java_home_retained)).hexdigest()
            == signer_java_tree_sha,
            "retained signer Java tree changed before PASS",
        )
        require(
            hashlib.sha256(retained_tree_manifest(python_stdlib_retained)).hexdigest()
            == python_tree_sha,
            "retained Python standard-library tree changed before PASS",
        )
        result["source_file_attestation_count"] = len(source_records)
        result["source_symlink_attestation_count"] = (
            len(java_symlinks) + len(signer_java_symlinks) + len(python_symlinks)
        )
        result["source_directory_attestation_count"] = (
            len(java_directories)
            + len(signer_java_directories)
            + len(python_directories)
        )
        result["status"] = "PASS_AUDIT_ONLY_NOT_FOR_IN_PLACE_FLASH"
        result["audit_completed_epoch"] = int(time.time())
        result["external_root_checksum"] = str(root_checksum_path)
        result_bytes = (
            json.dumps(result, indent=2, sort_keys=True) + "\n"
        ).encode("utf-8")
        status_bytes = (result["status"] + "\n").encode("ascii")
        replace_fsynced(
            evidence_dir / "audit-result.json",
            result_bytes,
        )
        replace_fsynced(
            evidence_dir / "status.txt", status_bytes
        )
        manifest_bytes = evidence_manifest(evidence_dir)
        verify_retained_records_in_manifest(
            source_records, evidence_dir, manifest_bytes
        )
        write_new_fsynced(evidence_dir / "evidence-sha256sums.txt", manifest_bytes)
        fsync_dir(evidence_dir)
        root_content = external_root_content(
            evidence_dir, logs_root, manifest_bytes
        )
        require(
            not os.path.lexists(root_checksum_path),
            "external root appeared before evidence verification",
        )
        verify_finalized_evidence(
            evidence_dir,
            root_checksum_path,
            manifest_bytes,
            result_bytes,
            status_bytes,
            source_records,
        )
        make_read_only(evidence_dir)
        verify_finalized_evidence(
            evidence_dir,
            root_checksum_path,
            manifest_bytes,
            result_bytes,
            status_bytes,
            source_records,
        )
        fsync_dir(evidence_dir)
        fsync_dir(evidence_dir.parent)
        require(
            not os.path.lexists(root_checksum_path),
            "external root appeared before commit",
        )
        publish_external_root(root_checksum_path, root_content)
        return result, evidence_dir, root_checksum_path
    except BaseException as exc:
        cleanup_failure: BaseException | None = None
        try:
            remove_external_root_durably(root_checksum_path)
        except BaseException as cleanup_exc:
            cleanup_failure = cleanup_exc
        prepare_failure_evidence(evidence_dir)
        try:
            (evidence_dir / "evidence-sha256sums.txt").unlink(missing_ok=True)
            result["status"] = "FAILED"
            result["failure"] = str(exc)
            result["audit_completed_epoch"] = int(time.time())
            replace_fsynced(
                evidence_dir / "audit-result.json",
                (json.dumps(result, indent=2, sort_keys=True) + "\n").encode("utf-8"),
            )
            replace_fsynced(
                evidence_dir / "status.txt", f"FAILED: {exc}\n".encode("utf-8")
            )
            fsync_dir(evidence_dir)
        except OSError:
            pass
        if cleanup_failure is not None:
            raise AuditError(
                "audit failed and a possible external completion anchor could "
                f"not be durably removed: {cleanup_failure}"
            ) from exc
        raise


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print(f"Usage: {Path(sys.argv[0]).name} <audit-config.json>", file=sys.stderr)
        return 2
    try:
        result, evidence_dir, root_checksum = audit(Path(argv[0]).absolute())
    except AuditError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(result["status"])
    print(f"Evidence: {evidence_dir}")
    print(f"External root checksum: {root_checksum}")
    print(f"Image SHA256: {result['image_sha256']}")
    print(f"Target-files SHA256: {result['target_files_sha256']}")
    print(f"Build log SHA256: {result['build_log_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
