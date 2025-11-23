import sqlite3
from pathlib import Path
from typing import Optional

# 负责 SQLite 连接与建表，保证上层只需要拿到连接对象即可。


class Database:
    """SQLite 数据库包装，启动时自动建表。"""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._conn: Optional[sqlite3.Connection] = None
        db_path.parent.mkdir(parents=True, exist_ok=True)

    def connect(self) -> sqlite3.Connection:
        if self._conn:
            return self._conn
        self._conn = sqlite3.connect(self.db_path)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys = ON;")
        self._init_schema()
        return self._conn

    def cursor(self) -> sqlite3.Cursor:
        return self.connect().cursor()

    def _init_schema(self) -> None:
        conn = self.connect()
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS habits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT DEFAULT '',
                category TEXT DEFAULT '其它',
                target_per_week INTEGER DEFAULT 7,
                enabled INTEGER DEFAULT 1,
                created_at TEXT NOT NULL,
                deleted_at TEXT
            );

            CREATE TABLE IF NOT EXISTS habit_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                habit_id INTEGER NOT NULL,
                date TEXT NOT NULL,
                is_completed INTEGER NOT NULL,
                note TEXT DEFAULT '',
                recorded_at TEXT NOT NULL,
                FOREIGN KEY(habit_id) REFERENCES habits(id) ON DELETE CASCADE,
                UNIQUE(habit_id, date)
            );

            CREATE INDEX IF NOT EXISTS idx_habit_records_habit_date
                ON habit_records(habit_id, date);

            CREATE TABLE IF NOT EXISTS pomodoro_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                habit_id INTEGER,
                start_time TEXT NOT NULL,
                end_time TEXT,
                duration_seconds INTEGER NOT NULL,
                status TEXT NOT NULL,
                FOREIGN KEY(habit_id) REFERENCES habits(id) ON DELETE SET NULL
            );

            CREATE INDEX IF NOT EXISTS idx_pomodoro_start_time
                ON pomodoro_sessions(start_time);

            CREATE TABLE IF NOT EXISTS app_config (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                work_minutes INTEGER NOT NULL DEFAULT 25,
                short_break_minutes INTEGER NOT NULL DEFAULT 5,
                long_break_minutes INTEGER NOT NULL DEFAULT 15,
                long_break_interval INTEGER NOT NULL DEFAULT 4
            );

            INSERT OR IGNORE INTO app_config(id, work_minutes, short_break_minutes, long_break_minutes, long_break_interval)
            VALUES (1, 25, 5, 15, 4);
            """
        )
        # 兼容旧版本表结构，补充 deleted_at 字段
        try:
            conn.execute("ALTER TABLE habits ADD COLUMN deleted_at TEXT;")
        except sqlite3.OperationalError:
            # 已存在该字段时忽略
            pass
        conn.commit()

    def close(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None
