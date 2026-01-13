#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import argparse
import os
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path


def _default_db_path() -> Path:
    project_root = Path(__file__).resolve().parent.parent
    return project_root / "src" / "data" / "word.db"


def _default_backup_dir() -> Path:
    project_root = Path(__file__).resolve().parent.parent
    return project_root / "backups"


def backup_sqlite(db_path: Path, backup_dir: Path, keep_days: int | None) -> Path:
    backup_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"word.db.{timestamp}.backup"

    # Open source DB in read-write so WAL checkpoint can run if enabled.
    src = sqlite3.connect(str(db_path), timeout=30, check_same_thread=False)
    try:
        src.execute("PRAGMA busy_timeout=5000")

        # If WAL is enabled, checkpoint to flush recent pages.
        try:
            src.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        except sqlite3.DatabaseError:
            # Not in WAL mode or checkpoint not supported; ignore.
            pass

        dst = sqlite3.connect(str(backup_path))
        try:
            src.backup(dst)
            dst.commit()
        finally:
            dst.close()
    finally:
        src.close()

    if keep_days is not None and keep_days > 0:
        cutoff = datetime.now() - timedelta(days=keep_days)
        for p in backup_dir.glob("word.db.*.backup"):
            try:
                mtime = datetime.fromtimestamp(p.stat().st_mtime)
                if mtime < cutoff:
                    p.unlink(missing_ok=True)
            except OSError:
                continue

    return backup_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Backup word.db safely (works with WAL).")
    parser.add_argument("--db-path", default=str(_default_db_path()), help="Path to SQLite DB")
    parser.add_argument("--out-dir", default=str(_default_backup_dir()), help="Backup output directory")
    parser.add_argument("--keep-days", type=int, default=30, help="Retention days (default: 30). Set 0 to disable cleanup.")
    args = parser.parse_args()

    db_path = Path(args.db_path)
    backup_dir = Path(args.out_dir)

    if not db_path.exists():
        raise SystemExit(f"DB not found: {db_path}")

    keep_days = None if args.keep_days == 0 else args.keep_days
    backup_path = backup_sqlite(db_path, backup_dir, keep_days)

    print(str(backup_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
