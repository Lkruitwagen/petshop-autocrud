from petshop.models.human import Human, HumanTable, Friendship
from petshop.models.pet import Pet, PetTable

Human.model_rebuild()
Pet.model_rebuild()

all_tables = dict(
    Human=HumanTable,
    Pet=PetTable,
)

response_models = dict(
    Human=Human,
    Pet=Pet,
)

__all__ = ["Human","Pet","HumanTable","PetTable", "all_tables", "response_models"]