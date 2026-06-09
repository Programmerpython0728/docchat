"""Text chunking — recursive character splitting"""
from dataclasses import dataclass


@dataclass
class Chunk:
    content: str
    index: int
    metadata: dict


def chunk_text(
    text: str,
    chunk_size: int = 500,
    overlap: int = 50,
) -> list[Chunk]:
    """
    Recursive chunking — paragraf chegaralarini hurmat qiladi.
    """
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    chunks: list[Chunk] = []
    current = ""
    index = 0

    for para in paragraphs:
        if len(current) + len(para) <= chunk_size:
            current += para + "\n\n"
        else:
            if current:
                chunks.append(Chunk(
                    content=current.strip(),
                    index=index,
                    metadata={"char_count": len(current)},
                ))
                index += 1
                current = current[-overlap:] + para + "\n\n"
            else:
                for i in range(0, len(para), chunk_size - overlap):
                    chunks.append(Chunk(
                        content=para[i:i + chunk_size],
                        index=index,
                        metadata={"char_count": chunk_size},
                    ))
                    index += 1
                current = ""

    if current.strip():
        chunks.append(Chunk(
            content=current.strip(),
            index=index,
            metadata={"char_count": len(current)},
        ))

    return chunks
