from fastapi import FastAPI
from sqlmodel import SQLModel

from petshop.models import (
    Human,
    Pet,
)
from petshop.core.database import engine

# create tables
SQLModel.metadata.create_all(engine)
print ('created tables')

# create app
app = FastAPI(title="Petshop - autocrud", separate_input_output_schemas=False)


# add routers
app.include_router(Human.router)
app.include_router(Pet.router)

