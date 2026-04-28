import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_DB_PATH = Path(__file__).resolve().parents[1] / "downloads.db"


def normalize_platform(platform: str | None) -> str:
    normalized = (platform or "").strip().lower()
    aliases = {
        "twitter": "x",
    }
    return aliases.get(normalized, normalized or "unknown")


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _db_path() -> str:
    return os.getenv("KIRARA_DB_PATH", str(DEFAULT_DB_PATH))


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(_db_path())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_database() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS downloads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                title TEXT,
                url TEXT NOT NULL,
                download_count INTEGER NOT NULL,
                file_format TEXT NOT NULL,
                file_type TEXT NOT NULL,
                platform TEXT NOT NULL,
                downloaded_at TEXT NOT NULL,
                is_cached BOOLEAN DEFAULT 0
            );
            """
        )
        try:
            conn.execute("ALTER TABLE downloads ADD COLUMN is_cached BOOLEAN DEFAULT 0;")
        except sqlite3.OperationalError:
            pass  # Column already exists
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS download_totals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                platform TEXT NOT NULL,
                total_count INTEGER NOT NULL DEFAULT 0,
                updated_at TEXT NOT NULL,
                UNIQUE(url, platform)
            );
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_downloads_platform_date
            ON downloads (platform, downloaded_at DESC, id DESC);
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_download_totals_url_platform
            ON download_totals (url, platform);
            """
        )
        conn.commit()


def _upsert_total_count(cursor: sqlite3.Cursor, url: str, platform: str, timestamp: str) -> int:
    cursor.execute(
        """
        INSERT INTO download_totals (url, platform, total_count, updated_at)
        VALUES (?, ?, 1, ?)
        ON CONFLICT(url, platform)
        DO UPDATE SET
            total_count = download_totals.total_count + 1,
            updated_at = excluded.updated_at;
        """,
        (url, platform, timestamp),
    )

    cursor.execute(
        """
        SELECT total_count
        FROM download_totals
        WHERE url = ? AND platform = ?;
        """,
        (url, platform),
    )
    row = cursor.fetchone()
    return int(row["total_count"]) if row else 1


def _prune_platform_history(cursor: sqlite3.Cursor, platform: str, keep_latest: int = 10) -> None:
    cursor.execute(
        """
        DELETE FROM downloads
        WHERE platform = ?
          AND id NOT IN (
              SELECT id
              FROM downloads
              WHERE platform = ?
              ORDER BY downloaded_at DESC, id DESC
              LIMIT ?
          );
        """,
        (platform, platform, keep_latest),
    )


def get_latest_title(url: str) -> str | None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT title
            FROM downloads
            WHERE url = ? AND title IS NOT NULL
            ORDER BY downloaded_at DESC
            LIMIT 1;
            """,
            (url,)
        )
        row = cursor.fetchone()
        return row["title"] if row else None

def record_download(
    *,
    name: str,
    title: str | None,
    url: str,
    file_format: str,
    file_type: str,
    platform: str,
    downloaded_at: str | None = None,
    is_cached: bool = False,
) -> dict[str, Any]:
    timestamp = downloaded_at or _utc_now_iso()
    normalized_platform = normalize_platform(platform)

    with get_connection() as conn:
        cursor = conn.cursor()
        total_count = _upsert_total_count(cursor, url, normalized_platform, timestamp)

        cursor.execute(
            """
            INSERT INTO downloads (
                name,
                title,
                url,
                download_count,
                file_format,
                file_type,
                platform,
                downloaded_at,
                is_cached
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
            (
                name,
                title,
                url,
                total_count,
                file_format,
                file_type,
                normalized_platform,
                timestamp,
                is_cached,
            ),
        )
        download_id = int(cursor.lastrowid)

        _prune_platform_history(cursor, normalized_platform, keep_latest=10)
        conn.commit()

    return {
        "id": download_id,
        "name": name,
        "title": title,
        "url": url,
        "download_count": total_count,
        "file_format": file_format,
        "file_type": file_type,
        "platform": normalized_platform,
        "downloaded_at": timestamp,
        "is_cached": is_cached,
    }


def list_downloads(platform: str | None = None, limit: int = 10) -> list[dict[str, Any]]:
    normalized_platform = normalize_platform(platform) if platform else None
    query = """
        SELECT
        id,
        name,
        title,
        url,
        download_count,
        file_format,
        file_type,
        platform,
        MAX(downloaded_at) AS downloaded_at,
        is_cached
    FROM downloads
    """
    params: list[Any] = []
    if normalized_platform:
        query += " WHERE platform = ?"
        params.append(normalized_platform)

    query += "GROUP BY url ORDER BY downloaded_at DESC, id DESC LIMIT ?"
    params.append(limit)

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()

    return [dict(row) for row in rows]
