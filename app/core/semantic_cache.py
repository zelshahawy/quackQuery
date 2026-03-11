from __future__ import annotations

from typing import Any

import chromadb
from chromadb.config import Settings as ChromaSettings

from app.config import settings


def _get_chroma_client() -> chromadb.Client:
    """Get or create Chroma client."""
    settings.chroma_dir.mkdir(parents=True, exist_ok=True)
    chroma_settings = ChromaSettings(
        chroma_db_impl="duckdb+parquet",
        persist_directory=str(settings.chroma_dir),
        anonymized_telemetry=False,
    )
    return chromadb.Client(chroma_settings)


def _get_collection(table_name: str) -> chromadb.Collection:
    """Get or create collection for a table."""
    client = _get_chroma_client()
    collection_name = f"queries_{table_name}".replace("-", "_")[:63]
    return client.get_or_create_collection(
        name=collection_name, metadata={"hnsw:space": "cosine"}
    )


def get_similar_cached_result(
    question: str, table_name: str, similarity_threshold: float = 0.85
) -> dict[str, Any] | None:
    """Find similar cached question and return its result."""
    try:
        collection = _get_collection(table_name)

        # Query for similar questions
        results = collection.query(
            query_texts=[question], n_results=1, where={"table_name": table_name}
        )

        if results["ids"] and results["ids"][0]:
            # Check similarity score
            distance = results["distances"][0][0]
            similarity = 1 - distance  # Convert distance to similarity

            if similarity >= similarity_threshold:
                metadata = results["metadatas"][0][0]
                return {
                    "question": metadata["question"],
                    "sql": metadata["sql"],
                    "df_json": metadata["df_json"],
                    "similarity": similarity,
                }

        return None
    except Exception as e:
        print(f"Semantic cache query error: {e}")
        return None


def cache_semantic_result(
    question: str, table_name: str, sql: str, df_json: str
) -> None:
    """Cache a query result with semantic embeddings."""
    try:
        collection = _get_collection(table_name)

        # Store with metadata
        collection.add(
            ids=[f"{table_name}_{hash(question) % 10**9}"],
            documents=[question],
            metadatas=[
                {
                    "question": question,
                    "table_name": table_name,
                    "sql": sql,
                    "df_json": df_json,
                }
            ],
        )
    except Exception as e:
        print(f"Semantic cache store error: {e}")


def clear_semantic_cache(table_name: str | None = None) -> None:
    """Clear semantic cache for a table or all tables."""
    try:
        client = _get_chroma_client()
        if table_name:
            collection_name = f"queries_{table_name}".replace("-", "_")[:63]
            client.delete_collection(name=collection_name)
        else:
            # Delete all query collections
            for collection in client.list_collections():
                if collection.name.startswith("queries_"):
                    client.delete_collection(name=collection.name)
    except Exception as e:
        print(f"Semantic cache clear error: {e}")
