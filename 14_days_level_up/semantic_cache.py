"""
# Jour 1 — Structures de données

Voici ton exercice. Lis l'énoncé entièrement avant de commencer, puis code **sans aide, sans autocomplétion**.

---

## Énoncé — 1h30

Tu implémentes un système de **cache sémantique** pour un pipeline LLM. Quand une requête arrive, on vérifie si une requête "similaire" a déjà été posée pour éviter un appel API coûteux.

### Partie 1 — LRU Cache (30 min)

Implémente un `LRUCache` avec une capacité fixe.

```
LRUCache(capacity=3)
  .put("a", 1)
  .put("b", 2)
  .put("c", 3)
  .get("a")        → 1  (remonte en tête)
  .put("d", 4)     → évicte "b" (le moins récemment utilisé)
  .get("b")        → None
```

**Contrainte** : `get` et `put` doivent être **O(1)**. Pas de `collections.OrderedDict`. Implémente toi-même la structure sous-jacente.

---

### Partie 2 — File de priorité (30 min)

Tu veux traiter les requêtes par ordre de priorité (les requêtes urgentes passent devant).

Implémente un `PriorityQueue` sans utiliser `heapq`.

```
pq = PriorityQueue()
pq.push("requête normale", priority=5)
pq.push("requête urgente", priority=1)
pq.push("requête basse", priority=9)
pq.pop()  → "requête urgente"  (priorité la plus basse = urgente)
```

**Contrainte** : `push` en O(log n), `pop` en O(log n). Implémente le heap manuellement avec un array.

---

### Partie 3 — Assemblage (30 min)

Combine les deux : un `SemanticCache` qui :
- stocke les paires `(query_embedding, response)` dans un LRU Cache de capacité 100
- expose une méthode `get_similar(embedding, threshold=0.85)` qui retourne la réponse si un embedding stocké a une **similarité cosinus ≥ threshold**
- expose une méthode `put(embedding, response, priority)` qui utilise ta PriorityQueue pour décider quelle entrée évicte en premier si le cache est plein (priorité haute = on évicte en dernier)

```python
cache = SemanticCache(capacity=3)
cache.put([1.0, 0.0], "Paris est la capitale", priority=1)
cache.put([0.9, 0.1], "La tour Eiffel...", priority=3)
cache.put([0.0, 1.0], "Le Python est un langage...", priority=2)

cache.get_similar([0.95, 0.05])  → "La tour Eiffel..."  (cosinus ≈ 0.995)
cache.put([0.5, 0.5], "Nouvelle entrée", priority=5)
# évicte la réponse de priorité 3 (priorité la plus basse restante)
```

---

## Ce qu'on évalue

- La structure sous-jacente du LRU (doubly linked list + hashmap — tu sais pourquoi ?)
- La correction du heap : `_sift_up` et `_sift_down` bien implémentés
- La gestion des edge cases : cache vide, capacité 1, embeddings identiques
- La lisibilité : nommage, séparation des responsabilités
- Les complexités : tu les commentes dans le code

"""
import math

class LRUCache():
    """
        LRUCache(capacity=3)
    .put("a", 1)
    .put("b", 2)
    .put("c", 3)
    .get("a")        → 1  (remonte en tête)
    .put("d", 4)     → évicte "b" (le moins récemment utilisé)
    .get("b")        → None
    """
class Node:
    def __init__(self, key=None, value=None, prev=None, next=None):
        self.key = key
        self.value = value
        self.prev = prev
        self.next = next

class LRUCache:

    def __init__(self, capacity=3):
        self.capacity = capacity
        self.cache = {} #hashmap : key -> node

        # Sentinelles, bougent jamais
        self.head = Node()
        self.tail = Node()

        # Double linked list
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node):
        node.prev.next = node.next
        node.next.prev = node.prev
        node.prev = None
        node.next = None

    def _insert_head(self, node):
        node.prev = self.head
        node.next = self.head.next
        self.head.next.prev = node
        self.head.next = node

        

    def put(self, key, value):
        if key in self.cache:
            self._remove(self.cache[key])
            del self.cache[key]
            
        node = Node(key=key, value=value)
        self._insert_head(node=node)
        self.cache[key] = node

        if len(self.cache) > self.capacity:
            lru = self.tail.prev
            self._remove(lru)
            del self.cache[lru.key]


    def get(self, key):
        if key in self.cache:
            node = self.cache[key]
            self._remove(node)
            self._insert_head(node)
            return self.cache[key].value
        return -1
    
    def values(self):
        # O(n) — parcourt la liste chaînée
        result = []
        node = self.head.next
        while node != self.tail:
            result.append((node.key, node.value))
            node = node.next
        return result
    
    
class PriorityQueue:
    """On veut implémenter une heap queue from scratch avec un array"""
    def __init__(self):
        self.heap = [] # Liste de tuples (priority, value)
        

    # parent = (i-1) // 2
    # left = 2i + 1 
    # right = 2i + 2


    def _sift_up(self, i):
        while i > 0:
            parent = (i - 1) // 2
            if self.heap[i][0] < self.heap[parent][0]:
                self.heap[i], self.heap[parent] = self.heap[parent], self.heap[i]
                i = parent
            else:
                break
    
    def _sift_down(self, i):
        n = len(self.heap)
        while True:
            left = 2*i + 1
            right = 2*i + 2
            smallest = i

            if left < n and self.heap[left][0] < self.heap[smallest][0]:
                smallest = left
            if right < n and self.heap[right][0] < self.heap[smallest][0]:
                smallest = right
            
            if smallest == i:
                break

            self.heap[i], self.heap[smallest] = self.heap[smallest], self.heap[i]
            i = smallest

    def push(self, value, priority):
        self.heap.append((priority, value))
        self._sift_up(len(self.heap) - 1)


    def pop(self):
        if not self.heap:
            return None

        # Swap racine et dernier élément
        self.heap[0], self.heap[-1] = self.heap[-1], self.heap[0]
        _, value = self.heap.pop()  # retire l'ancien minimum (maintenant en queue)
        self._sift_down(0)          # redescend le nouveau sommet
        return value

    def peek(self):
        return self.heap[0][1] if self.heap else None


class SemanticCache:

    def __init__(self, capacity=100):
        self.capacity = capacity
        self.lru = LRUCache(capacity=capacity)
        self.pq = PriorityQueue()

    def cosine_similarity(self, a, b):
        dot = sum_a = sum_b = 0
        for ea, eb in zip(a, b):
            dot   += ea * eb
            sum_a += ea ** 2
            sum_b += eb ** 2
        denom = math.sqrt(sum_a) * math.sqrt(sum_b)
        return dot / denom if denom != 0 else 0.0  

    def get_similar(self, embedding, threshold=0.85):
        # O(n) — pas d'index vectoriel, on parcourt tout
        for stored_key, response in self.lru.values():
            sim = self.cosine_similarity(embedding, list(stored_key))
            if sim >= threshold:
                return response
        return None

    def put(self, embedding, response, priority):
        if len(self.lru.cache) >= self.capacity:
            to_evict = self.pq.pop()       
            self.lru.put(tuple(to_evict), None) 

        key = tuple(embedding)              
        self.lru.put(key, response)
        self.pq.push(response, priority)