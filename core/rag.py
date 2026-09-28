"""RAG : ChromaDB + LangChain. Embeddings locaux par hachage (aucun téléchargement,
fonctionne hors-ligne) — remplaçables par HuggingFaceEmbeddings en production."""
import re
import unicodedata
import zlib
from functools import lru_cache

import numpy as np
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_text_splitters import MarkdownTextSplitter

from core import config


class HashEmbeddings(Embeddings):
    def __init__(self, dim: int = 512):
        self.dim = dim

    def _vec(self, text: str) -> list[float]:
        text = unicodedata.normalize("NFD", text.lower())
        text = "".join(c for c in text if unicodedata.category(c) != "Mn")
        v = np.zeros(self.dim)
        toks = re.findall(r"[a-z0-9]{3,}", text)
        for t in toks + [a + "_" + b for a, b in zip(toks, toks[1:])]:
            v[zlib.crc32(t.encode()) % self.dim] += 1.0
        n = np.linalg.norm(v)
        return (v / n if n else v).tolist()

    def embed_documents(self, texts):
        return [self._vec(t) for t in texts]

    def embed_query(self, text):
        return self._vec(text)


@lru_cache(maxsize=1)
def get_store() -> Chroma:
    store = Chroma(collection_name="mc2_knowledge", embedding_function=HashEmbeddings(),
                   persist_directory=config.CHROMA_DIR)
    if store._collection.count() == 0:
        splitter = MarkdownTextSplitter(chunk_size=700, chunk_overlap=80)
        docs: list[Document] = []
        for f in sorted(config.KNOWLEDGE_DIR.glob("*.md")):
            for chunk in splitter.split_text(f.read_text(encoding="utf-8")):
                docs.append(Document(page_content=chunk, metadata={"source": f.stem}))
        store.add_documents(docs)
    return store


def retrieve(query: str, k: int = 3) -> list[Document]:
    return get_store().similarity_search(query, k=k)
