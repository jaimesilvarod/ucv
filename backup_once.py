import os
import csv
import json
import zipfile
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]  # ideal: SERVICE_ROLE solo local/admin

TABLES = ["incidentes"]  # agrega aquí más tablas si existen
EVIDENCE_DIR = Path("evidence")
OUT_DIR = Path("backup_out")
OUT_DIR.mkdir(exist_ok=True)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def fetch_all(table: str, page_size: int = 1000):
    rows = []
    start = 0

    while True:
        end = start + page_size - 1
        res = supabase.table(table).select("*").range(start, end).execute()
        batch = res.data or []
        rows.extend(batch)

        if len(batch) < page_size:
            break

        start += page_size

    return rows


def export_table(table: str):
    rows = fetch_all(table)

    json_path = OUT_DIR / f"{table}.json"
    csv_path = OUT_DIR / f"{table}.csv"

    json_path.write_text(
        json.dumps(rows, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8"
    )

    if rows:
        fields = sorted({k for row in rows for k in row.keys()})
        with csv_path.open("w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
    else:
        csv_path.write_text("", encoding="utf-8")

    return [json_path, csv_path]


def create_backup():
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    zip_path = Path(f"backup_aurora_{ts}.zip")
    manifest = {}

    files_to_zip = []

    for table in TABLES:
        files_to_zip.extend(export_table(table))

    if EVIDENCE_DIR.exists():
        files_to_zip.extend([p for p in EVIDENCE_DIR.rglob("*") if p.is_file()])

    for path in files_to_zip:
        manifest[str(path)] = sha256_file(path)

    manifest_path = OUT_DIR / "MANIFEST_SHA256.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    files_to_zip.append(manifest_path)

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for path in files_to_zip:
            z.write(path, arcname=str(path))

    print(f"OK: {zip_path}")
    print(f"SHA256 ZIP: {sha256_file(zip_path)}")


if __name__ == "__main__":
    create_backup()
