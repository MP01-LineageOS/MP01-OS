#!/usr/bin/env python3

from __future__ import annotations

import copy
import importlib.util
import json
import os
from pathlib import Path
import stat
import sys
import tempfile
import time
import unittest
from unittest import mock
import zipfile


SPEC = importlib.util.spec_from_file_location(
    "mp01_artifact_audit", Path(__file__).with_name("audit.py")
)
assert SPEC is not None and SPEC.loader is not None
AUDIT = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = AUDIT
SPEC.loader.exec_module(AUDIT)


def evidence_fixture() -> bytes:
    values = {
        "format": "mp01-signer-compatibility-evidence-v1",
        "mode": "test-key-audit",
        "comparison_status": "INCOMPATIBLE",
        "flash_disposition": "NOT_FOR_IN_PLACE_FLASH",
        "target_files_sha256": "1" * 64,
        "expected_manifest_sha256": "2" * 64,
        "expected_baseline_archive_sha256": "3" * 64,
        "expected_baseline_image_sha256": "4" * 64,
        "expected_baseline_apk_inventory_sha256": "5" * 64,
        "expected_baseline_apex_inventory_sha256": "6" * 64,
        "expected_apk_coverage": "complete",
        "expected_apex_coverage": "complete",
        "actual_manifest_sha256": "7" * 64,
        "actual_apk_count": "221",
        "actual_apex_count": "33",
        "incompatibility_count": "1",
        "warning_count": "1",
        "apksigner_execution": "direct_java_jar",
        "apksigner_java_sha256": "8" * 64,
        "apksigner_jar_sha256": "9" * 64,
        "issue.0001": "incompatibility\tapex\tcom.example.apex\tchanged\told\tnew",
        "issue.0002": "warning\tapk\tcom.example.apk\tunconstrained\t-\tnew",
    }
    return ("\n".join(f"{key}={value}" for key, value in values.items()) + "\n").encode("ascii")


class StableCopyTests(unittest.TestCase):
    def test_revalidation_detects_source_mutation(self) -> None:
        with tempfile.TemporaryDirectory(dir="/tmp") as temporary:
            root = Path(temporary)
            source = root / "source"
            destination = root / "retained"
            source.write_bytes(b"stable input")
            records = []
            record = AUDIT.copy_stable_file(
                source.resolve(), destination.resolve(), "fixture", records
            )
            AUDIT.revalidate_source_file(record)
            source.write_bytes(b"changed input")
            with self.assertRaises(AUDIT.AuditError):
                AUDIT.revalidate_source_file(record)

    def test_absence_revalidation_detects_new_search_path(self) -> None:
        with tempfile.TemporaryDirectory(dir="/tmp") as temporary:
            root = Path(temporary).resolve()
            candidate = root / "python314.zip"
            record = AUDIT.attest_absent_path(candidate, "fixture search path")
            AUDIT.revalidate_absent_path(record, "fixture search path")
            candidate.write_bytes(b"unexpected archive")
            with self.assertRaises(AUDIT.AuditError):
                AUDIT.revalidate_absent_path(record, "fixture search path")

    def test_revalidation_rejects_retained_symlink_replacement(self) -> None:
        with tempfile.TemporaryDirectory(dir="/tmp") as temporary:
            root = Path(temporary)
            source = root / "source"
            destination = root / "retained"
            source.write_bytes(b"same bytes")
            records = []
            record = AUDIT.copy_stable_file(
                source.resolve(), destination.resolve(), "fixture", records
            )
            destination.unlink()
            os.symlink(source, destination)
            with self.assertRaises(AUDIT.AuditError):
                AUDIT.revalidate_source_file(record)

    def test_revalidation_rejects_same_byte_path_replacement_during_hash(self) -> None:
        with tempfile.TemporaryDirectory(dir="/tmp") as temporary:
            root = Path(temporary)
            for target_name in ("source", "retained"):
                case = root / target_name
                case.mkdir()
                source = case / "source"
                destination = case / "retained"
                source.write_bytes(b"same bytes")
                records = []
                record = AUDIT.copy_stable_file(
                    source.resolve(), destination.resolve(), "fixture", records
                )
                target = getattr(record, target_name)
                replacement = case / f"{target_name}.replacement"
                replacement.write_bytes(target.read_bytes())
                replacement.chmod(stat.S_IMODE(target.lstat().st_mode))
                replaced = False

                def replace_after_open(path: Path) -> None:
                    nonlocal replaced
                    if path == target:
                        os.replace(replacement, target)
                        replaced = True

                with self.subTest(target=target_name), self.assertRaises(
                    AUDIT.AuditError
                ):
                    AUDIT.revalidate_source_file(record, replace_after_open)
                self.assertTrue(replaced)


