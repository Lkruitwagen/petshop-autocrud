from fastapi import FastAPI
from sqlmodel import SQLModel, Field, create_engine

from petshop.mixins import ReadMixin
from petshop.core.database import engine
from petshop.core.config import settings


ReadMixin.__config__ = None


class Human(ReadMixin, SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    first_name: str | None
    last_name: str | None

class Pet(ReadMixin, SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    species: str

print(Human)
print(Pet)

print (SQLModel.metadata)

# create tables
#SQLModel.metadata.create_all(engine)
#print ('created tables')

# create app
app = FastAPI(title="Petshop - autocrud", separate_input_output_schemas=False)


# add routers
app.include_router(Human.router)
app.include_router(Pet.router)

