import json
import os
from functools import wraps
from typing import Callable, List, Type
from urllib.parse import quote_plus

from bson import ObjectId
from dotenv import load_dotenv
from flask import Response, make_response
from pydantic import BaseModel
from pydantic_core import ValidationError
from pymongo.collection import Collection
from pymongo.errors import *
from pymongo.mongo_client import MongoClient
from utils.logger import logger
from utils.response import make_error_response, make_success_response
from utils.string_utils import (check_password, hash_password,
                                serialize_name_entries)

from .models.case import Case
from .models.role import Role, RoleEnum
from .models.user import User


class AuthenticationError(Exception):
    pass

class UnauthorizedError(Exception):
    pass

def handle_db_error(func: Callable):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except InvalidOperation as e:
            logger.error(e)
            return make_error_response("Invalid query", 400)
        except AuthenticationError as e:
            logger.error(e)
            return make_error_response(f"Authentication failed", 401)
        except UnauthorizedError as e:
            logger.error(e)
            return make_error_response(f"Unauthorised", 403)
        except DuplicateKeyError as e:
            logger.error(e)
            return make_error_response(f"Value already exists", 409)
        except ValidationError as e: # Pydantic
            logger.error(e)
            return make_error_response("; ".join([err["msg"] for err in e.errors()]), 422)
        except WriteError as e:
            logger.error(e)
            return make_error_response(f"Failed to write to database", 500)
        except NetworkTimeout as e:
            logger.error(e)
            return make_error_response(f"Database network timeout", 502)
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(e)
            return make_error_response(f"Failed to connect to database", 503)
        except Exception as e:
            logger.error(e)
            return make_error_response(e.args[0], 500)
    return wrapper

# class InitGenerator(BaseModel):
#     model_config = ConfigDict(arbitrary_types_allowed=True)    
    
#     init_filename: str
#     Orm_class: Type[BaseClass]
#     table: Collection

