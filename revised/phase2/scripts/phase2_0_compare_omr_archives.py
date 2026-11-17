"""Stream and compare duplicate OMR CSV members; emit metadata only."""

from __future__ import annotations

import argparse
import hashlib
import subprocess
from pathlib import Path

import pandas as pd


def inspect_member(archive: Path, member: str) -> tuple[int, str, str]:
    proc = subprocess.Popen(
        ["tar", "-xOf", str(archive), member],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert proc.stdout is not None
    digest = hashlib.sha256()
    byte_count = 0
    header = bytearray()
    header_complete = False
    while block := proc.stdout.read(1024 * 1024):
        digest.update(block)
        byte_count += len(block)
        if not header_complete:
            newline = block.find(b"\n")
            if newline >= 0:
                header.extend(block[:newline])
                header_complete = True
            else:
                header.extend(block)
    stderr = proc.stderr.read().decode("utf-8", errors="replace") if proc.stderr else ""
    status = proc.wait()
    if status:
        raise RuntimeError(f"tar failed for {archive}:{member} ({status}): {stderr[-1000:]}")
    if not header_complete:
        raise RuntimeError(f"No CSV header terminator found in {archive}:{member}")
    return byte_count, digest.hexdigest(), header.decode("utf-8-sig", errors="replace")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-dir", type=Path, default=Path("data/raw"))
    parser.add_argument("--output", type=Path, default=Path("revised/phase2/aggregates/omr_archive_comparison.csv"))
    args = parser.parse_args()
    items = [
        (args.raw_dir / "hosp.rar", "omr.csv"),
        (args.raw_dir / "omr.rar", "omr.csv"),
    ]
    results = []
    for archive, member in items:
        size, sha256, header = inspect_member(archive, member)
        results.append({"archive": archive.name, "member": member, "uncompressed_bytes": size, "sha256": sha256, "csv_header": header, "stream_exit_success": True})
    same = results[0]["sha256"] == results[1]["sha256"] and results[0]["uncompressed_bytes"] == results[1]["uncompressed_bytes"]
    for row in results:
        row["copies_byte_identical"] = same
    args.output.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(results).to_csv(args.output, index=False)
    print(f"OMR members streamed; byte-identical={same}; metadata only -> {args.output}")


if __name__ == "__main__":
    main()
