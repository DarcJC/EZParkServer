from .app import app
from .settings import EnvironmentSettings


settings = EnvironmentSettings()

__all__ = ['app', 'settings', ]
