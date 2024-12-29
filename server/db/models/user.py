import re

import bcrypt
from pydantic import BaseModel, Field, field_serializer, field_validator
from pydantic_core import PydanticCustomError
from utils import string_utils
from utils.constants import MAX_PASSWORD_LENGTH, MIN_PASSWORD_LENGTH

from .error import PydanticError
from .role import RoleEnum


class User(BaseModel, use_enum_values=True):
    name: str
    username: str
    password: str
    role: RoleEnum = Field(default=RoleEnum.JUNIOR)

    @field_validator('name', mode='before')
    @classmethod
    def parse_name(cls, name: str) -> str:
        return name.strip().lower()
    
    @field_validator('username', mode='before')
    @classmethod
    def validate_username(cls, username: str) -> str:
        username = username.strip().lower()
        if re.search(r"[^A-Za-z0-9_]", username):
            raise PydanticCustomError(
                PydanticError.USERNAME_INVALID_CHARACTER.name,
                PydanticError.USERNAME_INVALID_CHARACTER.value
            )
        if re.match(r"^[0-9]", username):
            raise PydanticCustomError(
                PydanticError.USERNAME_NUMBER_START.name,
                PydanticError.USERNAME_NUMBER_START.value
            )
        return username
    
    @field_validator('password', mode='before')
    @classmethod
    def validate_password(cls, password: str) -> str:
        if not re.search(r"[A-Z]", password):
            raise PydanticCustomError(
                PydanticError.PASSWORD_MISSING_UPPERCASE.name,
                PydanticError.PASSWORD_MISSING_UPPERCASE.value
            )
        if not re.search(r"[a-z]", password):
            raise PydanticCustomError(
                PydanticError.PASSWORD_MISSING_LOWERCASE.name,
                PydanticError.PASSWORD_MISSING_LOWERCASE.value
            )
        if not re.search(r"[$&+,:;=?@#|'<>.^*()%!-]", password):
            raise PydanticCustomError(
                PydanticError.PASSWORD_MISSING_SPECIAL.name,
                PydanticError.PASSWORD_MISSING_SPECIAL.value
            )
        if len(password) < MIN_PASSWORD_LENGTH:
            raise PydanticCustomError(
                PydanticError.PASSWORD_TOO_SHORT.name,
                PydanticError.PASSWORD_TOO_SHORT.value
            )
        if len(password) > MAX_PASSWORD_LENGTH:
            raise PydanticCustomError(
                PydanticError.PASSWORD_TOO_LONG.name,
                PydanticError.PASSWORD_TOO_LONG.value
            )

        return string_utils.hash_password(password)
    
    @field_serializer('name')
    def serialize_name(self, name: str, _info):
        return string_utils.serialize_name(name)