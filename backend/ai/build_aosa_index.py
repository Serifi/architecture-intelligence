from pathlib import Path

import faiss
from sentence_transformers import SentenceTransformer
from pypdf import PdfReader

BACKEND_DIR = Path(__file__).resolve().parents[1]
PDF_PATH = BACKEND_DIR / "resources" / "docs" / "The Architecture Of Open Source Applications.pdf"
INDEX_PATH = BACKEND_DIR / "resources" / "aosa_index.faiss"
CHUNKS_PATH = BACKEND_DIR / "resources" / "aosa_chunks.txt"

EMBED_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def extract_chunks(pdf_path: Path, max_chars: int = 800) -> list[str]:
    reader = PdfReader(str(pdf_path))
    chunks: list[str] = []
    buffer = ""

    for page in reader.pages:
        text = page.extract_text() or ""
        for para in text.split("\n"):
            para = para.strip()
            if not para:
                continue

            if len(buffer) + len(para) + 1 > max_chars:
                if buffer:
                    chunks.append(buffer)
                buffer = para
            else:
                buffer = (buffer + " " + para).strip()

    if buffer:
        chunks.append(buffer)

    return chunks


def main():
    if not PDF_PATH.exists():
        raise FileNotFoundError(f"PDF not found at {PDF_PATH}")

    print(f"[build_aosa_index] Lese PDF: {PDF_PATH}")
    chunks = extract_chunks(PDF_PATH)
    print(f"[build_aosa_index] {len(chunks)} Text-Chunks extrahiert.")

    print("[build_aosa_index] Lade Embedding-Modell …")
    model = SentenceTransformer(EMBED_MODEL_NAME)

    print("[build_aosa_index] Berechne Embeddings …")
    embeddings = model.encode(chunks, show_progress_bar=True)

    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)

    print(f"[build_aosa_index] Speichere Index nach: {INDEX_PATH}")
    faiss.write_index(index, str(INDEX_PATH))

    print(f"[build_aosa_index] Speichere Chunks nach: {CHUNKS_PATH}")
    with open(CHUNKS_PATH, "w", encoding="utf-8") as f:
        for c in chunks:
            f.write(c.replace("\n", " ") + "\n---\n")

    print("[build_aosa_index] Fertig.")


if __name__ == "__main__":
    main()
