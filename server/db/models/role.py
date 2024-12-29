from enum import StrEnum

from pydantic import BaseModel


class RoleEnum(StrEnum):
    JUNIOR = "Junior"
    SENIOR = "Senior"
    ADMIN = "Admin"

class Role(BaseModel, use_enum_values=True):
    role: RoleEnum = RoleEnum.JUNIOR