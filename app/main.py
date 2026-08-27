
from fastapi import FastAPI

from . import databasemodels
from .database import engine
from .routers import posts, users, auth, vote, audio
from fastapi.middleware.cors import CORSMiddleware

#databasemodels.Base.metadata.create_all(bind=engine) #crea las tablas en la base de datos si no existen, utilizando psqlchemy
#ahora se hace con alembic, para poder hacer migraciones de la base de datos
app = FastAPI() 

origins = ["*"]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



app.include_router(posts.router)
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(vote.router)
app.include_router(audio.router)

@app.get("/")
def root():
    return {"message": "oe q vaina q no haya espacio"}