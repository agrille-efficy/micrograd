import asyncio
import hashlib
import time
from typing import Optional, AsyncIterator

class ProductionLLMClient:

    def __init__(self, llm_client, cache_ttl: int = 3600):
        self.llm = llm_client
        self.cache_ttl = cache_ttl
        self.semantic_cache = {}  # prompt_hash → {response, timestamp}
        self.metrics = {
            "total_calls": 0,
            "cache_hits": 0,
            "total_tokens": 0,
            "total_latency_ms": 0
        }

    def _hash_prompt(self, prompt: str) -> str:
        # Retourne le hash MD5 du prompt
        # Utilise hashlib.md5(prompt.encode()).hexdigest()
        return hashlib.md5(prompt.strip().lower().encode()).hexdigest()

    def _is_cache_valid(self, cache_entry: dict) -> bool:
        # Retourne True si l'entrée est encore valide (pas expirée)
        # Utilise self.cache_ttl et time.time()

        age = time.time() - cache_entry["timestamp"]
        return age < self.cache_ttl
        

    async def complete(self, prompt: str) -> str:
        # 1. Hash le prompt
        # 2. Vérifie le cache → si hit valide, retourne la réponse cachée
        # 3. Sinon : appelle self.llm.complete(prompt)
        # 4. Met à jour le cache
        # 5. Met à jour les métriques (total_calls, total_tokens, total_latency_ms)
        # 6. Retourne la réponse

        hashed_prompt = self._hash_prompt(prompt)
        if hashed_prompt in self.semantic_cache:
            entry = self.semantic_cache[hashed_prompt]
            if self._is_cache_valid(entry):
                self.metrics["cache_hits"] += 1
                return entry["response"]
            
        
        latency_start = time.time()
        response = await self.llm.complete(prompt)
        latency_end = time.time()

        self.semantic_cache[hashed_prompt] = {
            "response":response,
            "timestamp": time.time()
            }
        
        self.metrics["total_calls"] += 1
        self.metrics["total_latency_ms"] += (latency_end - latency_start) * 1000
        self.metrics["total_tokens"] += len(response.split(" "))
        


    async def complete_stream(self, prompt: str) -> AsyncIterator[str]:
        # Version streaming — yield les tokens au fur et à mesure
        # Appelle self.llm.stream(prompt) qui retourne un AsyncIterator
        # Yield chaque token reçu
        # Met à jour les métriques à la fin
        
        latency_start = time.time()
        full_reponse = ""
        async for token in self.llm.stream(prompt):
            full_response += token
            yield token

        latency_end = time.time()
        self.metrics["total_calls"] += 1
        self.metrics["total_latency_ms"] += (latency_end - latency_start) * 1000
        self.metrics["total_tokens"] += len(full_response.split(" "))

    def get_metrics(self) -> dict:
        # Retourne les métriques avec cache_hit_rate calculé
        total = self.metrics["total_calls"]
        return {
            **self.metrics,
            "cache_hit_rate": self.metrics["cache_hits"] / total if total > 0 else 0,
            "avg_latency_ms": self.metrics["total_latency_ms"] / total if total > 0 else 0
        }