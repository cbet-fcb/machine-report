# sample code for objects.py
# from mongoDb import mongoDb
# from dateutil import parser
# import datetime
# from utils import *
# import re
# from pydantic import BaseModel, Field, field_validator
# from typing import Optional, Union, List

# db = mongoDb()

# class User(BaseModel):
#     id: Optional[str] = Field(None, alias='_id')
#     # id: int = Field(..., alias='_id')
#     createdAt: datetime.datetime
#     isApproved: bool
#     displayName: str
#     email: str
#     roles: dict
#     version: int = Field(..., alias='_version')
#     image: str

#     @field_validator("createdAt", mode='before', check_fields=True)
#     def parse_created_at(cls, value):
#         if isinstance(value, datetime.datetime):
#             return value
#         elif isinstance(value, str):
#             for transformDate in ("%Y-%m-%dT%H:%M:%S",
#                                   "%a, %d %b %Y %H:%M:%S %Z"):
#                 try:
#                     return datetime.datetime.strptime(value, transformDate)
#                 except ValueError:
#                     continue
#             raise ValueError("createdAt must be a valid datetime string")
#         elif isinstance(value, (int, float)):
#             return datetime.datetime.fromtimestamp(value)
#         raise ValueError(
#             "createdAt must be a valid datetime, string, or timestamp")

#     def to_dict(self):
#         return {
#             '_id': self.id,
#             'createdAt': self.createdAt,
#             'isApproved': self.isApproved,
#             'displayName': self.displayName,
#             'image': self.image,
#             'email': self.email,
#             'roles': self.roles,
#             '_version': self._version
#         }

