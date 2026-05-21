from agently import Agently
from agently.integrations.chromadb import ChromaCollection

embedding = Agently.create_agent()
embedding.set_settings(
    "OpenAICompatible",
    {
        "model": "qwen3-embedding:0.6b",
        "base_url": "http://127.0.0.1:11434/v1/",
        "auth": "nothing",
        "model_type": "embeddings",
    },
)

collection = ChromaCollection(
    collection_name="demo",
    embedding_agent=embedding,
)

collection.add(
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
    ]
)

results = collection.query("Things that can move really fast")
print(results)

# Expected output (requires local Ollama with qwen3-embedding:0.6b):
# [{'document': 'Book about cars', 'metadata': {'book_name': '🚗'}, ...},
#  {'document': 'Book about vehicles', 'metadata': {'book_name': '🚘'}, ...}, ...]
# (car and vehicle entries rank first for "Things that can move really fast")
#
# How it works:
# ChromaCollection wraps a ChromaDB in-memory collection with an Agently embedding agent.
# add([{document, metadata}]) embeds each document using the embedding endpoint (model_type
# = "embeddings") and stores the vectors.  query(text) embeds the query string the same way
# and returns the top-k nearest documents by cosine similarity.
# The embedding agent uses the same Agently request pipeline as a chat agent but targets
# the embeddings model type instead of chat.
