from tortoise import Tortoise
from .client import ClientToken

Tortoise.init_models(['core.models', ], "models")