class EvidenceManifestFinalizationTests(unittest.TestCase):
    def make_finalized_fixture(self, root: Path):
        source = root / "source"
        source.write_bytes(b"retained source bytes\n")
        evidence = root / "evidence"
        evidence.mkdir()
        records = []
        record = AUDIT.copy_stable_file(
            source.resolve(),
            (evidence / "retained-source").resolve(),
            "retained fixture",
            records,
        )
        root_checksum = root / "evidence.root.sha256"
        result = {
            "external_root_checksum": str(root_checksum),
            "status": "PASS_AUDIT_ONLY_NOT_FOR_IN_PLACE_FLASH",
        }
        result_bytes = (
            json.dumps(result, indent=2, sort_keys=True) + "\n"
        ).encode("utf-8")
        status_bytes = (result["status"] + "\n").encode("ascii")
        AUDIT.write_new_fsynced(evidence / "audit-result.json", result_bytes)
        AUDIT.write_new_fsynced(evidence / "status.txt", status_bytes)
        manifest_bytes = AUDIT.evidence_manifest(evidence)
        AUDIT.write_new_fsynced(
            evidence / "evidence-sha256sums.txt", manifest_bytes
        )
        relative_manifest = (
            evidence / "evidence-sha256sums.txt"
        ).relative_to(root).as_posix()
        root_content = (
            "format=mp01-evidence-root-v1\n"
            f"evidence_manifest={relative_manifest}\n"
            f"evidence_manifest_sha256={AUDIT.hashlib.sha256(manifest_bytes).hexdigest()}\n"
        ).encode("ascii")
        return (
            evidence,
            root_checksum,
            manifest_bytes,
            root_content,
            result_bytes,
            status_bytes,
            records,
            record,
        )

    def test_manifest_rejects_symlink_replacement_during_hash(self) -> None:
        with tempfile.TemporaryDirectory(dir="/tmp") as temporary:
            root = Path(temporary)
            evidence = root / "evidence"
            evidence.mkdir()
            target = evidence / "target"
            target.write_bytes(b"original\n")
            replacement = root / "replacement"
            replacement.write_bytes(b"replacement\n")

            def replace_with_symlink(path: Path) -> None:
                if path == target:
                    path.unlink()
                    os.symlink(replacement, path)

            with self.assertRaises(AUDIT.AuditError):
                AUDIT.evidence_manifest(evidence, replace_with_symlink)

    def test_manifest_rejects_mutation_during_hash(self) -> None:
        with tempfile.TemporaryDirectory(dir="/tmp") as temporary:
            root = Path(temporary)
            evidence = root / "evidence"
            evidence.mkdir()
            target = evidence / "target"
            target.write_bytes(b"original\n")

            def mutate(path: Path) -> None:
                if path == target:
                    path.write_bytes(b"mutated!\n")

            with self.assertRaises(AUDIT.AuditError):
                AUDIT.evidence_manifest(evidence, mutate)

    def test_retained_record_mismatch_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory(dir="/tmp") as temporary:
            fixture = self.make_finalized_fixture(Path(temporary))
            evidence, _, manifest_bytes, *_, record = fixture
            bad_record = AUDIT.dataclasses.replace(record, sha256="0" * 64)
            with self.assertRaises(AUDIT.AuditError):
                AUDIT.verify_retained_records_in_manifest(
                    [bad_record], evidence, manifest_bytes
                )

    def test_post_write_manifest_and_root_are_verified(self) -> None:
        with tempfile.TemporaryDirectory(dir="/tmp") as temporary:
            root = Path(temporary)
            fixture = self.make_finalized_fixture(root)
            (
                evidence,
                root_checksum,
                manifest_bytes,
                root_content,
                result_bytes,
                status_bytes,
                records,
                _,
            ) = fixture
            self.assertFalse(os.path.lexists(root_checksum))
            AUDIT.verify_finalized_evidence(
                evidence,
                root_checksum,
                manifest_bytes,
                result_bytes,
                status_bytes,
                records,
            )
            self.assertFalse(os.path.lexists(root_checksum))
            AUDIT.publish_external_root(root_checksum, root_content)
            self.assertEqual(root_checksum.read_bytes(), root_content)
            AUDIT.remove_external_root_durably(root_checksum)
            self.assertFalse(os.path.lexists(root_checksum))

    def test_failure_before_commit_leaves_anchor_absent(self) -> None:
        with tempfile.TemporaryDirectory(dir="/tmp") as temporary:
            root = Path(temporary)
            fixture = self.make_finalized_fixture(root)
            (
                evidence,
                root_checksum,
                manifest_bytes,
                _,
                result_bytes,
                status_bytes,
                records,
                _,
            ) = fixture
            (evidence / "evidence-sha256sums.txt").write_bytes(
                manifest_bytes + b"unexpected\n"
            )
            with self.assertRaises(AUDIT.AuditError):
                AUDIT.verify_finalized_evidence(
                    evidence,
                    root_checksum,
                    manifest_bytes,
                    result_bytes,
                    status_bytes,
                    records,
                )
            self.assertFalse(os.path.lexists(root_checksum))

    def test_root_creation_and_readback_failures_remove_anchor_durably(self) -> None:
        with tempfile.TemporaryDirectory(dir="/tmp") as temporary:
            root = Path(temporary)
            root_checksum = root / "evidence.root.sha256"
            root_content = b"format=mp01-evidence-root-v1\n"

            def fail_after_partial_create(path: Path, content: bytes, mode: int) -> None:
                path.write_bytes(content[:8])
                raise OSError("injected root creation failure")

            with mock.patch.object(
                AUDIT, "write_new_fsynced", side_effect=fail_after_partial_create
            ), self.assertRaises(AUDIT.AuditError):
                AUDIT.publish_external_root(root_checksum, root_content)
            self.assertFalse(os.path.lexists(root_checksum))

            def corrupt_after_create(path: Path) -> None:
                os.chmod(path, 0o600)
                path.write_bytes(b"corrupt root\n")

            with mock.patch.object(
                AUDIT, "fsync_dir", wraps=AUDIT.fsync_dir
            ) as fsync_mock, self.assertRaises(AUDIT.AuditError):
                AUDIT.publish_external_root(
                    root_checksum, root_content, corrupt_after_create
                )
            self.assertFalse(os.path.lexists(root_checksum))
            parent_fsyncs = [
                call for call in fsync_mock.call_args_list if call.args == (root,)
            ]
            self.assertGreaterEqual(len(parent_fsyncs), 3)

            AUDIT.write_new_fsynced(root_checksum, root_content, 0o400)
            with mock.patch.object(
                Path,
                "unlink",
                side_effect=PermissionError("injected unlink failure"),
            ), self.assertRaises(AUDIT.AuditError):
                AUDIT.remove_external_root_durably(root_checksum)
            self.assertEqual(
                root_checksum.read_bytes(), b"INVALID_MP01_EVIDENCE_ROOT\n"
            )
            root_checksum.unlink()