class MongoDbClient():
    def __init__(self, init_db=False):
        load_dotenv()
        
        try:
            self.connect(
                os.getenv('MONGO_USERNAME'),
                quote_plus(os.getenv('MONGO_PASSWORD')),
                os.getenv('MONGO_CLUSTER'),
                os.getenv('MONGO_APP_NAME')
            )
            
            self.db = self.client["genvoice_db"]
            if init_db:
                self.init_roles_table()
                self.init_users_table()
                self.init_cases_table()
            
            # self.init_table_data([
            #     InitGenerator("users", Case, self.users_table),
            #     InitGenerator("roles", Role, self.roles_table),
            # ])
        except Exception as e:
            logger.error(e)

    def __del__(self):
        try:
            self.client.close()
            logger.info("Client connection closed")
        except Exception as e:
            logger.warning(e)
        finally:
            if hasattr(super(), "__del__"):
                super().__del__()
    
    def connect(self, username: str, password: str, cluster: str, app_name: str) -> None:
        self.client = MongoClient(
            f"mongodb+srv://{username}:{password}@{cluster}.mongodb.net/?retryWrites=true&w=majority&appName={app_name}",
            connectTimeoutMS=30000,
            socketTimeoutMS=30000
        )
        logger.info("Connected to client")
    
    def init_roles_table(self) -> None:
        self.roles_table = self.db["roles"]
        self.roles_table.create_index("role", unique=True)
        
        self.load_initial_rows(
            data=[Role(role=role).model_dump() for role in RoleEnum],
            table=self.roles_table,
            OrmClass=Role
        )
        logger.info("Initialized 'roles' table")

    def init_users_table(self) -> None:
        self.users_table = self.db["users"]
        self.users_table.create_index("username", unique=True)
        
        self.load_initial_rows(
            data=[{**row, "password": hash_password(str(row.get("password")))} for row in self.read_init_json("users")],
            table=self.users_table,
            OrmClass=User,
            validate=False
        )
        logger.info("Initialized 'users' table")
        
    def init_cases_table(self) -> None:
        self.cases_table = self.db["cases"]
        self.cases_table.create_index("name", unique=True)
        self.load_initial_rows(
            data=self.read_init_json("cases"),
            table=self.cases_table,
            OrmClass=Case
        )
        logger.info("Initialized 'cases' table")
        
    def read_init_json(self, filename: str, ) -> List[dict]:
        try:
            with open(f"{os.getcwd()}/db/init/{filename}.json", 'r') as init_file:
                data = json.load(init_file)
                if isinstance(data, dict):
                    data = [data]

                return data
        except Exception as e:
            logger.warning(f"Failed to load data from init file '{os.getcwd()}/db/init/{filename}.json'\n\t{e}")
            return []

    def load_initial_rows(
        self,
        data: List[dict],
        table: Collection,
        OrmClass: Type[BaseModel],
        validate: bool = True
    ) -> None:
        for row in ([OrmClass(**r).model_dump() for r in data] if validate else data):
            try:
                table.update_one(row, {"$setOnInsert": row}, upsert=True)
            except Exception as e:
                logger.warning(f"Failed to load row into {table.name}\n\t{e}\n\t{json.dumps(row)}")

    # def init_table_data(init_generators: List[InitGenerator]) -> None:
    #     for generator in init_generators:
    #         try:
    #             with open(f"./init/{generator.init_filename}.json", 'r') as init_file:
    #                 data = json.load(init_file)
    #                 if isinstance(data, dict):
    #                     data = [data]

    #                 for row in list(map(lambda r: generator.Orm_class(**r).dict())):
    #                     generator.table.update_one(row, {"$setOnInsert": row}, upsert=True)
                        
    #         except Exception as e:
    #             logger = logging.getLogger()
    #             logger.warning(e)
    
    def get_user_by_id(self, user_id: str) -> dict|None:
        if not user_id:
            raise InvalidOperation("Missing user_id")
        return self.users_table.find_one({'_id': ObjectId(user_id)})

    @handle_db_error
    def register_user(self, data: dict) -> Response:
        data = User(**data).model_dump()
        result = self.users_table.find_one({'username': data.get("username")})
        if result:
            raise DuplicateKeyError("User already exists")
        
        result = self.users_table.insert_one(data)
        data.update({"_id": str(result.inserted_id)})
        return make_response(data, 200)
    
    @handle_db_error
    def login(self, data: dict) -> Response:
        if not (data.get("username") and data.get("password")):
            raise InvalidOperation("Missing parameters username and/or password")
        result = self.users_table.find_one({'username': str(data.get("username")).strip().lower()})
        if not result or not check_password(data.get("password"), result["password"]):
            raise AuthenticationError()

        return make_response({**result, '_id': str(result['_id'])}, 200)
    
    @handle_db_error
    def promote_user(self, data: dict) -> Response:
        return self.change_user_role(data, RoleEnum.SENIOR)
    
    @handle_db_error
    def demote_user(self, data: dict) -> Response:
        return self.change_user_role(data, RoleEnum.JUNIOR)
        
    @handle_db_error
    def change_user_role(self, data: dict, to_role: RoleEnum) -> Response:
        res: Response = self.login(data)
        if 200 <= res.status_code <= 299:
            payload = json.loads(res.get_data().decode('utf-8'))
            if payload.get('role') and payload.get('role') == to_role.value:
                return make_success_response(f"User is already a {to_role.value}")
        
            result = self.users_table.update_one(
                {'_id': ObjectId(payload.get("_id"))},
                { "$set": { "role": to_role.value } }
            )
            if result.acknowledged:
                return make_success_response(f"User {'promoted' if to_role == RoleEnum.SENIOR else 'demoted'} successfully")
            raise WriteError()

        return res
    
    @handle_db_error
    def get_cases(self) -> Response:
        return make_response(
            [{**case, '_id': str(case['_id'])} for case in serialize_name_entries(self.cases_table.find())],
            200
        )
    
    @handle_db_error
    def upsert_case(self, data: dict) -> Response:
        data = Case(**data).model_dump()
        result = self.cases_table.update_one(
            {'name': data.get("name")},
            {"$set": data},
            upsert=True
        )
        
        id = result.upserted_id
        if not id:
            existing_doc = self.cases_table.find_one({"name": data["name"]})
            id = str(existing_doc["_id"])
        data.update({"_id": id})
        
        return make_response(data, 200)