#!/usr/bin/env python3
import shutil, unittest
from contextlib import contextmanager
from pathlib import Path
from rq16_manifest import ROOT, canonical_review_source_files, build_source_manifest, manifest_sha256

class ManifestTests(unittest.TestCase):
    @contextmanager
    def scratch(self):
        d=ROOT/".rq16-manifest-test"; shutil.rmtree(d,ignore_errors=True); d.mkdir()
        try: yield d
        finally: shutil.rmtree(d,ignore_errors=True)
    def test_clean_manifest_is_deterministic(self):
        files=canonical_review_source_files(ROOT)
        self.assertEqual(build_source_manifest(files),build_source_manifest(list(reversed(files))))
        self.assertEqual(len({x.relative_to(ROOT).as_posix() for x in files}),len(files))
    def test_source_byte_change_changes_manifest(self):
        with self.scratch() as d:
            p=d/"x.py"; p.write_bytes(b"x=1\n"); before=build_source_manifest([p],d); p.write_bytes(b"x=2\n"); self.assertNotEqual(before,build_source_manifest([p],d))
    def test_duplicate_path_rejected(self):
        with self.scratch() as d:
            p=d/"x"; p.write_bytes(b"x");
            with self.assertRaises(ValueError): build_source_manifest([p,p],d)
    def test_missing_file_fails(self):
        with self.assertRaises(FileNotFoundError): build_source_manifest([ROOT/"does-not-exist"],ROOT)
    def test_absolute_outside_root_rejected(self):
        with self.scratch() as d:
            p=d/"x"; p.write_bytes(b"x");
            with self.assertRaises(ValueError): build_source_manifest([Path("C:/outside-rq16/x")],ROOT)
    def test_generated_packet_is_not_source(self):
        names={p.name for p in canonical_review_source_files(ROOT)}
        self.assertNotIn("V24-I11-V6-RQ1-RQ16-PREREGISTRATION-REMEDIATION-6-REVIEW.md",names)
    def test_manifest_hash_is_content_hash(self):
        self.assertEqual(len(manifest_sha256(build_source_manifest())),64)

if __name__=="__main__": unittest.main(verbosity=2)
