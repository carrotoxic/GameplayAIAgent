from __future__ import annotations
from pathlib import Path
from typing import Optional

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from domain.ports.database_port import DatabasePort


class ChromaDatabase(DatabasePort):
    """
    - Save the query as a vector in Chroma
    - Save the result in the content (= page_content) so that it can be retrieved with one query
    """

    def __init__(
        self,
        collection_name: str,
        persist_dir: str | Path = "ckpt/vectordb",
        embedding_model: Optional[object] = None,
        score_threshold: float = 0.05,
        retrieval_top_k: int = 5,
    ) -> None:
        self._persist_dir = Path(persist_dir)
        self._collection_name = collection_name
        self._embeddings = embedding_model or HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        self._vectordb = Chroma(
            collection_name=self._collection_name,
            embedding_function=self._embeddings,
            persist_directory=str(self._persist_dir),
        )
        self._threshold = score_threshold
        self._retrieval_top_k = retrieval_top_k

    # ---------- Count ----------
    def count(self) -> int:
        return len(self._vectordb.get()['documents'])

    # ---------- Query ----------
    def lookup(self, query: str) -> list[str]:
        if self._vectordb._collection.count() == 0:
            return []

        docs_and_scores = self._vectordb.similarity_search_with_score(query, k=self._retrieval_top_k)
        if not docs_and_scores:
            return []

        doc, score = docs_and_scores[0]
        return doc.page_content if score < self._threshold else []

    # ---------- Command ----------
    def store(self, texts: list[str], metadatas: list[dict], ids: list[str] = None) -> None:
        # Save the result in the content (= page_content)
        self._vectordb.add_texts(texts=texts, metadatas=metadatas, ids=ids)

    # ---------- Clear ----------
    def clear(self) -> None:
        """Delete all entries in the Chroma collection."""
        all_docs = self._vectordb.get()
        ids = all_docs.get("ids", [])
        if ids:
            self._vectordb.delete(ids=ids)