class BuildLogTests(unittest.TestCase):
    HARNESS_SHA256 = "1" * 64
    HELPER_SHA256 = "2" * 64
    GSI_COMMIT = "3" * 40
    GSI_TREE = "4" * 40

    def make_contract(self, root: Path, mutate=None, start_content=None):
        after_epoch = int(time.time()) - 10
        build_log = root / "formal.log"
        start_record = Path(f"{build_log}.start-epoch")
        build_log.touch()
        start_record.write_bytes(
            start_content
            if start_content is not None
            else f"{after_epoch}\n".encode("ascii")
        )
        log_stat = build_log.stat()
        start_stat = start_record.stat()
        values = (
            AUDIT.FORMAL_BUILD_LOG_FORMAT_VERSION,
            self.HARNESS_SHA256,
            self.HELPER_SHA256,
            self.GSI_COMMIT,
            self.GSI_TREE,
            str(after_epoch),
            str(start_stat.st_dev),
            str(start_stat.st_ino),
            str(build_log),
            str(log_stat.st_dev),
            str(log_stat.st_ino),
            "test-key-audit",
            "1",
        )
        parts = {
            "header": [
                f"{key}={value}\n".encode("ascii")
                for key, value in zip(
                    AUDIT.FORMAL_BUILD_LOG_HEADER_KEYS, values, strict=True
                )
            ],
            "body": [
                b"formal build output\n",
                AUDIT.BUILD_LOG_SUCCESS_LINE,
                b"Image file: /tmp/system.img\n",
                AUDIT.BUILD_LOG_SIGNING_LINE,
            ],
            "footer": list(AUDIT.FORMAL_BUILD_LOG_FOOTER_LINES),
            "trailing": [],
        }
        if mutate is not None:
            mutate(parts)
        build_log.write_bytes(
            b"".join(
                (*parts["header"], *parts["body"], *parts["footer"], *parts["trailing"])
            )
        )
        evidence = root / "evidence"
        evidence.mkdir()
        records = []
        log_record = AUDIT.copy_stable_file(
            build_log.resolve(), evidence / "build.log", "build log", records
        )
        start_record_copy = AUDIT.copy_stable_file(
            start_record.resolve(),
            evidence / "build.start-epoch",
            "formal build start record",
            records,
        )
        return {
            "after_epoch": after_epoch,
            "build_log": build_log,
            "evidence": evidence,
            "log_record": log_record,
            "records": records,
            "start_record": start_record,
            "start_record_copy": start_record_copy,
        }

    def validate_contract(self, fixture, expected_sha256=None):
        record = fixture["log_record"]
        return AUDIT.validate_retained_build_log(
            record,
            fixture["start_record_copy"],
            expected_sha256 or record.sha256,
            fixture["after_epoch"],
            self.HARNESS_SHA256,
            self.HELPER_SHA256,
            self.GSI_COMMIT,
            self.GSI_TREE,
        )

    def test_contract_v1_positive_binds_sources_and_retained_inputs(self) -> None:
        with tempfile.TemporaryDirectory(dir="/tmp") as temporary:
            fixture = self.make_contract(Path(temporary))
            config = {"build_log": str(fixture["build_log"])}
            validated = AUDIT.validate_build_log_source(
                config, fixture["after_epoch"]
            )
            self.assertEqual(validated[0], fixture["build_log"])
            self.assertEqual(validated[1], fixture["log_record"].signature)
            self.assertEqual(validated[2], fixture["start_record"])
            self.assertEqual(validated[3], fixture["start_record_copy"].signature)
            contract = self.validate_contract(fixture)
            self.assertEqual(1, contract["format_version"])
            self.assertEqual(self.GSI_COMMIT, contract["gsi_commit"])
            self.assertEqual(self.GSI_TREE, contract["gsi_tree"])
            self.assertEqual(
                fixture["log_record"].signature.inode,
                contract["log_source_st_ino"],
            )
            manifest = AUDIT.evidence_manifest(fixture["evidence"])
            AUDIT.verify_retained_records_in_manifest(
                fixture["records"], fixture["evidence"], manifest
            )
            for record in fixture["records"]:
                AUDIT.revalidate_source_file(record)

    def test_every_header_field_order_and_reserved_duplicate_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory(dir="/tmp") as temporary:
            root = Path(temporary)
            case_index = 0
            mutators = []
            for header_index in range(len(AUDIT.FORMAL_BUILD_LOG_HEADER_KEYS)):
                def wrong_header(parts, index=header_index):
                    key = AUDIT.FORMAL_BUILD_LOG_HEADER_KEYS[index].encode("ascii")
                    parts["header"][index] = key + b"=wrong\n"

                mutators.append(wrong_header)
            mutators.append(
                lambda parts: parts["header"].__setitem__(
                    slice(0, 2), [parts["header"][1], parts["header"][0]]
                )
            )
            for key in (
                *AUDIT.FORMAL_BUILD_LOG_HEADER_KEYS,
                *AUDIT.FORMAL_BUILD_LOG_FOOTER_KEYS,
            ):
                mutators.append(
                    lambda parts, reserved=key: parts["body"].insert(
                        -1, f"{reserved}=0\n".encode("ascii")
                    )
                )
            for mutate in mutators:
                case = root / f"case-{case_index}"
                case.mkdir()
                case_index += 1
                fixture = self.make_contract(case, mutate)
                with self.subTest(case=case.name), self.assertRaises(AUDIT.AuditError):
                    self.validate_contract(fixture)

    def test_body_footer_hash_and_start_record_fail_closed(self) -> None:
        def remove_success(parts):
            parts["body"].remove(AUDIT.BUILD_LOG_SUCCESS_LINE)

        def duplicate_success(parts):
            parts["body"].insert(1, AUDIT.BUILD_LOG_SUCCESS_LINE)

        def wrong_signer(parts):
            parts["body"][-1] = AUDIT.BUILD_LOG_RELEASE_SIGNING_LINE

        def duplicate_signer(parts):
            parts["body"].insert(-1, AUDIT.BUILD_LOG_SIGNING_LINE)

        def signer_not_last(parts):
            parts["body"].append(b"output after signer\n")

        mutators = [
            remove_success,
            duplicate_success,
            wrong_signer,
            duplicate_signer,
            signer_not_last,
            lambda parts: parts["footer"].__setitem__(0, b"MP01_BUILD_EXIT_STATUS=1\n"),
            lambda parts: parts["footer"].__setitem__(slice(0, 2), list(reversed(parts["footer"][:2]))),
            lambda parts: parts["footer"].pop(),
            lambda parts: parts["footer"].append(parts["footer"][-1]),
            lambda parts: parts["trailing"].append(b"trailing\n"),
            lambda parts: parts["body"].insert(-1, b"x" * (1024 * 1024 + 1) + b"\n"),
            lambda parts: parts["body"].insert(-1, b"unterminated"),
        ]
        with tempfile.TemporaryDirectory(dir="/tmp") as temporary:
            root = Path(temporary)
            for index, mutate in enumerate(mutators):
                case = root / f"case-{index}"
                case.mkdir()
                fixture = self.make_contract(case, mutate)
                with self.subTest(index=index), self.assertRaises(AUDIT.AuditError):
                    self.validate_contract(fixture)
            valid = root / "valid"
            valid.mkdir()
            fixture = self.make_contract(valid)
            with self.assertRaises(AUDIT.AuditError):
                self.validate_contract(fixture, "0" * 64)
            invalid_start = root / "invalid-start"
            invalid_start.mkdir()
            fixture = self.make_contract(invalid_start, start_content=b"1\n")
            with self.assertRaises(AUDIT.AuditError):
                self.validate_contract(fixture)

    def test_missing_staging_and_unsafe_log_config_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory(dir="/tmp") as temporary:
            root = Path(temporary)
            valid_root = root / "valid"
            valid_root.mkdir()
            fixture = self.make_contract(valid_root)
            after_epoch = fixture["after_epoch"]
            build_log = fixture["build_log"]
            stale = root / "stale.log"
            stale.write_bytes(b"old build\n")
            os.utime(stale, ns=((after_epoch - 1) * 10**9,) * 2)
            linked = root / "linked.log"
            os.symlink(build_log, linked)
            empty = root / "empty.log"
            empty.touch()
            boundary = root / "boundary.log"
            boundary.write_bytes(b"boundary\n")
            os.utime(boundary, ns=(after_epoch * 10**9,) * 2)
            fifo = root / "fifo.log"
            os.mkfifo(fifo)
            no_start = root / "no-start.log"
            no_start.write_bytes(b"recent\n")
            staging = root / "formal.log.incomplete"
            staging.write_bytes(b"staging\n")
            (root / "subdir").mkdir()
            variants = (
                {},
                {"build_log": "relative.log"},
                {"build_log": str(root / "missing.log")},
                {"build_log": str(linked)},
                {"build_log": str(root / "subdir" / ".." / "no-start.log")},
                {"build_log": str(empty)},
                {"build_log": str(fifo)},
                {"build_log": str(boundary)},
                {"build_log": str(stale)},
                {"build_log": str(no_start)},
                {"build_log": str(staging)},
            )
            for variant in variants:
                with self.subTest(variant=variant), self.assertRaises(AUDIT.AuditError):
                    AUDIT.validate_build_log_source(variant, after_epoch)

    def test_log_and_start_record_substitution_after_copy_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory(dir="/tmp") as temporary:
            fixture = self.make_contract(Path(temporary))
            for record in fixture["records"]:
                replacement = record.source.with_name(record.source.name + ".replacement")
                replacement.write_bytes(record.source.read_bytes())
                os.replace(replacement, record.source)
                with self.subTest(label=record.label), self.assertRaises(AUDIT.AuditError):
                    AUDIT.revalidate_source_file(record)


