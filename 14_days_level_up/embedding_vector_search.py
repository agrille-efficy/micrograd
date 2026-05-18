import math
from typing import Optional

class VectorIndex:
    """
    Index vectoriel simple avec recherche par similarité cosinus.
    En prod ce serait FAISS ou Pinecone - ici on implémente from scratch
    """

    def __init__(self):
        self.vectors = {}
        self.metadata = {}

    def add(self, id: str, vector: list[float], metadata: dict = {}) -> None:
        # Normalize le vecteur avant stockage (pourquoi ?)
        # Stocke le vecteur et les métadonnées
        self.vectors[id] = self._normalize(vector)
        self.metadata[id] = metadata

    def _normalize(self, vector: list[float]) -> list[float]:
        # Retourne le vecteur normalisé (norme = 1)
        norm = math.sqrt(sum(x**2 for x in vector))
        if norm == 0:
            return vector
        
        return [x / norm for x in vector]

    def _dot_product(self, a: list[float], b: list[float]) -> float:
        # Produit scalaire entre deux vecteurs
        sum = 0
        for elem_a, elem_b in zip(a, b):
            sum += elem_a * elem_b

        return sum

    def search(self, query_vector: list[float], top_k: int = 5) -> list[dict]:
        # Normalise la query
        # Calcule la similarité avec tous les vecteurs
        # Retourne les top_k résultats triés par score décroissant 
        # Format : [{"id": ..., "score": ..., "metadata": ...}]
        if not self.vectors:
            return []
        normalized_query = self._normalize(query_vector)
        results = []
        for id, vector in self.vectors.items():
            score = self._dot_product(normalized_query, vector)
            results.append({"id": id, "score": score, "metadata": self.metadata[id]})
        return sorted(results, key=lambda x: x["score"], reverse=True)[:top_k]



    def delete(self, id: str) -> bool:
        # Supprime le vecteur, retourne True si supprimé, False si absent
        if not id in self.vectors:
            return False
        del self.vectors[id]
        del self.metadata[id]
        return True