import asyncio

async def get_embedding(doc: str) -> list[float]:
    await asyncio.sleep(0.5)
    return [0.1, 0.2, 0.3]

async def classify(doc: str) -> str:
    await asyncio.sleep(0.3)
    return "technical"

async def extract_entities(doc: str) -> list[str]:
    await asyncio.sleep(0.4)
    return ["Python", "API"]

async def enrich_document(doc: str) -> dict:
    embedding, category, entity = await asyncio.gather(get_embedding(doc), classify(doc), extract_entities(doc))
    return {"embedding": embedding, "category": category, "entity": entity}

    

async def enrich_batch(docs: list[str], max_concurrent: int = 5) -> list[dict]:

    sem = asyncio.Semaphore(max_concurrent)
    
    async def enrich_with_limit(doc):
        async with sem:
            return await enrich_document(doc)
        
    return await asyncio.gather(*[enrich_with_limit(doc) for doc in docs])



######################################################
####################   Partie 3   ####################
######################################################

import asyncio

async def process_doc(doc: str) -> str:
    await asyncio.sleep(0.1)
    return doc.upper()

async def pipeline(docs: list[str]) -> list[str]:
    tasks = []
    for doc in docs:
        task = asyncio.create_task(process_doc(doc))       # ligne A
        tasks.append(task)

    results = await asyncio.gather(*tasks)  # ligne B
    return results

def run_pipeline(docs: list[str]) -> list[str]:

    return asyncio.run(pipeline(docs))  # ligne C