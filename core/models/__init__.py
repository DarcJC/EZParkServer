from tortoise import Tortoise
from .client import ClientToken, AuditLog
from .vehicle import VehicleInfo, FeeRecord, FeeRule, EntryLog

Tortoise.init_models(['core.models', ], "models")
