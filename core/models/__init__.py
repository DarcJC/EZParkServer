from tortoise import Tortoise


Tortoise.init_models(['core.models', ], "models")


__all__ = []
