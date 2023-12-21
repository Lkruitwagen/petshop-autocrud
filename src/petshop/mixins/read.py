from inspect import getmro, Parameter, signature
from abc import ABC
from functools import wraps

from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session

from petshop.core.database import get_db
from petshop.core import exceptions
from petshop.mixins.base import AutoCrudMixinBase

# __all__ = ["get_db", "Depends"] # Method 1 only


class ReadParams(ABC):
    primary_key = None
    description = None
    summary = None
    operation_id = None
    tags = None


class ReadMixin(object):

    @classmethod
    def controller_factory_read(cls):
        schema_cls = getmro(cls)[0]

        # METHOD 1: using _exec_
        # arg_statement = f"{schema_cls.read_cfg.primary_key}: str, db = Depends(get_db)"

        #function_code = f"""async def f({arg_statement}):
        #    return db.query(cls).filter(cls.{schema_cls.read_cfg.primary_key} == {schema_cls.read_cfg.primary_key}).first()
        #"""

        #code = compile(function_code, "<string>", "exec")

        #all_obs = {}
        #all_obs.update(globals())
        #all_obs.update(locals())
        #exec(code, all_obs, globals())  # , locals(), globals())


        # METHOD 2: using params and function signature
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

        def inner(*args, **kwargs) -> cls:

            try:
                db = kwargs.get('db')
                primary_key = kwargs.get(schema_cls.read_cfg.primary_key)
                Q = db.query(cls)
                Q = Q.filter(getattr(cls, schema_cls.read_cfg.primary_key) == primary_key)
                obj = Q.first()

                if not obj:
                    raise exceptions.NotFoundError
                return obj

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
    def build_read_route(cls):

        schema_cls = getmro(cls)[0]

        if not hasattr(schema_cls, 'router'):
            schema_cls.router = APIRouter(
                prefix=schema_cls.router_cfg.prefix,
                tags=schema_cls.router_cfg.tags,
                dependencies=schema_cls.router_cfg.dependencies,
            )


        schema_cls.router.add_api_route(
            "/{id}",
            cls.controller_factory_read(),
            description=schema_cls.read_cfg.description,
            summary=schema_cls.read_cfg.summary,
            tags=schema_cls.read_cfg.tags,
            operation_id=schema_cls.read_cfg.operation_id,
            methods=["GET"],
            status_code=200,
            response_model=cls,
        )