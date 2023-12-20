from inspect import getmro, Parameter, signature
from abc import ABC
from functools import wraps

from fastapi import Depends, APIRouter
from pydantic import create_model, BaseModel
from sqlalchemy.orm import Session

from petshop.core.database import get_db
from petshop.utils import parse_field_info
from petshop.mixins.base import AutoCrudMixinBase

__all__ = ["get_db", "Depends"]


class CreateParams(ABC):
    required_params = None
    pop_params = None
    description = None
    summary = None
    operation_id = None
    tags = None


class CreateMixin(object):

    @classmethod
    def get_create_schema(cls):
        schema_cls = getmro(cls)[0]
        properties = schema_cls.model_json_schema().get('properties',{})
        required_properties = schema_cls.model_json_schema().get('required',[])

        field_definitions = {
            name: parse_field_info(field_info,name in required_properties)
            for name, field_info in properties.items()
            if name not in schema_cls.create_cfg.pop_params
        }

        return create_model(
            schema_cls.__name__,
            __base__ = BaseModel,
            **field_definitions,
        )


    @classmethod
    def controller_factory_create(cls):

        schema_cls = getmro(cls)[0]

        parameters = [
            Parameter(
                schema_cls.__name__.lower(),
                Parameter.POSITIONAL_OR_KEYWORD, 
                default=..., 
                annotation=cls.get_create_schema()
            ),
            Parameter(
                'db',
                Parameter.POSITIONAL_OR_KEYWORD, 
                default=Depends(get_db), 
                annotation=Session
            )
        ]

        def inner(*args, **kwargs) -> cls:
            db = kwargs.get('db')
            body = kwargs.get(schema_cls.__name__.lower())

            obj = cls(**body.model_dump())

            db.add(obj)
            db.commit()
            db.refresh(obj)
            return obj

        @wraps(inner)
        def f(*args, **kwargs):
            return inner(*args, **kwargs)

        # Override signature
        sig = signature(inner)
        sig = sig.replace(parameters=parameters)
        f.__signature__ = sig

        return f


    @classmethod
    def build_create_route(cls):

        schema_cls = getmro(cls)[0]

        if not hasattr(schema_cls, 'router'):
            schema_cls.router = APIRouter(
                prefix=schema_cls.router_cfg.prefix,
                tags=schema_cls.router_cfg.tags,
                dependencies=schema_cls.router_cfg.dependencies,
            )

        schema_cls.router.add_api_route(
            "",
            cls.controller_factory_create(),
            description=schema_cls.create_cfg.description,
            summary=schema_cls.create_cfg.summary,
            tags=schema_cls.create_cfg.tags,
            operation_id=schema_cls.create_cfg.operation_id,
            methods=["POST"],
            status_code=200,
            response_model=cls,
        )