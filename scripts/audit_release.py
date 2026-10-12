#!/usr/bin/env python3
"""Structural manifest/figure preflight (not scientific, visual or PDF compliance review).

Usage: python scripts/audit_release.py path/to/figure-manifest.json [--strict]
No network calls and no non-stdlib dependencies. Exit 0 = no errors (warnings may remain).
"""
from __future__ import annotations

import argparse
import json
import math
import struct
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
REQUIRED = {
    "figure_id": str, "title": str, "status": str, "question": str,
    "design": str, "data": dict, "inference": dict, "chart": dict,
    "provenance": dict, "exports": dict, "review": dict,
}
FIELDS = {
    "data": ("source", "source_kind", "unit_of_analysis", "population", "time_window",
             "n_observations", "missingness", "weights", "transformations"),
    "inference": ("estimand", "method", "uncertainty", "standard_errors", "reference_group"),
    "chart": ("x_label", "y_label", "denominator", "caption", "alt_text"),
    "provenance": ("code", "input_files", "data_restrictions"),
    "exports": ("png", "svg", "pdf"),
    "review": ("numeric_verified", "visual_verified", "method_verified", "reviewer", "notes"),
}


def png_info(path: Path) -> tuple[int, int, float | None]:
    """Read PNG signature, IHDR, pHYs chunks. This is not a full decoder."""
    with path.open("rb") as f:
        if f.read(8) != PNG_MAGIC:
            raise ValueError("PNG signature is invalid")
        width = height = None
        dpi = None
        for _ in range(3000):
            header = f.read(8)
            if len(header) != 8:
                break
            length, kind = struct.unpack(">I4s", header)
            if length > 64 * 1024 * 1024:
                raise ValueError("Suspicious PNG chunk length")
            chunk = f.read(length)
            crc = f.read(4)
            if len(chunk) != length or len(crc) != 4:
                raise ValueError("Truncated PNG chunk")
            if kind == b"IHDR":
                if length != 13:
                    raise ValueError("Invalid IHDR length")
                width, height = struct.unpack(">II", chunk[:8])
            if kind == b"pHYs" and length == 9:
                xppm, yppm, unit = struct.unpack(">IIB", chunk)
                if unit == 1 and xppm > 0 and yppm > 0:
                    dpi = min(xppm, yppm) * 0.0254
            if kind in (b"IDAT", b"IEND"):
                break
        if not width or not height:
            raise ValueError("Missing/invalid PNG IHDR")
    return width, height, dpi


def svg_info(path: Path) -> None:
    root = ET.parse(path).getroot()
    if root.tag.rsplit("}", 1)[-1] != "svg":
        raise ValueError("XML root is not <svg>")
    vb = root.attrib.get("viewBox")
    if not vb:
        raise ValueError("SVG is missing viewBox")
    parts = vb.replace(",", " ").split()
    if len(parts) != 4 or not all(math.isfinite(float(x)) for x in parts):
        raise ValueError("SVG has invalid viewBox")
    if float(parts[2]) <= 0 or float(parts[3]) <= 0:
        raise ValueError("SVG has non-positive viewport")
    if len(root) == 0:
        raise ValueError("SVG has no children")
    if any(el.tag.rsplit("}", 1)[-1] == "script" for el in root.iter()):
        raise ValueError("SVG contains executable script")


def pdf_info(path: Path) -> None:
    with path.open("rb") as f:
        head = f.read(16)
        if not head.startswith(b"%PDF-"):
            raise ValueError("Invalid PDF header")
        f.seek(max(0, path.stat().st_size - 2048))
        if b"%%EOF" not in f.read():
            raise ValueError("PDF appears truncated (missing EOF)")


