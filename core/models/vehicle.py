import enum
from datetime import datetime
from decimal import Decimal

from pydantic import constr
from tortoise import Model, fields
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.exceptions import DoesNotExist
from tortoise.queryset import QuerySet


class VehicleType(enum.IntEnum):
    TESTING = -1
    UNKNOWN = 0
    CAR = 1


class VehicleInfo(Model):
    id = fields.BigIntField(pk=True)
    plate = fields.CharField(max_length=32, index=True, unique=True, description="车牌信息")
    type = fields.IntEnumField(VehicleType, default=VehicleType.UNKNOWN, description="车辆类型")
    fee_records: fields.ReverseRelation["FeeRecord"]
    entry_records: fields.ReverseRelation['EntryLog']
    operation_logs: fields.ReverseRelation['AuditLog']


class FeeRule(Model):
    id = fields.IntField(pk=True)
    vehicle_type = fields.IntEnumField(VehicleType, description="对应的载具类型")
    priority = fields.SmallIntField(default=0, description="优先级 越大优先级越高")
    unit_fee = fields.DecimalField(max_digits=5, decimal_places=2, description="每分钟的费用 单位CNY")
    valid = fields.BooleanField(default=True, description="是否有效")
    related_records: fields.ReverseRelation['FeeRecord']


async def add_fee_rule(vehicle_type: VehicleType, unit_fee: Decimal, priority: int = 0) -> FeeRule:
    return await FeeRule.create(vehicle_type=vehicle_type, unit_fee=unit_fee, priority=priority)


async def deactivate_fee_rule(fid: int) -> FeeRule:
    fee_rule = await FeeRule.get(id=fid)
    fee_rule.valid = False
    await fee_rule.save()
    return fee_rule


class FeeRecord(Model):
    id = fields.UUIDField(pk=True)
    belongs_to: fields.ForeignKeyRelation[VehicleInfo] = fields.ForeignKeyField(
        model_name='models.VehicleInfo', related_name='fee_records',
    )
    created_at = fields.DatetimeField(auto_now_add=True)
    time_parked = fields.IntField(description="停车时间")
    based_rule: fields.ForeignKeyRelation[FeeRule] = fields.ForeignKeyField(
        model_name='models.FeeRule', related_name='related_records', on_delete=fields.RESTRICT,
    )


class EntryLog(Model):
    id = fields.BigIntField(pk=True)
    belongs_to: fields.ForeignKeyRelation[VehicleInfo] = fields.ForeignKeyField(
        model_name='models.VehicleInfo', related_name='entry_records',
    )
    start_time = fields.DatetimeField(auto_now_add=True)
    end_time = fields.DatetimeField(null=True, default=None)


EntryLogSchemaLite = pydantic_model_creator(EntryLog)


async def add_entry_log(vehicle_plate: constr(max_length=32, to_lower=True)) -> EntryLog:
    vehicle_info, _ = await VehicleInfo.get_or_create(plate=vehicle_plate)
    return await EntryLog.create(belongs_to=vehicle_info)


async def add_leave_log(vehicle_plate: constr(max_length=32, to_lower=True)) -> EntryLog:
    vehicle_info, _ = await VehicleInfo.get_or_create(plate=vehicle_plate)
    query_set: QuerySet[EntryLog] = vehicle_info.entry_records.filter(end_time=None)
    if query_set.count() == 0:
        raise DoesNotExist()
    cache = await query_set.first()
    await query_set.update(end_time=datetime.now())
    return await EntryLog.get(id=cache.id)


FeeRuleSchemaLite = pydantic_model_creator(FeeRule)
