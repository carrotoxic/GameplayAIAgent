from __future__ import annotations
from pathlib import Path
from typing import Optional

from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from domain.ports.qa_cache_port import QACachePort


class ChromaQACache(QACachePort):
    """
    - Save the question as a vector in Chroma
    - Save the answer in the content (= page_content) so that it can be retrieved with one query
    """

    _COLLECTION_NAME = "qa_cache_questions_vectordb"

    def __init__(
        self,
        persist_dir: str | Path = "ckpt/curriculum/vectordb",
        embedding_model: Optional[object] = None,
        score_threshold: float = 0.05,
    ) -> None:
        self._persist_dir = Path(persist_dir)
        self._embeddings = embedding_model or HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        self._vectordb = Chroma(
            collection_name=self._COLLECTION_NAME,
            embedding_function=self._embeddings,
            persist_directory=str(self._persist_dir),
        )
        self._threshold = score_threshold

    # ---------- QACachePort ----------
    def lookup(self, question: str) -> str | None:
        if self._vectordb._collection.count() == 0:
            return None

        docs_and_scores = self._vectordb.similarity_search_with_score(question, k=1)
        if not docs_and_scores:
            return None

        doc, score = docs_and_scores[0]
        return doc.page_content if score < self._threshold else None

    def store(self, question: str, answer: str) -> None:
        # Save the answer in the content (= page_content)
        self._vectordb.add_texts(texts=[answer], metadatas=[{"question": question}])
        self._vectordb.persist()
