from umongo import Document
from umongo.fields import *
from internal.databasemanager import instance


@instance.register
class GameOfLifeDoc(Document):
    attribute = StringField(required=True, max_length=200)
