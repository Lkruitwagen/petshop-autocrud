from typing import List, TYPE_CHECKING, Optional, Dict, Any, Type

from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import UniqueConstraint
from datetime import date, datetime
from pydantic import Extra

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
    from .pet import PetTable


ReadMixin.__config__ = None


class Friendship(SQLModel, table=True):
    __tablename__ = "friendships"

    best_friend: Optional[bool] = Field(
        default=None,
    )

    from_human_id: Optional[int] = Field(
        default=None,
        foreign_key="humans.id",
        primary_key=True,
    )
    to_human_id: Optional[int] = Field(
        default=None,
        foreign_key="humans.id",
        primary_key=True,
    )


    

    __table_args__ = (
        UniqueConstraint("from_human_id", "to_human_id", name='only_one_best_friend'),
    )

    def __repr__(self) -> str:
        return f"Friend({self.from_human_id} -> {self.to_human_id})"


class HumanBase(SQLModel, table=False):
    first_name: str | None
    last_name: str | None


class HumanTable(HumanBase, ReadMixin, CreateMixin, SearchMixin,  DeleteMixin, PatchMixin, table=True):
    __tablename__ = "humans"
    id: int | None = Field(default=None, primary_key=True)

    pets: List["PetTable"] = Relationship(back_populates="owner")

    friends_out: list["HumanTable"] = Relationship(
        link_model=Friendship,
        sa_relationship_kwargs={
            "primaryjoin":"HumanTable.id == Friendship.from_human_id",
            "secondaryjoin":"HumanTable.id == Friendship.to_human_id",
            "viewonly":True,
            "lazy": "selectin",
        },
    )
    friends_in: list["HumanTable"] = Relationship(
        link_model=Friendship,
        sa_relationship_kwargs={
            "primaryjoin":"HumanTable.id == Friendship.to_human_id",
            "secondaryjoin":"HumanTable.id == Friendship.from_human_id",
            "viewonly":True,
            "lazy": "selectin",
        },
    )
    best_friend: "HumanTable" = Relationship(
        link_model=Friendship,
        sa_relationship_kwargs={
            "primaryjoin":"HumanTable.id == Friendship.to_human_id",
            "secondaryjoin":"and_(HumanTable.id == Friendship.from_human_id, Friendship.best_friend == True)",
            "lazy": "selectin",
        },
    )   

    """
    class relationships:
        relationships = dict(
            pets = Optional[List["Pet"]],
            friends_out = Optional[List["Human"]],
            friends_in = Optional[List["Human"]],
            best_friend = Optional["Human"],
        )
    """
    class recursive_exclusions:
        exclude = {
            "pets":{"owner"}
        }

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

class Human(HumanBase):

    pets: Optional[List["Pet"]] = None

    friends_out: Optional[list["Human"]] = None

    friends_in: Optional[list["Human"]] = None

    best_friend: Optional["Human"] = None
