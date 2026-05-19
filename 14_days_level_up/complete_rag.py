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
        """
        # 1. Chunk le document (fixed-size, 200 mots par chunk, overlap 50 mots)
        # 2. Pour chaque chunk : génère l'embedding via self.llm.embed(text)
        # 3. Indexe dans self.index
        # 4. Stocke dans self.chunks
        # 5. Retourne la liste des chunks créés
        """

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
                position=len(chunks)
            )
            chunks.append(chunk)
            i += 150 #200 - 50 overlap


        # Embeddings en parallèle
        embeddings = await asyncio.gather(*[self.llm.embed(c.content) for c in chunks])

        # Indexation et stockage
        for chunk, embedding in zip(chunks, embeddings):
            chunk.embedding = embedding
            self.index.add(chunk.id, embedding, {"doc_id": doc.id})
            self.chunks[chunk.id] = chunk

        return chunks

    async def retrieve(self, query: str, top_k: int = 5) -> list[RetrievalResult]:
        """
        # 1. Embed la query via self.llm.embed(query)
        # 2. Recherche dans self.index
        # 3. Retourne les RetrievalResult triés par score
        """
        embedded_query = await self.llm.embed(query)
        results = self.index.search(embedded_query, top_k)
        retrieval_results = []
        for r in results:
            chunk = self.chunks[r["id"]]
            retrieval_results.append(RetrievalResult(chunk=chunk, score=r["score"]))
        return sorted(retrieval_results, key=lambda x: x.score, reverse=True)[:top_k]
        
     
    async def generate(self, query: str, context: list[RetrievalResult]) -> str:
        """
        # 1. Construit le prompt avec le contexte
        # 2. Appelle self.llm.complete(prompt)
        # 3. Retourne la réponse
        """
        context_text = "\n\n".join([r.chunk.content for r in context])
        prompt = f"Contexte:\n{context_text}\n\nQuestion:{query}\nRéponse:"
        return await self.llm.complete(prompt)

    async def query(self, question: str) -> dict:
        """
        # Pipeline complet :
        # 1. retrieve
        # 2. generate
        # Retourne {"answer": ..., "sources": [...chunk_ids...], "scores": [...]}
        """
        retrieved_results_list = await self.retrieve(question)
        result = await self.generate(question, retrieved_results_list)
        return {"answer": result, 
                "sources": [r.chunk.id for r in retrieved_results_list], 
                "scores": [r.score for r in retrieved_results_list]}
        


def rerank(
    query: str,
    results: list[RetrievalResult],
    top_k: int = 3
) -> list[RetrievalResult]:
    """
    # Score de reranking = nb de mots de la query présents dans le chunk
    # Retourne les top_k résultats triés par reranking score
    """

    query_words_set = set(query.lower().split(" "))

    def score(r):
        chunk_words = set(r.chunk.content.lower().split())
        return len(query_words_set & chunk_words)

    return sorted(results, key=score, reverse=True)[:top_k]
