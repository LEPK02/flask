from enum import StrEnum

from utils.constants import MAX_PASSWORD_LENGTH, MIN_PASSWORD_LENGTH
from pydantic import BaseModel


class PydanticError(StrEnum):
    USERNAME_INVALID_CHARACTER = 'Username should only contain letters, numbers and underscores'
    USERNAME_NUMBER_START = 'Username cannot begin with a number'
    PASSWORD_MISSING_UPPERCASE = 'Password should contain at least one uppercase character'
    PASSWORD_MISSING_LOWERCASE = 'Password should contain at least one lowercase character'
    PASSWORD_MISSING_SPECIAL = 'Password should contain at least one special character'
    PASSWORD_TOO_SHORT = f"Password should be at least {MIN_PASSWORD_LENGTH} characters long"
    PASSWORD_TOO_LONG = f"Password should be at least {MAX_PASSWORD_LENGTH} characters long"

class Error(BaseModel):
    pydantic_error: PydanticError
    status_code: int