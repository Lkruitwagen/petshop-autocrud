from typing import List, TYPE_CHECKING, Optional

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
    from .pet import Pet


ReadMixin.__config__ = None


class Human(SQLModel, ReadMixin, CreateMixin, SearchMixin,  DeleteMixin, PatchMixin, table=True):
    id: int | None = Field(default=None, primary_key=True)
    first_name: str | None
    last_name: str | None

    pets_relationship: Optional[List["Pet"]] = Relationship(back_populates="owner")

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
        results_limit = 100

        # for str:
        search_contains = True # string contains search
        search_trgm = ["last_name"] # string trigram search
        search_trgm_threshold = 0.7

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




Human.build_read_route()
Human.build_create_route()
Human.build_search_route()
Human.build_delete_route()
Human.build_patch_route()