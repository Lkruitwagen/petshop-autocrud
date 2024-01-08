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
    from .human import Human


ReadMixin.__config__ = None



class Pet(SQLModel, ReadMixin, CreateMixin, SearchMixin, DeleteMixin, PatchMixin, table=True):
    id: int | None = Field(default=None, primary_key=True)
    species: str
    birthday: date

    owner_id: Optional[int] = Field(default=None, foreign_key="human.id")
    owner_relationship: Optional["Human"] = Relationship(back_populates="pets")

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

Pet.build_read_route()
Pet.build_create_route()
Pet.build_search_route()
Pet.build_delete_route()
Pet.build_patch_route()

