from .. import databasemodels, squema, utils
from ..database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=squema.UserResponse)
def create_user(user: squema.UserCreate, db: Session = Depends(get_db)):
    
    #hash the password - user.password
    hashed_password = utils.hash_password(user.password) #contraseña hasheada
    user.password = hashed_password # ahora la nueva contraseña sera la contraseña hasheada
    
    new_user = databasemodels.User(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@router.get("/{id}", response_model=squema.UserResponse)
def get_user(id: int, db: Session = Depends(get_db)):
    query_buscaruser = db.query(databasemodels.User).filter(databasemodels.User.Id == id)
    user_buscado = query_buscaruser.first()
    if not user_buscado:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"user with id: {id} was not found")
    return user_buscado