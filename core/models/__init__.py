from tortoise import Tortoise
from tortoise.contrib.pydantic import pydantic_model_creator
from .client import ClientToken, AuditLog
from .vehicle import VehicleInfo, FeeRecord, FeeRule, EntryLog

Tortoise.init_models(['core.models', ], "models")

FeeRecordSchema = pydantic_model_creator(FeeRecord)
