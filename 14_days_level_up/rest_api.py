"""

## Jour 5 — APIs & REST Design

Lis l'énoncé entièrement avant de commencer. Pas d'aide, pas d'autocomplétion.

---

## Énoncé — 1h

Tu conçois l'API REST d'un système RAG en production. L'API doit être robuste, bien structurée, et respecter les conventions REST.

---

### Partie 1 — Design d'API (20 min)

Conçois les endpoints pour ce système RAG. Pour chaque endpoint, donne : la méthode HTTP, le path, le body/params, et le status code de retour.

**Fonctionnalités à couvrir :**
- Indexer un nouveau document
- Récupérer un document par ID
- Mettre à jour un document existant
- Supprimer un document
- Rechercher des documents similaires à une query
- Lister tous les documents avec pagination

**Réponds sous cette forme :**
```
POST /documents
Body: {...}
Response: 201 {...}
```

---

### Partie 2 — Implémentation FastAPI (30 min)

Implémente ces 3 endpoints avec FastAPI.

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

# Modèles à définir
class Document(BaseModel): ...
class SearchQuery(BaseModel): ...
class SearchResult(BaseModel): ...

# À implémenter :

# 1. POST /documents — indexe un document, retourne 201 + le document créé avec son id
# 2. GET /documents/{doc_id} — retourne le document ou 404
# 3. POST /documents/search — recherche sémantique, retourne liste de résultats
```

Utilise un dict en mémoire comme "base de données" :
```python
db: dict[str, Document] = {}
```

---

### Partie 3 — Error handling & edge cases (10 min)

Ce code a des problèmes. Identifie-les et corrige-les.

```python
@app.get("/documents/{doc_id}")
def get_document(doc_id: str):
    return db[doc_id]

@app.post("/documents")
def create_document(doc: Document):
    db[doc.id] = doc
    return doc

@app.delete("/documents/{doc_id}")
def delete_document(doc_id: str):
    del db[doc_id]
    return {"deleted": True}
```

---

## Ce qu'on évalue

- La maîtrise des conventions REST — méthodes HTTP, status codes, nommage
- La capacité à modéliser des ressources avec Pydantic
- La gestion des erreurs — 404, 422, 409
- Les edge cases : document déjà existant, query vide, pagination hors limites
- La lisibilité : types, docstrings, response models



"""


# POST /documents
# Body: {"content": "texte du document", "title": "mon doc"}
# Response: 201 {"id": "abc123", "content": "...", "title": "..."}

# GET /documents/{id}
# Body: {"id": "id du document"}
# Response: 200 {"id": "abc123", "content": "...", "title": "..."}

# PATCH  /documents/{id}
# Body: {"id": "abc123", "content": "texte du docuement", "title": "mon doc"}
# Response: 200 {"id": "abc123", "content": "....", "title": "..."}

# DELETE /documents/{id}
# Body: {"id"}
# Response: 204

# GET /query
# Body: {"content": "query"}
# Response: 201 {"content": "[list of similar docs]"}

# GET /documents?page=1&limit20
# Body {}
# Response 201 {"data": [...], "total": 123, "page": 1, "limit": 20}


# from fastapi import FastAPI, HTTPException, status
# from pydantic import BaseModel 

# class Document(BaseModel):
#     title: str
#     content: str

# app = FastAPI()

# #exemple get de base
# @app.get("/hello")
# def hello():
#     return {"message": "hello"}

# # Lire un path param
# @app.get("/documents/{doc_id}")
# def get_doc(doc_id: str)
#     return {"id": doc_id}

# # Lire un query param
# @app.get("/documents")
# def list_docs(page: int = 1, limit: int = 20):
#     return {"page": page, "limit": limit}

# #Lire un body
# @app.post("/documents", status_code=status.HTTP_201_CREATED)
# def create_doc(doc: Document):
#     return doc


# db = []
# #Retourner une erreur 
# @app.get("/documents/{doc_id}")
# def get_doc(doc_id: str):
#     if doc_id not in db:
#         raise HTTPException(status_code=404, detail="Document not found")
#     return db[doc_id]


from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import Optional
import uuid

app = FastAPI()
db: dict[str, dict] = {}

class DocumentCreate(BaseModel):
    title: str
    content: str

class Document(BaseModel):
    id: str
    title: str
    content: str

class SearchQuery(BaseModel):
    query: str
    limit: int = 5
    threshold: float = 0.85

class SearchResult(BaseModel):
    id: str
    title: str
    score: float

# Endpoint 1 - POST /documents

@app.post("/documents", status_code=status.HTTP_201_CREATED)
def create_documents(doc: DocumentCreate):
    id = str(uuid.uuid4())
    db[id] = {"id": id, "title":doc.title, "content": doc.content}
    return Document(id= id, title=doc.title, content=doc.content)

# Endpoint 2 - GET /documents/{doc_id}
@app.get("/documents/{doc_id}")
def get_document(doc_id: str) -> Document:
    if not doc_id in db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not in the database")
    return db[doc_id]
    
# Endpoint 3 - POST /documents/search
@app.post("/documents/search")
def search_document(query: SearchQuery) -> list[SearchResult]:
    if not query.query.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query cannot be empty"
        )
    
    if query.limit < 1 or query.limit > 100:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Limit must be between 1 and 100"
        )
    
    results = []
    for doc_id, doc in db.items():
        score = round(0.99 - (len(results) * 0.05, 2))
        if score >= query.threshold:
            results.append(SearchResult(
                id=doc_id,
                title=doc["title"],
                score=score
            ))
    results.sort(key=lambda x: x.score, reverse=True)
    return results



################# PARTIE 3 - DEBUG ##################
@app.get("/documents/{doc_id}")
def get_document(doc_id: str):
    if doc_id not in db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not in the db")
    return db[doc_id]

@app.post("/documents", status_code=status.HTTP_201_CREATED)
def create_document(doc: DocumentCreate) -> Document:
    if any(d["title"] == doc.title for d in db.values()):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Document already exists")
    doc_id = str(uuid.uuid4())
    db[doc_id] = {"id": doc_id, "title": doc.title, "content": doc.content}
    return Document(id=doc_id, title=doc.title, content=doc.content)

@app.delete("/documents/{doc_id}")
def delete_document(doc_id: str):
    if doc_id not in db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Could not delete document not in the database")
    del db[doc_id]