from pydantic import BaseModel, field_serializer, field_validator
from utils import string_utils

class Case(BaseModel):
    name: str
    description: str

    @field_validator('name', mode='before')
    @classmethod
    def parse_name(cls, name: str) -> str:
        return name.strip().lower()
    
    @field_validator('name', mode='before')
    @classmethod
    def parse_description(cls, name: str) -> str:
        return name.strip()
    
    @field_serializer('name')
    def serialize_name(self, name: str, _info):
        return string_utils.serialize_name(name)