from fastapi import FastAPI
from sqlmodel import SQLModel

from petshop.routers import (
    HumanTable,
    PetTable,
)
from petshop.core.database import engine

# create tables
SQLModel.metadata.create_all(engine)
print ('created tables')

# create app
app = FastAPI(title="Petshop - autocrud", separate_input_output_schemas=False)


# add routers
app.include_router(HumanTable.router)
app.include_router(PetTable.router)

