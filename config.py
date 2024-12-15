import datetime
from flask_login import UserMixin
from peewee import SqliteDatabase, Model, IntegerField, CharField, TextField, TimestampField, ForeignKeyField

db = SqliteDatabase("db.sqlite")


class User(UserMixin, Model):
    id = IntegerField(primary_key=True)  # 数字で自動連番
    name = CharField(unique=True)
    email = CharField(unique=True)
    password = TextField()

    class Meta:
        database = db
        table_name = "users"


class Message(Model):
    id = IntegerField(primary_key=True)
    user = ForeignKeyField(User, backref="messages", on_delete="CASCADE")
    content = TextField()
    pub_date = TimestampField(default=datetime.datetime.now)
    reply_to = ForeignKeyField("self", backref="messages", on_delete="CASCADE", null=True)

    class Meta:
        database = db
        table_name = "messages"


db.create_tables([User, Message])
db.pragma("foreign_keys", 1, permanent=True)
