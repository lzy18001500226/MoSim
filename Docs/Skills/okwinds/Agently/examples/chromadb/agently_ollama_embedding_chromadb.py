# Support Version: >=4.0.5.6

from agently import Agently
from agently.integrations.chromadb import ChromaData, ChromaEmbeddingFunction
from chromadb import Client as ChromaDBClient

embedding = Agently.create_agent()
embedding.set_settings(
    "OpenAICompatible",
    {
        "model": "qwen3-embedding:0.6b",
        "base_url": "http://127.0.0.1:11434/v1/",
        "auth": "nothing",
        "model_type": "embeddings",
    },
).set_settings("debug", False)

embedding_function = ChromaEmbeddingFunction(embedding_agent=embedding)

chroma_data = ChromaData(
    [
        {
            "document": "Book about Dogs",
            "metadata": {"book_name": "🐶"},
        },
        {
            "document": "Book about cars",
            "metadata": {"book_name": "🚗"},
        },
        {
            "document": "Book about vehicles",
            "metadata": {"book_name": "🚘"},
        },
        {
            "document": "Book about birds",
            "metadata": {"book_name": "🐦‍⬛"},
        },
    ],
)

chromadb = ChromaDBClient()
collection = chromadb.create_collection(
    name="test",
    get_or_create=True,
    metadata={
        "hnsw:space": "cosine",
    },
    configuration={
        "embedding_function": embedding_function,
    },
)

collection.add(**chroma_data.get_kwargs())
print("[ADD]:\n", chroma_data.get_original_data())

result = collection.query(query_texts=["Book about traffic"])
print(result)

# Expected output (requires local Ollama with qwen3-embedding:0.6b):
# [ADD]: [{'document': 'Book about Dogs', ...}, {'document': 'Book about cars', ...}, ...]
# <chromadb query result with car and vehicle entries ranked first for "Book about traffic">
#
# How it works:
# ChromaEmbeddingFunction wraps an Agently embedding agent as a chromadb EmbeddingFunction,
# letting you use the native chromadb client API directly (chromadb.Client) without going
# through ChromaCollection.  ChromaData converts [{document, metadata}] dicts into the
# kwargs format expected by chromadb's collection.add() (documents=, metadatas=, ids=).
# collection.query(query_texts=[...]) delegates embedding to ChromaEmbeddingFunction.
