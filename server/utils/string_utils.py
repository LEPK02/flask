import base64
from typing import List

import bcrypt


def serialize_name(name: str) -> str:
    return " ".join([n.capitalize() for n in name.strip().split(" ")])

def serialize_name_entries(rows: List[dict]) -> List[dict]:
    return [{**row, "name": serialize_name(row.get("name", ""))} for row in rows]

def encode_password(password: bytes) -> str:
    return base64.b64encode(password).decode('utf-8')

def decode_password(password: str) -> bytes:
    return base64.b64decode(password)

def hash_password(password: str) -> str|None:
    return encode_password(bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())) if password else None

def check_password(input_password: str, encoded_password: str) -> bool:
    return bcrypt.checkpw(input_password.encode('utf-8'), decode_password(encoded_password)) \
        if input_password and encoded_password else False