class PathPolicyTests(unittest.TestCase):
    def make_config(self, root: Path) -> tuple[dict, Path]:
        for name in (
            "logs",
            "config",
            "images",
            "metadata",
            "target",
            "tools",
            "build",
        ):
            (root / name).mkdir()
        target = root / "target" / "target.zip"
        tool = root / "tools" / "tool"
        build_log = root / "build" / "build.log"
        target.write_bytes(b"target")
        tool.write_bytes(b"tool")
        build_log.write_bytes(b"build log")
        config_path = root / "config" / "audit.json"
        config_path.write_text("{}\n")
        config = {
            "logs_root": str(root / "logs"),
            "evidence_dir": str(root / "logs" / "evidence"),
            "image_dir": str(root / "images"),
            "metadata_dir": str(root / "metadata"),
            "target_files": str(target),
            "build_log": str(build_log),
            "paths": {"fixture": str(tool)},
        }
        return config, config_path

    def test_valid_strict_descendant(self) -> None:
        with tempfile.TemporaryDirectory(dir="/tmp") as temporary:
            config, config_path = self.make_config(Path(temporary))
            logs, evidence, anchor = AUDIT.validate_evidence_location(config, config_path)
            self.assertEqual(evidence.parent, logs)
            self.assertEqual(anchor.parent, logs)

    def test_symlinked_evidence_ancestor_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory(dir="/tmp") as temporary:
            root = Path(temporary)
            config, config_path = self.make_config(root)
            (root / "logs" / "real").mkdir()
            os.symlink(root / "logs" / "real", root / "logs" / "linked")
            config["evidence_dir"] = str(root / "logs" / "linked" / "evidence")
            with self.assertRaises(AUDIT.AuditError):
                AUDIT.validate_evidence_location(config, config_path)

    def test_input_overlap_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory(dir="/tmp") as temporary:
            root = Path(temporary)
            config, config_path = self.make_config(root)
            config["logs_root"] = str(root)
            config["evidence_dir"] = str(root / "images" / "evidence")
            with self.assertRaises(AUDIT.AuditError):
                AUDIT.validate_evidence_location(config, config_path)

    def test_missing_build_log_and_build_log_overlap_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory(dir="/tmp") as temporary:
            root = Path(temporary)
            config, config_path = self.make_config(root)
            missing = copy.deepcopy(config)
            del missing["build_log"]
            with self.assertRaises(AUDIT.AuditError):
                AUDIT.validate_evidence_location(missing, config_path)

            config["logs_root"] = str(root)
            config["evidence_dir"] = str(root / "build" / "evidence")
            with self.assertRaises(AUDIT.AuditError):
                AUDIT.validate_evidence_location(config, config_path)


class ManifestUriTests(unittest.TestCase):
    def test_case_and_encoding_variants_are_rejected(self) -> None:
        variants = (
            "FiLe:///tmp/source",
            "f%69le:///tmp/source",
            "f%2569le%253A///tmp/source",
            "file%252525253A///tmp/source",
            "  FILE : ///tmp/source",
            "/home/user/source",
            "../source",
            "",
            "git://example.com/source",
        )
        for value in variants:
            with self.subTest(value=value), self.assertRaises(AUDIT.AuditError):
                AUDIT.reject_local_remote_fetch(value, "fixture")

    def test_xml_character_reference_is_decoded_then_rejected(self) -> None:
        root = AUDIT.ET.fromstring(
            '<manifest><remote name="local" fetch="FiLe&#58;///tmp/source"/></manifest>'
        )
        fetch = root.find("remote").get("fetch")
        with self.assertRaises(AUDIT.AuditError):
            AUDIT.reject_local_remote_fetch(fetch, "fixture")

    def test_excessive_nested_decoding_fails_closed(self) -> None:
        value = "file%3A///tmp/source"
        for _ in range(33):
            value = value.replace("%", "%25")
        with self.assertRaises(AUDIT.AuditError):
            AUDIT.reject_local_remote_fetch(value, "fixture")


class ZipEntryTests(unittest.TestCase):
    def test_regular_nonempty_entry_passes(self) -> None:
        entry = zipfile.ZipInfo("file")
        entry.file_size = 1
        entry.external_attr = (stat.S_IFREG | 0o644) << 16
        AUDIT.require_regular_zip_entry(entry, "fixture")

    def test_symlink_and_empty_entry_fail(self) -> None:
        symlink = zipfile.ZipInfo("link")
        symlink.file_size = 3
        symlink.external_attr = (stat.S_IFLNK | 0o777) << 16
        empty = zipfile.ZipInfo("empty")
        empty.file_size = 0
        empty.external_attr = (stat.S_IFREG | 0o644) << 16
        for entry in (symlink, empty):
            with self.subTest(entry=entry.filename), self.assertRaises(AUDIT.AuditError):
                AUDIT.require_regular_zip_entry(entry, entry.filename)


class SignerSchemaTests(unittest.TestCase):
    def test_complete_schema_passes(self) -> None:
        values, issues = AUDIT.parse_signer_evidence(evidence_fixture())
        self.assertEqual(values["incompatibility_count"], "1")
        self.assertEqual([issue[0] for issue in issues], ["incompatibility", "warning"])

    def test_gap_unknown_severity_and_bad_counts_fail(self) -> None:
        raw = evidence_fixture().decode("ascii")
        variants = (
            raw.replace("issue.0002=", "issue.0003="),
            raw.replace("warning\tapk", "notice\tapk"),
            raw.replace("warning_count=1", "warning_count=0"),
            raw.replace("comparison_status=INCOMPATIBLE", "comparison_status=COMPATIBLE_SIGNER_IDENTITIES"),
            raw.replace("apksigner_execution=direct_java_jar", "apksigner_execution=launcher"),
            raw.replace("apksigner_java_sha256=" + "8" * 64 + "\n", ""),
        )
        for value in variants:
            with self.subTest(value=value[-100:]), self.assertRaises(AUDIT.AuditError):
                AUDIT.parse_signer_evidence(value.encode("ascii"))

    def test_actual_manifest_counts_are_schema_checked(self) -> None:
        manifest = (
            "# mp01-public-signer-manifest-v1\n"
            "kind\tpackage\tsource_path\tformat\tversion_code\tsigner_cert_sha256\tcontainer_cert_sha256\tpayload_pubkey_sha256\n"
            "apk\tapp.one\tSYSTEM/app/One.apk\tapk\t1\t-\t-\t-\n"
            "apex\tapex.one\tSYSTEM/apex/One.apex\tapex\t1\t-\t-\t-\n"
        ).encode("ascii")
        self.assertEqual(AUDIT.signer_manifest_counts(manifest), (1, 1))
        with self.assertRaises(AUDIT.AuditError):
            AUDIT.signer_manifest_counts(manifest.replace(b"apex\t", b"other\t"))


