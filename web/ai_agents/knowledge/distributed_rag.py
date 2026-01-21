from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
import numpy as np
from .rag import Document

class VectorStore(ABC):
    """Abstract base for distributed vector storage."""
    
    @abstractmethod
    def add_documents(self, documents: List[Document]):
        pass
        
    @abstractmethod
    def search(self, query_embedding: np.ndarray, k: int = 5) -> List[tuple[Document, float]]:
        pass

    @abstractmethod
    def clear(self):
        pass

class RedisVectorStore(VectorStore):
    """Redis-backed vector store (simulated or using RedisSearch if available)."""
    
    def __init__(self, prefix: str = "ai_knowledge"):
        from django.core.cache import cache
        self.cache = cache
        self.prefix = prefix

    def _gen_key(self, doc_id: str) -> str:
        return f"{self.prefix}:doc:{doc_id}"

    def add_documents(self, documents: List[Document]):
        for doc in documents:
            key = self._gen_key(doc.doc_id)
            data = {
                "content": doc.content,
                "source": doc.source,
                "metadata": doc.metadata,
                "embedding": doc.embedding.tolist() if doc.embedding is not None else None
            }
            self.cache.set(key, data, timeout=None) # Permanent store
            
            # Add to a global list for search
            list_key = f"{self.prefix}:all_ids"
            all_ids = self.cache.get(list_key, [])
            if doc.doc_id not in all_ids:
                all_ids.append(doc.doc_id)
                self.cache.set(list_key, all_ids, timeout=None)

    def search(self, query_embedding: np.ndarray, k: int = 5) -> List[tuple[Document, float]]:
        list_key = f"{self.prefix}:all_ids"
        all_ids = self.cache.get(list_key, [])
        
        results = []
        for doc_id in all_ids:
            data = self.cache.get(self._gen_key(doc_id))
            if not data or data.get("embedding") is None:
                continue
            
            doc_embedding = np.array(data["embedding"])
            # Compute similarity
            score = np.dot(doc_embedding, query_embedding) / (
                np.linalg.norm(doc_embedding) * np.linalg.norm(query_embedding) + 1e-10
            )
            
            doc = Document(
                content=data["content"],
                source=data["source"],
                metadata=data["metadata"],
                doc_id=doc_id
            )
            results.append((doc, float(score)))
            
        # Sort and take top k
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:k]

    def clear(self):
        list_key = f"{self.prefix}:all_ids"
        all_ids = self.cache.get(list_key, [])
        for doc_id in all_ids:
            self.cache.delete(self._gen_key(doc_id))
        self.cache.delete(list_key)
