"""
### Strategy

class LLMProvider: 
    def complete(self, prompt: str) -> str:
        raise NotImplementedError


class OpenAIProvider(LLMProvider):
    def complete(self, prompt: str) -> str:
        return f"OpenAI: {prompt}"
    
class ClaudeProvider(LLMProvider):
    def complete(self, prompt: str) -> str:
        return f"Claude: {prompt}"
    
class App:
    def __init__(self, provider: LLMProvider):
        self.provider = provider

    def run(self, prompt: str) -> str:
        return self.provider.complete(prompt)
    
app = App(OpenAIProvider())
# app.run("Hello world")


### Observer

class EventBus:
    def __init__(self):
        self.subscribers = {}

    def subscribe(self, event: str, handler):
        if event not in self.subscribers:
            self.subscribers[event] = []
        self.subscribers[event].append(handler)

    def publish(self, event: str, data: dict):
        for handler in self.subscribers.get(event, []):
            handler(data)

def log_handler(data):
    print(f"LOG: {data}")

def billing_handler(data):
    print(f"BILLING: {data['tokens']} tokens")

bus = EventBus()
bus.subscribe("llm_call", log_handler)
bus.subscribe("llm_call", billing_handler)

# bus.publish("llm_call", {"tokens": 150, "model": "gpt-4"})


### Chain of reponsibility

class Step:
    def __init__(self):
        self.next_step = None

    def set_next(self, step):
        self.next_step = step
        return step
    
    def process(self, data):
        raise NotImplementedError
    
class Chunker(Step):
    def process(self, data: str) -> list:
        chunks = [data[i:i+100] for i in range(0, len(data), 100)]
        if self.next_step:
            return self.next_step.process(chunks)
        return chunks
    
class Embedder(Step):
    def process(self, chunks: list) -> list:
        embedded = [{"chunk": c, "embedding": [0.1, 0.2]} for c in chunks]
        if self.next_step:
            return self.next_step.process(embedded)
        return embedded
    
chunker = Chunker()
embedder = Embedder()
chunker.set_next(embedder)

result = chunker.process("document texte...")


### Decorator

class RetryDecorator(LLMProvider):
    def __init__(self, provider: LLMProvider, max_retries: int = 3):
        self.provider = provider
        self.max_retries = max_retries

    def complete(self, prompt: str) -> str:
        for attempt in range(self.max_retries):
            try:
                return self.provider.complete(prompt)
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise 

class LogDecorator(LLMProvider):
    def __init__(self, provider: LLMProvider):
        self.provider = provider

    def complete(self, prompt: str) -> str:
        print(f"Calling with: {prompt[:50]}")
        result = self.provider.complete(prompt)
        print(f"Got: {result[:50]}")
        return result
    
provider = OpenAIProvider()
provider = RetryDecorator(provider, max_retries=3)
provider = LogDecorator(provider)
provider.complete("hello")
"""


# Interface commune pour tous les LLMs
class LLMProvider:
    def complete(self, prompt: str) -> str:
        raise NotImplementedError

# À implémenter :
class OpenAIProvider(LLMProvider): 
    def complete(self, prompt: str) -> str:
        return f"OpenAI: {prompt}"
    
class ClaudeProvider(LLMProvider):
    def complete(self, prompt: str) -> str:
        return f"Claude: {prompt}"

class MistralProvider(LLMProvider):
    def complete(self, prompt: str) -> str:
        return f"Mistral: {prompt}"

class LLMRouter:
    # Règles de routing :
    # - prompt > 2000 chars → Claude
    # - prompt contient "code" → Mistral
    # - sinon → OpenAI
    def __init__(self, providers: dict):
        self.providers = providers

    def route(self, prompt: str) -> str:
        if len(prompt) > 2000:
            provider = self.providers["claude"]
        elif "code" in prompt:
            provider = self.providers["mistral"]
        else:
            provider = self.providers["openai"]
        return provider.complete(prompt)

class LLMEventBus:
    def __init__(self):
        self.subscribers = {}

    def subscribe(self, event: str, handler):
        if not event in self.subscribers:
            self.subscribers[event] = []
        self.subscribers[event].append(handler)

    def publish(self, event: str, data: dict):
        for handler in self.subscribers.get(event, []):
            handler.handle(data)


class BillingHandler:
    def handle(self, data: dict):  # calcule le coût : 0.01$ par token
        price = (data["tokens"]) * 0.01
        print(f"Billed: ${price}")

class CacheHandler:
    def __init__(self):
        self.cache = {}

    def handle(self, data: dict):  # stocke prompt → response dans un dict
        self.cache[data["prompt"]] = data["response"]
        print("Cache mis à jour")

class LogHandler:
    def handle(self, data: dict):  # print "LOG: {event} - {data}"
        print(f"LOG: {data['event']} - {data}")

bus = LLMEventBus()
bus.subscribe("llm_call", BillingHandler())
bus.subscribe("llm_call", CacheHandler())
bus.subscribe("llm_call", LogHandler())

bus.publish("llm_call", {
    "event": "llm_call",
    "prompt": "explain this code",
    "response": "Mistral: ...",
    "tokens": 42
})




# Usage attendu
providers = {
    "openai": OpenAIProvider(),
    "claude": ClaudeProvider(),
    "mistral": MistralProvider()
}
router = LLMRouter(providers)
router.route("explain this code")  # → "Mistral: explain this code"


        