from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from ..database import get_db
from .. import squema, databasemodels, utils, oauth2


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/login", response_model=squema.Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):

    user = db.query(databasemodels.User).filter(databasemodels.User.email == user_credentials.username).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")
    
    if not utils.verify_password(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials")
    
    access_token = oauth2.create_access_token(data={"user_id": user.Id})



    return {"access_token" : access_token, "token_type": "bearer"} #estos parametros deben ser iguales a los que se definen en el modelo Token de squema.py
    #ya que usamos la respuesta de este endpoint como squema.Token, que es un modelo de Pydantic, y este modelo tiene dos campos: 
    #access_token y token_type. Por lo tanto, la respuesta debe tener estos dos campos para que Pydantic pueda validar y serializar la respuesta correctamente.