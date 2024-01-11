from typing import Optional, TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship
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

if TYPE_CHECKING:
    from .human import HumanTable


ReadMixin.__config__ = None

class PetBase(SQLModel, table=False):
    name: str
    species: str
    birthday: date


class PetTable(PetBase, ReadMixin, CreateMixin, SearchMixin, DeleteMixin, PatchMixin, table=True):
    __tablename__ = "pets"
    id: int | None = Field(default=None, primary_key=True)

    owner_id: Optional[int] = Field(default=None, foreign_key="humans.id")
    owner: Optional["HumanTable"] = Relationship(back_populates="pets", sa_relationship_kwargs={"lazy": "selectin"})

    """
    class relationships:
        relationships = dict(
            owner = Optional["Human"],
        )
    """ 

    

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
        results_limit = 100

        search_eq = True # is precisely equal to
        search_lt = True # less than, list[str] | bool
        search_lte = True # less than or equal to, list[str] | bool
        search_trgm_threshold = 0.7

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

class Pet(PetBase):
    owner: Optional["Human"]

