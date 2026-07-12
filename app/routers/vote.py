from .. import databasemodels, squema, oauth2
from ..database import get_db
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/vote",
    tags=["Votes"]
)

@router.post("/", status_code=status.HTTP_201_CREATED)
def vote(vote: squema.Vote, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    query_existencia_post = db.query(databasemodels.Post).filter(databasemodels.Post.Id == vote.post_id)
    existencia_post = query_existencia_post.first()

    if not existencia_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {vote.post_id} does not exist")

    query_existencia_voto = db.query(databasemodels.Vote).filter(databasemodels.Vote.post_id == vote.post_id, databasemodels.Vote.user_id == current_user.Id)
    existencia_voto = query_existencia_voto.first()

    if vote.dir == 1:
        if existencia_voto:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"user {current_user.Id} has already voted on post {vote.post_id}")
        
        voto_creado = databasemodels.Vote(post_id=vote.post_id, user_id=current_user.Id)
        db.add(voto_creado)
        db.commit()
        return {"message": "has dado laiki"}
    else:
        if not existencia_voto:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"vote not found for user {current_user.Id} and post {vote.post_id}")
        
        query_existencia_voto.delete(synchronize_session=False)
        db.commit()
        return {"message": "has quitado el laiki"}