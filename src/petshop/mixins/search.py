from inspect import getmro, Parameter, signature
from abc import ABC
from functools import wraps
from datetime import date, datetime

from fastapi import Depends, APIRouter
from pydantic import create_model, BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import or_

from petshop.core.database import get_db
from petshop.utils import parse_field_info
from petshop.mixins.base import AutoCrudMixinBase

__all__ = ["get_db", "Depends"]


class SearchParams(ABC):
    required_params = None
    pop_params = None

    # for float, int, datetime:
    search_eq = None # is precisely equal to
    search_gt = None # greater than, list[str] | bool
    search_gte = None # greater than or equal to, list[str] | bool
    search_lt = None # less than, list[str] | bool
    search_lte = None # less than or equal to, list[str] | bool

    # for str:
    search_contains = None # string contains search
    search_trgm = None # string trigram search

    # router method
    description = None
    summary = None
    operation_id = None
    tags = None


class SearchMixin(object):

    @classmethod
    def get_search_schema(cls):
        schema_cls = getmro(cls)[0]
        properties = schema_cls.model_json_schema().get('properties',{})
        required_properties = schema_cls.model_json_schema().get('required',[])

        field_definitions = {
            name: parse_field_info(field_info,name in required_properties)
            for name, field_info in properties.items()
            if name not in schema_cls.create_cfg.pop_params
        }

        model = create_model(
            schema_cls.__name__,
            __base__ = BaseModel,
            **field_definitions,
        )

        def bridge()

        model.bridge = 

        return model


    @classmethod
    def controller_factory_search(cls):

        schema_cls = getmro(cls)[0]

        parameters = [
            Parameter(
                'query',
                Parameter.POSITIONAL_OR_KEYWORD, 
                default=Depends(cls.get_search_schema().bridge), 
                annotation=cls.get_search_schema()
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
            query = kwargs.get('query')

            Q = db.query(cls)

            for name, val in query.model_dump().items():
                if val is not None:
                    param_name = '_'.join(name.split('_')[:-1])

                    # check type of param

                    if param_type in [int,float,date,datetime]:

                        compare_type = name.split('_')[-1]

                        if compare_type == 'eq':
                            Q = Q.filter(getattr(cls, param_name) == val)
                        elif compare_type == 'gte':
                            Q = Q.filter(getattr(cls, param_name) >= val)
                        elif compare_type == 'gt':
                            Q = Q.filter(getattr(cls, param_name) > val)
                        elif compare_type == 'lte':
                            Q = Q.filter(getattr(cls, param_name) <= val)
                        elif compare_type == 'lt':
                            Q = Q.filter(getattr(cls, param_name) < val)

                    if param_type == str:

                        if schema_cls.search_cfg.search_contains and schema_cls.search_cfg.search_trgm:
                            # if contains AND trgm
                            Q = Q.filter(
                                _or(
                                    getattr(cls, param_name).contains(val),
                                    func.similarity(getattr(cls, param_name), val) > query.threshold
                                )
                            )

                        elif schema_cls.search_cfg.search_contains:
                            # if just contains
                            Q = Q.filter(getattr(cls, param_name).contains(val))

                        elif schema_cls.search_cfg.search_trgm:
                            # if just trgm
                            Q = Q.filter(func.similarity(getattr(cls, param_name),val)> query.threshold)

                        else:
                            # else jsut extact match
                            Q = Q.filter(getattr(cls, param_name) == val)

            # pagination
            # Count total results (without fetching)
            n_total_results = db.query(func.count()).select_from(Q.subquery()).scalar()

            # Get filtered set of results
            filtered_results = (
                Q.offset(query.page * query.limit).limit(query.limit).all()
            )

            return filtered_results

        @wraps(inner)
        def f(*args, **kwargs):
            return inner(*args, **kwargs)

        # Override signature
        sig = signature(inner)
        sig = sig.replace(parameters=parameters)
        f.__signature__ = sig

        return f


    @classmethod
    def build_search_route(cls):

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