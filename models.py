import datetime
from config import DB
from peewee import *

from playhouse.migrate import *

import logging
import coloredlogs
logger = logging.getLogger(__name__)
coloredlogs.install(level=logging.DEBUG, logger=logger)

host = '127.0.0.1'
db = PostgresqlDatabase(
    'database', user='postgres2', password='1234',
    host=host, port=5433,
    autorollback=True, autoconnect=True
)


class BaseModel(Model):
    class Meta:
        database = db


class UserData(BaseModel):
    name = CharField()
    user_id = BigIntegerField(unique=True)
    expire_vpn_datetime = DateTimeField(null=True)
    wallet = IntegerField(default=0)

    def set_name(self, name):
        self.name = name
        self.save()

    def set_expire_vpn_datetime(self, expire_vpn_datetime):
        self.expire_vpn_datetime = expire_vpn_datetime
        self.save()

    def set_wallet(self, wallet):
        self.wallet = wallet
        self.save()


class Services(BaseModel):
    owner = ForeignKeyField(
        UserData, backref='services')
    name = CharField(default='name')
    plan = CharField(null=True)
    location = CharField()
    ip = CharField()
    port = CharField()
    transmission = CharField(default="ws")
    protocol = CharField(default='vless')
    status = BooleanField(default=True)
    expire_datetime = DateTimeField()
    traffic_used = FloatField(default=0.0)

    def set_owner(self, owner):
        self.owner = owner
        self.save()

    def set_name(self, name):
        self.name = name
        self.save()

    def set_port(self, port):
        self.port = port
        self.save()

    def set_status(self, status):
        self.status = status
        self.save()

    def set_expire_datetime(self, expire_datetime):
        self.expire_datetime = expire_datetime
        self.save()

    def set_ip(self, ip):
        self.ip = ip
        self.save()

    def set_protocol(self, protocol):
        self.protocol = protocol
        self.save()

    def set_transmission(self, transmission):
        self.transmission = transmission
        self.save()

    def set_traffic_used(self, traffic_used):
        self.traffic_used = traffic_used
        self.save()


class PayLoadUsers(BaseModel):
    owner = ForeignKeyField(
        UserData, backref='payloadusers')
    user_id = BigIntegerField(unique=True)


class ZarinpalPaying(BaseModel):
    owner = ForeignKeyField(
        UserData, backref='hubpaying')
    continuation = IntegerField(null=True)


class Payments(BaseModel):
    owner = ForeignKeyField(
        UserData, backref='payments')
    ref_id = BigIntegerField(null=True)
    amount = IntegerField()
    membership = CharField()
    # datetime of paymanet
    datetime = DateTimeField()


def create_db_tables():
    logger.info("Checking database...")
    try:
        logger.info("Database does not exist...")
        with db:
            db.create_tables(
                [UserData,Services, PayLoadUsers, ZarinpalPaying, Payments])
            logger.info("Tables created!")
    except:
        pass


create_db_tables()
# print(datetime.datetime.utcnow())
# for user in UserData.select():
#     print(user.expire_vpn_datetime)

migrator = PostgresqlMigrator(db)
# def alter_id():
#     print("--altering...")
#     migrate(
#         migrator.alter_column_type(
#             'userdata', 'user_id', BigIntegerField())
#     )
#     print("--altered!")

# def alter_id():
#     print("--altering...")
#     migrate(
#         migrator.add_column(
#             'services', 'plan', CharField(null=True))
#     )
#     print("--altered!")


# alter_id()
