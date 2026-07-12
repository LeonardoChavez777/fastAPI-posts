from typing import List

from sqlalchemy import func
from .. import databasemodels, squema, oauth2
from ..database import get_db
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)


#OBTENER TODOS LOS POSTS // , response_model=List[squema.AllpostsResponse],
@router.get("/", response_model=List[squema.PostResponseWithVotes])
def get_posts(db: Session = Depends(get_db), limit: int = 10, skip: int = 0,search: str = ""):
    #cursor.execute("SELECT * FROM posts")
    #misposteos = cursor.fetchall()
    #return {"data": misposteos}
    

    posts = db.query(databasemodels.Post, func.count(databasemodels.Vote.post_id).label("votos")).join(databasemodels.Vote, databasemodels.Vote.post_id == databasemodels.Post.Id, isouter= True).group_by(databasemodels.Post.Id).filter(databasemodels.Post.title.contains(search)).order_by(databasemodels.Post.created_at.desc()).limit(limit).offset(skip).all()


    if not posts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No posts found")

    return posts

#OBTENER SOLO MIS LOS POSTS
@router.get("/myposts", response_model=List[squema.PostResponseWithVotes],)
def get_my_posts(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    #cursor.execute("SELECT * FROM posts")
    #misposteos = cursor.fetchall()
    #return {"data": misposteos}
    
    posts = db.query(databasemodels.Post, func.count(databasemodels.Vote.post_id).label("votos")).join(databasemodels.Vote, databasemodels.Vote.post_id == databasemodels.Post.Id, isouter= True).group_by(databasemodels.Post.Id).filter(databasemodels.Post.owner_id == current_user.Id).all()

    if not posts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No posts found for user: {current_user.email}")

    return posts

#CREAR UN POST
@router.post("/", status_code=status.HTTP_201_CREATED)
def create_posts(post: squema.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # cursor.execute("INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *", (new_post.title, new_post.content, new_post.published))
    # nuevo_posteo = cursor.fetchone()
    # connection.commit()
    # return {"data": nuevo_posteo}

    new_post = databasemodels.Post(**post.model_dump(), owner_id=current_user.Id)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


#OBTENER UN POST POR ID
@router.get("/{id}", response_model=squema.PostResponseWithVotes, )
def get_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    # cursor.execute("""SELECT * FROM posts WHERE posts."Id" = %s""", (id,))
    # posteo_buscado = cursor.fetchone()
    query_buscarpost = db.query(databasemodels.Post, func.count(databasemodels.Vote.post_id).label("votos")).join(databasemodels.Vote, databasemodels.Vote.post_id == databasemodels.Post.Id, isouter= True).group_by(databasemodels.Post.Id).filter(databasemodels.Post.Id == id)
    posteo_buscado = query_buscarpost.first() #.first() devuelve el primer resultado de la consulta, o None si no se encuentra ningún resultado. Es útil para obtener un single registro basado en una condición específica, como en este caso, buscar un post por su ID.
    if not posteo_buscado:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")
    return posteo_buscado
    

#BORRAR UN POST POR ID
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    # cursor.execute("""DELETE FROM posts WHERE posts."Id" = %s RETURNING *""", (id,))
    # posteo_borrado = cursor.fetchone()
    #connection.commit()
    query_borrado = db.query(databasemodels.Post).filter(databasemodels.Post.Id == id)
    posteo_borrado = query_borrado.first()
    if not posteo_borrado:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")
    
    if posteo_borrado.owner_id != current_user.Id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    
    query_borrado.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


#ACTUALIZAR UN POST POR ID
@router.put("/{id}", response_model=squema.PostResponse)
def update_post(id: int, post: squema.PostCreate, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    # cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE posts."Id" = %s RETURNING *""", (post.title, post.content, post.published, id))
    # posteo_actualizado = cursor.fetchone()
    
    query_actualizar = db.query(databasemodels.Post).filter(databasemodels.Post.Id == id) #esto devuelve la consulta, aun no el post
    post_buscado = query_actualizar.first() # con first ya tenemos el post o none

    if post_buscado == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"post with id: {id} was not found")
    
    if post_buscado.owner_id != current_user.Id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")
    
    query_actualizar.update(post.model_dump(), synchronize_session=False) # reutilizo la consulta anterior para hacer una nueva con update y le paso los datos del post recibido por el usuario

    db.commit() #refrescar la base de datos para que se guarden los cambios

    #ahora la query_actualizar es la misma de arriba pero como se hizo el commit los datos recibidos seran los actualizados.
    post_actualizado = query_actualizar.first() # con first obtengo el post actualizado

    return post_actualizado