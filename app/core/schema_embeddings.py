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


def _get_schema_collection() -> chromadb.Collection:
    """Get or create collection for schema embeddings."""
    client = _get_chroma_client()
    return client.get_or_create_collection(
        name="schema_columns", metadata={"hnsw:space": "cosine"}
    )


def index_schema(table_name: str, columns: list[tuple[str, str]]) -> None:
    """Index table schema (column names and types) for semantic search."""
    try:
        collection = _get_schema_collection()

        # Create documents combining column name and type
        documents = []
        ids = []
        metadatas = []

        for col_name, col_type in columns:
            # Create a descriptive document for each column
            doc = f"Column {col_name} of type {col_type}"
            doc_id = f"{table_name}_{col_name}"

            documents.append(doc)
            ids.append(doc_id)
            metadatas.append(
                {
                    "table_name": table_name,
                    "column_name": col_name,
                    "column_type": col_type,
                }
            )

        # Add to collection
        collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
        )
    except Exception as e:
        print(f"Schema indexing error: {e}")


def find_relevant_columns(
    query: str, table_name: str, top_k: int = 5
) -> list[dict[str, Any]]:
    """Find relevant columns for a query using semantic search."""
    try:
        collection = _get_schema_collection()

        # Query for relevant columns
        results = collection.query(
            query_texts=[query], n_results=top_k, where={"table_name": table_name}
        )

        relevant_cols = []
        if results["ids"]:
            for i, col_id in enumerate(results["ids"][0]):
                metadata = results["metadatas"][0][i]
                distance = results["distances"][0][i]
                similarity = 1 - distance

                relevant_cols.append(
                    {
                        "column_name": metadata["column_name"],
                        "column_type": metadata["column_type"],
                        "similarity": similarity,
                    }
                )

        return relevant_cols
    except Exception as e:
        print(f"Schema search error: {e}")
        return []


def get_schema_context(
    query: str, table_name: str, columns: list[tuple[str, str]]
) -> str:
    """Generate schema context for the LLM based on query relevance."""
    # Find relevant columns
    relevant = find_relevant_columns(query, table_name, top_k=10)

    if not relevant:
        # Fallback to all columns if no semantic match
        relevant = [
            {"column_name": col, "column_type": typ, "similarity": 0.5}
            for col, typ in columns
        ]

    # Sort by similarity
    relevant.sort(key=lambda x: x["similarity"], reverse=True)

    # Build context string
    context = "Most relevant columns for this query:\n"
    for item in relevant[:10]:
        context += f"  - {item['column_name']}: {item['column_type']}\n"

    return context


def clear_schema_embeddings(table_name: str | None = None) -> None:
    """Clear schema embeddings for a table or all tables."""
    try:
        collection = _get_schema_collection()
        if table_name:
            # Delete all columns for this table
            results = collection.get(where={"table_name": table_name})
            if results["ids"]:
                collection.delete(ids=results["ids"])
        else:
            # Delete all
            client = _get_chroma_client()
            client.delete_collection(name="schema_columns")
    except Exception as e:
        print(f"Schema clear error: {e}")