class EnvironmentAndContractTests(unittest.TestCase):
    def test_environment_is_exact_and_minimal(self) -> None:
        environment = AUDIT.command_environment(
            Path("/tmp/evidence"), Path("/tmp/java"), Path("/tmp/tools")
        )
        self.assertEqual(
            set(environment),
            {
                "HOME",
                "JAVA_HOME",
                "LANG",
                "LC_ALL",
                "OPENSSL_CONF",
                "OPENSSL_MODULES",
                "PATH",
                "TMPDIR",
                "TZ",
            },
        )

    def test_java_properties_are_evidence_confined(self) -> None:
        self.assertEqual(
            AUDIT.java_system_properties(Path("/tmp/evidence")),
            [
                "-Duser.home=/tmp/evidence/home",
                "-Djava.io.tmpdir=/tmp/evidence/tmp",
            ],
        )

    def test_example_contract_has_exact_path_keys(self) -> None:
        config = json.loads(Path(__file__).with_name("config.example.json").read_text())
        self.assertEqual(set(config["paths"]), AUDIT.REQUIRED_PATH_KEYS)
        self.assertEqual(
            set(config["expected"]["tool_sha256"]),
            AUDIT.REQUIRED_PATH_KEYS
            - {
                "android_host_out",
                "java_home",
                "signer_java_home",
                "python_stdlib",
            },
        )
        self.assertFalse(
            set(AUDIT.MANDATORY_BUILD_INFO_KEYS) - set(config["expected"]["build_info"])
        )
        self.assertEqual(config["after_epoch"], 1784095155)
        self.assertEqual(
            config["build_log"],
            "/home/user/MP01-LineageOS/.android-build/logs/"
            "mp01-final-c88e03999276-20260715T055915Z-93cb550cc58a.log",
        )
        self.assertEqual(
            config["target_files"],
            "/home/user/MP01-LineageOS/.android-build/los23.2-microg/out/target/"
            "product/generic_arm64/obj/PACKAGING/target_files_intermediates/"
            "lineage_arm64_bmN4-target_files.zip",
        )
        self.assertEqual(
            config["expected"]["build_info"]["Android OUT_DIR interface"],
            "out",
        )
        self.assertEqual(
            config["expected"]["build_info"]["Android product output name"],
            "generic_arm64",
        )
        self.assertEqual(
            config["paths"]["vendor_lineage_no_kernel_patch"],
            "/home/user/MP01-LineageOS/MP01-LineageGSI/patches/personal/"
            "platform_vendor_lineage/"
            "0003-build-handle-generated-headers-for-no-kernel-targets.patch",
        )
        self.assertEqual(
            config["paths"]["no_kernel_header_policy_verifier"],
            "/home/user/MP01-LineageOS/.android-build/los23.2-microg/.mp01/"
            "verify-no-kernel-header-policy.py",
        )
        no_kernel_build_info = {
            "vendor/lineage base commit": "7f67df02757caeecd806c290f7914612d3d449f6",
            "vendor/lineage base tree": "85f81c3aa61d9b59473c01350ed595f6655471a9",
            "vendor/lineage prepared commit": "b085bb0f60ea6409d121f83b870f506f241ed653",
            "vendor/lineage prepared tree": "1620732b96199fb17c0add4302124a621c5c8be4",
            "vendor/lineage no-kernel header patch": (
                "patches/personal/platform_vendor_lineage/"
                "0003-build-handle-generated-headers-for-no-kernel-targets.patch"
            ),
            "vendor/lineage no-kernel header patch SHA256": (
                "7aeb8693d713baa4c024a5d48fa15d6ccd19ac1a0354701eadefdf45c112cc4a"
            ),
            "No-kernel header policy verifier": (
                "/home/user/MP01-LineageOS/.android-build/los23.2-microg/.mp01/"
                "verify-no-kernel-header-policy.py"
            ),
            "No-kernel header policy verifier SHA256": (
                "24822db54c1ae98f9963666b214be311c64d49f8e3e32ee80c32ca64ad8aff45"
            ),
            "Android TARGET_NO_KERNEL": "true",
        }
        for key, value in no_kernel_build_info.items():
            self.assertEqual(config["expected"]["build_info"][key], value)
        self.assertEqual(
            config["expected"]["tool_sha256"]["vendor_lineage_no_kernel_patch"],
            "7aeb8693d713baa4c024a5d48fa15d6ccd19ac1a0354701eadefdf45c112cc4a",
        )
        self.assertEqual(
            config["expected"]["tool_sha256"]["no_kernel_header_policy_verifier"],
            "24822db54c1ae98f9963666b214be311c64d49f8e3e32ee80c32ca64ad8aff45",
        )
        self.assertEqual(
            config["paths"]["partner_gms_presigned_apk_patch"],
            "/home/user/MP01-LineageOS/MP01-LineageGSI/patches/personal/"
            "platform_vendor_partner_gms/"
            "0001-build-preserve-presigned-partner-APK-bytes.patch",
        )
        self.assertEqual(
            config["paths"]["presigned_partner_apk_policy_verifier"],
            "/home/user/MP01-LineageOS/.android-build/los23.2-microg/.mp01/"
            "verify-presigned-partner-apk-policy.py",
        )
        self.assertEqual(
            config["paths"]["partner_zipalign"],
            "/home/user/MP01-LineageOS/.android-build/los23.2-microg/out/host/"
            "linux-x86/bin/zipalign",
        )
        self.assertEqual(
            config["paths"]["runtime_libcxx"],
            "/home/user/MP01-LineageOS/.android-build/los23.2-microg/out/host/"
            "linux-x86/lib64/libc++.so",
        )
        self.assertEqual(
            config["expected"]["partner_apk_sha256"],
            {
                "GmsCore": (
                    "52597e77fd25fdd347574d0457ed1936a4b9561cf4c8d34e7ac8dd8191dfd4b9"
                ),
                "FakeStore": (
                    "a973e0235a2829773a4faf36d235d5f703d1c04a2adff674ebaa535a2e78f937"
                ),
                "GsfProxy": (
                    "86891b174301f06a1c84187b545a0a2a57044c6b768f3e84e865908743349692"
                ),
                "FDroid": (
                    "985f5181d48bb6bafd54083a048b391271e0ab28385881cc41294fb01a222762"
                ),
                "FDroidPrivilegedExtension": (
                    "1008525a17b4f6a93ac690f9c50dcb675b6bebf53d2879dbc98ba65a1cb2e28d"
                ),
            },
        )
        partner_build_info = {
            "vendor/partner_gms base commit": (
                "4b3b48033245800142045ce78038166f8aff6b01"
            ),
            "vendor/partner_gms base tree": (
                "3c554b8fabffd2bdd0727aac770e403d9fec0505"
            ),
            "vendor/partner_gms prepared commit": (
                "67e492737184fe9584750e07ad4c0ecfb40af67e"
            ),
            "vendor/partner_gms prepared tree": (
                "06afb50166f27672b02c7b168b24de0bf30f8f21"
            ),
            "vendor/partner_gms presigned APK patch": (
                "patches/personal/platform_vendor_partner_gms/"
                "0001-build-preserve-presigned-partner-APK-bytes.patch"
            ),
            "vendor/partner_gms presigned APK patch SHA256": (
                "146aa1a9307452217e087d818028bb158e8adf0a5a3a52e6bcaebe0665e7a1bf"
            ),
            "Presigned partner APK policy verifier": (
                "/home/user/MP01-LineageOS/.android-build/los23.2-microg/.mp01/"
                "verify-presigned-partner-apk-policy.py"
            ),
            "Presigned partner APK policy verifier SHA256": (
                "ac198d84ad18824656024e014ce02d7d5865d6a7c47c857fa770344b9300b0bf"
            ),
            "Presigned partner APK byte preservation": "verified",
            "Presigned partner APK alignment": "verified",
        }
        for key, value in partner_build_info.items():
            self.assertEqual(config["expected"]["build_info"][key], value)
        self.assertEqual(
            config["expected"]["tool_sha256"]["partner_gms_presigned_apk_patch"],
            "146aa1a9307452217e087d818028bb158e8adf0a5a3a52e6bcaebe0665e7a1bf",
        )
        self.assertEqual(
            config["expected"]["tool_sha256"][
                "presigned_partner_apk_policy_verifier"
            ],
            "ac198d84ad18824656024e014ce02d7d5865d6a7c47c857fa770344b9300b0bf",
        )
        self.assertEqual(
            config["expected"]["tool_sha256"]["partner_zipalign"],
            "5bd0a7ac65cb4901058d9aaa49e88b905010338964c4e2ae00afdb39e5d8f2f8",
        )
        self.assertEqual(
            config["expected"]["tool_sha256"]["runtime_libcxx"],
            "aab89aa18f9bec8e01c632b4230f4544fb6128b5d3df7ce6971c52b8c77bb11c",
        )
        self.assertTrue(
            {entry for _, entry in AUDIT.PARTNER_APK_TARGETS}
            <= set(AUDIT.REQUIRED_TARGET_FILES)
        )
        partner_projects = [
            project
            for project in config["expected"]["custom_projects"]
            if project["path"] == "vendor/partner_gms"
        ]
        self.assertEqual(
            partner_projects,
            [
                {
                    "path": "vendor/partner_gms",
                    "name": "lineageos4microg/android_vendor_partner_gms",
                    "revision": "67e492737184fe9584750e07ad4c0ecfb40af67e",
                }
            ],
        )
        self.assertEqual(
            config["expected"]["build_info"]["Live MP01-LineageGSI commit"],
            "c88e039992760ada12f1df874453c2243d784862",
        )
        self.assertEqual(
            config["expected"]["build_info"]["Live MP01-LineageGSI tree"],
            "9d4bfca308b640e2b28f58f3502af40a7adf0c21",
        )
        self.assertEqual(
            config["paths"]["formal_build_harness"],
            "/home/user/MP01-LineageOS/MP01-LineageGSI/scripts/run-formal-build.sh",
        )
        self.assertEqual(
            config["paths"]["formal_build_log_helper"],
            "/home/user/MP01-LineageOS/MP01-LineageGSI/scripts/formal-build-log.py",
        )
        self.assertEqual(
            config["expected"]["tool_sha256"]["formal_build_harness"],
            "938cc2842ca860704f727cfbd4f890227ccb93d44387f64e6be3f704b3403204",
        )
        self.assertEqual(
            config["expected"]["tool_sha256"]["formal_build_log_helper"],
            "cf8a04c7d334caeb177750b7f2e9c2855e2835e231f9e45d21933619fd9ead07",
        )
        self.assertEqual(
            config["expected"]["audit_sha256"]["audit.py"],
            AUDIT.sha256_file(Path(__file__).with_name("audit.py")),
        )
        self.assertEqual(
            config["expected"]["audit_sha256"]["audit.sh"],
            AUDIT.sha256_file(Path(__file__).with_name("audit.sh")),
        )
        self.assertEqual(
            config["expected"]["build_log_sha256"],
            "87681b4c33c0d9584cb5067b223c2f92219544dfafd1147017511d49d0f25d3a",
        )
        self.assertEqual(
            config["expected"]["resolved_manifest_sha256"],
            "ece2fc1f579f006f9f7a71f1adcaae836ed27d7b6bceffc0f852b6984f8930a6",
        )
        self.assertEqual(
            config["expected"]["build_info"][
                "Prepared source manifest lock SHA256"
            ],
            config["expected"]["resolved_manifest_sha256"],
        )
        self.assertEqual(
            config["expected"]["build_info"]["Source input manifest lock"],
            AUDIT.SOURCE_INPUT_MANIFEST_LOCK,
        )
        self.assertEqual(
            config["expected"]["build_info"]["Source input manifest lock SHA256"],
            "a960a72bee3827697673c64c29ade2d61fa4ce09eeff1af28be8215dee50d5b9",
        )
        self.assertEqual(
            config["expected"]["build_info"]["Prepared source manifest lock"],
            AUDIT.PREPARED_SOURCE_MANIFEST_LOCK,
        )
        self.assertEqual(
            config["expected"]["tool_sha256"]["source_input_manifest_lock"],
            config["expected"]["build_info"]["Source input manifest lock SHA256"],
        )
        self.assertEqual(
            config["expected"]["tool_sha256"]["prepared_source_manifest_lock"],
            config["expected"]["resolved_manifest_sha256"],
        )
        self.assertEqual(
            config["expected"]["build_info"]["Resolved manifest SHA256"],
            config["expected"]["resolved_manifest_sha256"],
        )

    def test_partner_gms_prepared_manifest_revision_is_enforced(self) -> None:
        config = json.loads(Path(__file__).with_name("config.example.json").read_text())
        expected = copy.deepcopy(config["expected"])
        expected["project_count"] = len(expected["custom_projects"])
        root = AUDIT.ET.Element("manifest")
        AUDIT.ET.SubElement(
            root,
            "remote",
            name="mp01-local",
            fetch=expected["mp01_local_fetch"],
        )
        partner = None
        for project in expected["custom_projects"]:
            element = AUDIT.ET.SubElement(root, "project", **project)
            if project["path"] == "vendor/partner_gms":
                partner = element
        self.assertIsNotNone(partner)

        with tempfile.TemporaryDirectory(dir="/tmp") as temporary:
            manifest = Path(temporary) / "manifest.xml"
            AUDIT.ET.ElementTree(root).write(
                manifest, encoding="utf-8", xml_declaration=True
            )
            expected["resolved_manifest_sha256"] = AUDIT.sha256_file(manifest)
            AUDIT.verify_manifest(manifest, expected, {})

            partner.set("revision", "4b3b48033245800142045ce78038166f8aff6b01")
            AUDIT.ET.ElementTree(root).write(
                manifest, encoding="utf-8", xml_declaration=True
            )
            expected["resolved_manifest_sha256"] = AUDIT.sha256_file(manifest)
            with self.assertRaises(AUDIT.AuditError):
                AUDIT.verify_manifest(manifest, expected, {})


