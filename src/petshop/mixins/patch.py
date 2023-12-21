from inspect import getmro, Parameter, signature
from typing import Optional
from abc import ABC
from functools import wraps
from datetime import date, datetime

from fastapi import Depends, APIRouter
from pydantic import create_model, BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import or_

from petshop.core.database import get_db
from petshop.utils import parse_field_info, parse_type, get_base_type
from petshop.mixins.base import AutoCrudMixinBase



class PatchParams(ABC):
    primary_key = None
    patchable_params = None
    nonpatchable_params = None

    # router method
    description = None
    summary = None
    operation_id = None
    tags = None

class PatchMixin(object):

    @classmethod
    def get_patch_schema(cls):

        schema_cls = getmro(cls)[0]
        properties = schema_cls.model_json_schema().get('properties',{})
        required_properties = schema_cls.model_json_schema().get('required',[])

        if schema_cls.patch_cfg.patchable_params is None:
            if schema_cls.patch_cfg.nonpatchable_params is None:
                # default to all params
                schema_cls.patch_cfg.patchable_params = [p for p in list(properties.keys()) if p!=schema_cls.patch_cfg.primary_key]
            else:
                schema_cls.patch_cfg.patchable_params = [
                    p for p in list(properties.keys()) 
                    if (
                        (p!=schema_cls.patch_cfg.primary_key) and 
                        (p not in schema_cls.patch_cfg.nonpatchable_params)
                    )
                ]

        field_definitions = {
            name: parse_field_info(field_info,required=False)
            for name, field_info in properties.items()
            if name in schema_cls.patch_cfg.patchable_params
        }

        return create_model(
            schema_cls.__name__,
            __base__ = BaseModel,
            **field_definitions,
        )


    @classmethod
    def controller_factory_patch(cls):

        schema_cls = getmro(cls)[0]

        parameters = [
            Parameter(
                schema_cls.patch_cfg.primary_key,
                Parameter.POSITIONAL_OR_KEYWORD, 
                default=..., 
                annotation=str
            ),
            Parameter(
                'patch',
                Parameter.POSITIONAL_OR_KEYWORD, 
                default=..., 
                annotation=cls.get_patch_schema()
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
            patch = kwargs.get('patch')


            Q = db.query(cls)
            Q = Q.filter(getattr(cls, schema_cls.patch_cfg.primary_key) == eval({schema_cls.patch_cfg.primary_key}))
            obj = Q.first()

            for name, val in patch.model_dump().items():
                if val is not None:
                    setattr(obj, name, val)

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
    def build_patch_route(cls):

        schema_cls = getmro(cls)[0]

        if not hasattr(schema_cls, 'router'):
            schema_cls.router = APIRouter(
                prefix=schema_cls.router_cfg.prefix,
                tags=schema_cls.router_cfg.tags,
                dependencies=schema_cls.router_cfg.dependencies,
            )

        schema_cls.router.add_api_route(
            "/{id}",
            cls.controller_factory_patch(),
            description=schema_cls.patch_cfg.description,
            summary=schema_cls.patch_cfg.summary,
            tags=schema_cls.patch_cfg.tags,
            operation_id=schema_cls.patch_cfg.operation_id,
            methods=["PATCH"],
            status_code=200,
            response_model=cls,
        )