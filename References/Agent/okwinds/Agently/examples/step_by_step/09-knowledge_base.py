from agently import Agently
from agently.integrations.chromadb import ChromaCollection


## Knowledge Base: Embedding + Retrieval + Answer
def knowledge_base_demo():
    # Embedding agent for vector search
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

    # Build a small knowledge base
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

    # Query the knowledge base
    query = "Things that can move really fast"
    results = collection.query(query)
    print("[retrieval]", results)

    # Use retrieval results in a normal agent response
    agent = Agently.create_agent()
    agent.set_settings(
        "OpenAICompatible",
        {
            "base_url": "http://127.0.0.1:11434/v1",
            "model": "qwen2.5:7b",
        },
    )
    answer = (
        agent.input(query).info({"retrieval_results": results}).instruct("Answer based on {retrieval_results}.").start()
    )
    print("[answer]", answer)


# knowledge_base_demo()

# knowledge_base_demo() is commented out — requires local Ollama with:
#   embedding model: qwen3-embedding:0.6b  (for ChromaDB indexing)
#   chat model:      qwen2.5:7b            (for answering)
#
# Expected output shape:
#   [retrieval] [{'document': 'Book about cars', ...}, {'document': 'Book about vehicles', ...}, ...]
#   [answer]    <model answer mentioning cars/vehicles as fast things>
#
# How it works:
# ChromaCollection wraps a ChromaDB collection.  add([{document, metadata}, …]) embeds
# each document using the embedding_agent and stores the vectors.  query(text) embeds
# the query the same way and returns the closest documents by cosine similarity.
# The retrieved documents are injected into the model request as .info({"retrieval_results":…})
# so the chat model can ground its answer in the retrieved content.
# This is a minimal RAG (Retrieval-Augmented Generation) pattern:
#   embed corpus -> store vectors -> embed query -> retrieve top-k -> inject -> answer.
