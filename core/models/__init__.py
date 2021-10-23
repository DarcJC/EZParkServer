from tortoise import Tortoise
from .client import ClientToken
from .vehicle import VehicleInfo, FeeRecord, FeeRule

Tortoise.init_models(['core.models', ], "models")