class ResolvedManifestIdentityTests(unittest.TestCase):
    @staticmethod
    def make_fixture() -> tuple[dict, AUDIT.ET.Element]:
        config = json.loads(Path(__file__).with_name("config.example.json").read_text())
        expected = copy.deepcopy(config["expected"])
        expected["project_count"] = len(expected["custom_projects"]) + 1

        root = AUDIT.ET.Element("manifest")
        AUDIT.ET.SubElement(
            root,
            "remote",
            name="aosp",
            fetch="https://android.googlesource.com/",
        )
        AUDIT.ET.SubElement(
            root,
            "remote",
            name="mp01-local",
            fetch=expected["mp01_local_fetch"],
        )
        for project in expected["custom_projects"]:
            AUDIT.ET.SubElement(root, "project", **project, remote="mp01-local")
        AUDIT.ET.SubElement(
            root,
            "project",
            name="platform/frameworks/base",
            path="frameworks/base",
            revision="1" * 40,
            remote="aosp",
        )
        return expected, root

    @staticmethod
    def write_manifest(root: AUDIT.ET.Element, path: Path) -> str:
        AUDIT.ET.ElementTree(root).write(
            path, encoding="utf-8", xml_declaration=True
        )
        return AUDIT.sha256_file(path)

    @staticmethod
    def non_custom_project(root: AUDIT.ET.Element) -> AUDIT.ET.Element:
        return next(
            project
            for project in root.findall("./project")
            if project.get("path") == "frameworks/base"
        )

    @staticmethod
    def aosp_remote(root: AUDIT.ET.Element) -> AUDIT.ET.Element:
        return next(
            remote
            for remote in root.findall("./remote")
            if remote.get("name") == "aosp"
        )

    def test_exact_full_manifest_digest_is_required_and_recorded(self) -> None:
        expected, root = self.make_fixture()
        with tempfile.TemporaryDirectory(dir="/tmp") as temporary:
            manifest = Path(temporary) / "manifest.xml"
            digest = self.write_manifest(root, manifest)
            expected["resolved_manifest_sha256"] = digest
            result: dict = {}

            AUDIT.verify_manifest(manifest, expected, result)

            self.assertEqual(result["resolved_manifest_expected_sha256"], digest)
            self.assertEqual(result["resolved_manifest_sha256"], digest)

            for bad_value in (None, "0" * 63, "A" * 64):
                invalid = copy.deepcopy(expected)
                if bad_value is None:
                    del invalid["resolved_manifest_sha256"]
                else:
                    invalid["resolved_manifest_sha256"] = bad_value
                with self.subTest(bad_value=bad_value), self.assertRaises(
                    AUDIT.AuditError
                ):
                    AUDIT.verify_manifest(manifest, invalid, {})

    def test_all_non_custom_project_and_remote_mutations_fail_digest(self) -> None:
        expected, original = self.make_fixture()
        with tempfile.TemporaryDirectory(dir="/tmp") as temporary:
            manifest = Path(temporary) / "manifest.xml"
            expected["resolved_manifest_sha256"] = self.write_manifest(
                original, manifest
            )
            AUDIT.verify_manifest(manifest, expected, {})

            def add_project(root: AUDIT.ET.Element) -> None:
                AUDIT.ET.SubElement(
                    root,
                    "project",
                    name="platform/packages/apps/Settings",
                    path="packages/apps/Settings",
                    revision="2" * 40,
                    remote="aosp",
                )

            def remove_project(root: AUDIT.ET.Element) -> None:
                root.remove(self.non_custom_project(root))

            mutations = (
                (
                    "non-custom revision",
                    lambda root: self.non_custom_project(root).set(
                        "revision", "2" * 40
                    ),
                ),
                (
                    "non-custom name",
                    lambda root: self.non_custom_project(root).set(
                        "name", "platform/frameworks/base-substituted"
                    ),
                ),
                (
                    "non-custom path",
                    lambda root: self.non_custom_project(root).set(
                        "path", "frameworks/base-substituted"
                    ),
                ),
                (
                    "non-custom remote association",
                    lambda root: self.non_custom_project(root).set(
                        "remote", "mp01-local"
                    ),
                ),
                (
                    "remote name",
                    lambda root: self.aosp_remote(root).set(
                        "name", "aosp-substituted"
                    ),
                ),
                (
                    "remote fetch",
                    lambda root: self.aosp_remote(root).set(
                        "fetch", "https://example.com/"
                    ),
                ),
                ("project added", add_project),
                ("project removed", remove_project),
            )
            for label, mutate in mutations:
                changed = copy.deepcopy(original)
                mutate(changed)
                self.write_manifest(changed, manifest)
                with self.subTest(label=label), self.assertRaisesRegex(
                    AUDIT.AuditError, "resolved manifest SHA256 mismatch"
                ):
                    AUDIT.verify_manifest(manifest, expected, {})


