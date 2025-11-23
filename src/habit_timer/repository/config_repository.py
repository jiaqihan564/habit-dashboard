from ..domain.models import AppConfig
from .database import Database


class ConfigRepository:
    """应用全局配置的持久化。"""

    def __init__(self, db: Database):
        self.db = db

    def load(self) -> AppConfig:
        row = self.db.cursor().execute("SELECT * FROM app_config WHERE id=1").fetchone()
        if not row:
            return AppConfig()
        return AppConfig(
            id=row["id"],
            work_minutes=row["work_minutes"],
            short_break_minutes=row["short_break_minutes"],
            long_break_minutes=row["long_break_minutes"],
            long_break_interval=row["long_break_interval"],
        )

    def save(self, config: AppConfig) -> None:
        cursor = self.db.cursor()
        cursor.execute(
            """
            INSERT INTO app_config(id, work_minutes, short_break_minutes, long_break_minutes, long_break_interval)
            VALUES(1, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                work_minutes=excluded.work_minutes,
                short_break_minutes=excluded.short_break_minutes,
                long_break_minutes=excluded.long_break_minutes,
                long_break_interval=excluded.long_break_interval
            """,
            (
                config.work_minutes,
                config.short_break_minutes,
                config.long_break_minutes,
                config.long_break_interval,
            ),
        )
        self.db.connect().commit()
