from __future__ import annotations
import asyncio
from pathlib import Path
from typing import Optional, Sequence

from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from domain.ports.database_port import DatabasePort
from domain.models import Skill
import chromadb
from dataclasses import asdict

class ChromaDatabase(DatabasePort):
    """
    - Save the query as a vector in Chroma
    - Save the result in the content (= page_content) so that it can be retrieved with one query
    """

    def __init__(
        self,
        collection_name: str,
        embedding_model: GoogleGenerativeAIEmbeddings,
        persist_dir: str | Path = "ckpt/vectordb",
        score_threshold: float = 0.5,
        retrieval_top_k: int = 5,
    ) -> None:
        self._persist_dir = Path(persist_dir)
        self._collection_name = collection_name
        self._embeddings = embedding_model
        self._score_threshold = score_threshold
        self._retrieval_top_k = retrieval_top_k
        self._client = None
        self._vectorstore = None
        self._lock = asyncio.Lock()

    async def _initialize(self):
        async with self._lock:
            if self._vectorstore is None:
                # This now runs the synchronous _init_chroma in a thread
                await asyncio.to_thread(self._init_chroma)

    def _init_chroma(self):
        # This is a synchronous method that will be run in a separate thread
        self._client = chromadb.PersistentClient(path=str(self._persist_dir))
        
        collection = self._client.get_or_create_collection(
            name=self._collection_name,
            metadata={"hnsw:space": "cosine"},
        )

        self._vectorstore = Chroma(
            client=self._client,
            collection_name=collection.name, # Use the name from the returned collection
            embedding_function=self._embeddings,
        )

    # --- Interface Methods ---

    def count(self) -> int:
        return 0 

    def lookup(self, key: str) -> str | None:
        return None

    def store(self, key: str, value: str) -> None:
        pass

    async def add(self, documents: Sequence[Skill]):
        await self._initialize()
        texts = [doc.description for doc in documents]
        metadatas = [asdict(doc) for doc in documents]
        ids = [doc.name for doc in documents]
        await asyncio.to_thread(self._vectorstore.add_texts, texts=texts, metadatas=metadatas, ids=ids)

    async def query(self, query: str) -> Sequence[Skill]:
        await self._initialize()
        
        # Check if collection exists and has documents
        collections = await asyncio.to_thread(self._client.list_collections)
        if not any(c.name == self._collection_name for c in collections):
            return []
            
        collection = await asyncio.to_thread(self._client.get_collection, name=self._collection_name)
        if await asyncio.to_thread(collection.count) == 0:
            return []

        docs_and_scores = await asyncio.to_thread(
            self._vectorstore.similarity_search_with_score, query, k=self._retrieval_top_k
        )
        if not docs_and_scores:
            return []
        return [
            Skill(**doc.metadata) for doc, score in docs_and_scores
            if score <= self._score_threshold
        ]

    async def clear(self) -> None:
        await self._initialize()
        # Check if collection exists before trying to delete from it
        collections = await asyncio.to_thread(self._client.list_collections)
        if any(c.name == self._collection_name for c in collections):
             await asyncio.to_thread(self._client.delete_collection, name=self._collection_name)
        
        # After deleting, we must re-initialize to recreate the collection and vectorstore
        self._vectorstore = None
        await self._initialize()

    # ---------- Show All ----------
    def show_all(self) -> None:
        if not self._vectorstore:
            print("Vector store not initialized. Call an async method first.")
            return
        all_data = self._vectorstore.get()
        ids = all_data.get("ids", [])
        documents = all_data.get("documents", [])
        metadatas = all_data.get("metadatas", [])

        for i, (doc, meta) in enumerate(zip(documents, metadatas)):
            print(meta)