class BuildInfoContractTests(unittest.TestCase):
    def make_fields(self) -> dict[str, str]:
        fields = {key: "expected" for key in AUDIT.MANDATORY_BUILD_INFO_KEYS}
        fields["Android OUT_DIR interface"] = "out"
        fields["Android product output name"] = "generic_arm64"
        fields["Android TARGET_NO_KERNEL"] = "true"
        fields["Presigned partner APK byte preservation"] = "verified"
        fields["Presigned partner APK alignment"] = "verified"
        fields["Build log"] = "/tmp/formal-build.log"
        return fields

    def test_required_output_and_build_log_fields_pass(self) -> None:
        fields = self.make_fields()
        AUDIT.verify_build_info_expectations(fields, copy.deepcopy(fields))
        AUDIT.verify_derived_build_info_fields(
            fields,
            {
                "Android OUT_DIR interface": "out",
                "Android product output name": "generic_arm64",
                "Android TARGET_NO_KERNEL": "true",
                "Presigned partner APK byte preservation": "verified",
                "Presigned partner APK alignment": "verified",
                "Build log": "/tmp/formal-build.log",
            },
        )

    def test_build_log_pointer_mismatch_fails_closed(self) -> None:
        fields = self.make_fields()
        with self.assertRaises(AUDIT.AuditError):
            AUDIT.verify_derived_build_info_fields(
                fields, {"Build log": "/tmp/different-build.log"}
            )

    def test_missing_new_output_field_fails_closed(self) -> None:
        fields = self.make_fields()
        expectations = copy.deepcopy(fields)
        del expectations["Android OUT_DIR interface"]
        with self.assertRaises(AUDIT.AuditError):
            AUDIT.verify_build_info_expectations(fields, expectations)

    def test_missing_no_kernel_contract_fields_fail_closed(self) -> None:
        fields = self.make_fields()
        no_kernel_keys = (
            "vendor/lineage base commit",
            "vendor/lineage base tree",
            "vendor/lineage prepared commit",
            "vendor/lineage prepared tree",
            "vendor/lineage no-kernel header patch",
            "vendor/lineage no-kernel header patch SHA256",
            "No-kernel header policy verifier",
            "No-kernel header policy verifier SHA256",
            "Android TARGET_NO_KERNEL",
        )
        for key in no_kernel_keys:
            with self.subTest(key=key):
                expectations = copy.deepcopy(fields)
                del expectations[key]
                with self.assertRaises(AUDIT.AuditError):
                    AUDIT.verify_build_info_expectations(fields, expectations)

    def test_wrong_target_no_kernel_fails_closed(self) -> None:
        fields = self.make_fields()
        fields["Android TARGET_NO_KERNEL"] = "false"
        with self.assertRaises(AUDIT.AuditError):
            AUDIT.verify_derived_build_info_fields(
                fields, {"Android TARGET_NO_KERNEL": "true"}
            )

    def test_no_kernel_policy_input_hash_mismatches_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source_verifier = root / "source-verifier.py"
            retained_verifier = root / "retained-verifier.py"
            retained_patch = root / "retained.patch"
            source_verifier.write_bytes(b"verified policy\n")
            retained_verifier.write_bytes(source_verifier.read_bytes())
            retained_patch.write_bytes(b"verified patch\n")
            source_paths = {
                "no_kernel_header_policy_verifier": source_verifier,
            }
            retained = {
                "no_kernel_header_policy_verifier": retained_verifier,
                "vendor_lineage_no_kernel_patch": retained_patch,
            }
            fields = {
                "No-kernel header policy verifier": str(source_verifier),
                "No-kernel header policy verifier SHA256": AUDIT.sha256_file(
                    retained_verifier
                ),
                "vendor/lineage no-kernel header patch SHA256": AUDIT.sha256_file(
                    retained_patch
                ),
            }
            AUDIT.verify_no_kernel_policy_build_info(fields, source_paths, retained)
            wrong_path = copy.deepcopy(fields)
            wrong_path["No-kernel header policy verifier"] = str(
                root / "different-verifier.py"
            )
            with self.assertRaises(AUDIT.AuditError):
                AUDIT.verify_no_kernel_policy_build_info(
                    wrong_path, source_paths, retained
                )
            for key in (
                "No-kernel header policy verifier SHA256",
                "vendor/lineage no-kernel header patch SHA256",
            ):
                with self.subTest(key=key):
                    mismatched = copy.deepcopy(fields)
                    mismatched[key] = "0" * 64
                    with self.assertRaises(AUDIT.AuditError):
                        AUDIT.verify_no_kernel_policy_build_info(
                            mismatched, source_paths, retained
                        )

    def test_missing_partner_apk_contract_fields_fail_closed(self) -> None:
        fields = self.make_fields()
        partner_keys = (
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
        )
        for key in partner_keys:
            with self.subTest(key=key):
                expectations = copy.deepcopy(fields)
                del expectations[key]
                with self.assertRaises(AUDIT.AuditError):
                    AUDIT.verify_build_info_expectations(fields, expectations)
                actual = copy.deepcopy(fields)
                del actual[key]
                with self.assertRaises(AUDIT.AuditError):
                    AUDIT.verify_build_info_expectations(actual, fields)

    def test_wrong_partner_apk_verification_status_fails_closed(self) -> None:
        for key in (
            "Presigned partner APK byte preservation",
            "Presigned partner APK alignment",
        ):
            fields = self.make_fields()
            fields[key] = "unverified"
            with self.subTest(key=key), self.assertRaises(AUDIT.AuditError):
                AUDIT.verify_derived_build_info_fields(fields, {key: "verified"})

    def test_partner_apk_policy_input_hash_mismatches_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source_verifier = root / "source-verifier.py"
            retained_verifier = root / "retained-verifier.py"
            retained_patch = root / "retained.patch"
            source_verifier.write_bytes(b"verified policy\n")
            retained_verifier.write_bytes(source_verifier.read_bytes())
            retained_patch.write_bytes(b"verified patch\n")
            source_paths = {
                "presigned_partner_apk_policy_verifier": source_verifier,
            }
            retained = {
                "presigned_partner_apk_policy_verifier": retained_verifier,
                "partner_gms_presigned_apk_patch": retained_patch,
            }
            fields = {
                "Presigned partner APK policy verifier": str(source_verifier),
                "Presigned partner APK policy verifier SHA256": AUDIT.sha256_file(
                    retained_verifier
                ),
                "vendor/partner_gms presigned APK patch SHA256": AUDIT.sha256_file(
                    retained_patch
                ),
            }
            AUDIT.verify_partner_apk_policy_build_info(
                fields, source_paths, retained
            )
            wrong_path = copy.deepcopy(fields)
            wrong_path["Presigned partner APK policy verifier"] = str(
                root / "different-verifier.py"
            )
            with self.assertRaises(AUDIT.AuditError):
                AUDIT.verify_partner_apk_policy_build_info(
                    wrong_path, source_paths, retained
                )
            for key in (
                "Presigned partner APK policy verifier SHA256",
                "vendor/partner_gms presigned APK patch SHA256",
            ):
                with self.subTest(key=key):
                    mismatched = copy.deepcopy(fields)
                    mismatched[key] = "0" * 64
                    with self.assertRaises(AUDIT.AuditError):
                        AUDIT.verify_partner_apk_policy_build_info(
                            mismatched, source_paths, retained
                        )

    def test_wrong_android_output_interface_fails_closed(self) -> None:
        fields = self.make_fields()
        fields["Android OUT_DIR interface"] = "/absolute/out"
        with self.assertRaises(AUDIT.AuditError):
            AUDIT.verify_derived_build_info_fields(
                fields, {"Android OUT_DIR interface": "out"}
            )

    def test_missing_or_wrong_product_output_name_fails_closed(self) -> None:
        fields = self.make_fields()
        expectations = copy.deepcopy(fields)
        del expectations["Android product output name"]
        with self.assertRaises(AUDIT.AuditError):
            AUDIT.verify_build_info_expectations(fields, expectations)

        fields["Android product output name"] = "arm64_bmN4"
        with self.assertRaises(AUDIT.AuditError):
            AUDIT.verify_derived_build_info_fields(
                fields, {"Android product output name": "generic_arm64"}
            )


