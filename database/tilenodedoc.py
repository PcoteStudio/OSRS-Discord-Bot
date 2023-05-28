from umongo import Document
from umongo.fields import *
from bson.objectid import ObjectId
from internal.databasemanager import instance


@instance.register
class TileNodeDoc(Document):
    _id = ObjectIdField(unique=True, default=ObjectId)
    index = IntegerField(unique=True)
    task = StringField()
    exits = ListField(ObjectIdField())
