from inspect import getmro, Parameter, signature
from abc import ABC
from functools import wraps

from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session

from petshop.core.database import get_db
from petshop.core import exceptions
from petshop.mixins.base import AutoCrudMixinBase


class DeleteParams(ABC):
    primary_key = None
    description = None
    summary = None
    operation_id = None
    tags = None


class DeleteMixin(object):

    @classmethod
    def controller_factory_delete(cls):
        schema_cls = getmro(cls)[0]

        parameters = [
            Parameter(
                schema_cls.read_cfg.primary_key,
                Parameter.POSITIONAL_OR_KEYWORD, 
                default=..., 
                annotation=str
            ),
            Parameter(
                'db',
                Parameter.POSITIONAL_OR_KEYWORD, 
                default=Depends(get_db), 
                annotation=Session
            )
        ]

        def inner(*args, **kwargs) -> int:

            try:

                db = kwargs.get('db')
                primary_key = kwargs.get(schema_cls.read_cfg.primary_key)

                Q = db.query(cls)
                Q = Q.filter(getattr(cls, schema_cls.read_cfg.primary_key) == primary_key)
                n_deleted = Q.delete()

                if n_deleted ==0:
                    raise exceptions.NotFoundError

                db.commit()
                return n_deleted

            except Exception as e:
                raise exceptions.handler(e)
            finally:
                import traceback
                print(traceback.format_exc())
            

        @wraps(inner)
        def f(*args, **kwargs):
            return inner(*args, **kwargs)

        # Override signature
        sig = signature(inner)
        sig = sig.replace(parameters=parameters)
        f.__signature__ = sig

        return f


    @classmethod
    def build_delete_route(cls):

        schema_cls = getmro(cls)[0]

        if not hasattr(schema_cls, 'router'):
            schema_cls.router = APIRouter(
                prefix=schema_cls.router_cfg.prefix,
                tags=schema_cls.router_cfg.tags,
                dependencies=schema_cls.router_cfg.dependencies,
            )


        schema_cls.router.add_api_route(
            "/{id}",
            cls.controller_factory_delete(),
            description=schema_cls.delete_cfg.description,
            summary=schema_cls.delete_cfg.summary,
            tags=schema_cls.delete_cfg.tags,
            operation_id=schema_cls.delete_cfg.operation_id,
            methods=["DELETE"],
            status_code=200,
            response_model=int,
        )