class PartnerApkArtifactTests(unittest.TestCase):
    def make_fixture(
        self, root: Path, zipalign_status: int = 0
    ) -> tuple[Path, dict[str, Path], dict[str, str], Path, dict[str, str]]:
        evidence = root / "evidence"
        evidence.mkdir()
        target_apks: dict[str, Path] = {}
        expected_hashes: dict[str, str] = {}
        for module, _ in AUDIT.PARTNER_APK_TARGETS:
            target = root / f"{module}.apk"
            target.write_bytes(f"fixture APK for {module}\n".encode("ascii"))
            target_apks[module] = target
            expected_hashes[module] = AUDIT.sha256_file(target)
        zipalign = root / "zipalign"
        zipalign.write_text(
            f"#!/bin/sh\nexit {zipalign_status}\n", encoding="ascii"
        )
        zipalign.chmod(0o500)
        return evidence, target_apks, expected_hashes, zipalign, {"PATH": "/usr/bin"}

    def test_all_five_hashes_and_alignment_checks_pass(self) -> None:
        with tempfile.TemporaryDirectory(dir="/tmp") as temporary:
            fixture = self.make_fixture(Path(temporary))
            evidence, targets, expected, zipalign, environment = fixture
            verified = AUDIT.verify_partner_apk_artifacts(
                evidence, targets, expected, zipalign, environment
            )
            self.assertEqual(verified, expected)
            self.assertEqual(
                len(list(evidence.glob("partner-apk-*-alignment.invocation.json"))),
                5,
            )
            for module, _ in AUDIT.PARTNER_APK_TARGETS:
                invocation = json.loads(
                    (
                        evidence
                        / f"partner-apk-{module.casefold()}-alignment.invocation.json"
                    ).read_text()
                )
                self.assertEqual(
                    invocation["argv"],
                    [str(zipalign), "-c", "-p", "4", str(targets[module])],
                )

    def test_corrupted_target_apk_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory(dir="/tmp") as temporary:
            fixture = self.make_fixture(Path(temporary))
            evidence, targets, expected, zipalign, environment = fixture
            targets["GmsCore"].write_bytes(b"corrupted APK\n")
            with self.assertRaises(AUDIT.AuditError):
                AUDIT.verify_partner_apk_artifacts(
                    evidence, targets, expected, zipalign, environment
                )

    def test_wrong_expected_hash_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory(dir="/tmp") as temporary:
            fixture = self.make_fixture(Path(temporary))
            evidence, targets, expected, zipalign, environment = fixture
            expected["GmsCore"] = "0" * 64
            with self.assertRaises(AUDIT.AuditError):
                AUDIT.verify_partner_apk_artifacts(
                    evidence, targets, expected, zipalign, environment
                )

    def test_missing_zipalign_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory(dir="/tmp") as temporary:
            fixture = self.make_fixture(Path(temporary))
            evidence, targets, expected, zipalign, environment = fixture
            zipalign.unlink()
            with self.assertRaises(AUDIT.AuditError):
                AUDIT.verify_partner_apk_artifacts(
                    evidence, targets, expected, zipalign, environment
                )

    def test_failed_alignment_check_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory(dir="/tmp") as temporary:
            fixture = self.make_fixture(Path(temporary), zipalign_status=1)
            evidence, targets, expected, zipalign, environment = fixture
            with self.assertRaises(AUDIT.AuditError):
                AUDIT.verify_partner_apk_artifacts(
                    evidence, targets, expected, zipalign, environment
                )


if __name__ == "__main__":
    unittest.main()
