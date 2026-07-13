#!/usr/bin/env python3
import argparse
import datetime
import hashlib
import sqlite3
from pathlib import Path


def online_backup(source, destination):
    destination.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(f"file:{source}?mode=ro", uri=True) as source_db:
        with sqlite3.connect(destination) as backup_db:
            source_db.backup(backup_db)


def integrity(path):
    with sqlite3.connect(f"file:{path}?mode=ro", uri=True) as database:
        return database.execute("pragma integrity_check").fetchone()[0]


def table_count(path, table):
    with sqlite3.connect(f"file:{path}?mode=ro", uri=True) as database:
        found = database.execute(
            "select 1 from sqlite_master where type = 'table' and name = ?", (table,)
        ).fetchone()
        if found is None:
            return None
        return database.execute(f'select count(*) from "{table}"').fetchone()[0]


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def restore_test(backup, destination):
    if destination.exists():
        destination.unlink()
    online_backup(backup, destination)
    return integrity(destination)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pj-db", default=str(Path.home() / ".local/share/pj-general/p0.sqlite"))
    parser.add_argument("--vikunja-db", default="/srv/pj-general/data/vikunja/db/vikunja.db")
    parser.add_argument("--backup-root", default=str(Path.home() / ".local/share/pj-general/backups"))
    args = parser.parse_args()

    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_dir = Path(args.backup_root) / stamp
    sources = {
        "pj-general": (Path(args.pj_db), "candidates"),
        "vikunja": (Path(args.vikunja_db), "tasks"),
    }
    for name, (source, count_table) in sources.items():
        backup = backup_dir / f"{name}.sqlite"
        restored = backup_dir / f"{name}.restore-test.sqlite"
        online_backup(source, backup)
        backup_integrity = integrity(backup)
        restore_integrity = restore_test(backup, restored)
        count = table_count(restored, count_table)
        links = table_count(restored, "execution_links")
        print(
            f"{name} backup={backup_integrity} restore={restore_integrity} "
            f"{count_table}={count} execution_links={links if links is not None else 0} "
            f"bytes={backup.stat().st_size} sha256={sha256(backup)} restore_sha256={sha256(restored)}"
        )
    print(f"backup-ready path={backup_dir}")


if __name__ == "__main__":
    main()