def audit(path: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    try:
        m = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return [f"Cannot read JSON manifest: {exc}"], warnings
    if not isinstance(m, dict):
        return ["Manifest root must be a JSON object"], warnings
    for key, typ in REQUIRED.items():
        if key not in m or not isinstance(m[key], typ):
            errors.append(f"Missing/wrong type: {key} (expected {typ.__name__})")
    if errors:
        return errors, warnings
    for key in ("figure_id", "title", "question", "design"):
        if not m[key].strip():
            errors.append(f"Empty required value: {key}")
    if m["status"] not in ("demo", "research"):
        errors.append("status must be 'demo' or 'research'")
    for section, fields in FIELDS.items():
        for field in fields:
            if field not in m[section]:
                errors.append(f"Missing: {section}.{field}")
            elif section not in ("exports", "review") and field not in ("input_files", "n_observations"):
                if not isinstance(m[section][field], str) or not m[section][field].strip():
                    errors.append(f"Empty/wrong type: {section}.{field}")
    if errors:
        return errors, warnings
    data = m["data"]
    if data["source_kind"] not in ("observed", "synthetic_demo", "restricted", "literature"):
        errors.append("data.source_kind must be observed/synthetic_demo/restricted/literature")
    if (m["status"] == "demo") != (data["source_kind"] == "synthetic_demo"):
        errors.append("Demo status and synthetic_demo source_kind must match")
    n = data["n_observations"]
    if n is not None and (type(n) is not int or n < 0):
        errors.append("data.n_observations must be a nonnegative integer or null")
    if m["status"] == "research" and n is None:
        warnings.append("Research sample N not supplied; justify if unavailable")
    review = m["review"]
    for key in ("numeric_verified", "visual_verified", "method_verified"):
        if type(review[key]) is not bool:
            errors.append(f"review.{key} must be boolean")
        elif not review[key]:
            warnings.append(f"Human review still pending: {key}")
    if not isinstance(m["provenance"]["input_files"], list) or any(
        not isinstance(x, str) for x in m["provenance"]["input_files"]
    ):
        errors.append("provenance.input_files must be a list of paths")
    if not isinstance(review["notes"], str) or not isinstance(review["reviewer"], str):
        errors.append("review.reviewer and review.notes must be text")
    if not review["reviewer"].strip() and any(review.get(k) is True for k in
                                              ("numeric_verified", "visual_verified", "method_verified")):
        errors.append("Verified flags require a reviewer name")
    base = path.parent
    src = m["provenance"]["code"]
    if isinstance(src, str) and src.strip() and not (base / src).is_file():
        warnings.append(f"Provenance code path is not accessible: {src}")
    if isinstance(m["provenance"]["input_files"], list):
        for filename in m["provenance"]["input_files"]:
            if isinstance(filename, str) and filename.strip() and not (base / filename).is_file():
                warnings.append(f"Input file not available locally: {filename} (restricted data may be intentional)")
    exports = m["exports"]
    for ext in ("png", "svg", "pdf"):
        target = exports.get(ext)
        if not isinstance(target, str) or not target.strip() or Path(target).suffix.lower() != "." + ext:
            errors.append(f"exports.{ext} requires a relative .{ext} filename")
            continue
        p = Path(target)
        if p.is_absolute() or ".." in p.parts:
            errors.append(f"exports.{ext} must stay within manifest directory")
            continue
        f = base / p
        if not f.is_file() or f.stat().st_size < 30:
            errors.append(f"exports.{ext} missing or too small: {f}")
            continue
        try:
            if ext == "png":
                w, h, dpi = png_info(f)
                if w < 800 or h < 500:
                    warnings.append(f"Small PNG ({w}x{h}); verify target display size")
                if dpi is None:
                    warnings.append("PNG lacks readable pHYs resolution metadata")
                elif dpi < 295:
                    warnings.append(f"PNG reports {dpi:.0f} DPI; check final print sizing")
            elif ext == "svg":
                svg_info(f)
            else:
                pdf_info(f)
        except (OSError, ValueError, ET.ParseError, struct.error) as exc:
            errors.append(f"exports.{ext} failed structure check: {exc}")
    if m["status"] == "demo":
        warnings.append("SIMULATED DEMO: do not present these data as research findings")
    return errors, warnings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--strict", action="store_true", help="Treat warnings as failure")
    args = parser.parse_args(argv)
    errors, warnings = audit(args.manifest)
    for err in errors:
        print(f"ERROR: {err}")
    for warn in warnings:
        print(f"WARN:  {warn}")
    print(f"Structural audit: {len(errors)} error(s), {len(warnings)} warning(s).")
    print("NOTE: No numerical recomputation, full PDF parsing, font-embedding, or visual review was performed.")
    return 1 if errors or (args.strict and warnings) else 0


if __name__ == "__main__":
    sys.exit(main())
