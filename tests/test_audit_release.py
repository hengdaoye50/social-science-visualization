"""Self-contained tests for structural auditor (stdlib only)."""
from __future__ import annotations
import copy
import importlib.util
import json
import struct
import tempfile
import unittest
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("audit_release", ROOT / "scripts/audit_release.py")
audit_release = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit_release)


def chunk(kind: bytes, data: bytes) -> bytes:
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xffffffff)


def tiny_png(path: Path, width: int = 1000, height: int = 700) -> None:
    # Self-contained 1-color RGBA PNG to test header handling; compressible image, but valid.
    header = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    raw = (b"\x00" + b"\xff\xff\xff\xff" * width) * height
    content = (audit_release.PNG_MAGIC + chunk(b"IHDR", header) +
               chunk(b"pHYs", struct.pack(">IIB", 11811, 11811, 1)) +
               chunk(b"IDAT", zlib.compress(raw, 6)) + chunk(b"IEND", b""))
    path.write_bytes(content)


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.d = Path(self.tmp.name)
        self.m = json.loads((ROOT / "assets/figure-manifest.template.json").read_text(encoding="utf-8"))
        self.m.update(status="demo", question="a mock question")
        self.m["data"].update(source_kind="synthetic_demo", n_observations=3)
        self.m["provenance"].update(code="plot.py")
        (self.d / "plot.py").write_text("# mock\n")
        self.m["review"].update(numeric_verified=False, method_verified=False, visual_verified=False)
        (self.d / "plot.pdf").write_bytes(b"%PDF-1.4\n1 0 obj <<>> endobj\n%%EOF\n")
        (self.d / "plot.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><path d="M0 0 L100 100"/></svg>')
        tiny_png(self.d / "plot.png")
        self.m["exports"] = {ext: "plot." + ext for ext in ("png", "svg", "pdf")}
        self.path = self.d / "figure-manifest.json"

    def check(self, m=None):
        self.path.write_text(json.dumps(m or self.m), encoding="utf-8")
        return audit_release.audit(self.path)

    def test_valid_fixture_passes_structure_with_warnings(self):
        errors, warnings = self.check()
        self.assertFalse(errors, errors)
        self.assertTrue(any("SIMULATED" in w for w in warnings))

    def test_invalid_source_kind(self):
        m = copy.deepcopy(self.m)
        m["data"]["source_kind"] = "guessed"
        errors, _ = self.check(m)
        self.assertTrue(any("source_kind" in e for e in errors))

    def test_missing_export(self):
        (self.d / "plot.pdf").unlink()
        errors, _ = self.check()
        self.assertTrue(any("pdf" in e for e in errors))

    def test_path_traversal_blocked(self):
        m = copy.deepcopy(self.m)
        m["exports"]["svg"] = "../elsewhere.svg"
        errors, _ = self.check(m)
        self.assertTrue(any("manifest directory" in e for e in errors))

    def test_svg_script_rejected(self):
        (self.d / "plot.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1 1"><script>evil()</script></svg>')
        errors, _ = self.check()
        self.assertTrue(any("script" in e for e in errors))

    def test_review_claim_requires_reviewer(self):
        m = copy.deepcopy(self.m)
        m["review"].update(numeric_verified=True, reviewer="")
        errors, _ = self.check(m)
        self.assertTrue(any("reviewer" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
