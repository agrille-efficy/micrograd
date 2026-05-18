from dataclasses import dataclass
from typing import Optional
import asyncio
import uuid

@dataclass
class Document:
    id: str
    content: str
    metadata: dict

@dataclass
class Chunk:
    id: str
    doc_id: str
    content: str
    position: int
    embedding: Optional[list[float]] = None

@dataclass
class RetrievalResult:
    chunk: Chunk
    score: float

class RAGPipeline:

    def __init__(self, vector_index, llm_client):
        self.index = vector_index
        self.llm = llm_client
        self.chunks = {}  # chunk_id → Chunk

    async def index_document(self, doc: Document) -> list[Chunk]:
        # 1. Chunk le document (fixed-size, 200 mots par chunk, overlap 50 mots)
        # 2. Pour chaque chunk : génère l'embedding via self.llm.embed(text)
        # 3. Indexe dans self.index
        # 4. Stocke dans self.chunks
        # 5. Retourne la liste des chunks créés

        # Chunking sur les mots
        words = doc.content.split()
        chunks = []
        i = 0
        while i < len(words):
            chunk_words = words[i:i+200]
            chunk = Chunk(
                id=str(uuid.uuid4()),
                doc_id=doc.id,
                content=" ".join(chunk_words),
                position=len(chunk)
            )
            chunks.append(chunk)
            i += 150 #200 - 50 overlap


        # Embeddings en parallèle
        embeddings = await asyncio.gather(*[self.llm.embed(c.content) for c in chunks])

        # Indexation et stockage
        for chunk, embedding in zip(chunks, embeddings):
            chunk.embedding = embeddings
            self.index.add(chunk.id, embedding, {"doc_id": doc.id})
            self.chunks[chunk.id] = chunk

        return chunks

    async def retrieve(self, query: str, top_k: int = 5) -> list[RetrievalResult]:
        # 1. Embed la query via self.llm.embed(query)
        # 2. Recherche dans self.index
        # 3. Retourne les RetrievalResult triés par score
        ...

    async def generate(self, query: str, context: list[RetrievalResult]) -> str:
        # 1. Construit le prompt avec le contexte
        # 2. Appelle self.llm.complete(prompt)
        # 3. Retourne la réponse
        ...

    async def query(self, question: str) -> dict:
        # Pipeline complet :
        # 1. retrieve
        # 2. generate
        # Retourne {"answer": ..., "sources": [...chunk_ids...], "scores": [...]}
        ...


