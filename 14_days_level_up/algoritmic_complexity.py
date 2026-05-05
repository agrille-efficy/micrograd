# # Fonction A
# def find_duplicates(docs: list[str]) -> list[str]:
#     duplicates = set()
#     seen = set()
#     for doc in docs:
    
#         if doc in seen: #O(1) car duplicates est un set
#             duplicates.add(doc)
#         else:
#             seen.add(doc)
#     return list(duplicates)


# # Fonction B
# def chunk_documents(docs: list[str], chunk_size: int) -> list[list[str]]:
#     chunks = []
#     for doc in docs:
#         for i in range(0, len(doc), chunk_size):
#             chunks.append(doc[i:i+chunk_size])
#     return chunks

# """Complexité O(n²) pareil que fct A meme si on fait avec des chunks. """

# # Fonction C
# def build_index(chunks: list[str]) -> dict:
#     index = {}
#     for chunk in chunks:
#         words = chunk.split()
#         for word in words:
#             if word not in index:
#                 index[word] = []
#             index[word].append(chunk)
#     return index



# # Fonction D
# def search(index: dict, query: str) -> list[str]:
#     results = set()
#     query_words = query.split()
#     for word in query_words:
#         if word in index:
#             results.update(index[word])
#     return results

def process_pipeline(documents: list[str]) -> dict:
    # Étape 1 : dédoublonnage
    unique_docs = []
    for doc in documents: # O(n)
        if doc not in unique_docs:  # O(n)
            unique_docs.append(doc)
            # -> O(n²)

    # Étape 2 : chunking
    chunks = []
    for doc in unique_docs: # O(n)
        words = doc.split()
        for i in range(0, len(words), 100): # O(m)
            chunks.append(" ".join(words[i:i+100]))
            # -> O(n * m)

    # Étape 3 : indexation
    index = {}
    for chunk in chunks: # O(n)
        for word in chunk.split(): #O(m)
            if word not in index: # O(1)
                index[word] = set()
            index[word].add(chunk)

    return index    
    # -> o(n * m)

def process_pipeline_fast(documents: list[str]) -> str:
    seen = set()
    unique_docs = []
    for doc in documents:
        if doc not in seen:
            seen.add(doc)
            unique_docs.append(doc)

    return unique_docs