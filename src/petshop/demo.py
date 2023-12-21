from fastapi import FastAPI
from sqlmodel import SQLModel, Field, create_engine
from pydantic import BaseModel
from datetime import date, datetime

from petshop.mixins import (
    ReadMixin, 
    ReadParams, 
    RouterParams, 
    CreateParams, 
    CreateMixin, 
    SearchMixin,
    SearchParams,
    DeleteMixin,
    DeleteParams,
    PatchMixin,
    PatchParams,
)
from petshop.core.database import engine
from petshop.core.config import settings


ReadMixin.__config__ = None


class Human(SQLModel, ReadMixin, CreateMixin, SearchMixin,  DeleteMixin, PatchMixin, table=True):
    id: int | None = Field(default=None, primary_key=True)
    first_name: str | None
    last_name: str | None

    class read_cfg(ReadParams):
        primary_key = 'id'
        description = "Retrieve a Human record by ID"
        summary = "Retrieve Humans by ID"
        operation_id = "read_humans_by_id"

    class create_cfg(CreateParams):
        required_params = None
        pop_params = ['id']
        description = "Create human"
        summary = "Create human"
        operation_id = "create_human"

    class search_cfg(SearchParams):
        required_params = []
        pop_params=["id"]
        description = "Search human"
        summary = "Search human"
        operation_id = "search_human"

        # for str:
        search_contains = True # string contains search
        search_trgm = ["last_name"] # string trigram search

    class delete_cfg(DeleteParams):
        primary_key = "id"
        description = "Delete human"
        summary = "Delete human"
        operation_id = "delete_human"

    class patch_cfg(PatchParams):
        primary_key = "id"
        description = "Patch human"
        summary = "Patch human"
        operation_id = "patch_human"

    class router_cfg(RouterParams):
        prefix = "/humans"
        tags=["humans"]
        dependencies = []




class Pet(SQLModel, ReadMixin, CreateMixin, SearchMixin, DeleteMixin, PatchMixin, table=True):
    id: int | None = Field(default=None, primary_key=True)
    species: str
    birthday: date

    class read_cfg(ReadParams):
        primary_key = 'id'
        description = "Retrieve a Pet record by ID"
        summary = "Retrieve Pets by ID"
        operation_id = "read_pets_by_id"

    class create_cfg(CreateParams):
        required_params = None
        pop_params = ['id']
        description = "Create pet"
        summary = "Create pet"
        operation_id = "create_pet"

    class search_cfg(SearchParams):
        required_params = []
        pop_params=["id"]
        description = "Search pet"
        summary = "Search pet"
        operation_id = "search_pet"

        search_eq = True # is precisely equal to
        search_lt = True # less than, list[str] | bool
        search_lte = True # less than or equal to, list[str] | bool

    class delete_cfg(DeleteParams):
        primary_key = "id"
        description = "Delete pet"
        summary = "Delete pet"
        operation_id = "delete_pet"

    class patch_cfg(PatchParams):
        primary_key = "id"
        description = "Patch pet"
        summary = "Patch pet"
        operation_id = "patch_pet"

    class router_cfg(RouterParams):
        prefix = "/pets"
        tags=["pets"]
        dependencies = []


Human.build_read_route()
Human.build_create_route()
Human.build_search_route()
Human.build_delete_route()
Human.build_patch_route()


Pet.build_read_route()
Pet.build_create_route()
Pet.build_search_route()
Pet.build_delete_route()
Pet.build_patch_route()

# create tables
#SQLModel.metadata.create_all(engine)
#print ('created tables')

# create app
app = FastAPI(title="Petshop - autocrud", separate_input_output_schemas=False)


# add routers
app.include_router(Human.router)
app.include_router(Pet.router)

