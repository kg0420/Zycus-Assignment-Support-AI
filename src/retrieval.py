from pathlib import Path
from typing import List

from rank_bm25 import BM25Okapi


class KnowledgeBaseRetriever:

    def __init__(self, kb_directory: Path):
        self.kb_directory = kb_directory

        self.documents = []
        self.bm25 = None

        self._load_documents()

    def _load_documents(self):
        """
        Load all Markdown files from the knowledge base.
        """

        for file_path in sorted(self.kb_directory.rglob("*.md")):

            text = file_path.read_text(
                encoding="utf-8"
            ).strip()

            if not text:
                continue

            # The assignment recommends using document sections.
            chunks = self._split_document(text)

            for index, chunk in enumerate(chunks):

                self.documents.append(
                    {
                        "id": f"{file_path.stem}_{index}",
                        "source": file_path.name,
                        "text": chunk,
                    }
                )

        if not self.documents:
            raise RuntimeError(
                f"No Markdown documents found in {self.kb_directory}"
            )

        corpus = [
            self._tokenize(doc["text"])
            for doc in self.documents
        ]

        self.bm25 = BM25Okapi(corpus)

    @staticmethod
    def _split_document(text: str) -> List[str]:
        """
        Split documents into useful chunks.

        The supplied assignment recommends using `---`
        as a logical boundary where appropriate.
        """

        chunks = [
            chunk.strip()
            for chunk in text.split("---")
            if chunk.strip()
        ]

        return chunks

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        return text.lower().split()

    def search(
        self,
        query: str,
        top_k: int = 3
    ) -> List[dict]:

        if not query.strip():
            return []

        query_tokens = self._tokenize(query)

        scores = self.bm25.get_scores(query_tokens)

        ranked_indexes = sorted(
            range(len(scores)),
            key=lambda i: scores[i],
            reverse=True
        )

        results = []

        for index in ranked_indexes[:top_k]:

            doc = self.documents[index].copy()

            doc["score"] = float(scores[index])

            results.append(doc)

        return results