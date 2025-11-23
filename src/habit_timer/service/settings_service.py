from ..domain.models import AppConfig
from ..repository.config_repository import ConfigRepository


class SettingsService:
    """设置读写的业务包装。"""

    def __init__(self, repo: ConfigRepository):
        self.repo = repo

    def get_config(self) -> AppConfig:
        return self.repo.load()

    def update_config(self, config: AppConfig) -> AppConfig:
        self.repo.save(config)
        return config
