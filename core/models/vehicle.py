import enum

from tortoise import Model, fields


class VehicleType(enum.IntEnum):
    UNKNOWN = 0
    CAR = 1


class VehicleInfo(Model):
    id = fields.BigIntField(pk=True)
    plate = fields.CharField(max_length=32, description="车牌信息")
    type = fields.IntEnumField(VehicleType, default=VehicleType.UNKNOWN, description="车辆类型")
    fee_records: fields.ReverseRelation["FeeRecord"]
    entry_records: fields.ReverseRelation['EntryLog']


class FeeRule(Model):
    id = fields.IntField(pk=True)
    vehicle_type = fields.IntEnumField(VehicleType, description="对应的载具类型")
    priority = fields.SmallIntField(default=0, description="优先级 越大优先级越高")
    unit_fee = fields.DecimalField(max_digits=5, decimal_places=2, description="每分钟的费用 单位CNY")
    valid = fields.BooleanField(default=True, description="是否有效")
    related_records: fields.ReverseRelation['FeeRecord']


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
