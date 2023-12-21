from inspect import getmro, Parameter, signature
from typing import Optional
from abc import ABC
from functools import wraps
from datetime import date, datetime

from fastapi import Depends, APIRouter
from pydantic import create_model, BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import or_, func

from petshop.core.database import get_db
from petshop.utils import parse_field_info, parse_type, get_base_type
from petshop.mixins.base import AutoCrudMixinBase

__all__ = ["get_db", "Depends"]


class SearchParams(ABC):
    required_params = None
    pop_params = None

    results_limit = None

    # for float, int, datetime:
    search_eq = None # is precisely equal to
    search_gt = None # greater than, list[str] | bool
    search_gte = None # greater than or equal to, list[str] | bool
    search_lt = None # less than, list[str] | bool
    search_lte = None # less than or equal to, list[str] | bool

    # for str:
    search_contains = None # string contains search
    search_trgm = None # string trigram search
    search_trgm_threshold = None

    # router method
    description = None
    summary = None
    operation_id = None
    tags = None

class SearchMixin(object):

    @classmethod
    def get_search_schema(cls):

        def maybe_add_param(search_cfg, name):
            add_param_fields = []

            # equals param
            if isinstance(search_cfg.search_eq, bool):
                if search_cfg.search_eq:
                    add_param_fields.append(name+'_eq')
            elif isinstance(search_cfg.search_eq, list):
                if name in search_cfg.search_eq:
                    add_param_fields.append(name+'_eq')

            # greater than param
            if isinstance(search_cfg.search_gt, bool):
                if search_cfg.search_gt:
                    add_param_fields.append(name+'_gt')
            elif isinstance(search_cfg.search_gt, list):
                if name in search_cfg.search_gt:
                    add_param_fields.append(name+'_gt')

            # greater than or equal param
            if isinstance(search_cfg.search_gte, bool):
                if search_cfg.search_gte:
                    add_param_fields.append(name+'_gte')
            elif isinstance(search_cfg.search_gte, list):
                if name in search_cfg.search_gte:
                    add_param_fields.append(name+'_gte')

            # less than param
            if isinstance(search_cfg.search_lt, bool):
                if search_cfg.search_lt:
                    add_param_fields.append(name+'_lt')
            elif isinstance(search_cfg.search_lt, list):
                if name in search_cfg.search_lt:
                    add_param_fields.append(name+'_lt')

            # less than or equal param
            if isinstance(search_cfg.search_lte, bool):
                if search_cfg.search_lte:
                    add_param_fields.append(name+'_lte')
            elif isinstance(search_cfg.search_lte, list):
                if name in search_cfg.search_lte:
                    add_param_fields.append(name+'_lte')

            return add_param_fields

        schema_cls = getmro(cls)[0]
        properties = schema_cls.model_json_schema().get('properties',{})
        required_properties = schema_cls.model_json_schema().get('required',[])

        # build the query fields
        query_fields = {}
        for name, field_info in properties.items():
            if name not in schema_cls.search_cfg.pop_params:

                type_annotation = parse_type(field_info)

                base_type = get_base_type(type_annotation)

                if base_type in [float, int, date, datetime]:
                    # handle filtering on numeric data
                    add_fields = maybe_add_param(schema_cls.search_cfg, name)

                    for new_field in add_fields:
                        if name in schema_cls.search_cfg.required_params:
                            query_fields[new_field] = (
                                base_type, 
                                Field(
                                    title=new_field,
                                    default=...
                                )
                            )
                        else:
                            query_fields[new_field] = (
                                Optional[base_type], 
                                Field(
                                    title=new_field,
                                    default=None
                                )
                            )

                elif base_type ==str:
                    # add filtering for string data
                    if name in schema_cls.search_cfg.required_params:
                        query_fields[name] = (str, Field(title=name, default=...))
                    else:
                        query_fields[name] = (Optional[str], Field(title=name, default=None))

                else:
                    # name
                    print ('unknown', name, base_type)
                    print (repr(base_type))

        # add pagination
        query_fields['limit'] = (int, Field(title='limit', default=schema_cls.search_cfg.results_limit))
        query_fields['page'] = (int, Field(title='page', default=0))

        # maybe add trgm threshold
        if schema_cls.search_cfg.search_trgm is not None:
            query_fields['threshold'] = (float, Field(title='threshold', default=0.7))



        query_model = create_model(
            schema_cls.__name__,
            __base__ = BaseModel,
            **query_fields,
        )

        bridge_parameters = [
            Parameter(
                name,
                Parameter.POSITIONAL_OR_KEYWORD, 
                default=field.default, 
                annotation=type_annotation
            )
            for name, (type_annotation, field) in query_fields.items()
        ]

        def bridge_inner(*args, **kwargs) -> cls:
            return query_model(**kwargs)
            

        @wraps(bridge_inner)
        def bridge(*args, **kwargs):
            return bridge_inner(*args, **kwargs)

        # Override signature
        sig = signature(bridge_inner)
        sig = sig.replace(parameters=bridge_parameters)
        bridge.__signature__ = sig

        query_model.bridge = bridge

        return query_model


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

        def inner(*args, **kwargs) -> list[cls]:
            db = kwargs.get('db')
            query = kwargs.get('query')

            Q = db.query(cls)

            for name, val in query.model_dump().items():
                if val is not None:
                    

                    # check type of param

                    if type(val) in [int,float,date,datetime]:

                        compare_type = name.split('_')[-1]
                        param_name = '_'.join(name.split('_')[:-1])

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

                    if type(val) == str:

                        if schema_cls.search_cfg.search_contains and schema_cls.search_cfg.search_trgm:
                            # if contains AND trgm
                            Q = Q.filter(
                                or_(
                                    getattr(cls, name).contains(val),
                                    func.similarity(getattr(cls, name), val) > query.threshold
                                )
                            )

                        elif schema_cls.search_cfg.search_contains:
                            # if just contains
                            Q = Q.filter(getattr(cls, name).contains(val))

                        elif schema_cls.search_cfg.search_trgm:
                            # if just trgm
                            Q = Q.filter(func.similarity(getattr(cls, name),val)> query.threshold)

                        else:
                            # else jsut extact match
                            Q = Q.filter(getattr(cls, name) == val)

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
            cls.controller_factory_search(),
            description=schema_cls.search_cfg.description,
            summary=schema_cls.search_cfg.summary,
            tags=schema_cls.search_cfg.tags,
            operation_id=schema_cls.search_cfg.operation_id,
            methods=["GET"],
            status_code=200,
            response_model=list[cls],
        )