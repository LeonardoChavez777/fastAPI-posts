# este archivo se encarga de definir los modelos de datos que se utilizarán en la aplicación,
# utilizando la biblioteca Pydantic para validar y serializar los datos. En este caso, se define 
# un modelo Post con tres campos: title, content y published. El campo published tiene un valor predeterminado de True.
# Este modelo se utilizará para validar los datos de entrada en las rutas de la aplicación y para serializar los datos de salida.

from datetime import datetime
from pydantic import BaseModel, conint
from pydantic import EmailStr

class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True

class PostCreate(PostBase):
    pass

class AllpostsResponse(BaseModel):
    Id: int
    title: str
    content: str
    published: bool = True
    created_at: datetime
    owner_id: int
    owner: "UserResponse"

    model_config = {
        "from_attributes": True
    }


class PostResponse(BaseModel):
    title: str
    content: str
    owner_id: int
    owner: "UserResponse"

    model_config = {
        "from_attributes": True
    } #esto es para que la respuesta que es un modelo de Pydantic(que es algo parecido a un diccionario) se convierta en un diccionario y pueda ser mostrado en JSON

class PostResponseWithVotes(BaseModel):
    Post: AllpostsResponse
    votos: int

    model_config = {
        "from_attributes": True
    }

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    Id: int
    email: EmailStr
    created_at: datetime

    model_config = {
        "from_attributes": True
    }

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel): 
    Id: str | None = None 

class Vote(BaseModel):
    post_id: int
    dir: conint(le=1) # type: ignore