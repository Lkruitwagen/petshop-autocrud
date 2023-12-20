from fastapi import FastAPI
from sqlmodel import SQLModel, Field, create_engine
from pydantic import BaseModel

from petshop.mixins import ReadMixin, ReadParams, RouterParams, CreateParams, CreateMixin
from petshop.core.database import engine
from petshop.core.config import settings


ReadMixin.__config__ = None


class Human(SQLModel, ReadMixin, CreateMixin, table=True):
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

    class router_cfg(RouterParams):
        prefix = "/humans"
        tags=["humans"]
        dependencies = []




class Pet(SQLModel, ReadMixin, CreateMixin, table=True):
    id: int | None = Field(default=None, primary_key=True)
    species: str

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

    class router_cfg(RouterParams):
        prefix = "/pets"
        tags=["pets"]
        dependencies = []


Human.build_read_route()
Pet.build_read_route()
Human.build_create_route()
Pet.build_create_route()

# create tables
#SQLModel.metadata.create_all(engine)
#print ('created tables')

# create app
app = FastAPI(title="Petshop - autocrud", separate_input_output_schemas=False)


# add routers
app.include_router(Human.router)
app.include_router(Pet.router)

