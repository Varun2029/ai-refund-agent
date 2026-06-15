"""
RAG Policy Store — SentenceTransformers embeddings + FAISS vector search.

Loads policy markdown documents from the ``policies/`` directory, splits them
into overlapping chunks, embeds each chunk with a lightweight transformer
model, and indexes the vectors with FAISS for sub-millisecond retrieval.

Usage::

    from app.rag.policy_store import PolicyStore

    store = PolicyStore.get_instance()
    results = store.query("What is the return window for electronics?")
    for r in results:
        print(r["score"], r["source"], r["text"][:100])
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration constants
# ---------------------------------------------------------------------------

POLICY_DIR = Path(__file__).parent / "policies"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
CHUNK_SIZE = 512
CHUNK_OVERLAP = 50
TOP_K = 5

# ---------------------------------------------------------------------------
# PolicyStore
# ---------------------------------------------------------------------------


class PolicyStore:
    """Singleton vector store backed by FAISS over policy document embeddings.

    On first instantiation the store:

    1. Reads every ``.md`` file from :data:`POLICY_DIR`.
    2. Splits the text into overlapping character-level chunks.
    3. Encodes chunks with *all-MiniLM-L6-v2* (384-dim, ~22 MB).
    4. Builds a FAISS ``IndexFlatIP`` (inner-product ≡ cosine on normalised
       vectors) for exact nearest-neighbour search.

    Subsequent calls to :meth:`get_instance` return the same object.
    """

    _instance: Optional["PolicyStore"] = None

    def __init__(self) -> None:
        # Lazy imports so the module can be imported even if optional
        # dependencies are missing at import-time.
        import faiss  # noqa: WPS433
        from sentence_transformers import SentenceTransformer  # noqa: WPS433

        logger.info(
            "Initialising PolicyStore  model=%s  chunk=%d  overlap=%d",
            EMBEDDING_MODEL,
            CHUNK_SIZE,
            CHUNK_OVERLAP,
        )

        self._model = SentenceTransformer(EMBEDDING_MODEL)
        self._chunks: list[dict] = []
        self._index: Optional[faiss.IndexFlatIP] = None  # type: ignore[name-defined]
        self._build_index()

    # ----- singleton accessor ------------------------------------------------

    @classmethod
    def get_instance(cls) -> "PolicyStore":
        """Return (and lazily create) the singleton :class:`PolicyStore`."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    # ----- public API --------------------------------------------------------

    def query(self, question: str, top_k: int = TOP_K) -> list[dict]:
        """Retrieve the *top_k* most relevant policy chunks for *question*.

        Args:
            question: Natural-language query.
            top_k:    Number of results to return (default :data:`TOP_K`).

        Returns:
            List of dicts with keys ``text``, ``source``, ``offset``,
            and ``score`` (cosine similarity, higher is better).
        """
        if self._index is None or len(self._chunks) == 0:
            logger.warning("PolicyStore has no indexed documents — returning []")
            return []

        q_embedding = self._model.encode(
            [question], normalize_embeddings=True
        )
        scores, indices = self._index.search(
            np.array(q_embedding, dtype=np.float32), top_k
        )

        results: list[dict] = []
        for score, idx in zip(scores[0], indices[0]):
            if 0 <= idx < len(self._chunks):
                chunk = self._chunks[idx].copy()
                chunk["score"] = round(float(score), 4)
                results.append(chunk)

        logger.debug(
            "PolicyStore query  q=%s  top_k=%d  results=%d",
            question[:60],
            top_k,
            len(results),
        )
        return results

    @property
    def chunk_count(self) -> int:
        """Total number of indexed chunks."""
        return len(self._chunks)

    # ----- internals ---------------------------------------------------------

    def _load_policies(self) -> list[dict[str, str]]:
        """Read all ``.md`` files from the policies directory."""
        if not POLICY_DIR.is_dir():
            logger.warning("Policy directory not found: %s", POLICY_DIR)
            return []

        docs: list[dict[str, str]] = []
        for path in sorted(POLICY_DIR.glob("*.md")):
            text = path.read_text(encoding="utf-8")
            docs.append({"source": path.name, "text": text})
            logger.info(
                "Loaded policy  source=%s  length=%d chars",
                path.name,
                len(text),
            )
        return docs

    @staticmethod
    def _chunk_text(text: str, source: str) -> list[dict]:
        """Split *text* into overlapping character-level chunks.

        Each chunk is a dict with keys ``text``, ``source``, and ``offset``
        (character offset into the original document).
        """
        chunks: list[dict] = []
        step = max(CHUNK_SIZE - CHUNK_OVERLAP, 1)

        for offset in range(0, len(text), step):
            snippet = text[offset : offset + CHUNK_SIZE].strip()
            if snippet:
                chunks.append(
                    {"text": snippet, "source": source, "offset": offset}
                )
        return chunks

    def _build_index(self) -> None:
        """Load policies, chunk, embed, and build the FAISS index."""
        import faiss  # noqa: WPS433

        docs = self._load_policies()
        for doc in docs:
            self._chunks.extend(self._chunk_text(doc["text"], doc["source"]))

        if not self._chunks:
            logger.warning("No policy chunks produced — index will be empty")
            return

        texts = [c["text"] for c in self._chunks]
        logger.info("Encoding %d chunks with %s …", len(texts), EMBEDDING_MODEL)
        embeddings = self._model.encode(texts, normalize_embeddings=True)

        dim = embeddings.shape[1]
        self._index = faiss.IndexFlatIP(dim)
        self._index.add(np.array(embeddings, dtype=np.float32))

        logger.info(
            "FAISS index built  dim=%d  vectors=%d",
            dim,
            self._index.ntotal,
        )
