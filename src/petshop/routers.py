from petshop.models import (
    HumanTable,
    PetTable,
    response_models
)

HumanTable.build_read_route(response_models["Human"])
HumanTable.build_create_route()
HumanTable.build_search_route()
HumanTable.build_delete_route()
HumanTable.build_patch_route()

PetTable.build_read_route()
PetTable.build_create_route()
PetTable.build_search_route()
PetTable.build_delete_route()
PetTable.build_patch_route()


