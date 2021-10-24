import enum
from decimal import Decimal

from fastapi import HTTPException
from pydantic import constr, conint
from tortoise import Model, fields, timezone
from tortoise.contrib.pydantic import pydantic_model_creator
from tortoise.exceptions import DoesNotExist, ValidationError
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
    unit_fee = fields.DecimalField(max_digits=128, decimal_places=16, description="每秒钟的费用 单位CNY")
    valid = fields.BooleanField(default=True, description="是否有效")


async def add_fee_rule(vehicle_type: VehicleType, unit_fee: Decimal, priority: int = 0) -> FeeRule:
    return await FeeRule.create(vehicle_type=vehicle_type, unit_fee=unit_fee, priority=priority)


async def deactivate_fee_rule(fid: int) -> FeeRule:
    fee_rule = await FeeRule.get(id=fid)
    fee_rule.valid = False
    await fee_rule.save()
    return fee_rule


async def get_fee_rule(vehicle_type: VehicleType) -> FeeRule:
    result = await FeeRule.filter(vehicle_type=vehicle_type, valid=True).order_by("-priority").first()
    if result is None:
        raise DoesNotExist()
    return result


class FeeRecord(Model):
    id = fields.UUIDField(pk=True)
    belongs_to: fields.ForeignKeyRelation['EntryLog'] = fields.ForeignKeyField(
        model_name='models.EntryLog', related_name='fee_records',
    )
    created_at = fields.DatetimeField(auto_now_add=True)
    time_parked = fields.IntField(description="停车时间 单位秒")
    total_fee = fields.DecimalField(max_digits=128, decimal_places=16)
    paid = fields.BooleanField(default=False, description="是否支付")
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
    related_records: fields.ReverseRelation['FeeRecord']


async def generate_fee_record(entry_log_id: conint(ge=0)) -> FeeRecord:
    entry_log = await EntryLog.get(id=entry_log_id)
    if entry_log.end_time is None:
        raise HTTPException(406, dict(
            detail='target entry_log has no end time',
        ))
    fee_rule = await get_fee_rule((await entry_log.belongs_to).type)
    diff = entry_log.end_time - entry_log.start_time
    time_parked = diff.total_seconds()
    return await FeeRecord.create(
        belongs_to=entry_log,
        time_parked=time_parked,
        total_fee=Decimal(fee_rule.unit_fee) * Decimal(time_parked),
        based_rule=fee_rule,
    )


EntryLogSchemaLite = pydantic_model_creator(EntryLog)


async def add_entry_log(vehicle_plate: constr(max_length=32, to_lower=True)) -> EntryLog:
    vehicle_info, _ = await VehicleInfo.get_or_create(plate=vehicle_plate)
    return await EntryLog.create(belongs_to=vehicle_info)


async def add_leave_log(vehicle_plate: constr(max_length=32, to_lower=True)) -> EntryLog:
    vehicle_info, _ = await VehicleInfo.get_or_create(plate=vehicle_plate)
    query_set: QuerySet[EntryLog] = vehicle_info.entry_records.filter(end_time=None)
    cache = await query_set.first()
    if cache is None:
        raise DoesNotExist()
    await query_set.update(end_time=timezone.now())
    return await EntryLog.get(id=cache.id)


FeeRuleSchemaLite = pydantic_model_creator(FeeRule)
