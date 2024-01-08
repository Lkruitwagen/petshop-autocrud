from fastapi import APIRouter
from abc import ABC


class Controllers(object):
    pass

class AutoCrudMixinBase(object):
    """
    expose a router on a db object table
    """
    router = APIRouter(
        prefix="",
        tags=[],
        dependencies=None,
    )

class RouterParams(ABC):
    prefix = None
    tags = None
    dependencies = None





